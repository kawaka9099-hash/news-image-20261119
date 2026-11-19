#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261119.

Copies the pre-rendered front page (entry.png, drawn by draw.py in this same
repository) to /output/entry.png. Standard library only, no network, fully
deterministic: the output bytes are exactly the input bytes, so two runs
always produce identical output.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    with open(src, "rb") as fin:
        data = fin.read()
    # sanity: must be a real PNG, and within the competition's 1 MiB cap
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a PNG file")
    if len(data) > 1024 * 1024:
        raise SystemExit("entry.png is over the 1 MiB cap")
    os.makedirs("/output", exist_ok=True)
    dst = os.path.join("/output", "entry.png")
    with open(dst, "wb") as fout:
        fout.write(data)
    print("wrote %s (%d bytes)" % (dst, len(data)))


if __name__ == "__main__":
    main()
