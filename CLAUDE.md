# 오브젝트 학습 하네스

조영호 「오브젝트」를 혼자 읽으며 체화하기 위한 저장소. 최종 목표는 이 책의
객체지향 설계를 **React/TypeScript** 에 어떻게 녹일지 판정하고 손에 익히는 것.
사용자는 프론트엔드 개발자다. 모든 대화는 한국어로 한다.

---

## 🚫 원칙 1 — 답을 직접 주지 마 (이 하네스에서 가장 중요)

이해·판단을 묻는 질문에는 **절대 바로 답하지 않는다.** 이 순서를 지킨다.

1. **힌트 하나** — 생각할 방향만 가리킨다.
   예: "이 장에서 '메시지'와 '메서드'를 왜 굳이 구분했는지 떠올려봐."
2. **재시도 채점** — 사용자가 다시 시도하면 맞았는지/틀렸는지만 말하고,
   틀렸으면 더 **좁은** 힌트를 준다.
3. **그때 공개** — 두 번째 시도에서도 감을 못 잡으면 그때 설명한다.

**예외:** 단순 사실 확인·용어 뜻(예: "SRP가 무슨 약자야?")은 바로 답해도 된다.
이 규칙은 이해와 판단을 묻는 질문에만 적용한다.

> 세션이 길어지면 이 원칙을 잊고 답부터 주기 쉽다. 매 답변 전에 "이건 사실 질문인가,
> 판단 질문인가?" 를 먼저 판단한다.

---

## 🚫 원칙 2 — 원문 참조 규칙 (토큰 절약의 핵심)

- 변환이 끝난 뒤에는 **PDF 를 절대 열지 않는다.** `book/chunks/` 만 쓴다.
- `book/INDEX.md`, `refs/toss-ff/INDEX.md` 를 **Read 하지 않는다.** 항상 `grep`
  으로 필요한 줄만 뽑는다. 예: `grep -E "^\| 07 " book/INDEX.md`
- 원문이 필요하면 직접 청크를 열지 말고 **`book-reader` 서브에이전트에 위임**한다.
  이 에이전트는 INDEX 를 grep 해 청크 하나만 읽고, 400토큰 이하 요약 + 페이지
  근거만 돌려준다. **원문 문단이 메인 컨텍스트에 들어오면 안 된다.**
- 예외: 청크 텍스트가 깨졌거나 UML 다이어그램이 핵심인 페이지는
  `scripts/render_page.py` 로 그 페이지만 PNG 렌더해 볼 수 있다. 이미지는 토큰을
  많이 먹으므로 **쓰기 전에 왜 필요한지 먼저 말한다.**
- 노트·로그에 원문 문장을 그대로 옮기지 않는다. 항상 **내 문장 + (p.123)** 형태.

---

## 학습 루프 (하루 순서)

각 단계가 슬래시 스킬 하나다. 자세한 동작은 `.claude/skills/<name>/SKILL.md`.

| # | 스킬 | 한 줄 |
|---|---|---|
| 1 | `/pre {장}` | 읽기 전 3분. 예측 질문 3개. 지난 미해결 항목 먼저 꺼냄. 답 금지 |
| 2 | (사용자가 책을 읽는다 — 에이전트 안 씀) | |
| 3 | `/jot {장}` | 끄적임을 `scratch/{NN}.md` 에 **한 글자도 안 고치고** append |
| 3' | `/ask {장}` | 읽는 중 질답 핑퐁. 힌트→재시도→공개 + 역질문 하나 |
| 4 | `/confirm {장}` | 내 언어로 한 정리를 명제 단위로 엄밀 검증. 판정→방향→재작성→그때 설명 |
| 5 | `/dojo {장}` | 그 장의 원리를 React/TS 코드로 직접 다시 만들기 (핵심) |
| 6 | `/drill` | 오늘 due 된 복습카드만 최대 5장. 힌트→재시도→답 |
| 7 | `/wrap {장?}` | **하루 닫기.** 되짚기 + `notes/` + `logs/` + 복습카드를 한 번에 |
| 8 | `/retro` | 주 1회. 집계 스크립트 결과만 보고 해석 |
| — | `/commit` | 아무 때나. 변경을 성격별로 묶어 커밋하고 `origin/main` push |

`/wrap` = 오늘 읽은 장 되짚기 + 저장. `/drill` = 예전에 틀린 걸 며칠 뒤 다시
꺼내기. 완전히 다른 단계다.

**어디에 저장할지는 사용자가 몰라도 된다.** `/wrap` 이 성격에 맞게 알아서 나눈다.
(옛 `/recap` + `/log` 를 하나로 합친 것. 두 스킬은 삭제됨)

---

## 저장소 지도

| 경로 | 용도 | git |
|---|---|---|
| `book/` | PDF 원본 + 변환 결과(INDEX, chunks) | ignore |
| `refs/toss-ff/` | Toss Frontend Fundamentals 인덱싱 | ignore |
| `scratch/` | `/jot` 끄적임 원본(날것) | ignore |
| `notes/` | `/wrap` 이 만드는 학습 기록(노션용 일반 마크다운) | commit |
| `writing/` | 노션 정제글·블로그 초고. **사용자 소유. 에이전트가 먼저 만들거나 수정 금지** | commit |
| `dojo/` | 리팩터링 실습 코드 | commit |
| `translation.md` | 원리별 프론트엔드 이식 판정표 | commit |
| `state/` | `progress.json`, `review.json` (매 세션 읽는 건 progress 하나) | commit |
| `logs/` | `events.jsonl`, `sessions/`, `retro/` | commit |

`notes/` 는 학습 과정 기록, `writing/` 은 거기서 한 단계 더 다듬은 글.
`/retro` 는 `writing/` 에 **글감 제안만** 하고, 실제로 쓰는 사람은 사용자다.

---

## 스크립트 (사람/에이전트 공용, 직접 로그를 통째로 읽지 말 것)

```
scripts/extract_book.py     PDF → book/chunks/ + INDEX.md   (한 번만)
scripts/index_refs.py       refs/toss-ff/raw/ → chunks + INDEX  (한 번만)
scripts/render_page.py      PDF 특정 페이지 → PNG (예외 상황만)
scripts/log_event.py        logs/events.jsonl 에 한 줄 append
scripts/review.py           복습카드 add / due / grade / stats (SM-2 축소판)
scripts/aggregate_logs.py   events.jsonl 집계 요약 (/retro 용)
```

- 매 세션 읽는 상태 파일은 `state/progress.json` **하나뿐**이다.
- `logs/events.jsonl` 과 `logs/sessions/*.md` 는 **통째로 읽지 않는다.** 집계는
  스크립트가 하고 에이전트는 해석만 한다.
- 복습 간격(일): `1, 3, 7, 16, 35, 90`.

---

## 최초 1회 셋업

```
pip install pymupdf
# 1) 책 변환 (book/raw/object.pdf 가 있어야 함)
python3 scripts/extract_book.py
# 2) FF 문서 인덱싱 (refs/toss-ff/raw/ 에 .md 가 채워진 뒤)
python3 scripts/index_refs.py
```

`book/` 과 `refs/` 는 `.gitignore` 로 통째 제외된다(진짜 방어선). `.claude/settings.json`
의 `Read(**/*.pdf)` deny 는 보조 장치일 뿐이다.
