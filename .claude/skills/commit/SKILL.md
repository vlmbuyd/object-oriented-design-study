---
name: commit
description: 변경사항을 알아서 파악하고 성격이 같은 것끼리 묶어 커밋한 뒤 push 한다. 트리거 예 "/commit", "커밋해줘", "커밋하고 푸시", "올려줘", "정리해서 커밋", "푸시해줘".
---

# /commit — 묶어서 커밋하고 push

`git status` 를 읽고, 성격이 같은 변경끼리 **여러 개의 커밋으로 나눠** 만든 뒤
`origin` 에 push 한다. 사용자는 무엇이 어느 커밋에 들어가는지 미리 정하지 않아도
된다. **묶는 판단은 이 스킬 책임이다.**

이 저장소는 **개인 학습 저장소**다. `main` 에 직접 커밋하는 것이 기본이고,
브랜치를 새로 파지 않는다.

---

## 절차

### 1. 상태 파악
```
git status --short
git diff --stat
git diff --stat --cached
git log --format="%s" -5
```
새로 생긴 파일(`??`)은 **내용을 확인한다.** 무엇인지 모르는 파일을 커밋하지 않는다.
디렉터리째 `??` 로 잡히면 `git status --short --untracked-files=all` 로 펼쳐 본다.

### 2. 성격별로 묶는다

기본 묶음. 해당 없으면 건너뛴다. 한 묶음에 변경이 하나뿐이어도 그대로 간다.

| 묶음 | 경로 | 커밋 메시지 예 |
|---|---|---|
| 학습 기록 | `notes/`, `logs/`, `state/` | `2장 되짚기 노트 추가` |
| 실습 코드 | `dojo/` | `2장 dojo 할인 정책 다형성 실습` |
| 하네스 설정 | `.claude/`, `CLAUDE.md` | `/wrap 스킬 추가하고 /recap·/log 통합` |
| 스크립트 | `scripts/` | `review.py 간격 계산 수정` |
| 판정표 | `translation.md` | `개방-폐쇄 원칙 프론트 이식 판정 추가` |
| 사용자 글 | `writing/` | `블로그 초고 갱신` |

- **`writing/` 은 항상 단독 커밋.** 사용자 소유라서 다른 변경과 섞지 않는다.
  내용은 **읽기만** 하고 절대 고치지 않는다.
- 학습 기록(`notes` + `logs` + `state`)은 같은 세션 결과물이라 **한 커밋으로 묶는다.**
  나누면 오히려 히스토리가 지저분해진다.
- 위 표에 안 걸리는 게 나오면 성격을 보고 새 묶음을 만든다. 억지로 끼워넣지 않는다.

### 3. 계획을 표로 보여준다
커밋하기 **전에** 한 번, 짧게. 승인을 기다리지는 않는다 — 보여주고 바로 실행한다.

```
1. 2장 되짚기 노트 추가        notes/02-*.md, logs/, state/
2. /wrap 스킬 추가             .claude/skills/wrap/, CLAUDE.md
→ 2개 커밋 후 origin/main push
```

### 4. 커밋
묶음마다 **경로를 명시해서** 스테이징한다.

```
git add notes/ logs/ state/
git commit -m "$(cat <<'EOF'
2장 되짚기 노트 추가

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

커밋 직전 `git status --short` 로 **계획한 것만 스테이징됐는지 확인**한다.

### 5. push
```
git push origin main
```
실패하면 (원격이 앞서 있으면) **`--force` 를 쓰지 않는다.** `git pull --rebase` 를
시도하고, 충돌이 나면 멈추고 사용자에게 상황을 말한다.

### 6. 결과 보고 (짧게)
커밋 해시 + 제목 한 줄씩, push 결과 한 줄. diff 를 다시 붙여넣지 않는다.

---

## 커밋 메시지 규칙

이 저장소의 기존 스타일을 따른다 (`학습 하네스 스캐폴드 구축`,
`dojo React/TS 플레이그라운드 추가`).

- **한국어.** 50자 이내. 마침표 없음
- `feat:` `chore:` 같은 **접두사를 붙이지 않는다**
- 명사형(`~ 추가`, `~ 구축`, `~ 수정`)으로 끝낸다
- **무엇을 했는지**를 쓴다. 파일 이름 나열이 아니라 의미를 쓴다
  - ✗ `SKILL.md 3개 수정`
  - ✓ `/wrap 스킬 추가하고 /recap·/log 통합`
- 본문은 **이유가 필요할 때만.** 대부분은 제목 한 줄로 끝난다
- 끝에 `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` 를 붙인다

## 절대 하지 말 것

- `git add -A`, `git add .` — **경로를 항상 명시한다**
- `git add -f` — `book/`, `refs/`, `scratch/` 는 `.gitignore` 로 막혀 있고
  **저작권·토큰 위생 때문에 절대 커밋하지 않는다**
- `git push --force`, `git reset --hard`, `git rebase -i`
- 새 브랜치 만들기 (개인 학습 저장소다)
- `writing/` 내용 수정
- 커밋 계획 없이 바로 `git commit`

## 멈추고 물어야 할 때

- API 키·토큰·`.env` 처럼 보이는 게 스테이징 대상에 들어올 때
- 삭제(`D`)가 대량으로 잡혔는데 이유를 모를 때
- push 가 충돌로 실패했을 때
- 변경이 하나도 없을 때 → `커밋할 변경 없음` 하고 그냥 끝낸다
