#!/usr/bin/env python3

###
# Generates a *.ctx file, usable for "Context" on https://decomp.me.
#
# Usage:
#   python3 tools/decompctx.py src/file.cpp
#
# If changes are made, please submit a PR to
# https://github.com/encounter/dtk-template
###

import argparse
import os
import re

script_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, ".."))
src_dir = os.path.join(root_dir, "src")
include_dir = os.path.join(root_dir, "include")

include_pattern = re.compile(r'^#include\s*[<"](.+?)[>"]$')
guard_pattern = re.compile(r"^#ifndef\s+(.*)$")

defines = set[str]()
quiet = False


def import_h_file(in_file: str, r_path: str) -> str:
    rel_path = os.path.join(root_dir, r_path, in_file)
    inc_path = os.path.join(include_dir, in_file)
    if os.path.exists(rel_path):
        return import_c_file(rel_path)
    elif os.path.exists(inc_path):
        return import_c_file(inc_path)
    else:
        if not quiet:
            print("Failed to locate", in_file)
        exit(1)


def import_c_file(in_file: str) -> str:
    in_file = os.path.relpath(in_file, root_dir)
    out_text = ""

    try:
        with open(in_file, encoding="utf-8") as file:
            out_text += process_file(in_file, list(file))
    except Exception:
        with open(in_file) as file:
            out_text += process_file(in_file, list(file))
    return out_text


def process_file(in_file: str, lines: list[str]) -> str:
    out_text = ""
    for idx, line in enumerate(lines):
        guard_match = guard_pattern.match(line.strip())
        if idx == 0:
            if guard_match:
                if guard_match[1] in defines:
                    break
                defines.add(guard_match[1])
            if not quiet:
                print("Processing file", in_file)
        include_match = include_pattern.match(line.strip())
        if include_match and not include_match[1].endswith(".s"):
            out_text += f'/* "{in_file}" line {idx} "{include_match[1]}" */\n'
            out_text += import_h_file(include_match[1], os.path.dirname(in_file))
            out_text += f'/* end "{include_match[1]}" */\n'
        else:
            out_text += line

    return out_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="""Create a context file which can be used for decomp.me"""
    )
    parser.add_argument(
        "c_file",
        help="""File from which to create context""",
    )
    parser.add_argument(
        "--relative",
        dest="relative",
        help="Extract context relative to the source file",
        action="store_true",
    )
    parser.add_argument(
        "--quiet", dest="quiet", help="Don't print anything", action="store_true"
    )
    args = parser.parse_args()

    global quiet
    quiet = args.quiet
    c_file = args.c_file
    content = import_c_file(c_file)
    filename = (
        f"{c_file}.ctx" if args.relative else os.path.join(root_dir, "context.ctx")
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    main()
