"""Run: streamlit run app.py"""
from datetime import date, timedelta, datetime, timezone
import time
import pandas as pd
import streamlit as st
import yfinance as yf
from src.metrics import calculate_metrics

st.set_page_config(page_title='NVDA 股票跟踪', layout='wide')
st.title('NVDA 股票跟踪助手')
st.caption('历史日线 · 收益与风险 · 可下载数据')

@st.cache_data(ttl=900)
def load_prices(ticker, start, end):
    # Cache failures too, so widget changes do not repeatedly hit the provider.
    try:
        frame = yf.Ticker(ticker).history(start=start, end=end, auto_adjust=True, raise_errors=True)
        if frame.empty or 'Close' not in frame:
            return None, None, '没有取得行情，请检查代码和日期。'
        return frame, datetime.now(timezone.utc).isoformat(timespec='seconds'), None
    except Exception:
        return None, None, '行情服务暂时不可用或请求受限，请稍后重试。'

with st.sidebar:
    st.header('跟踪设置')
    ticker = st.text_input('股票代码', 'NVDA').strip().upper()
    start = st.date_input('开始日期', date.today() - timedelta(days=365))
    end = st.date_input('结束日期（包含当天）', date.today())
    rate = st.number_input('假设年化无风险利率（%）', min_value=0.0, max_value=50.0, value=0.0, step=0.25)
    uploaded = st.file_uploader('备用：上传该股票的调整日线 CSV', type=['csv'])
    st.caption('CSV 第一列为日期，价格列使用 Adj Close 或 Close；Close 应为调整价格。')
    refresh = st.button('刷新行情（至少间隔 60 秒）')
if refresh:
    now = time.monotonic()
    if now - st.session_state.get('last_refresh', float('-inf')) >= 60:
        load_prices.clear(ticker, start.isoformat(), (end + timedelta(days=1)).isoformat())
        st.session_state['last_refresh'] = now
    else:
        st.warning('请等待 60 秒后再刷新，频繁刷新可能延长限流。')
if not ticker or start >= end:
    st.info('请输入股票代码，并让开始日期早于结束日期。')
    st.stop()
source = 'Yahoo Finance（通过 yfinance）'
try:
    key = (ticker, start.isoformat(), end.isoformat())
    if uploaded is not None:
        frame = pd.read_csv(uploaded, index_col=0)
        frame.index = pd.to_datetime(frame.index, errors='raise', utc=True)
        frame = frame.loc[(frame.index.date >= start) & (frame.index.date <= end)]
        if 'Adj Close' in frame:
            frame['Close'] = frame['Adj Close']
        if 'Close' not in frame:
            raise ValueError('CSV 缺少 Adj Close 或 Close 列。')
        source = '用户上传 CSV（请确认属于当前股票且为调整价格）'
        retrieved = datetime.now(timezone.utc).isoformat(timespec='seconds')
    else:
        frame, retrieved, error = load_prices(ticker, start.isoformat(), (end + timedelta(days=1)).isoformat())
        if error:
            st.warning(error)
            previous = st.session_state.get('last_success', {}).get(key)
            if previous is None:
                st.info('当前没有可用缓存。可在侧栏上传此前导出的真实价格 CSV 继续分析，或稍后刷新行情。')
                st.stop()
            frame, retrieved = previous
            st.info('正在展示本会话此前成功获取的缓存数据，时间见下方。')
        else:
            st.session_state.setdefault('last_success', {})[key] = (frame.copy(), retrieved)
    frame = frame.sort_index()
    frame = frame.loc[~frame.index.duplicated(keep='last')]
    close = pd.to_numeric(frame['Close'], errors='coerce').dropna()
    metrics = calculate_metrics(close, rate / 100)
except Exception as exc:
    st.error(f'无法完成数据读取或计算：{exc}')
    st.stop()

st.subheader(f'{ticker} · 最近可用日线')
st.write(f'最后数据日期：{close.index[-1].date()} ｜ 获取/导入时间（UTC）：{retrieved}')
st.caption(f'来源：{source}。使用调整价格口径，不是实时行情；当天日线可能尚未完成。')
cols = st.columns(5)
cols[0].metric('最新调整收盘价（USD）', f'{close.iloc[-1]:,.2f}')
cols[1].metric('区间收益率', f'{metrics["total_return"]:.2%}')
cols[2].metric('年化波动率', f'{metrics["annualized_volatility"]:.2%}')
cols[3].metric('年化 Sharpe', '不适用' if metrics['sharpe_ratio'] is None else f'{metrics["sharpe_ratio"]:.2f}')
cols[4].metric('区间最大回撤', f'{metrics["max_drawdown"]:.2%}')
st.subheader('调整收盘价走势')
st.line_chart(close.rename('调整收盘价'))
st.subheader('区间回撤')
st.area_chart((close / close.cummax() - 1).rename('回撤'))
output = frame.copy()
output['Daily Return'] = close.pct_change()
st.subheader('历史价格表')
st.dataframe(output.sort_index(ascending=False), use_container_width=True)
st.download_button('下载本次历史数据 CSV', output.to_csv().encode('utf-8-sig'), f'{ticker}_{start}_{end}.csv', 'text/csv')
with st.expander('指标怎么算？'):
    st.markdown('收益率 = 末日调整价格 / 首日调整价格 − 1。\n\n年化波动率 = 日简单收益率样本标准差 × √252。\n\nSharpe = 日均超额收益 × 252 / 年化波动率；年化无风险利率按复利换算为日利率。\n\n最大回撤 = 调整价格相对区间内此前最高价的最大跌幅。所有指标仅覆盖选定日期，未扣交易成本。')
st.caption('本版本展示历史数据和计算结果，不包含 AI 新闻分析或买卖建议。')
