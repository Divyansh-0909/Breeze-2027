#!/usr/bin/env python3
"""Safely apply an extracted Phase 2 checkpoint to a verified Phase 1 project."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def under(root, name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Unsafe manifest path")
    return root / path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True, help="Restored Phase 1 project/ directory")
    parser.add_argument("--overlay", type=Path, default=Path("project"), help="Extract all Phase 2 ZIPs into one directory; this is its project/ child")
    parser.add_argument("--manifest", type=Path, default=Path("recovery-phase2/phase2-file-manifest.json"))
    args = parser.parse_args()
    baseline, overlay = args.base.resolve(), args.overlay.resolve()
    data = json.loads(args.manifest.read_text())
    for row in data["requiredBaselineFiles"]:
        target = under(baseline, row["path"])
        if not target.is_file() or digest(target) != row["sha256"]:
            raise ValueError("Wrong/incomplete protected Phase 1 baseline: " + row["path"])
    pending, identical = [], 0
    # Preflight the ENTIRE overlay before modifying any destination file.
    for row in data["files"]:
        source, target = under(overlay, row["path"]), under(baseline, row["path"])
        if not source.is_file() or source.stat().st_size != row["bytes"] or digest(source) != row["sha256"]:
            raise ValueError("Incomplete/corrupt Phase 2 payload: " + row["path"])
        if target.is_file():
            current = digest(target)
            if current == row["sha256"]:
                identical += 1
                continue
            if current != row.get("beforeSHA256"):
                raise ValueError("Refusing to overwrite unrelated user changes: " + row["path"])
        elif target.exists():
            raise ValueError("Destination is not a regular file: " + row["path"])
        pending.append((source, target))
    for source, target in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".phase2-restoring")
        if temporary.exists():
            raise ValueError("Inspect previous partial restore before proceeding: " + str(temporary))
        # Atomic replacement also preserves any hard-linked Phase 1 reference.
        with source.open("rb") as reader, temporary.open("xb") as writer:
            shutil.copyfileobj(reader, writer)
        temporary.replace(target)
    for row in data["files"]:
        if digest(under(baseline, row["path"])) != row["sha256"]:
            raise ValueError("Final restored checksum mismatch: " + row["path"])
    print(json.dumps({"status": "PASS", "restored": len(pending), "alreadyIdentical": identical,
                      "verifiedFiles": len(data["files"]), "protectedBaseline": True}))


if __name__ == "__main__":
    main()
