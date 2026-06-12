#!/usr/bin/env python3
"""Fetch OncoTree tumor types and write a normalized oncotree_file.txt TSV.

Uses the flat /api/tumorTypes endpoint. Each row is one tumor type with fixed
level_N columns and trailing metadata (metamaintype, metacolor, etc.).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.request

API_URL = "https://oncotree.mskcc.org/api/tumorTypes?version={version}"
DEFAULT_VERSION = "oncotree_latest_stable"
DEFAULT_MAX_LEVELS = 7
METADATA_COLUMNS = ["metamaintype", "metacolor", "metanci", "metaumls", "history"]


def fetch_tumor_types(version: str) -> list[dict]:
    url = API_URL.format(version=version)
    try:
        with urllib.request.urlopen(url) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"OncoTree API request failed ({exc.code}): {url}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"OncoTree API request failed: {exc}") from exc


def build_ancestry(by_code: dict[str, dict], code: str) -> list[str]:
    path = []
    while code and code in by_code:
        node = by_code[code]
        path.append(f"{node['name']} ({node['code']})")
        code = node.get("parent")
        if code == "TISSUE":
            break
    return list(reversed(path))


def first_ref(refs: dict, key: str) -> str:
    values = refs.get(key) or []
    return values[0] if values else ""


def node_to_row(node: dict, by_code: dict[str, dict], max_levels: int) -> list[str]:
    levels = build_ancestry(by_code, node["code"])
    levels.extend([""] * (max_levels - len(levels)))
    refs = node.get("externalReferences") or {}
    history = ";".join(node.get("history") or [])
    return levels[:max_levels] + [
        node.get("mainType") or "",
        node.get("color") or "",
        first_ref(refs, "NCI"),
        first_ref(refs, "UMLS"),
        history,
    ]


def write_oncotree_tsv(
    nodes: list[dict],
    output,
    max_levels: int = DEFAULT_MAX_LEVELS,
) -> None:
    by_code = {node["code"]: node for node in nodes}
    header = [f"level_{i}" for i in range(1, max_levels + 1)] + METADATA_COLUMNS
    writer = csv.writer(output, delimiter="\t", lineterminator="\n")
    writer.writerow(header)
    for node in sorted(nodes, key=lambda n: (n.get("level", 0), n.get("name", ""))):
        writer.writerow(node_to_row(node, by_code, max_levels))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export normalized oncotree_file.txt from the OncoTree tumorTypes API.",
    )
    parser.add_argument(
        "-v",
        "--version",
        default=DEFAULT_VERSION,
        help=f"OncoTree version tag (default: {DEFAULT_VERSION})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="-",
        help="Output TSV path (default: stdout)",
    )
    parser.add_argument(
        "--max-levels",
        type=int,
        default=DEFAULT_MAX_LEVELS,
        help=f"Number of level_N columns (default: {DEFAULT_MAX_LEVELS})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    nodes = fetch_tumor_types(args.version)
    if args.output == "-":
        write_oncotree_tsv(nodes, sys.stdout, args.max_levels)
    else:
        with open(args.output, "w", newline="", encoding="utf-8") as handle:
            write_oncotree_tsv(nodes, handle, args.max_levels)


if __name__ == "__main__":
    main()
