#!/usr/bin/env python3
"""object.pdf 의 특정 페이지를 PNG 로 렌더링한다.

청크 텍스트가 깨졌거나 UML 다이어그램이 핵심인 페이지에서만 예외적으로 사용.
이미지는 토큰을 많이 먹으므로, 쓰기 전에 "왜 필요한지" 를 먼저 밝힌 뒤 렌더한다.

사용
  python3 scripts/render_page.py 123            # 123페이지 → book/_render/p123.png
  python3 scripts/render_page.py 123 130 --dpi 150
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PDF = ROOT / "book" / "raw" / "object.pdf"
OUT_DIR = ROOT / "book" / "_render"


def load_fitz():
    try:
        import fitz
        return fitz
    except ImportError:
        sys.exit("pymupdf 가 필요합니다.  실행:  pip install pymupdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pages", nargs="+", type=int, help="렌더할 페이지 번호(1-index)")
    ap.add_argument("--pdf", default=str(DEFAULT_PDF))
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        sys.exit(f"PDF 가 없습니다: {pdf}")

    fitz = load_fitz()
    doc = fitz.open(pdf)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    written = []
    for pno in args.pages:
        if not (1 <= pno <= doc.page_count):
            print(f"건너뜀: {pno} (범위 1-{doc.page_count})", file=sys.stderr)
            continue
        pix = doc.load_page(pno - 1).get_pixmap(dpi=args.dpi)
        out = OUT_DIR / f"p{pno}.png"
        pix.save(out)
        written.append(out)
        print(f"렌더: {out}")
    doc.close()
    if not written:
        sys.exit("렌더된 페이지 없음")


if __name__ == "__main__":
    main()
