#!/usr/bin/env python3
"""학습 행위 한 건을 logs/events.jsonl 에 append-only 로 기록.

이 파일은 append 전용이며 통째로 읽지 않는다. 집계는 aggregate_logs.py 가 한다.

예)
  python3 scripts/log_event.py --type recap --chapter 07 --note notes/007-역할책임협력.md
  python3 scripts/log_event.py --type drill --chapter 05 --score 0.6 --tags 결합도,캡슐화
  python3 scripts/log_event.py --type dojo --chapter 07 --tags 의존성역전 --note dojo/07/after.tsx
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "logs" / "events.jsonl"

KNOWN_TYPES = ["pre", "jot", "recap", "dojo", "drill", "log", "retro"]


def append_event(**fields):
    fields = {k: v for k, v in fields.items() if v is not None}
    fields.setdefault("ts", datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"))
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")
    return fields


def main():
    p = argparse.ArgumentParser(description="events.jsonl 에 한 줄 기록")
    p.add_argument("--type", required=True, help=f"종류 (관례: {', '.join(KNOWN_TYPES)})")
    p.add_argument("--chapter", default=None, help="장번호 예: 07")
    p.add_argument("--score", type=float, default=None, help="0.0~1.0")
    p.add_argument("--note", default=None, help="노트/코드 경로")
    p.add_argument("--tags", default=None, help="약점태그 콤마구분 예: 결합도,캡슐화")
    args = p.parse_args()

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    ev = append_event(type=args.type, chapter=args.chapter, score=args.score,
                      note=args.note, tags=tags)
    print("기록:", json.dumps(ev, ensure_ascii=False))


if __name__ == "__main__":
    main()
