import json, argparse, sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional


def load_data(path: Path):
    """
    Load data from JSON and extract ALL relevant data
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    packets = []
    for item in data:
        layers = item["_source"]["layers"]
        frame = layers.get("frame", {})
        usb = layers.get("usb", {})
        payload = layers.get("usbhid.data")

        time = frame.get("frame.time")
        time_sec = parse_time(time) if time else None

        packets.append(
            {
                "time_sec": time_sec,
                "frame_no": int(frame.get("frame.number", -1)),
                "endpoint": usb.get("usb.endpoint_address"),  # "0x01" typically
                "data_len": int(usb.get("usb.data_len", "0")),
                "payload": payload,
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


def extract_hid_payloads(packets: List[dict]) -> List[str]:
    payloads: List[str] = []
    for p in packets:
        if p.get("payload"):
            payloads.append(p["payload"])

    return payloads


def mask_payloads_across_logs(payloads_by_log: List[List[str]]) -> List[str]:
    """playloads_by_log: list of logs, each a list of payload strings (colon-separated)
    Returns: masked payload per packet indes (one masked hex string per packet)
    """
    masked_lines: List[str] = []

    num_packets = min(len(log) for log in payloads_by_log)

    for i in range(num_packets):
        bs: List[bytes] = []
        for log in payloads_by_log:
            bs.append(hex_payload(log[i]))

        min_len = min(len(b) for b in bs)

        out_bytes: List[str] = []
        for j in range(min_len):
            b0 = bs[0][j]
            if all(b[j] == b0 for b in bs):
                out_bytes.append(f"{b0:02x}")
            else:
                out_bytes.append("??")

        masked_lines.append(format_groups(out_bytes, width=16))

    return masked_lines


# ---------- helpers ----------


def parse_time(s: str) -> float:
    """
    Convert time string to unix seconds for relative timing inside a log
    keep microseconds only
    """
    s = s.replace("Z", "")
    if "." in s:
        base, frac = s.split(".")
        frac = (frac + "000000")[:6]
        s = f"{base}.{frac}"
    dt = datetime.fromisoformat(s)
    return dt.timestamp()


def normalize_hex_payload(usbhid_data) -> str:
    """
    Convert a colon-separated hex byte string like:
    "41:0F:00:64: ..."
    into a contiguous lowercase hex string:
    "410f0064..."
    """
    parts = usbhid_data.strip().split(":")
    norm = ""
    for p in parts:
        norm += p
    return norm.lower()


def hex_payload(colon_hex: str) -> bytes:
    return bytes(int(b, 16) for b in colon_hex.split(":"))


def format_groups(byte_tokens: List[str], width: int = 16) -> str:
    lines = []
    for off in range(0, len(byte_tokens), width):
        lines.append(" ".join(byte_tokens[off : off + width]))
    return "\n".join(lines)


# ---------- helpers ----------

log_files = [
    Path("docs/wireshark/init/out_1.json"),
    Path("docs/wireshark/init/out_2.json"),
    Path("docs/wireshark/init/out_3.json"),
    Path("docs/wireshark/init/out_4.json"),
    Path("docs/wireshark/init/out_5.json"),
]

packets = []
for p in log_files:
    packets.append(load_data(p))

payloads = []
for p in packets:
    payload = extract_hid_payloads(p)
    payloads.append(payload)

masked_lines = mask_payloads_across_logs(payloads)
for i in range(len(masked_lines)):
    print(masked_lines[i])
    print()
