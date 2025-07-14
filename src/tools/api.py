# 主流虚拟币 symbol 映射表（支持20种）

from typing import Dict, Any, List
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
import json
import numpy as np
from src.utils.logging_config import setup_logger
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.tools.algogene_client import AlgogeneClient
import yfinance as yf

# 设置日志记录
logger = setup_logger('api')
CRYPTO_SYMBOLS = {
    "BTC": "BTCUSD", "ETH": "ETHUSD", "BNB": "BNBUSD", "SOL": "SOLUSD", "XRP": "XRPUSD", "ADA": "ADAUSD",
    "DOGE": "DOGEUSD", "DOT": "DOTUSD", "AVAX": "AVAXUSD", "MATIC": "MATICUSD", "LTC": "LTCUSD", "TRX": "TRXUSD",
    "LINK": "LINKUSD", "ATOM": "ATOMUSD", "FIL": "FILUSD", "XMR": "XMRUSD", "UNI": "UNIUSD", "APT": "APTUSD",
    "OP": "OPUSD", "ARB": "ARBUSD"
}

def get_financial_metrics(symbol: str) -> Dict[str, Any]:
    """获取财务指标数据"""
    logger.info(f"Getting financial indicators for {symbol}...")
    try:
        symbol_upper = symbol.upper().replace("-", "")
        # 主流币种自动分流
        if symbol_upper in CRYPTO_SYMBOLS:
            logger.info(f"Fetching crypto financial metrics for {symbol} using yfinance...")
            ticker = yf.Ticker(symbol + "-USD" if not symbol.endswith("-USD") else symbol)
            info = ticker.info
            metrics = {
                "market_cap": info.get("marketCap"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "pe_ratio": info.get("trailingPE"),
                "price_to_book": info.get("priceToBook"),
                "price_to_sales": info.get("priceToSalesTrailing12Months"),
                "earnings_per_share": info.get("trailingEps"),
                "revenue": info.get("totalRevenue"),
                "net_income": info.get("netIncomeToCommon"),
                "return_on_equity": info.get("returnOnEquity"),
                "net_margin": info.get("netMargins"),
                "operating_margin": info.get("operatingMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "book_value_growth": None,
                "current_ratio": info.get("currentRatio"),
                "debt_to_equity": info.get("debtToEquity"),
                "free_cash_flow_per_share": None
            }
            logger.info(f"Crypto financial metrics: {metrics}")
            return [metrics]
        # 美股分流（原有逻辑）
        if symbol.isalpha() or symbol.upper() in ["BTC-USD", "ETH-USD"]:
            logger.info(f"Fetching US/crypto financial metrics for {symbol} using yfinance...")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            metrics = {
                "market_cap": info.get("marketCap"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "pe_ratio": info.get("trailingPE"),
                "price_to_book": info.get("priceToBook"),
                "price_to_sales": info.get("priceToSalesTrailing12Months"),
                "earnings_per_share": info.get("trailingEps"),
                "revenue": info.get("totalRevenue"),
                "net_income": info.get("netIncomeToCommon"),
                "return_on_equity": info.get("returnOnEquity"),
                "net_margin": info.get("netMargins"),
                "operating_margin": info.get("operatingMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "book_value_growth": None,
                "current_ratio": info.get("currentRatio"),
                "debt_to_equity": info.get("debtToEquity"),
                "free_cash_flow_per_share": None
            }
            logger.info(f"US/crypto financial metrics: {metrics}")
            return [metrics]
        # A股逻辑（雪球/东财/新浪）
        logger.info("Fetching A股 financial metrics...")
        try:
            stock_data = {}
            try:
                stock_info = ak.stock_individual_spot_xq(symbol="SH"+symbol)
                if stock_info is not None and not stock_info.empty:
                    for _, row in stock_info.iterrows():
                        item = str(row['item']) if 'item' in row else str(row.iloc[0])
                        value = row['value'] if 'value' in row else row.iloc[1]
                        stock_data[item] = value
                logger.info("✓ Individual stock spot data from XueQiu fetched")
            except Exception as e:
                logger.error(f"Error getting individual stock spot data from XueQiu: {e}")
                stock_data = {}
            if not stock_data:
                try:
                    stock_info_em = ak.stock_individual_info_em(symbol=symbol)
                    if stock_info_em is not None and not stock_info_em.empty:
                        for _, row in stock_info_em.iterrows():
                            item = row['item'] if 'item' in row else str(row.iloc[0])
                            value = row['value'] if 'value' in row else str(row.iloc[1])
                            stock_data[item] = value
                        logger.info("✓ Fallback to EastMoney data successful")
                except Exception as e:
                    logger.error(f"Fallback also failed: {e}")
                    stock_data = {}
            current_year = datetime.now().year
            financial_data = ak.stock_financial_analysis_indicator(symbol=symbol, start_year=str(current_year-1))
            if financial_data is None or financial_data.empty:
                logger.warning("No financial indicator data available")
                return [{}]
            financial_data['日期'] = pd.to_datetime(financial_data['日期'])
            financial_data = financial_data.sort_values('日期', ascending=False)
            latest_financial = financial_data.iloc[0] if not financial_data.empty else pd.Series()
            try:
                income_statement = ak.stock_financial_report_sina(stock=f"sh{symbol}", symbol="利润表")
                if not income_statement.empty:
                    latest_income = income_statement.iloc[0]
                else:
                    latest_income = pd.Series()
            except Exception as e:
                latest_income = pd.Series()
            def convert_percentage(value: float) -> float:
                try:
                    return float(value) / 100.0 if value is not None else 0.0
                except:
                    return 0.0
            def safe_float(value, default=0.0):
                try:
                    if isinstance(value, str):
                        value = value.replace('万', '').replace('亿', '').replace(',', '').replace('元', '').replace('%', '')
                    return float(value) if value and str(value).strip() != '-' else default
                except:
                    return default
            if stock_data:
                market_cap = safe_float(stock_data.get("资产净值/总市值", 0))
                float_market_cap = safe_float(stock_data.get("流通值", 0))
                pe_ratio = safe_float(stock_data.get("市盈率(TTM)", 0))
                price_to_book = safe_float(stock_data.get("市净率", 0))
                earnings_per_share = safe_float(stock_data.get("每股收益", 0))
            else:
                market_cap = 0
                float_market_cap = 0
                pe_ratio = 0
                price_to_book = 0
                earnings_per_share = 0
            all_metrics = {
                "market_cap": market_cap,
                "float_market_cap": float_market_cap,
                "revenue": float(latest_income.get("营业总收入", 0)),
                "net_income": float(latest_income.get("净利润", 0)),
                "return_on_equity": convert_percentage(latest_financial.get("净资产收益率(%)", 0)),
                "net_margin": convert_percentage(latest_financial.get("销售净利率(%)", 0)),
                "operating_margin": convert_percentage(latest_financial.get("营业利润率(%)", 0)),
                "revenue_growth": convert_percentage(latest_financial.get("主营业务收入增长率(%)", 0)),
                "earnings_growth": convert_percentage(latest_financial.get("净利润增长率(%)", 0)),
                "book_value_growth": convert_percentage(latest_financial.get("净资产增长率(%)", 0)),
                "current_ratio": float(latest_financial.get("流动比率", 0)),
                "debt_to_equity": convert_percentage(latest_financial.get("资产负债率(%)", 0)),
                "free_cash_flow_per_share": float(latest_financial.get("每股经营性现金流(元)", 0)),
                "earnings_per_share": earnings_per_share if earnings_per_share > 0 else float(latest_financial.get("加权每股收益(元)", 0)),
                "pe_ratio": pe_ratio,
                "price_to_book": price_to_book,
                "price_to_sales": market_cap / float(latest_income.get("营业总收入", 1)) if float(latest_income.get("营业总收入", 0)) > 0 and market_cap > 0 else 0,
            }
            agent_metrics = {
                "return_on_equity": all_metrics["return_on_equity"],
                "net_margin": all_metrics["net_margin"],
                "operating_margin": all_metrics["operating_margin"],
                "revenue_growth": all_metrics["revenue_growth"],
                "earnings_growth": all_metrics["earnings_growth"],
                "book_value_growth": all_metrics["book_value_growth"],
                "current_ratio": all_metrics["current_ratio"],
                "debt_to_equity": all_metrics["debt_to_equity"],
                "free_cash_flow_per_share": all_metrics["free_cash_flow_per_share"],
                "earnings_per_share": all_metrics["earnings_per_share"],
                "pe_ratio": all_metrics["pe_ratio"],
                "price_to_book": all_metrics["price_to_book"],
                "price_to_sales": all_metrics["price_to_sales"],
            }
            logger.info("✓ A股指标构建成功")
            return [agent_metrics]
        except Exception as e:
            logger.error(f"Error building A股 indicators: {e}")
            return [{}]
    except Exception as e:
        logger.error(f"Error getting financial indicators: {e}")
        return [{}]


def get_financial_statements(symbol: str) -> Dict[str, Any]:
    """获取财务报表数据"""
    logger.info(f"Getting financial statements for {symbol}...")
    try:
        symbol_upper = symbol.upper().replace("-", "")
        # 主流币种自动分流
        if symbol_upper in CRYPTO_SYMBOLS:
            logger.info(f"Fetching crypto financial statements for {symbol}: no statements available.")
            empty_item = {
                "net_income": None,
                "operating_revenue": None,
                "operating_profit": None,
                "working_capital": None,
                "depreciation_and_amortization": None,
                "capital_expenditure": None,
                "free_cash_flow": None
            }
            return [empty_item, empty_item]
        # 美股分流（原有逻辑）
        if symbol.isalpha() or symbol.upper() in ["BTC-USD", "ETH-USD"]:
            logger.info(f"Fetching US/crypto financial statements for {symbol} using yfinance...")
            if symbol.upper() in ["BTC-USD", "ETH-USD"]:
                empty_item = {
                    "net_income": None,
                    "operating_revenue": None,
                    "operating_profit": None,
                    "working_capital": None,
                    "depreciation_and_amortization": None,
                    "capital_expenditure": None,
                    "free_cash_flow": None
                }
                return [empty_item, empty_item]
            ticker = yf.Ticker(symbol)
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow
            periods = financials.columns.tolist()
            line_items = []
            for i in range(min(2, len(periods))):
                period = periods[i]
                current_item = {
                    "net_income": float(financials.loc["Net Income", period]) if "Net Income" in financials.index else None,
                    "operating_revenue": float(financials.loc["Total Revenue", period]) if "Total Revenue" in financials.index else None,
                    "operating_profit": float(financials.loc["Operating Income", period]) if "Operating Income" in financials.index else None,
                    "working_capital": float(balance_sheet.loc["Total Current Assets", period]) - float(balance_sheet.loc["Total Current Liabilities", period]) if "Total Current Assets" in balance_sheet.index and "Total Current Liabilities" in balance_sheet.index else None,
                    "depreciation_and_amortization": float(financials.loc["Depreciation", period]) if "Depreciation" in financials.index else None,
                    "capital_expenditure": float(cashflow.loc["Capital Expenditures", period]) if "Capital Expenditures" in cashflow.index else None,
                    "free_cash_flow": float(cashflow.loc["Free Cash Flow", period]) if "Free Cash Flow" in cashflow.index else None
                }
                line_items.append(current_item)
            logger.info(f"US financial statements: {line_items}")
            return line_items
        # A股逻辑（新浪/东财）
        logger.info("Fetching A股 financial statements...")
        try:
            # 获取资产负债表数据
            try:
                balance_sheet = ak.stock_financial_report_sina(stock=f"sh{symbol}", symbol="资产负债表")
                if not balance_sheet.empty:
                    latest_balance = balance_sheet.iloc[0]
                    previous_balance = balance_sheet.iloc[1] if len(balance_sheet) > 1 else balance_sheet.iloc[0]
                else:
                    latest_balance = pd.Series()
                    previous_balance = pd.Series()
            except Exception as e:
                latest_balance = pd.Series()
                previous_balance = pd.Series()
            # 获取利润表数据
            try:
                income_statement = ak.stock_financial_report_sina(stock=f"sh{symbol}", symbol="利润表")
                if not income_statement.empty:
                    latest_income = income_statement.iloc[0]
                    previous_income = income_statement.iloc[1] if len(income_statement) > 1 else income_statement.iloc[0]
                else:
                    latest_income = pd.Series()
                    previous_income = pd.Series()
            except Exception as e:
                latest_income = pd.Series()
                previous_income = pd.Series()
            # 获取现金流量表数据
            try:
                cash_flow = ak.stock_financial_report_sina(stock=f"sh{symbol}", symbol="现金流量表")
                if not cash_flow.empty:
                    latest_cash_flow = cash_flow.iloc[0]
                    previous_cash_flow = cash_flow.iloc[1] if len(cash_flow) > 1 else cash_flow.iloc[0]
                else:
                    latest_cash_flow = pd.Series()
                    previous_cash_flow = pd.Series()
            except Exception as e:
                latest_cash_flow = pd.Series()
                previous_cash_flow = pd.Series()
            line_items = []
            try:
                current_item = {
                    "net_income": float(latest_income.get("净利润", 0)),
                    "operating_revenue": float(latest_income.get("营业总收入", 0)),
                    "operating_profit": float(latest_income.get("营业利润", 0)),
                    "working_capital": float(latest_balance.get("流动资产合计", 0)) - float(latest_balance.get("流动负债合计", 0)),
                    "depreciation_and_amortization": float(latest_cash_flow.get("固定资产折旧、油气资产折耗、生产性生物资产折旧", 0)),
                    "capital_expenditure": abs(float(latest_cash_flow.get("购建固定资产、无形资产和其他长期资产支付的现金", 0))),
                    "free_cash_flow": float(latest_cash_flow.get("经营活动产生的现金流量净额", 0)) - abs(float(latest_cash_flow.get("购建固定资产、无形资产和其他长期资产支付的现金", 0)))
                }
                line_items.append(current_item)
                previous_item = {
                    "net_income": float(previous_income.get("净利润", 0)),
                    "operating_revenue": float(previous_income.get("营业总收入", 0)),
                    "operating_profit": float(previous_income.get("营业利润", 0)),
                    "working_capital": float(previous_balance.get("流动资产合计", 0)) - float(previous_balance.get("流动负债合计", 0)),
                    "depreciation_and_amortization": float(previous_cash_flow.get("固定资产折旧、油气资产折耗、生产性生物资产折旧", 0)),
                    "capital_expenditure": abs(float(previous_cash_flow.get("购建固定资产、无形资产和其他长期资产支付的现金", 0))),
                    "free_cash_flow": float(previous_cash_flow.get("经营活动产生的现金流量净额", 0)) - abs(float(previous_cash_flow.get("购建固定资产、无形资产和其他长期资产支付的现金", 0)))
                }
                line_items.append(previous_item)
                logger.info("✓ A股财务报表构建成功")
            except Exception as e:
                default_item = {
                    "net_income": 0,
                    "operating_revenue": 0,
                    "operating_profit": 0,
                    "working_capital": 0,
                    "depreciation_and_amortization": 0,
                    "capital_expenditure": 0,
                    "free_cash_flow": 0
                }
                line_items = [default_item, default_item]
            return line_items
        except Exception as e:
            default_item = {
                "net_income": 0,
                "operating_revenue": 0,
                "operating_profit": 0,
                "working_capital": 0,
                "depreciation_and_amortization": 0,
                "capital_expenditure": 0,
                "free_cash_flow": 0
            }
            return [default_item, default_item]
    except Exception as e:
        logger.error(f"Error getting financial statements: {e}")
        default_item = {
            "net_income": 0,
            "operating_revenue": 0,
            "operating_profit": 0,
            "working_capital": 0,
            "depreciation_and_amortization": 0,
            "capital_expenditure": 0,
            "free_cash_flow": 0
        }
        return [default_item, default_item]


def get_market_data(symbol: str) -> Dict[str, Any]:
    try:
        symbol_upper = symbol.upper().replace("-", "")
        # 主流币种自动分流
        if symbol_upper in CRYPTO_SYMBOLS:
            import yfinance as yf
            logger.info(f"Fetching crypto market data for {symbol} using yfinance...")
            ticker = yf.Ticker(symbol + "-USD" if not symbol.endswith("-USD") else symbol)
            info = ticker.info
            market_cap = info.get("marketCap", 0)
            volume = info.get("volume", info.get("regularMarketVolume", 0))
            average_volume = info.get("averageVolume", 0)
            fifty_two_week_high = info.get("fiftyTwoWeekHigh", 0)
            fifty_two_week_low = info.get("fiftyTwoWeekLow", 0)
            return {
                "market_cap": market_cap,
                "volume": volume,
                "average_volume": average_volume,
                "fifty_two_week_high": fifty_two_week_high,
                "fifty_two_week_low": fifty_two_week_low
            }
        # 美股分流（原有逻辑）
        if symbol.isalpha() or symbol.upper() in ["BTC-USD", "ETH-USD"]:
            import yfinance as yf
            logger.info(f"Fetching US/crypto market data for {symbol} using yfinance...")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            market_cap = info.get("marketCap", 0)
            volume = info.get("volume", info.get("regularMarketVolume", 0))
            average_volume = info.get("averageVolume", 0)
            fifty_two_week_high = info.get("fiftyTwoWeekHigh", 0)
            fifty_two_week_low = info.get("fiftyTwoWeekLow", 0)
            return {
                "market_cap": market_cap,
                "volume": volume,
                "average_volume": average_volume,
                "fifty_two_week_high": fifty_two_week_high,
                "fifty_two_week_low": fifty_two_week_low
            }
        # A股逻辑（雪球/东财）
        # ...existing code...
        try:
            stock_info = ak.stock_individual_spot_xq(symbol="SH"+symbol)
            stock_data = {}
            if stock_info is not None and not stock_info.empty:
                for _, row in stock_info.iterrows():
                    item = str(row['item']) if 'item' in row else str(row.iloc[0])
                    value = row['value'] if 'value' in row else row.iloc[1]
                    stock_data[item] = value
            else:
                # 备选：使用东财接口
                stock_info = ak.stock_individual_info_em(symbol=symbol)
                if stock_info is not None and not stock_info.empty:
                    for _, row in stock_info.iterrows():
                        item = row['item'] if 'item' in row else str(row.iloc[0])
                        value = row['value'] if 'value' in row else str(row.iloc[1])
                        stock_data[item] = value
            def safe_float(value, default=0.0):
                try:
                    if isinstance(value, str):
                        value = value.replace('万', '').replace('亿', '').replace(',', '').replace('元', '')
                    return float(value) if value and str(value).strip() != '-' else default
                except:
                    return default
            market_cap = safe_float(stock_data.get("资产净值/总市值", 0))
            volume = safe_float(stock_data.get("成交量", 0))
            week_52_high = safe_float(stock_data.get("52周最高", 0))
            week_52_low = safe_float(stock_data.get("52周最低", 0))
            return {
                "market_cap": market_cap,
                "volume": volume,
                "average_volume": volume,
                "fifty_two_week_high": week_52_high,
                "fifty_two_week_low": week_52_low
            }
        except Exception as e:
            logger.error(f"Error getting A股 market data: {e}")
            return {}
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return {}
        # 🔧 使用雪球的实际字段名
        market_cap = safe_float(stock_data.get("资产净值/总市值", 0))
        volume = safe_float(stock_data.get("成交量", 0))
        week_52_high = safe_float(stock_data.get("52周最高", 0))
        week_52_low = safe_float(stock_data.get("52周最低", 0))

        return {
            "market_cap": market_cap,
            "volume": volume,
            "average_volume": volume,  # A股用当日成交量代替
            "fifty_two_week_high": week_52_high,
            "fifty_two_week_low": week_52_low
        }

    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return {}


def get_price_history(symbol: str, start_date: str = None, end_date: str = None, adjust: str = "qfq") -> pd.DataFrame:
    """获取历史价格数据

    Args:
        symbol: 股票代码
        start_date: 开始日期，格式：YYYY-MM-DD，如果为None则默认获取过去一年的数据
        end_date: 结束日期，格式：YYYY-MM-DD，如果为None则使用昨天作为结束日期
        adjust: 复权类型，可选值：
               - "": 不复权
               - "qfq": 前复权（默认）
               - "hfq": 后复权

    Returns:
        包含以下列的DataFrame：
        - date: 日期
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量（手）
        - amount: 成交额（元）
        - amplitude: 振幅（%）
        - pct_change: 涨跌幅（%）
        - change_amount: 涨跌额（元）
        - turnover: 换手率（%）

        技术指标：
        - momentum_1m: 1个月动量
        - momentum_3m: 3个月动量
        - momentum_6m: 6个月动量
        - volume_momentum: 成交量动量
        - historical_volatility: 历史波动率
        - volatility_regime: 波动率区间
        - volatility_z_score: 波动率Z分数
        - atr_ratio: 真实波动幅度比率
        - hurst_exponent: 赫斯特指数
        - skewness: 偏度
        - kurtosis: 峰度
    """
    try:
        symbol_upper = symbol.upper().replace("-", "")
        if symbol_upper in CRYPTO_SYMBOLS:
            # Algogene 虚拟币分支
            client = AlgogeneClient()
            algogene_symbol = CRYPTO_SYMBOLS[symbol_upper]
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            count = (end_dt - start_dt).days + 1
            interval = "D"
            timestamp = end_date + " 00:00:00"
            result = client.get_price_history(count=count, instrument=algogene_symbol, interval=interval, timestamp=timestamp)
            prices = result.get("res", [])
            if prices:
                df = pd.DataFrame(prices)
                df = df.rename(columns={
                    "t": "date",
                    "o": "open",
                    "h": "high",
                    "l": "low",
                    "c": "close",
                    "v": "volume"
                })
                df["date"] = pd.to_datetime(df["date"])
                df = df[["date", "open", "high", "low", "close", "volume"]]
                df = df.sort_values("date")
                df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
                df["amount"] = df["close"] * df["volume"]
                df["amplitude"] = (df["high"] - df["low"]) / df["close"] * 100
                df["pct_change"] = df["close"].pct_change() * 100
                df["change_amount"] = df["close"].diff()
                df["turnover"] = None
                df["momentum_1m"] = df["close"].pct_change(periods=20)
                df["momentum_3m"] = df["close"].pct_change(periods=60)
                df["momentum_6m"] = df["close"].pct_change(periods=120)
                df["volume_ma20"] = df["volume"].rolling(window=20).mean()
                df["volume_momentum"] = df["volume"] / df["volume_ma20"]
                returns = df["close"].pct_change()
                df["historical_volatility"] = returns.rolling(window=20).std() * np.sqrt(252)
                volatility_120d = returns.rolling(window=120).std() * np.sqrt(252)
                vol_min = volatility_120d.rolling(window=120).min()
                vol_max = volatility_120d.rolling(window=120).max()
                vol_range = vol_max - vol_min
                df["volatility_regime"] = np.where(
                    vol_range > 0,
                    (df["historical_volatility"] - vol_min) / vol_range,
                    0
                )
                vol_mean = df["historical_volatility"].rolling(window=120).mean()
                vol_std = df["historical_volatility"].rolling(window=120).std()
                df["volatility_z_score"] = (df["historical_volatility"] - vol_mean) / vol_std
                tr = pd.DataFrame()
                tr["h-l"] = df["high"] - df["low"]
                tr["h-pc"] = abs(df["high"] - df["close"].shift(1))
                tr["l-pc"] = abs(df["low"] - df["close"].shift(1))
                tr["tr"] = tr[["h-l", "h-pc", "l-pc"]].max(axis=1)
                df["atr"] = tr["tr"].rolling(window=14).mean()
                df["atr_ratio"] = df["atr"] / df["close"]
                def calculate_hurst(series):
                    try:
                        series = series.dropna()
                        if len(series) < 30:
                            return np.nan
                        log_returns = np.log(series / series.shift(1)).dropna()
                        if len(log_returns) < 30:
                            return np.nan
                        lags = range(2, min(11, len(log_returns) // 4))
                        tau = []
                        for lag in lags:
                            std = log_returns.rolling(window=lag).std().dropna()
                            if len(std) > 0:
                                tau.append(np.mean(std))
                        if len(tau) < 3:
                            return np.nan
                        lags_log = np.log(list(lags))
                        tau_log = np.log(tau)
                        reg = np.polyfit(lags_log, tau_log, 1)
                        hurst = reg[0] / 2.0
                        if np.isnan(hurst) or np.isinf(hurst):
                            return np.nan
                        return hurst
                    except Exception as e:
                        return np.nan
                log_returns = np.log(df["close"] / df["close"].shift(1))
                df["hurst_exponent"] = log_returns.rolling(window=120, min_periods=60).apply(calculate_hurst)
                df["skewness"] = returns.rolling(window=20).skew()
                df["kurtosis"] = returns.rolling(window=20).kurt()
                df = df.sort_values("date")
                df = df.reset_index(drop=True)
                logger.info(f"Successfully fetched crypto price history data ({len(df)} records)")
                return df
            else:
                logger.warning(f"No crypto price history data found for {symbol}")
                return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume", "amount", "amplitude", "pct_change", "change_amount", "turnover"])
        elif symbol.isalpha():
            # 美股分流（原有逻辑完全保留）
            client = AlgogeneClient()
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            count = (end_dt - start_dt).days + 1
            interval = "D"
            timestamp = end_date + " 00:00:00"
            result = client.get_price_history(count=count, instrument=symbol, interval=interval, timestamp=timestamp)
            prices = result.get("res", [])
            if prices:
                df = pd.DataFrame(prices)
                df = df.rename(columns={
                    "t": "date",
                    "o": "open",
                    "h": "high",
                    "l": "low",
                    "c": "close",
                    "v": "volume"
                })
                df["date"] = pd.to_datetime(df["date"])
                df = df[["date", "open", "high", "low", "close", "volume"]]
                df = df.sort_values("date")
                df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
                df["amount"] = df["close"] * df["volume"]
                df["amplitude"] = (df["high"] - df["low"]) / df["close"] * 100
                df["pct_change"] = df["close"].pct_change() * 100
                df["change_amount"] = df["close"].diff()
                try:
                    ticker_yf = yf.Ticker(symbol)
                    shares_outstanding = ticker_yf.info.get("sharesOutstanding")
                    if shares_outstanding and shares_outstanding > 0:
                        df["turnover"] = df["volume"] / shares_outstanding * 100
                    else:
                        df["turnover"] = None
                except Exception as e:
                    logger.warning(f"Failed to get sharesOutstanding for {symbol}: {e}")
                    df["turnover"] = None
                df["momentum_1m"] = df["close"].pct_change(periods=20)
                df["momentum_3m"] = df["close"].pct_change(periods=60)
                df["momentum_6m"] = df["close"].pct_change(periods=120)
                df["volume_ma20"] = df["volume"].rolling(window=20).mean()
                df["volume_momentum"] = df["volume"] / df["volume_ma20"]
                returns = df["close"].pct_change()
                df["historical_volatility"] = returns.rolling(window=20).std() * np.sqrt(252)
                volatility_120d = returns.rolling(window=120).std() * np.sqrt(252)
                vol_min = volatility_120d.rolling(window=120).min()
                vol_max = volatility_120d.rolling(window=120).max()
                vol_range = vol_max - vol_min
                df["volatility_regime"] = np.where(
                    vol_range > 0,
                    (df["historical_volatility"] - vol_min) / vol_range,
                    0
                )
                vol_mean = df["historical_volatility"].rolling(window=120).mean()
                vol_std = df["historical_volatility"].rolling(window=120).std()
                df["volatility_z_score"] = (df["historical_volatility"] - vol_mean) / vol_std
                tr = pd.DataFrame()
                tr["h-l"] = df["high"] - df["low"]
                tr["h-pc"] = abs(df["high"] - df["close"].shift(1))
                tr["l-pc"] = abs(df["low"] - df["close"].shift(1))
                tr["tr"] = tr[["h-l", "h-pc", "l-pc"]].max(axis=1)
                df["atr"] = tr["tr"].rolling(window=14).mean()
                df["atr_ratio"] = df["atr"] / df["close"]
                def calculate_hurst(series):
                    try:
                        series = series.dropna()
                        if len(series) < 30:
                            return np.nan
                        log_returns = np.log(series / series.shift(1)).dropna()
                        if len(log_returns) < 30:
                            return np.nan
                        lags = range(2, min(11, len(log_returns) // 4))
                        tau = []
                        for lag in lags:
                            std = log_returns.rolling(window=lag).std().dropna()
                            if len(std) > 0:
                                tau.append(np.mean(std))
                        if len(tau) < 3:
                            return np.nan
                        lags_log = np.log(list(lags))
                        tau_log = np.log(tau)
                        reg = np.polyfit(lags_log, tau_log, 1)
                        hurst = reg[0] / 2.0
                        if np.isnan(hurst) or np.isinf(hurst):
                            return np.nan
                        return hurst
                    except Exception as e:
                        return np.nan
                log_returns = np.log(df["close"] / df["close"].shift(1))
                df["hurst_exponent"] = log_returns.rolling(window=120, min_periods=60).apply(calculate_hurst)
                df["skewness"] = returns.rolling(window=20).skew()
                df["kurtosis"] = returns.rolling(window=20).kurt()
                df = df.sort_values("date")
                df = df.reset_index(drop=True)
                logger.info(f"Successfully fetched US price history data ({len(df)} records)")
                return df
            else:
                logger.warning(f"No US price history data found for {symbol}")
                return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume", "amount", "amplitude", "pct_change", "change_amount", "turnover"])
        else:
            # A股原有逻辑
            # ...existing code...
            current_date = datetime.now()
            yesterday = current_date - timedelta(days=1)
            if not end_date:
                end_date = yesterday
            else:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                if end_date > yesterday:
                    end_date = yesterday
            if not start_date:
                start_date = end_date - timedelta(days=365)
            else:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            logger.info(f"\nGetting price history for {symbol}...")
            logger.info(f"Start date: {start_date.strftime('%Y-%m-%d')}")
            logger.info(f"End date: {end_date.strftime('%Y-%m-%d')}")
            def get_and_process_data(start_date, end_date):
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                    adjust=adjust
                )
                if df is None or df.empty:
                    return pd.DataFrame()
                df = df.rename(columns={
                    "日期": "date",
                    "开盘": "open",
                    "最高": "high",
                    "最低": "low",
                    "收盘": "close",
                    "成交量": "volume",
                    "成交额": "amount",
                    "振幅": "amplitude",
                    "涨跌幅": "pct_change",
                    "涨跌额": "change_amount",
                    "换手率": "turnover"
                })
                df["date"] = pd.to_datetime(df["date"])
                return df
            df = get_and_process_data(start_date, end_date)
            if df is None or df.empty:
                logger.warning(f"Warning: No price history data found for {symbol}")
                return pd.DataFrame()
        # 检查数据量是否足够
        min_required_days = 120  # 至少需要120个交易日的数据
        if len(df) < min_required_days:
            logger.warning(
                f"Warning: Insufficient data ({len(df)} days) for all technical indicators")
            logger.info("Attempting to fetch more data...")

            # 扩大时间范围到2年
            start_date = end_date - timedelta(days=730)
            df = get_and_process_data(start_date, end_date)

            if len(df) < min_required_days:
                logger.warning(
                    f"Warning: Even with extended time range, insufficient data ({len(df)} days)")

        # 计算动量指标
        df["momentum_1m"] = df["close"].pct_change(periods=20)  # 20个交易日约等于1个月
        df["momentum_3m"] = df["close"].pct_change(periods=60)  # 60个交易日约等于3个月
        df["momentum_6m"] = df["close"].pct_change(
            periods=120)  # 120个交易日约等于6个月

        # 计算成交量动量（相对于20日平均成交量的变化）
        df["volume_ma20"] = df["volume"].rolling(window=20).mean()
        df["volume_momentum"] = df["volume"] / df["volume_ma20"]

        # 计算波动率指标
        # 1. 历史波动率 (20日)
        returns = df["close"].pct_change()
        df["historical_volatility"] = returns.rolling(
            window=20).std() * np.sqrt(252)  # 年化

        # 2. 波动率区间 (相对于过去120天的波动率的位置)
        volatility_120d = returns.rolling(window=120).std() * np.sqrt(252)
        vol_min = volatility_120d.rolling(window=120).min()
        vol_max = volatility_120d.rolling(window=120).max()
        vol_range = vol_max - vol_min
        df["volatility_regime"] = np.where(
            vol_range > 0,
            (df["historical_volatility"] - vol_min) / vol_range,
            0  # 当范围为0时返回0
        )

        # 3. 波动率Z分数
        vol_mean = df["historical_volatility"].rolling(window=120).mean()
        vol_std = df["historical_volatility"].rolling(window=120).std()
        df["volatility_z_score"] = (
            df["historical_volatility"] - vol_mean) / vol_std

        # 4. ATR比率
        tr = pd.DataFrame()
        tr["h-l"] = df["high"] - df["low"]
        tr["h-pc"] = abs(df["high"] - df["close"].shift(1))
        tr["l-pc"] = abs(df["low"] - df["close"].shift(1))
        tr["tr"] = tr[["h-l", "h-pc", "l-pc"]].max(axis=1)
        df["atr"] = tr["tr"].rolling(window=14).mean()
        df["atr_ratio"] = df["atr"] / df["close"]

        # 计算统计套利指标
        # 1. 赫斯特指数 (使用过去120天的数据)
        def calculate_hurst(series):
            """
            计算Hurst指数。

            Args:
                series: 价格序列

            Returns:
                float: Hurst指数，或在计算失败时返回np.nan
            """
            try:
                series = series.dropna()
                if len(series) < 30:  # 降低最小数据点要求
                    return np.nan

                # 使用对数收益率
                log_returns = np.log(series / series.shift(1)).dropna()
                if len(log_returns) < 30:  # 降低最小数据点要求
                    return np.nan

                # 使用更小的lag范围
                # 减少lag范围到2-10天
                lags = range(2, min(11, len(log_returns) // 4))

                # 计算每个lag的标准差
                tau = []
                for lag in lags:
                    # 计算滚动标准差
                    std = log_returns.rolling(window=lag).std().dropna()
                    if len(std) > 0:
                        tau.append(np.mean(std))

                # 基本的数值检查
                if len(tau) < 3:  # 进一步降低最小要求
                    return np.nan

                # 使用对数回归
                lags_log = np.log(list(lags))
                tau_log = np.log(tau)

                # 计算回归系数
                reg = np.polyfit(lags_log, tau_log, 1)
                hurst = reg[0] / 2.0

                # 只保留基本的数值检查
                if np.isnan(hurst) or np.isinf(hurst):
                    return np.nan

                return hurst

            except Exception as e:
                return np.nan

        # 使用对数收益率计算Hurst指数
        log_returns = np.log(df["close"] / df["close"].shift(1))
        df["hurst_exponent"] = log_returns.rolling(
            window=120,
            min_periods=60  # 要求至少60个数据点
        ).apply(calculate_hurst)

        # 2. 偏度 (20日)
        df["skewness"] = returns.rolling(window=20).skew()

        # 3. 峰度 (20日)
        df["kurtosis"] = returns.rolling(window=20).kurt()

        # 按日期升序排序
        df = df.sort_values("date")

        # 重置索引
        df = df.reset_index(drop=True)

        logger.info(
            f"Successfully fetched price history data ({len(df)} records)")

        # 检查并报告NaN值
        nan_columns = df.isna().sum()
        if nan_columns.any():
            logger.warning(
                "\nWarning: The following indicators contain NaN values:")
            for col, nan_count in nan_columns[nan_columns > 0].items():
                logger.warning(f"- {col}: {nan_count} records")

        return df
    except Exception as e:
        logger.error(f"Error getting price history: {e}")
        return pd.DataFrame()


def prices_to_df(prices):
    """Convert price data to DataFrame with standardized column names"""
    try:
        df = pd.DataFrame(prices)

        # 标准化列名映射
        column_mapping = {
            '收盘': 'close',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            '振幅': 'amplitude',
            '涨跌幅': 'change_percent',
            '涨跌额': 'change_amount',
            '换手率': 'turnover_rate'
        }

        # 重命名列
        for cn, en in column_mapping.items():
            if cn in df.columns:
                df[en] = df[cn]

        # 确保必要的列存在
        required_columns = ['close', 'open', 'high', 'low', 'volume']
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0.0  # 使用0填充缺失的必要列

        return df
    except Exception as e:
        logger.error(f"Error converting price data: {str(e)}")
        # 返回一个包含必要列的空DataFrame
        return pd.DataFrame(columns=['close', 'open', 'high', 'low', 'volume'])


def get_price_data(
    ticker: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """获取股票价格数据

    Args:
        ticker: 股票代码
        start_date: 开始日期，格式：YYYY-MM-DD
        end_date: 结束日期，格式：YYYY-MM-DD

    Returns:
        包含价格数据的DataFrame
    """
    return get_price_history(ticker, start_date, end_date)


if __name__ == "__main__":
    # 测试 get_financial_metrics 和 get_financial_statements

    # A股测试
    res_a = get_market_data("600519")
    print("A股市场数据:", res_a)
    a_metrics = get_financial_metrics("600519")
    print("A股财务指标:", a_metrics)
    a_statements = get_financial_statements("600519")
    print("A股财务报表:", a_statements)

    # 美股测试
    res_us = get_market_data("AAPL")
    print("美股市场数据:", res_us)
    us_metrics = get_financial_metrics("AAPL")
    print("美股财务指标:", us_metrics)
    us_statements = get_financial_statements("AAPL")
    print("美股财务报表:", us_statements)

    # 主流币种测试
    for crypto in ["BTC", "ETH", "BNB"]:
        print(f"\n--- 测试 {crypto} ---")
        crypto_market = get_market_data(crypto)
        print(f"{crypto} 市场数据:", crypto_market)
        crypto_metrics = get_financial_metrics(crypto)
        print(f"{crypto} 财务指标:", crypto_metrics)
        crypto_statements = get_financial_statements(crypto)
        print(f"{crypto} 财务报表:", crypto_statements)
