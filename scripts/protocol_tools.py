"""
protocol_tools.py

Generic helpers for protocol reverse engineering:
- hex parsing
- masking stable bytes across multiple runs
- formatting and output
"""

from __future__ import annotations

from typing import List

def hex_payload(colon_hex: str) -> bytes:
    """Convert a colon-separated hex byte string into raw bytes."""
    return bytes(int(b, 16) for b in colon_hex.split(":"))


def format_groups(byte_tokens: List[str], width: int = 16) -> str:
    """Format a flat list of byte tokens into fixed-width rows."""
    lines: List[str] = []
    for off in range(0, len(byte_tokens), width):
        lines.append(" ".join(byte_tokens[off : off + width]))
    return "\n".join(lines)


def format_masked_blocks(masked_blocks: List[str]) -> str:
    """Join packet blocks separated by a blank line (nice for side-by-side viewing)."""
    return "\n\n".join(masked_blocks) + "\n"


def mask_payloads_across_logs(payloads_by_log: List[List[str]]) -> List[str]:
    """
    Compute a per-packet mask across multiple logs (aligned by packet index).

    Returns one formatted block per packet index. Identical bytes across all runs
    remain visible; differing bytes become '??'.
    """
    if not payloads_by_log:
        return []

    num_packets = min(len(log) for log in payloads_by_log)
    masked_blocks: List[str] = []

    for i in range(num_packets):
        bs = [hex_payload(log[i]) for log in payloads_by_log]
        min_len = min(len(b) for b in bs)

        out: List[str] = []
        for j in range(min_len):
            b0 = bs[0][j]
            out.append(f"{b0:02x}" if all(b[j] == b0 for b in bs) else "??")

        masked_blocks.append(format_groups(out, width=16))

    return masked_blocks


def iter_mask_tokens(mask_block: str) -> List[str]:
    """
    Convert a formatted mask block back into a flat token list.
    Tokens are like '41', '0f', '??'.
    """
    tokens: List[str] = []
    for line in mask_block.splitlines():
        line = line.strip()
        if not line:
            continue
        tokens.extend(line.split())
    return tokens

def segment_responses(packets: List[dict], window_ms: float = 100.0, k: int = 3):
    out_pkts = [p for p in packets if p.get("endpoint") == "0x01" and p.get("payload")]
    in_pkts = [p for p in packets if p.get("endpoint") == "0x81" and p.get("payload")]

    segments = []
    in_idx = 0

    for outp in out_pkts:
        t0 = outp["time_rel_ms"]
        t1 = t0 + window_ms

        # advance pointer to first in-packet at/after t0
        while in_idx < len(in_pkts) and in_pkts[in_idx]["time_rel_ms"] < t0:
            in_idx += 1

        resp = []
        j = in_idx
        while j < len(in_pkts) and in_pkts[j]["time_rel_ms"] < t1 and len(resp) < k:
            resp.append(in_pkts[j]["payload"])
            j += 1

        segments.append((outp["payload"], resp))

    return segments