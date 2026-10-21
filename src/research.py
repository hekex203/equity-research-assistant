"""Source-linked news and a reproducible, non-LLM research snapshot."""
from urllib.parse import urlparse


def normalize_news(items):
    """Accept current and legacy yfinance news records; reject unsafe links."""
    result, seen = [], set()
    for item in items or []:
        if not isinstance(item, dict):
            continue
        content = item.get('content') or item
        if not isinstance(content, dict):
            continue
        title = content.get('title')
        canonical = content.get('canonicalUrl') or {}
        url = canonical.get('url') if isinstance(canonical, dict) else None
        url = url or content.get('link')
        if not isinstance(title, str) or not isinstance(url, str):
            continue
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc or url in seen:
            continue
        provider = content.get('provider') or {}
        publisher = provider.get('displayName') if isinstance(provider, dict) else None
        result.append({'title': title, 'url': url,
                       'publisher': publisher or content.get('publisher') or '未提供',
                       'published': str(content.get('pubDate') or content.get('providerPublishTime') or '未提供')})
        seen.add(url)
    return result


def build_report(ticker, close, metrics, rate, retrieved, news, news_status, source='Yahoo Finance / yfinance'):
    sharpe = metrics['sharpe_ratio']
    lines = [f'# {ticker} 股票跟踪简报', '',
             '本简报由程序模板生成，未调用 LLM；新闻仅展示标题和来源，未核验全文。', '',
             '## 行情与计算结果',
             f'- 实际数据区间：{close.index[0].date()} 至 {close.index[-1].date()}',
             f'- 行情抓取时间（UTC）：{retrieved}',
             f'- 数据来源：{source}；调整日线，非实时行情。',
             f'- 最新调整收盘价：{close.iloc[-1]:,.2f} USD',
             f'- 区间收益率：{metrics["total_return"]:.2%}',
             f'- 年化波动率：{metrics["annualized_volatility"]:.2%}',
             '- 年化 Sharpe：' + ('不适用' if sharpe is None else f'{sharpe:.2f}'),
             f'- 区间最大回撤：{metrics["max_drawdown"]:.2%}',
             f'- 假设年化无风险利率：{rate:.2%}；年化按 252 个交易日；未扣交易成本。', '',
             '## 新闻线索（不按行情区间筛选）', f'获取状态：{news_status}']
    for row in news:
        lines.extend([f'- 标题：{row["title"]}', f'  来源：{row["publisher"]}；发布时间：{row["published"]}', f'  原文：{row["url"]}'])
    lines.extend(['', '## 待核验问题',
                  '- 对照公司投资者关系页面和监管公告，核验新闻涉及的财务数字与事件日期。',
                  '- 检查营收增长、利润率、现金流与估值是否支持研究假设。',
                  '- 新闻与价格同时变化不能证明因果关系；本简报不推断涨跌原因。', '',
                  '历史指标不能预测未来收益；本简报用于学习和研究。'])
    return '\n'.join(lines) + '\n'
