"""
trace_mask.py

CLI utility to mask stable bytes across multiple Wireshark HID captures.
"""

from __future__ import annotations

import argparse

from protocol_tools import mask_payloads_across_logs, format_masked_blocks
from dataset import (
    load_init,
    load_change_mode,
    load_payload_runs,
    output_path_init,
    output_path_change,
    write_output,
)


def run_init() -> None:
    payloads = load_payload_runs(load_init())
    masked = mask_payloads_across_logs(payloads)
    text = format_masked_blocks(masked)
    out_path = output_path_init()
    write_output(text, out_path)
    print(f"[ok] written {out_path}")


def run_change(end: str, start: str) -> None:
    payloads = load_payload_runs(load_change_mode(end=end, start=start))
    masked = mask_payloads_across_logs(payloads)
    text = format_masked_blocks(masked)
    out_path = output_path_change(end, start)
    write_output(text, out_path)
    print(f"[ok] written {out_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trace_mask",
        description="Mask stable HID payload bytes across multiple Wireshark JSON runs.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Mask the initialization sequence.")
    p_init.set_defaults(cmd="init")

    p_change = sub.add_parser("change", help="Mask a directed mode transition.")
    p_change.add_argument("--end", required=True, help="Target mode (e.g. absorbance).")
    p_change.add_argument("--start", required=True, help="Source mode (e.g. 405nm).")
    p_change.set_defaults(cmd="change")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.cmd == "init":
        run_init()
    elif args.cmd == "change":
        run_change(end=args.end, start=args.start)
    else:
        raise RuntimeError(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
