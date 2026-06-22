#!/usr/bin/env python3
"""Xuất ma trận audit nội dung học ra CSV."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Export learning content audit matrix CSV")
    parser.add_argument(
        "-o",
        "--output",
        default=str(ROOT / "docs" / "exports" / "content-matrix.csv"),
        help="Output CSV path",
    )
    args = parser.parse_args()

    from app.db.session import SessionLocal
    from app.data.learning_content_audit import audit_content_matrix, export_matrix_csv

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    try:
        n = export_matrix_csv(db, str(out))
        summary = audit_content_matrix(db)["summary"]
        print(json.dumps({"rows": n, "summary": summary, "path": str(out)}, ensure_ascii=False, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
