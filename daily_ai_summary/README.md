# Daily AI Summary

AI RSS에서 최신 기사 5개를 수집해 날짜별 Markdown과 Jekyll 사이트로 제공합니다.
수집 스크립트는 RSS 설명의 최대 40단어 발췌를 만듭니다. 아래 스킬로 실행하면 Codex가 한국어 요약·해외 번역을 보완합니다. 기본 흐름에 별도 AI API 키는 필요 없습니다.

## 실행

저장소 루트에서 Python 3.12 이상을 권장합니다.

```sh
python3 -m venv .venv
.venv/bin/pip install -r daily_ai_summary/requirements.txt
.venv/bin/python daily_ai_summary/scripts/fetch_summarize.py
.venv/bin/python -m unittest discover -s daily_ai_summary/tests -v
```

- `sources.md`: 원래 조사한 참고 출처 10개
- `feeds.md`: 실제 수집하는 AI 전용 RSS 3개
- `site/content/YYYY-MM-DD.md`: 한국 시간 기준 수집일별 결과
- `site/index.md`: 최신 요약과 날짜별 기록

발행일이 없는 기사와 미래 기사는 제외하고 URL 중복을 제거합니다. 오늘 발행된 기사만으로 제한하지 않습니다.
일부 출처가 실패해도 나머지 출처를 사용하며, 유효한 기사가 5개 미만이면 오류로 종료하고 기존 파일을 보존합니다.
같은 날짜에 다시 실행하면 해당 날짜 파일이 갱신됩니다. 발행일 정렬은 언론사 RSS 데이터에 따릅니다.

## GitHub Pages

`main`에 push하면 `.github/workflows/pages.yml`이 테스트와 Jekyll 빌드를 실행합니다.
GitHub Pages의 Source를 GitHub Actions로 설정한 뒤 저장소 Actions 변수 `PAGES_ENABLED=true`를 설정하면 배포합니다.
현재 URL 설정은 `https://konlo.github.io/ai_study`입니다.

비공개 저장소는 Pages를 지원하는 유료 요금제가 필요합니다. 무료 요금제로 공개하려면 저장소 공개 전환이 필요합니다.
자동 수집 일정은 아직 설정하지 않았습니다. 수집 스크립트를 실행하고 결과를 커밋·push하면 페이지가 갱신됩니다.

`.env`는 Git 추적에서 제외합니다. 토큰을 코드, 문서, 워크플로에 넣지 마세요.

## 한국 뉴스

```sh
.venv/bin/python daily_ai_summary/scripts/fetch_korean.py
```

`feeds_ko.md`의 국내 RSS 6개를 조회하고 AI 관련 제목의 최근 72시간 기사 중 매체 다양성을 고려해 5개를 골라 `site/content/YYYY-MM-DD-korea.md`로 저장합니다.
AI타임스와 ZDNET Korea에 조건을 만족하는 기사가 있으면 우선 포함합니다. 목록과 선정 근거는 `site/sources-korea.md`에 있습니다.
스크립트는 RSS 발췌를 만들며, 이번 2026-09-15 한국판은 그 설명을 바탕으로 AI가 한국어 요약을 별도 작성했습니다.
이미 저장된 한국판은 기본적으로 덮어쓰지 않습니다. `--replace`는 편집한 요약도 대체하므로 의도적으로 다시 수집할 때만 사용합니다.
해외판 수집 스크립트는 기존대로 같은 날짜 파일을 덮어쓰므로 번역된 파일을 재생성할 때 주의하세요.
한국 뉴스와 해외 뉴스는 메인 페이지에서 구분됩니다. RSS 상태와 순위가 아닌 선정 기준을 공개합니다.


## 스킬로 시작하기

개인 스킬 `daily-ai-news`를 설치한 후, Codex에서 이 저장소를 열고 다음을 입력합니다.

```text
$daily-ai-news 오늘 국내·해외 AI 뉴스를 각각 5개씩 요약하고 해외 기사에는 한국어 번역을 함께 저장한 뒤 배포해줘.
```

한국 뉴스만 필요하면:

```text
$daily-ai-news 오늘 한국 뉴스 5개만 요약해서 저장해줘. 배포는 하지 마.
```

스킬 원본은 [skills/daily-ai-news/SKILL.md](../skills/daily-ai-news/SKILL.md)입니다.
다른 컴퓨터에서는 이 저장소 루트에서 아래 명령으로 설치합니다. 같은 이름의 기존 개인 스킬이 있으면 먼저 내용을 비교해 필요한 변경만 반영하세요.

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/daily-ai-news "${CODEX_HOME:-$HOME/.codex}/skills/"
```

스킬 선택 목록에 아직 나타나지 않으면 새 작업에서 확인하거나 `skills/daily-ai-news/SKILL.md를 읽고 오늘 국내·해외 뉴스를 요약해줘`라고 직접 요청할 수 있습니다.
호출 한 번에 한 차례 실행합니다. 스킬 설치 자체는 매일 자동 실행 예약을 만들지 않습니다.
임시 폴더에서 기사를 수집하므로 기존에 편집한 요약·번역을 수집 단계에서 덮어쓰지 않습니다.
