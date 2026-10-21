"""Metrics from split/dividend-adjusted daily closing prices."""
import math
import pandas as pd


def calculate_metrics(prices, risk_free_rate=0.0):
    prices = pd.Series(prices, dtype=float).dropna()
    if len(prices) < 3 or not prices.gt(0).all() or not prices.map(math.isfinite).all():
        raise ValueError('至少需要三个有效、正数价格。')
    if not math.isfinite(risk_free_rate) or risk_free_rate <= -1:
        raise ValueError('无风险利率必须为有限值且大于 -100%。')
    returns = prices.pct_change().dropna()
    volatility = float(returns.std(ddof=1) * math.sqrt(252))
    daily_rf = (1 + risk_free_rate) ** (1 / 252) - 1
    sharpe = float((returns.mean() - daily_rf) * 252 / volatility) if volatility > 1e-12 else None
    drawdown = prices / prices.cummax() - 1
    return {
        'total_return': float(prices.iloc[-1] / prices.iloc[0] - 1),
        'annualized_volatility': volatility,
        'sharpe_ratio': sharpe,
        'max_drawdown': float(drawdown.min()),
    }
