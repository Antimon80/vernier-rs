import json
from pathlib import Path
from datetime import datetime


def parse_time(s: str) -> float:
    # keep microseconds only
    # convert to unix seconds for relative timing inside a run
    s = s.replace("Z", "")
    if "." in s:
        base, frac = s.split(".")
        frac = (frac + "000000")[:6]
        s = f"{base}.{frac}"
    dt = datetime.fromisoformat(s)
    return dt.timestamp()


def hex_payload(colon_hex: str) -> bytes:
    return bytes(int(b, 16) for b in colon_hex.split(":"))


def load_data(path: Path):
    # load json file end extract relevant data
    data = json.loads(path.read_text(encoding="utf-8"))
    packets = []
    for item in data:
        layers = item["_source"]["layers"]
        frame = layers.get("frame", {})
        usb = layers.get("usb", {})
        payload_s = layers.get("usbhid.data")

        time = frame.get("frame.time")
        time_sec = parse_time(time) if time else None

        packets.append(
            {
                "time_sec": time_sec,
                "frame_no": int(frame.get("frame.number", -1)),
                "endpoint": usb.get("usb.endpoint_address"),  # "0x01" typically
                "data_len": int(usb.get("usb.data_len", "0")),
                "payload": hex_payload(payload_s),
            }
        )
    
    # relative time
    if packets and packets[0]["time_sec"] is not None:
        t0 = packets[0]["time_sec"]
        for p in packets:
            p["time_rel_ms"] = (p["time_sec"] - t0) * 1000.0
    else:
        for p in packets:
            p["time_rel_ms"] = None
    
    return packets

def hex64(b: bytes) -> str:
    return b.hex()

def main():
    log_files = [
        Path("docs/wireshark/init/init_out_1.json"),
        Path("docs/wireshark/init/init_out_2.json"),
        Path("docs/wireshark/init/init_out_3.json"),
        Path("docs/wireshark/init/init_out_4.json"),
        Path("docs/wireshark/init/init_out_5.json")
    ]

    logs = [load_data(p) for p in log_files]

    for _ in enumerate(logs, start=1):
        min_len = min(len(l) for l in logs)
        print(f"\nAligned by index: comparing first {min_len} pacekts across all runs")

        constant_posititons = []
        variable_positions = []

        for idx in range(min_len):
            payloads = [logs[l][idx]["payload"] for l in range(len(logs))]
            if all(p == payloads[0] for p in payloads[1:]):
                constant_posititons.append(idx)
            else:
                variable_positions.append(idx)
        
        print(f"Constant positions: {len(constant_posititons)}")
        print(f"Variable positions: {len(variable_positions)}")

        for idx in variable_positions[:50]:
            payloads = [logs[l][idx]["payload"] for l in range(len(logs))]
            base = payloads[0]
            diff_mask = []
            for b_i in range(len(base)):
                vals = {p[b_i] for p in payloads}
                diff_mask.append(".." if len(vals) == 1 else "XX")
            msg_type = base[0]
            print(f"\nIDX {idx} type=0x{msg_type:02x}")
            print("mask:", " ".join(diff_mask))
            for l_i, p in enumerate(payloads, start=1):
                print(f"log{l_i}:", p.hex())

if __name__ == "__main__":
    main()
