#!/usr/bin/env python3
"""object.pdf 를 장 단위로 쪼개 book/chunks/ 에 저장하고 book/INDEX.md 를 만든다.

한 번만 돌리고 끝. 변환 후에는 PDF 를 다시 열지 않는다(chunks/ 만 사용).

장 경계 잡는 순서 (앞이 우선)
  1) TOC 북마크 중 진짜 장 헤딩 "CHAPTER NN _ 제목" (본문 시작 페이지를 가리킴).
     주의: 책 앞쪽 '인쇄된 목차' 를 가리키는 "NN _ 제목" 항목과 섞이면 안 되므로
     CHAPTER 헤딩을 최우선으로 쓴다.
  2) 그것도 없으면 "N장 제목" / "NN 제목" TOC 항목(폴백).
  3) TOC 자체가 없으면 각 페이지 상단 몇 줄에서 "N장 제목" 패턴을 찾는 폴백.
마지막 장의 끝은 '마치며/부록/찾아보기' 경계에서 자른다(없으면 마지막 페이지).
한 장이 너무 길면(--max-chars 초과) 페이지 경계로 part 를 나눈다.

사용
  pip install pymupdf
  python3 scripts/extract_book.py [--pdf book/raw/object.pdf] [--max-chars 24000]
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
CHUNKS = BOOK / "chunks"
INDEX = BOOK / "INDEX.md"

# 진짜 장 헤딩: "CHAPTER 01 _ 객체, 설계"
CH_HEADING_RE = re.compile(r"^\s*CHAPTER\s+0?(\d{1,2})\s*[_\-:.]?\s*(.*)$", re.I)
# 폴백: "7장 제목" / "07 제목"
CHAPTER_KO_RE = re.compile(r"^\s*(?:Chapter\s*)?0?(\d{1,2})\s*장\s*[_\-:.]?\s*(.*)$", re.I)
NUM_PREFIX_RE = re.compile(r"^\s*0?(\d{1,2})\s*[_\-:.]\s*(\S.*)$")
# 마지막 장 뒤 경계(본문 종료 지점)
BOUNDARY_RE = re.compile(r"^\s*(마치며|부록|찾아보기|색인|참고문헌|INDEX)", re.I)


def load_fitz():
    try:
        import fitz  # PyMuPDF
        return fitz
    except ImportError:
        sys.exit("pymupdf 가 필요합니다.  실행:  pip install pymupdf")


def clean_title(t):
    return re.sub(r"\s+", " ", t.strip().lstrip("_").strip(" _-:.")).strip()


def slugify(title):
    t = re.sub(r"[\s/\\:*?\"<>|]+", "-", clean_title(title))
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t[:50] or "untitled"


def dedup_by_num(entries):
    """(num, title, page0) 목록에서 장번호별 첫 등장만, 페이지순 정렬."""
    seen, uniq = set(), []
    for num, name, pg in sorted(entries, key=lambda x: x[2]):
        if num in seen:
            continue
        seen.add(num)
        uniq.append((num, name, pg))
    return uniq


def chapters_from_headings(toc):
    """1순위: 'CHAPTER NN _ 제목' 진짜 장 헤딩."""
    found = [(int(m.group(1)), clean_title(m.group(2) or title), page - 1)
             for _, title, page in toc
             for m in [CH_HEADING_RE.match(title)] if m]
    return dedup_by_num(found)


def chapters_from_toc_fallback(toc):
    """2순위: 'N장 제목' 또는 'NN _ 제목' TOC 항목."""
    found = []
    for _, title, page in toc:
        m = CHAPTER_KO_RE.match(title) or NUM_PREFIX_RE.match(title)
        if m:
            found.append((int(m.group(1)), clean_title(m.group(2) or title), page - 1))
    return dedup_by_num(found)


def chapters_from_pages(doc, head_lines=6):
    """3순위: TOC 가 없을 때 각 페이지 상단에서 'N장 제목' 스캔."""
    found, seen = [], set()
    for i in range(doc.page_count):
        for line in doc.load_page(i).get_text("text").splitlines()[:head_lines]:
            m = CHAPTER_KO_RE.match(line)
            if m and int(m.group(1)) not in seen:
                num = int(m.group(1))
                seen.add(num)
                found.append((num, clean_title(m.group(2)), i))
                break
    return sorted(found, key=lambda x: x[2])


def last_boundary_page0(toc, last_start0, page_count):
    """마지막 장의 끝(본문 종료). '마치며/부록/찾아보기' 중 장 시작 이후 첫 지점."""
    cands = [page - 1 for _, title, page in toc
             if BOUNDARY_RE.match(title) and (page - 1) > last_start0]
    return min(cands) if cands else page_count


def page_text(doc, i):
    return doc.load_page(i).get_text("text")


def write_chapter(num, name, start, end, doc, max_chars):
    """[start, end) 페이지 범위를 chunk 파일로. 너무 길면 part 분할. INDEX 행 반환."""
    if end <= start:
        return []  # 빈 범위(중복/경계 오류) 방어
    parts, cur, cur_len, cur_pages = [], [], 0, []
    for p in range(start, end):
        txt = page_text(doc, p)
        if cur and cur_len + len(txt) > max_chars:
            parts.append((cur_pages[:], "".join(cur)))
            cur, cur_len, cur_pages = [], 0, []
        cur.append(txt)
        cur_len += len(txt)
        cur_pages.append(p)
    if cur:
        parts.append((cur_pages, "".join(cur)))

    rows = []
    slug = slugify(name or f"{num}장")
    width = len(str(len(parts)))
    for idx, (pgs, body) in enumerate(parts, 1):
        suffix = f"-part{idx:0{width}d}" if len(parts) > 1 else ""
        path = CHUNKS / f"{num:03d}-{slug}{suffix}.md"
        p_from, p_to = pgs[0] + 1, pgs[-1] + 1  # 사람 기준 1-index
        header = f"# {num}장 {name}".rstrip()
        if len(parts) > 1:
            header += f" (part {idx}/{len(parts)})"
        path.write_text(f"{header}\n\n> 원문 pp.{p_from}-{p_to}\n\n{body}", encoding="utf-8")
        rows.append(f"| {num:02d} | {name} | {p_from}-{p_to} | {path.relative_to(ROOT)} |")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default=str(BOOK / "raw" / "object.pdf"))
    ap.add_argument("--max-chars", type=int, default=24000)
    ap.add_argument("--head-lines", type=int, default=6)
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        sys.exit(f"PDF 가 없습니다: {pdf}\nbook/raw/object.pdf 에 원본을 두고 다시 실행하세요.")

    fitz = load_fitz()
    doc = fitz.open(pdf)
    toc = doc.get_toc(simple=True)

    chapters, source = chapters_from_headings(toc), "TOC: CHAPTER 헤딩"
    if not chapters:
        chapters, source = chapters_from_toc_fallback(toc), "TOC: 번호 항목(폴백)"
    if not chapters:
        chapters, source = chapters_from_pages(doc, args.head_lines), "페이지 상단 스캔(폴백)"
    if not chapters:
        sys.exit("장 경계를 찾지 못했습니다. --head-lines 를 늘리거나 목차를 확인하세요.")

    # 경계 목록: 각 장 시작 + 마지막 장의 끝
    ends = [chapters[i + 1][2] for i in range(len(chapters) - 1)]
    ends.append(last_boundary_page0(toc, chapters[-1][2], doc.page_count))

    CHUNKS.mkdir(parents=True, exist_ok=True)
    for old in CHUNKS.glob("*.md"):
        old.unlink()

    index_rows, skipped = [], []
    for (num, name, start), end in zip(chapters, ends):
        rows = write_chapter(num, name, start, end, doc, args.max_chars)
        if rows:
            index_rows += rows
        else:
            skipped.append(num)

    INDEX.write_text(
        "# 오브젝트 — 장 인덱스\n\n"
        f"> 출처: {source}. 이 파일은 Read 하지 말고 항상 grep 으로 필요한 줄만 뽑는다.\n\n"
        "| 장 | 제목 | 페이지 | 청크 |\n|---|---|---|---|\n"
        + "\n".join(index_rows) + "\n",
        encoding="utf-8",
    )
    doc.close()
    kept = sorted({int(r.split('|')[1]) for r in index_rows})
    print(f"완료: {len(chapters)}개 장 감지 → 청크 {len(index_rows)}개 ({source})")
    print(f"장 목록: {kept}")
    if skipped:
        print(f"⚠ 빈 범위로 건너뜀: {skipped}")
    print(f"인덱스: {INDEX}")


if __name__ == "__main__":
    main()
