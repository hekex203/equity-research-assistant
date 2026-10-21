import unittest
import pandas as pd
from src.metrics import calculate_metrics
from src.research import normalize_news, build_report


class ResearchTests(unittest.TestCase):
    def test_news_shapes_duplicates_and_unsafe_links(self):
        rows = normalize_news([
            {'content': {'title': 'New', 'canonicalUrl': {'url': 'https://example.com/a'}, 'provider': {'displayName': 'Publisher'}, 'pubDate': '2026-10-21'}},
            {'title': 'Old', 'link': 'https://example.com/b', 'publisher': 'Legacy'},
            {'title': 'Duplicate', 'link': 'https://example.com/a'},
            {'title': 'Unsafe', 'link': 'javascript:alert(1)'},
            {'content': 'malformed'}, None])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['publisher'], 'Publisher')
        self.assertEqual(rows[1]['title'], 'Old')

    def test_report_is_explicit_about_missing_news_and_method(self):
        close = pd.Series([100, 100, 100], index=pd.date_range('2026-01-01', periods=3))
        report = build_report('NVDA', close, calculate_metrics(close), 0, '2026-01-04', [], '新闻抓取失败')
        for expected in ['NVDA', '不适用', '新闻抓取失败', '未调用 LLM', '252', '2026-01-03']:
            self.assertIn(expected, report)


if __name__ == '__main__':
    unittest.main()
