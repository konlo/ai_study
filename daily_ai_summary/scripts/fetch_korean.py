#!/usr/bin/env python3
"""Collect Korean AI news without overwriting an existing curated digest."""
import argparse
import datetime as dt
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo

from fetch_summarize import ROOT, fetch_feed, read_sources, select_top_articles, escape, excerpt
import re

AI_TOPIC = re.compile(r'(?<![A-Za-z])AI(?![A-Za-z])|인공지능|생성형|챗GPT|챗지피티|클로드|제미나이|거대언어모델', re.I)


def select_korean(entries, now=None, limit=5):
    now = now if now is not None else dt.datetime.now(dt.timezone.utc).timestamp()
    candidates = [e for e in entries if AI_TOPIC.search(e['title']) and now - 72 * 3600 <= e['timestamp'] <= now]
    ranked = select_top_articles(candidates, limit=len(candidates), now=now)
    selected, seen_sources = [], set()
    # Include the explicitly requested specialist outlets when eligible.
    for source in ('AI타임스', 'ZDNET Korea'):
        match = next((e for e in ranked if e['source'] == source), None)
        if match:
            selected.append(match)
            seen_sources.add(source)
    for entry in ranked:
        if len(selected) >= limit:
            break
        if entry['source'] not in seen_sources:
            selected.append(entry)
            seen_sources.add(entry['source'])
    for entry in ranked:
        if len(selected) >= limit:
            break
        if entry not in selected:
            selected.append(entry)
    return sorted(selected, key=lambda e: e['timestamp'], reverse=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replace', action='store_true', help='Explicitly replace an existing digest, including curated summaries')
    args = parser.parse_args()
    today = dt.datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat()
    output = ROOT / 'site' / 'content' / f'{today}-korea.md'
    if output.exists() and not args.replace:
        raise SystemExit('Existing Korean digest preserved. Use --replace only to intentionally overwrite it.')
    sources = read_sources(ROOT / 'feeds_ko.md')
    with ThreadPoolExecutor(max_workers=4) as pool:
        entries = [e for group in pool.map(fetch_feed, sources) for e in group]
    articles = select_korean(entries)
    if len(articles) < 5:
        raise SystemExit(f'Only {len(articles)} recent AI articles; no output written.')
    lines = ['---', 'layout: page', f'title: "한국 AI 뉴스 · {today}"', f'summary_date: "{today}"',
             'edition: korea', '---', '',
             '한국 언론이 보도한 AI 기사 5개입니다. 최근 72시간의 제목에 AI 키워드가 있는 기사 중 출처 다양성을 우선합니다. 조회수 순위가 아니며, 해외 소식을 다룬 국내 기사도 포함합니다.', '',
             'AI타임스와 ZDNET Korea에 해당 기사가 있으면 우선 포함하고, 다른 매체별 최신 기사를 한 편씩 선정한 뒤 부족한 수를 최신순으로 채웁니다.', '',
             '아래 내용은 RSS 설명을 짧게 발췌한 것입니다.', '',
             '[한국 뉴스 출처 목록]({{ "/sources-korea.html" | relative_url }})', '']
    for article in articles:
        date = dt.datetime.fromtimestamp(article['timestamp'], ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M KST')
        lines += [f"## {escape(article['title'])}", '', f"{escape(article['source'])} · {date}", '',
                  '**RSS 발췌:** ' + escape(excerpt(article['summary'])), '',
                  f'<a href="{escape(article["link"])}">한국어 원문 읽기</a>', '']
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.tmp')
    temporary.write_text('\n'.join(lines), encoding='utf-8')
    temporary.replace(output)
    print(f'Wrote {output}')


if __name__ == '__main__':
    main()
