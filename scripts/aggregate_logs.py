#!/usr/bin/env python3
"""events.jsonl 를 집계해 요약만 출력한다. /retro 는 이 결과만 읽고 해석한다.

원본 로그를 통째로 컨텍스트에 넣지 않기 위한 스크립트. 기본은 사람이 읽는 요약,
--json 은 기계용.

예)
  python3 scripts/aggregate_logs.py --days 7
  python3 scripts/aggregate_logs.py --days 7 --json
"""
import argparse
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "logs" / "events.jsonl"


def parse_ts(ts):
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def load_events(days):
    if not EVENTS.exists():
        return []
    cutoff = None
    if days:
        cutoff = datetime.now().astimezone() - timedelta(days=days)
    out = []
    for line in EVENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = parse_ts(ev.get("ts", ""))
        if cutoff and ts and ts < cutoff:
            continue
        out.append(ev)
    return out


def aggregate(events):
    by_type = Counter(e.get("type", "?") for e in events)
    chapters = sorted({e["chapter"] for e in events if e.get("chapter")})
    tag_counter = Counter()
    for e in events:
        for t in (e.get("tags") or []):
            tag_counter[t] += 1
    scores = [e["score"] for e in events if isinstance(e.get("score"), (int, float))]
    # 장별 마지막 단계(진도 감각)
    stage_order = {"pre": 0, "jot": 1, "recap": 2, "dojo": 3, "drill": 4, "log": 5}
    furthest = {}
    for e in events:
        ch, ty = e.get("chapter"), e.get("type")
        if ch and ty in stage_order and stage_order[ty] >= stage_order.get(furthest.get(ch, ""), -1):
            furthest[ch] = ty
    return {
        "event_count": len(events),
        "by_type": dict(by_type),
        "chapters_touched": chapters,
        "furthest_stage_per_chapter": furthest,
        "weakness_tags_top": tag_counter.most_common(8),
        "avg_score": round(sum(scores) / len(scores), 2) if scores else None,
        "score_samples": len(scores),
    }


def main():
    p = argparse.ArgumentParser(description="학습 로그 집계 요약")
    p.add_argument("--days", type=int, default=7, help="최근 N일 (0=전체)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    events = load_events(args.days or None)
    summary = aggregate(events)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
        return

    window = "전체" if not args.days else f"최근 {args.days}일"
    print(f"[{window}] 이벤트 {summary['event_count']}건")
    print("단계별:", ", ".join(f"{k}:{v}" for k, v in summary["by_type"].items()) or "-")
    print("다룬 장:", ", ".join(summary["chapters_touched"]) or "-")
    if summary["furthest_stage_per_chapter"]:
        print("장별 최종단계:",
              ", ".join(f"{k}→{v}" for k, v in sorted(summary["furthest_stage_per_chapter"].items())))
    print("약점태그:",
          ", ".join(f"{t}:{n}" for t, n in summary["weakness_tags_top"]) or "-")
    if summary["avg_score"] is not None:
        print(f"평균 점수: {summary['avg_score']} (n={summary['score_samples']})")


if __name__ == "__main__":
    main()
