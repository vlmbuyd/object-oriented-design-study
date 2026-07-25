---
name: drill
description: 오늘 due 된 복습카드만 최대 5장 묻는다. 틀리면 힌트→재시도→답. 맞히면 간격이 벌어지고 틀리면 내일로 리셋. 트리거 예 "/drill", "복습", "오늘 복습", "카드 풀기", "간격 복습".
---

# /drill — 간격 복습

`/recap` 이 "오늘 읽은 장 되짚기" 라면, 이건 "예전에 틀린 것이 며칠 뒤 다시 나오는
것" 이다. 완전히 다른 단계다.

## 절차
1. 오늘 풀 카드를 스크립트로 가져온다. **review.json 을 직접 읽지 않는다.**
   `python3 scripts/review.py due --limit 5 --json`
2. 없으면 "오늘 복습할 카드 없음" 하고 끝낸다.
3. 카드마다 **앞면(front)만** 보여주고 답하게 한다. back 을 먼저 노출하지 않는다.
4. 채점은 원칙 1을 따른다.
   - **맞음** → `python3 scripts/review.py grade <id> good` (간격이 벌어짐)
   - **틀림** → 답을 바로 주지 않는다. **힌트 → 재시도 → (또 틀리면) 답** 순서.
     최종적으로 `python3 scripts/review.py grade <id> again` (내일로 리셋)
   - **애매하게 맞음/오래 걸림** → `grade <id> hard` (같은 간격 유지)
5. 5장을 넘기지 않는다.

## 기록
- 세션 끝에 한 번: `python3 scripts/log_event.py --type drill --score <정답비율> --tags <틀린 원리들>`
  (정답비율 = 맞은 카드 수 / 푼 카드 수)
