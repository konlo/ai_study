import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from fetch_korean import select_korean
from fetch_summarize import entry_timestamp


class KoreanNewsTests(unittest.TestCase):
    def test_aitimes_local_timestamp(self):
        # 2026-09-15 07:00 KST equals 2026-09-14 22:00 UTC.
        from datetime import datetime, timezone
        expected = datetime(2026, 9, 14, 22, tzinfo=timezone.utc).timestamp()
        self.assertEqual(entry_timestamp({'published': '2026-09-15 07:00:00'}, 'AI타임스'), expected)

    def test_specialists_diversity_and_relevance(self):
        now = 300000
        entries = [dict(source=source, title=title, timestamp=stamp, link=f'https://example.com/{i}')
                   for i, (source, title, stamp) in enumerate([
                       ('AI타임스', 'AI 개발 속도', now - 100),
                       ('ZDNET Korea', '인공지능 규칙', now - 90),
                       ('전자신문', '생성형 도구', now - 20),
                       ('동아일보', '클로드 출시', now - 30),
                       ('SBS', '챗GPT 연구', now - 40),
                       ('전자신문', 'AI 후속 기사', now - 10),
                       ('게임', 'Thailand 여행', now - 1),
                       ('오래된매체', 'AI 옛 뉴스', 1),
                       ('미래매체', 'AI 미래 뉴스', now + 100),
                   ])]
        chosen = select_korean(entries, now=now)
        self.assertEqual(len(chosen), 5)
        self.assertEqual({e['source'] for e in chosen}, {'AI타임스', 'ZDNET Korea', '전자신문', '동아일보', 'SBS'})


if __name__ == '__main__':
    unittest.main()
