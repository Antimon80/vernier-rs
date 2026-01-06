"""
trace_mask.py

CLI utility to mask stable bytes across multiple Wireshark HID captures.
This is used for protocol reverse engineering: bytes that are identical in all
runs remain visible, varying bytes are replaced with '??'.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from util import *


def mask_payloads_across_logs(payloads_by_log: List[List[str]]) -> List[str]:
    """
    Compute a per-packet mask across multiple logs.

    Args:
        payloads_by_log:
            A list of logs. Each log is a list of payload strings in colon-separated
            hex format (e.g. '41:0f:00:64:...'), preserving packet order.

    Returns:
        One masked, human-readable block per packet index. For each byte position:
        - if all runs have the same value: keep it (e.g. '4a')
        - otherwise: replace with '??'

    Notes:
        This function aligns packets by index (packet i across all runs).
        It assumes captures are comparable and have the same packet ordering
        for the transition being analyzed.
    """
    masked_lines: List[str] = []

    # Align by packet index: only process indices that exist in all logs.
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


def format_groups(byte_tokens: List[str], width: int = 16) -> str:
    """
    Format a flat list of byte tokens into fixed-width rows for readability.

    Args:
        byte_tokens: Tokens like ['00', '4a', '??', ...]
        width: Number of tokens per row.

    Returns:
        Multi-line string with 'width' tokens per line.
    """
    lines = []
    for off in range(0, len(byte_tokens), width):
        lines.append(" ".join(byte_tokens[off : off + width]))
    return "\n".join(lines)


def format_masked_blocks(masked_blocks: List[str]) -> str:
    """
    Render masked payload blocks into a single text representation.

    Each packet block is separated by a blank line to preserve visual alignment
    when comparing multiple output files side by side.
    """
    return "\n\n".join(masked_blocks) + "\n"


# ---------- run traces ----------


def run_init() -> None:
    log_files = load_init()
    payloads = load_out(log_files)
    masked = mask_payloads_across_logs(payloads)

    text = format_masked_blocks(masked)
    out_path = output_path_init()
    write_output(text, out_path)

    print(f"[ok] written {out_path}")


def rund_change(end: str, start: str) -> None:
    log_files = load_change_mode(end=end, start=start)
    payloads = load_out(log_files)
    masked = mask_payloads_across_logs(payloads)

    text = format_masked_blocks(masked)
    out_path = output_path_change(end, start)
    write_output(text, out_path)

    print(f"[ok] written {out_path}")


# ---------- CLI ----------


def build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI parser with subcommands for different capture sets.
    """
    parser = argparse.ArgumentParser(
        prog="trace_mask",
        description="Mask stable HID payload bytes across multiple Wireshark JSON runs.",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Mask the initialization sequence.")
    p_init.set_defaults(cmde="init")

    p_change = sub.add_parser("change", help="Mask a direct mode transition.")
    p_change.add_argument(
        "--end",
        required=True,
        help="Target mode after the transition (e. g. absorbance).",
    )
    p_change.add_argument(
        "--start",
        required=True,
        help="Source mode before the transition (e. g. 405nm or fluorescence_405nm).",
    )
    p_change.set_defaults(cmd="change")

    return parser


def main() -> None:
    """
    CLI entry point.
    """
    args = build_parser().parse_args()

    if args.cmd == "init":
        run_init()
    elif args.cmd == "change":
        rund_change(end=args.end, start=args.start)
    else:
        raise RuntimeError(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
