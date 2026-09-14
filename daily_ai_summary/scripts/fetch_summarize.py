#!/usr/bin/env python3
"""Collect the five latest dated AI feed articles; no paid AI API is used."""
import calendar
import datetime as dt
import html
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import feedparser
import requests

ROOT = Path(__file__).resolve().parents[1]


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        if tag in ('p', 'br', 'div', 'li'):
            self.parts.append(' ')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)
        self.parts.append(' ')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain(value):
    parser = PlainText()
    parser.feed(value)
    return ' '.join(''.join(parser.parts).split())


def read_sources(path):
    sources = []
    for line in path.read_text(encoding='utf-8').splitlines():
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(cells) == 3 and cells[2].startswith('https://'):
            sources.append((cells[0], cells[2]))
    if not sources:
        raise ValueError('No RSS sources configured')
    return sources


def fetch_feed(source):
    name, url = source
    try:
        response = requests.get(url, timeout=(10, 30), headers={'User-Agent': 'DailyAISummary/1.0 RSS reader'})
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        if not feed.entries:
            raise ValueError('No feed entries')
        entries = []
        for entry in feed.entries:
            published = entry.get('published_parsed') or entry.get('updated_parsed')
            link = entry.get('link', '')
            if not published or urlsplit(link).scheme not in ('http', 'https'):
                continue
            entries.append({'title': plain(entry.get('title', '(untitled)')),
                            'link': link, 'source': name,
                            'timestamp': calendar.timegm(published),
                            'summary': plain(entry.get('summary', ''))})
        print(f'{name}: {len(entries)} dated articles', file=sys.stderr)
        return entries
    except (requests.RequestException, ValueError) as exc:
        print(f'WARNING {name}: {exc}', file=sys.stderr)
        return []


def select_top_articles(entries, limit=5, now=None):
    now = now if now is not None else dt.datetime.now(dt.timezone.utc).timestamp()
    selected, seen = [], set()
    for entry in sorted(entries, key=lambda e: e['timestamp'], reverse=True):
        link = entry['link'].split('#')[0]
        if entry['timestamp'] > now or link in seen:
            continue
        seen.add(link)
        selected.append(entry)
        if len(selected) == limit:
            break
    return selected


def excerpt(text):
    # Short attributed feed excerpt; never imply a generated/translated summary.
    words = text.split()
    result = ' '.join(words[:40])
    if len(words) > 40:
        result += '…'
    return result or '요약문이 제공되지 않았습니다. 원문 링크를 확인하세요.'


def escape(text):
    return html.escape(text).replace('|', '&#124;').replace('[', '&#91;').replace(']', '&#93;').replace('{', '&#123;').replace('}', '&#125;')


def main():
    sources = read_sources(ROOT / 'feeds.md')
    with ThreadPoolExecutor(max_workers=4) as pool:
        entries = [e for group in pool.map(fetch_feed, sources) for e in group]
    articles = select_top_articles(entries)
    if len(articles) < 5:
        raise SystemExit(f'Only {len(articles)} valid articles; existing output preserved.')
    today = dt.datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat()
    lines = ['---', 'layout: page', f'title: "AI 뉴스 · {today}"', f'summary_date: "{today}"', '---', '',
             '수집 시점 기준 최신 기사 5개입니다. 발행일은 아래에 표시하며, 오늘 발행된 기사만으로 제한하지 않습니다.', '',
             '요약은 RSS에서 제공한 설명의 짧은 발췌입니다. AI 생성·번역 요약이 아닙니다.', '']
    for article in articles:
        date = dt.datetime.fromtimestamp(article['timestamp'], ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M KST')
        lines += [f"## {escape(article['title'])}", '', f"{escape(article['source'])} · {date}", '',
                  escape(excerpt(article['summary'])), '',
                  f'<a href="{html.escape(article["link"], quote=True)}">원문 읽기</a>', '']
    output = ROOT / 'site' / 'content' / f'{today}.md'
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.tmp')
    temporary.write_text('\n'.join(lines), encoding='utf-8')
    temporary.replace(output)
    print(f'Wrote {output}: {len(articles)} articles')


if __name__ == '__main__':
    main()
