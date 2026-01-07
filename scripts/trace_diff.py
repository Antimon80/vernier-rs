"""
trace_diff.py

Compare two masked transitions and report stable byte differences with offsets.
"""

from __future__ import annotations

import argparse
from typing import List, Tuple

from protocol_tools import (
    mask_payloads_across_logs,
    iter_mask_tokens
)
from dataset import (
    load_change_mode,
    load_payload_runs,
    output_path_diff,
    write_output
)


def stable_diff(mask_a: List[str], mask_b: List[str]) -> str:
    """
    Compare two masked traces packet-by-packet and list offsets where both sides
    have stable bytes but with different values.

    Output is human-oriented and suitable for committing as artifacts.
    """
    out_lines: List[str] = []
    n = min(len(mask_a), len(mask_b))

    for i in range(n):
        tok_a = iter_mask_tokens(mask_a[i])
        tok_b = iter_mask_tokens(mask_b[i])
        m = min(len(tok_a), len(tok_b))

        report_id = tok_a[0] if tok_a and tok_a[0] != "??" else "??"

        diffs_stable: List[Tuple[int, str, str]] = []
        diffs_stable_vs_var: List[Tuple[int, str, str]] = []

        for off in range(m):
            a = tok_a[off]
            b = tok_b[off]

            # Case 1: both stable but different
            if a != "??" and b != "??" and a != b:
                diffs_stable.append((off, a, b))

            # Case 2: one stable, the other varies across runs
            elif a != "??" and b == "??":
                diffs_stable_vs_var.append((off, a, b))
            elif a == "??" and b != "??":
                diffs_stable_vs_var.append((off, a, b))

        if diffs_stable or diffs_stable_vs_var:
            out_lines.append(f"packet {i}: report_id={report_id}")

            if diffs_stable:
                out_lines.append("  [stable != stable]")
                for off, a, b in diffs_stable:
                    out_lines.append(f"    offset 0x{off:02x}: A={a}  B={b}")

            if diffs_stable_vs_var:
                out_lines.append("  [stable vs variable across runs]")
                for off, a, b in diffs_stable_vs_var:
                    out_lines.append(f"    offset 0x{off:02x}: A={a}  B={b}")

            out_lines.append("")

    return "\n".join(out_lines).rstrip() + "\n"


def run_diff(a_end: str, a_start: str, b_end: str, b_start: str) -> None:
    a_payloads = load_payload_runs(load_change_mode(end=a_end, start=a_start))
    b_payloads = load_payload_runs(load_change_mode(end=b_end, start=b_start))

    a_mask = mask_payloads_across_logs(a_payloads)
    b_mask = mask_payloads_across_logs(b_payloads)

    text = stable_diff(a_mask, b_mask)
    out_path = output_path_diff(a_end, a_start, b_end, b_start)
    write_output(text, out_path)
    print(f"[ok] written {out_path}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trace_diff", description="Diff two masked transitions."
    )
    p.add_argument("--a-end", required=True)
    p.add_argument("--a-start", required=True)
    p.add_argument("--b-end", required=True)
    p.add_argument("--b-start", required=True)
    return p


def main() -> None:
    args = build_parser().parse_args()
    run_diff(args.a_end, args.a_start, args.b_end, args.b_start)


if __name__ == "__main__":
    main()
