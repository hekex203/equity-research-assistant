# Equity Research Assistant

一个以英伟达 **NVDA** 为默认股票的 Python 研究作品集项目。第一版支持历史行情、收益与风险分析；也可输入其他美股代码。

## 在电脑上运行

需要 Python 3.10 或更新版本。在 GitHub 点击 Code → Download ZIP 并解压，打开终端进入项目目录，然后运行：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Windows 激活命令为 `.venv\Scripts\activate`。运行后打开终端显示的本地网址。仅上传 GitHub 不会自动启动网页。

## 已完成

- 默认跟踪 NVDA，可更换代码及日期
- 股息、拆股调整后的历史日线表和价格图
- 区间收益率、年化波动率、年化 Sharpe、区间最大回撤
- 回撤图和 CSV 导出
- 数据日期、抓取时间、来源及计算口径展示
- 无数据、异常输入及下载失败提示

页面打开/重新执行时读取行情，缓存 15 分钟；点击刷新可重新获取。没有后台定时抓取、实时推送或自动交易。

## 数据与方法

Yahoo Finance 数据由 yfinance 读取，需要网络访问，不需要 API key。数据可用性和服务限流可能影响下载。使用 `auto_adjust=True`，因此显示的是调整价格，不等于原始历史成交价。区间末日包含用户选择的结束日期；非交易日返回最近可用日线。

日简单收益率用于计算；年化假设为 252 个交易日。Sharpe 的无风险利率由用户输入，默认 0%，并非实时国债利率。零波动时 Sharpe 不定义。最大回撤仅考察所选区间，不是上市以来最大回撤。结果未扣交易成本。

## 验证

```bash
python -m unittest discover -s tests -v
```

## 下一步

接入可核验来源的新闻/公告，再加入 AI 研究报告；报告分别列出事实、计算结果、分析和待核验问题。当前版本尚未接入 LLM。

本项目用于学习和研究，历史指标不能预测未来收益。
