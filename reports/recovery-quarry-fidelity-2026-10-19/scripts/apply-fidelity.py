#!/usr/bin/env python3
"""Safely apply an extracted fidelity-correction checkpoint to a verified Phase 1 + Phase 2 + Phase 3 project."""
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
    target = root / path
    if target.is_symlink() or any(parent.is_symlink() for parent in target.parents if parent != root and root in parent.parents):
        raise ValueError("Refusing symlink in restore destination: " + name)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True, help="Restored Phase 3 project/ directory")
    parser.add_argument("--overlay", type=Path, default=Path("project"), help="Extract all fidelity ZIPs into one directory; this is its project/ child")
    parser.add_argument("--manifest", type=Path, default=Path("recovery-fidelity/fidelity-file-manifest.json"))
    args = parser.parse_args()
    baseline, overlay = args.base.resolve(), args.overlay.resolve()
    data = json.loads(args.manifest.read_text())
    for row in data["requiredBaselineFiles"]:
        target = under(baseline, row["path"])
        if not target.is_file() or digest(target) != row["sha256"]:
            raise ValueError("Wrong/incomplete protected Phase 1 + Phase 2 + Phase 3 baseline: " + row["path"])
    pending, identical = [], 0
    # Preflight the ENTIRE overlay before modifying any destination file.
    for row in data["files"]:
        source, target = under(overlay, row["path"]), under(baseline, row["path"])
        if not source.is_file() or source.stat().st_size != row["bytes"] or digest(source) != row["sha256"]:
            raise ValueError("Incomplete/corrupt fidelity payload: " + row["path"])
        if target.is_file():
            current = digest(target)
            if current == row["sha256"]:
                identical += 1
                continue
            if current != row.get("beforeSHA256"):
                raise ValueError("Refusing to overwrite unrelated user changes: " + row["path"])
        elif target.exists():
            raise ValueError("Destination is not a regular file: " + row["path"])
        temporary = target.with_name(target.name + ".fidelity-restoring")
        if temporary.exists():
            raise ValueError("Inspect previous partial restore before proceeding: " + str(temporary))
        pending.append((source, target))
    for source, target in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".fidelity-restoring")
        if temporary.exists():
            raise ValueError("Inspect previous partial restore before proceeding: " + str(temporary))
        # Atomic replacement also preserves any hard-linked Phase 1 + Phase 2 + Phase 3 reference.
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
