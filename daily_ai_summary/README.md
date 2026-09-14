# Daily AI Summary

AI RSS에서 최신 기사 5개를 수집해 날짜별 Markdown과 Jekyll 사이트로 제공합니다.
요약은 RSS 설명의 최대 40단어 발췌이며, AI 생성·한국어 번역은 하지 않습니다. API 키는 필요 없습니다.

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
