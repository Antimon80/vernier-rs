import json
from pathlib import Path
from datetime import datetime
from typing import List

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LOAD_DIR = Path("docs/wireshark/spectrovis/json_files")
OUTPUT_DIR = PROJECT_ROOT / "docs" / "protocol"
MODE = {
    "405nm": "fluorescence_405nm",
    "500nm": "fluorescence_500nm",
}


def load_data(path: Path):
    """
    Load a Wireshark-exported JSON file and extract the relevant USB/HID
    packet fields into a flat, analysis-friendly structure.

    Computes a per-log relative timestamp (milliseconds) based on the first
    packet to allow temporal alignment within a single capture.
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
    """
    Extract the raw HID payload strings from a list of parsed packet records,
    preserving packet order and discarding packets without HID data.
    """
    payloads: List[str] = []
    for p in packets:
        if p.get("payload"):
            payloads.append(p["payload"])

    return payloads


def parse_time(s: str) -> float:
    """
    Parse an ISO 8601 timestamp string as used by Wireshark and convert it
    to Unix time (seconds since epoch), preserving microsecond precision.

    Used to derive relative timing within a single capture.
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
    Normalize a colon-separated hex byte string (e.g. '41:0F:00:64')
    into a contiguous lowercase hex string without separators.

    Intended for comparisons, hashing, or textual diffing of payloads.
    """
    parts = usbhid_data.strip().split(":")
    norm = ""
    for p in parts:
        norm += p
    return norm.lower()


def hex_payload(colon_hex: str) -> bytes:
    """
    Convert a colon-separated hex byte string into a raw bytes object.

    Useful for byte-wise comparisons and protocol-level analysis.
    """
    return bytes(int(b, 16) for b in colon_hex.split(":"))


def load_out(log_files) -> List[List[str]]:
    """
    Load multiple Wireshark JSON log files and extract the ordered HID
    payload sequences for each log.

    Returns a list of payload lists, one per capture, suitable for
    cross-run comparison and masking.
    """
    packets = []
    for p in log_files:
        packets.append(load_data(p))

    payloads = []
    for p in packets:
        payload = extract_hid_payloads(p)
        payloads.append(payload)

    return payloads


# ---------- path to log files ----------


def list_runs(path: Path, pattern: str = "out_*.json") -> List[Path]:
    """
    List and sort all log files in a directory matching the given pattern.

    Raises an error if no matching files are found to avoid silent mis-analysis.
    """
    files = sorted(path.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No log files found in dir: {path}")
    return files


def mode_alias(mode: str) -> str:
    """
    Normalize shorthand or user-facing mode names to their canonical
    directory names used in the dataset.
    """
    return MODE.get(mode, mode)


def load_init() -> List[Path]:
    """
    Load all capture files belonging to the device initialization sequence.
    """
    path = LOAD_DIR / "init"
    return list_runs(path)


def load_change_mode(end: str, start: str) -> List[Path]:
    """
    Load all capture files for a directed operating-mode transition.

    'start' denotes the previous device mode,
    'end' denotes the resulting device mode after the transition.

    The direction of the transition is significant and preserved.
    """
    end = mode_alias(end)
    start = mode_alias(start)
    path = LOAD_DIR / "change_mode" / end / start

    return list_runs(path)

# ---------- output ----------

def write_output(text: str, path: Path) -> None:
    """
    Write the given text to a UTF-8 encoded file, creating parent directories
    if necessary.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def output_path_init() -> Path:
    return OUTPUT_DIR / "trace_mask" / "init.txt"

def output_path_change(end: str, start: str) -> Path:
    return OUTPUT_DIR / "trace_mask" / f"change_{end}_from_{start}.txt"
