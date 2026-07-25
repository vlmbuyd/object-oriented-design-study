#!/usr/bin/env python3
"""복습 카드 간격 반복(SM-2 축소판).

상태 파일: state/review.json  (사람이 직접 읽지 말 것. 이 스크립트로만 다룬다.)
간격(일): 1, 3, 7, 16, 35, 90

서브커맨드
  add    새 카드 등록          --chapter 07 --front "..." --back "..." [--tags a,b] [--id X]
  due    오늘 풀 카드 목록      [--limit 5] [--json]
  grade  채점                   <card_id> <good|again|hard>
  stats  집계(요약)             [--json]

채점 규칙
  good  : 다음 간격으로 벌어짐 (index+1, 최대치에서 멈춤)
  again : 내일로 리셋          (index=0, 오답 1회 누적)
  hard  : 같은 간격 유지        (index 그대로, 오늘+현재간격)
"""
import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state" / "review.json"
DEFAULT_INTERVALS = [1, 3, 7, 16, 35, 90]


def load():
    if not STATE.exists():
        return {"intervals_days": DEFAULT_INTERVALS, "cards": [], "updated_at": None}
    return json.loads(STATE.read_text(encoding="utf-8"))


def save(data):
    data["updated_at"] = date.today().isoformat()
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def intervals(data):
    return data.get("intervals_days") or DEFAULT_INTERVALS


def next_id(data):
    nums = [int(c["id"].lstrip("c")) for c in data["cards"] if c["id"].lstrip("c").isdigit()]
    return f"c{(max(nums) + 1) if nums else 1:03d}"


def cmd_add(args):
    data = load()
    ivals = intervals(data)
    cid = args.id or next_id(data)
    if any(c["id"] == cid for c in data["cards"]):
        sys.exit(f"이미 존재하는 카드 id: {cid}")
    today = date.today()
    card = {
        "id": cid,
        "chapter": args.chapter,
        "front": args.front,
        "back": args.back,
        "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()],
        "interval_index": 0,
        # 등록 당일에는 /drill 에 안 나오게 첫 간격만큼 뒤로. (recap 당일 재출제 방지)
        "due": (today + timedelta(days=ivals[0])).isoformat(),
        "created": today.isoformat(),
        "reps": 0,
        "lapses": 0,
    }
    data["cards"].append(card)
    save(data)
    print(f"등록: {cid} (장 {args.chapter}) due {card['due']}")


def cmd_due(args):
    data = load()
    today = date.today().isoformat()
    due = [c for c in data["cards"] if c["due"] <= today]
    due.sort(key=lambda c: (c["due"], c["id"]))
    if args.limit:
        due = due[: args.limit]
    if args.json:
        print(json.dumps(due, ensure_ascii=False))
        return
    if not due:
        print("오늘 풀 카드 없음.")
        return
    for c in due:
        tags = f" [{', '.join(c['tags'])}]" if c["tags"] else ""
        print(f"{c['id']} (장 {c['chapter']}){tags}\n  Q. {c['front']}")


def cmd_grade(args):
    data = load()
    ivals = intervals(data)
    card = next((c for c in data["cards"] if c["id"] == args.card_id), None)
    if not card:
        sys.exit(f"카드 없음: {args.card_id}")
    today = date.today()
    g = args.grade
    if g == "good":
        card["interval_index"] = min(card["interval_index"] + 1, len(ivals) - 1)
        card["reps"] += 1
    elif g == "hard":
        card["reps"] += 1
    elif g == "again":
        card["interval_index"] = 0
        card["lapses"] += 1
    else:
        sys.exit("grade 는 good | again | hard 중 하나")
    step = ivals[card["interval_index"]]
    card["due"] = (today + timedelta(days=step)).isoformat()
    save(data)
    print(f"{card['id']}: {g} → 다음 복습 {card['due']} (간격 {step}일)")


def cmd_stats(args):
    data = load()
    today = date.today().isoformat()
    cards = data["cards"]
    by_chapter, by_tag = {}, {}
    due_now = 0
    for c in cards:
        by_chapter[c["chapter"]] = by_chapter.get(c["chapter"], 0) + 1
        if c["due"] <= today:
            due_now += 1
        for t in c["tags"]:
            by_tag[t] = by_tag.get(t, 0) + 1
    lapses = sorted(cards, key=lambda c: c["lapses"], reverse=True)
    weak = [{"id": c["id"], "chapter": c["chapter"], "lapses": c["lapses"], "front": c["front"]}
            for c in lapses if c["lapses"] > 0][:5]
    out = {
        "total": len(cards),
        "due_now": due_now,
        "by_chapter": by_chapter,
        "by_tag": by_tag,
        "weakest": weak,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
        return
    print(f"카드 {out['total']}개 / 오늘 풀 것 {out['due_now']}개")
    print("장별:", ", ".join(f"{k}:{v}" for k, v in sorted(by_chapter.items())) or "-")
    print("약점태그:", ", ".join(f"{k}:{v}" for k, v in sorted(by_tag.items(), key=lambda x: -x[1])) or "-")
    if weak:
        print("자주 틀림:")
        for w in weak:
            print(f"  {w['id']} (장 {w['chapter']}, {w['lapses']}회) {w['front']}")


def main():
    p = argparse.ArgumentParser(description="복습 카드 간격 반복(SM-2 축소판)")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("--chapter", required=True)
    a.add_argument("--front", required=True)
    a.add_argument("--back", required=True)
    a.add_argument("--tags", default="")
    a.add_argument("--id", default=None)
    a.set_defaults(func=cmd_add)

    d = sub.add_parser("due")
    d.add_argument("--limit", type=int, default=None)
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=cmd_due)

    g = sub.add_parser("grade")
    g.add_argument("card_id")
    g.add_argument("grade", choices=["good", "again", "hard"])
    g.set_defaults(func=cmd_grade)

    s = sub.add_parser("stats")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_stats)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
