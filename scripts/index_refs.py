"""refs/toss-ff/raw/ 의 마크다운을 청크로 정규화하고 INDEX.md 를 만든다.

Toss Frontend Fundamentals 문서를 book 과 같은 방식으로 인덱싱한다.
raw/ 아래 디렉터리 이름을 '기준'(가독성/예측가능성/응집도/결합도)으로 본다.
raw/ 는 웹에서 받아 채운다(변환 후 다시 웹을 열지 않는다).

사용
  python3 scripts/index_refs.py
  python3 scripts/index_refs.py --refs refs/toss-ff
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CATEGORY_LABEL = {
    "readability": "가독성",
    "predictability": "예측가능성",
    "cohesion": "응집도",
    "coupling": "결합도",
    "overview": "개요",
    "": "기타",
}


def slugify(title):
    t = re.sub(r"[\s/\\:*?\"<>|]+", "-", title.strip())
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t[:50] or "untitled"


def first_heading(text, fallback):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return fallback


def category_of(rel_parts):
    for part in rel_parts:
        key = part.lower()
        if key in CATEGORY_LABEL:
            return CATEGORY_LABEL[key]
    return CATEGORY_LABEL[""]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs", default=str(ROOT / "refs" / "toss-ff"))
    args = ap.parse_args()

    base = Path(args.refs)
    raw = base / "raw"
    chunks = base / "chunks"
    index = base / "INDEX.md"

    if not raw.exists():
        raise SystemExit(f"raw/ 가 없습니다: {raw}\n먼저 FF 문서를 raw/ 에 채우세요.")

    chunks.mkdir(parents=True, exist_ok=True)
    for old in chunks.glob("*.md"):
        old.unlink()

    md_files = sorted(raw.rglob("*.md"))
    rows = []
    for i, src in enumerate(md_files, 1):
        text = src.read_text(encoding="utf-8")
        rel_parts = src.relative_to(raw).parts[:-1]
        cat = category_of(rel_parts)
        title = first_heading(text, src.stem)
        slug = slugify(title)
        fname = f"{i:03d}-{slug}.md"
        dst = chunks / fname
        origin = src.relative_to(ROOT)
        header = f"# {title}\n\n> 기준: {cat} · 원본: {origin}\n\n"
        dst.write_text(header + text, encoding="utf-8")
        rows.append(f"| {cat} | {title} | {dst.relative_to(ROOT)} |")

    index.write_text(
        "# Toss Frontend Fundamentals — 인덱스\n\n"
        "> 이 파일은 Read 하지 말고 항상 grep 으로 필요한 줄만 뽑는다.\n"
        "> 기준 컬럼으로 필터: 가독성 / 예측가능성 / 응집도 / 결합도\n\n"
        "| 기준 | 제목 | 청크 |\n|---|---|---|\n"
        + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    print(f"완료: 청크 {len(rows)}개 → {chunks}")
    print(f"인덱스: {index}")


if __name__ == "__main__":
    main()
