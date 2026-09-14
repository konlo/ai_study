import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('fetch', Path(__file__).resolve().parents[1] / 'scripts/fetch_summarize.py')
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)


class FeedTests(unittest.TestCase):
    def test_markdown_trailing_pipe(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'feeds.md'
            path.write_text('| 출처 | 범위 | RSS URL |\n| Example | AI | https://example.com/feed |\n')
            self.assertEqual(fetch.read_sources(path), [('Example', 'https://example.com/feed')])

    def test_latest_unique_without_future_articles(self):
        entries = [{'link': link, 'timestamp': timestamp} for link, timestamp in
                   [('https://a', 10), ('https://b', 20), ('https://b#ref', 20), ('https://future', 40)]]
        self.assertEqual([e['link'] for e in fetch.select_top_articles(entries, now=30)], ['https://b', 'https://a'])

    def test_html_and_template_content_is_inert(self):
        self.assertEqual(fetch.plain('<p>Hello <b>world</b></p><script>bad()</script>'), 'Hello world')
        self.assertNotIn('{', fetch.escape('{{ site.secret }}'))
        self.assertNotIn('<', fetch.escape('<script>'))

    def test_excerpt_word_limit(self):
        self.assertEqual(len(fetch.excerpt(' '.join(['word'] * 100)).split()), 40)


if __name__ == '__main__':
    unittest.main()
