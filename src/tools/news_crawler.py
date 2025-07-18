
import os
import sys
import json
from datetime import datetime
import akshare as ak
import requests
from bs4 import BeautifulSoup
from src.tools.openrouter_config import get_chat_completion, logger as api_logger
import time
import pandas as pd
import traceback



# --- 美股新闻抓取逻辑（集成自 stock_news_alt.py） ---
import yfinance as yf
from newspaper import Article
import logging
def get_us_stock_news(symbol: str, max_news: int = 10) -> list:
    """
    获取美股新闻，支持可选 SOCKS5 代理。
    Args:
        symbol (str): 美股代码
        max_news (int): 获取的新闻条数
        use_proxy (bool): 是否启用代理
    Returns:
        list: 新闻列表
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f"正在为美股代码获取新闻: {symbol}")
    stock = yf.Ticker(symbol)
    news_list = []
    seen_links = set()

    def _extract_article_text(url):
        if not url:
            return ''
        try:
            article = Article(url, request_timeout=10, verify_ssl=False)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            logging.warning(f"无法从 {url} 提取文本。原因: {e}")
            return ''

    def _normalize_and_add_news(raw_item, news_list, seen_links, source_type):
        # 字段对齐A股格式
        title, url, source, publish_time, content, keyword = '', '', '', '', '', ''
        if source_type == 'stock_news':
            content_raw = raw_item.get('content', {})
            title = str(content_raw.get('title', '')).strip()
            url = str(content_raw.get('canonicalUrl', {}).get('url', '')).strip()
            source = str(content_raw.get('provider', {}).get('displayName', '')).strip()
            pub_date_str = str(content_raw.get('pubDate', '')).strip()
            # 转为标准时间字符串
            if pub_date_str:
                try:
                    dt = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    publish_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    publish_time = pub_date_str
            else:
                publish_time = ''
            content = str(content_raw.get('summary', '') or title).strip()
        elif source_type == 'search_api':
            title = str(raw_item.get('title', '')).strip()
            url = str(raw_item.get('link', '')).strip()
            source = str(raw_item.get('publisher', '')).strip()
            timestamp = raw_item.get('providerPublishTime', 0)
            if timestamp:
                try:
                    dt = datetime.utcfromtimestamp(timestamp)
                    publish_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    publish_time = str(timestamp)
            else:
                publish_time = ''
            content = str(raw_item.get('summary', '') or title).strip()
        # 补齐正文
        if not content or len(content) < 10:
            content = _extract_article_text(url)
        # keyword可用symbol/company_name
        keyword = symbol
        if url and url not in seen_links and title and source:
            seen_links.add(url)
            news_item = {
                "title": title,
                "content": content,
                "publish_time": publish_time,
                "source": source,
                "url": url,
                "keyword": keyword
            }
            news_list.append(news_item)

    # 来源1: stock.news 属性
    try:
        direct_news = stock.news
        if direct_news:
            for item in direct_news:
                _normalize_and_add_news(item, news_list, seen_links, 'stock_news')
    except Exception as e:
        logging.warning(f"无法为 {symbol} 从 stock.news 获取新闻。原因: {e}")

    # 来源2: 关键词搜索 API
    keywords = []
    try:
        index_keywords = {
            'IXIC': ['Nasdaq Composite', 'Nasdaq Index', 'US stock market'],
            '^IXIC': ['Nasdaq Composite', 'Nasdaq Index', 'US stock market'],
            'GSPC': ['S&P 500', 'US stock market'],
            '^GSPC': ['S&P 500', 'US stock market'],
        }
        if symbol.upper() in index_keywords:
            keywords = index_keywords[symbol.upper()]
            keywords.append(symbol)
        else:
            info = stock.info
            company_name = info.get('longName') or info.get('shortName')
            if company_name:
                keywords.append(company_name)
            else:
                keywords.append(symbol)
        for kw in keywords:
            try:
                url = f"https://query2.finance.yahoo.com/v1/finance/search?q={kw}"
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(url, headers=headers, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                search_news = data.get('news', [])
                for item in search_news:
                    _normalize_and_add_news(item, news_list, seen_links, 'search_api')
            except Exception as e:
                logging.error(f"搜索关键词 '{kw}' 时发生错误: {e}")
    except Exception as e:
        logging.error(f"为 {symbol} 生成关键词或获取股票信息失败。原因: {e}")
    return news_list[:max_news]

# --- A股新闻抓取逻辑（原有实现，略） ---
def get_cn_stock_news(symbol: str, max_news: int = 10) -> list:
    """
    获取A股新闻，返回统一格式。
    Args:
        symbol (str): A股代码
        max_news (int): 获取的新闻条数
    Returns:
        list: 新闻列表
    """
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)
    max_news = min(max_news, 100)
    # cache_file = "src/data/stock_news_cache.json"
    # os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    # cache = {}
    # # 读取缓存
    # if os.path.exists(cache_file):
    #     try:
    #         with open(cache_file, 'r', encoding='utf-8') as f:
    #             cache = json.load(f)
    #     except Exception:
    #         cache = {}
    # cache_key = f"{symbol}_{max_news}"
    # # 判断缓存是否有效（24小时内）
    # if cache_key in cache:
    #     cached = cache[cache_key]
    #     cache_time = cached.get('cache_time', 0)
    #     if time.time() - cache_time < 86400 and cached.get('news_list'):
    #         return cached['news_list']
    news_list = []
    try:
        print(ak.__version__)
        news_df = ak.stock_news_em(symbol=symbol)
        if news_df is None or len(news_df) == 0:
            return []
        for _, row in news_df.head(int(max_news * 1.5)).iterrows():
            try:
                content = row["新闻内容"] if "新闻内容" in row and not pd.isna(row["新闻内容"]) else ""
                if not content:
                    content = row["新闻标题"]
                content = content.strip()
                if len(content) < 10:
                    continue
                keyword = row["关键词"] if "关键词" in row and not pd.isna(row["关键词"]) else ""
                news_item = {
                    "title": row["新闻标题"].strip(),
                    "content": content,
                    "publish_time": row["发布时间"],
                    "source": row["文章来源"].strip(),
                    "url": row["新闻链接"].strip(),
                    "keyword": keyword.strip()
                }
                news_list.append(news_item)
                print(f"成功添加新闻: {news_item['title']}")
            except Exception:
                continue
        news_list.sort(key=lambda x: x["publish_time"], reverse=True)
        news_list = news_list[:max_news]
        # 写入缓存
        # cache[cache_key] = {
        #     'cache_time': time.time(),
        #     'news_list': news_list
        # }
        # try:
        #     with open(cache_file, 'w', encoding='utf-8') as f:
        #         json.dump(cache, f, ensure_ascii=False, indent=2)
        # except Exception:
        #     pass
        return news_list
    except Exception as e:
        print(f"ak.stock_news_em 异常: {e}")
        traceback.print_exc()
        return []

# --- 统一入口 ---
def get_stock_news(symbol: str, market_type: str = "cn", max_news: int = 10) -> list:
    """
    获取并处理个股新闻，支持 A股、美股。
    Args:
        symbol (str): 股票代码
        max_news (int): 获取的新闻条数
    Returns:
        list: 新闻列表，字段统一为 title, link, publisher, time, text
    """
    """
    按 symbol 自动分流：A股走 get_cn_stock_news，美股走 get_us_stock_news，虚拟币只用 yfinance。
    字段结构完全一致。
    """
    from src.tools.crypto_symbols import CRYPTO_SYMBOLS
    symbol_upper = symbol.upper().replace("-", "")
    # 虚拟币分流直接调用美股分流逻辑，字段结构100%一致
    if symbol_upper in CRYPTO_SYMBOLS:
        # 虚拟币 symbol 需转为 yfinance 格式（如 BTC -> BTC-USD）
        yf_symbol = symbol + "-USD" if not symbol.endswith("-USD") else symbol
        return get_us_stock_news(yf_symbol, max_news)
    # A股分流（symbol为纯数字）
    elif symbol.isdigit():
        return get_cn_stock_news(symbol, max_news)
    # 美股分流（symbol为纯字母或带-USD）
    else:
        return get_us_stock_news(symbol, max_news)


def get_news_sentiment(news_list: list, num_of_news: int = 5) -> float:
    """分析新闻情感得分

    Args:
        news_list (list): 新闻列表
        num_of_news (int): 用于分析的新闻数量，默认为5条

    Returns:
        float: 情感得分，范围[-1, 1]，-1最消极，1最积极
    """
    if not news_list:
        return 0.0

    # # 获取项目根目录
    # project_root = os.path.dirname(os.path.dirname(
    #     os.path.dirname(os.path.abspath(__file__))))

    # 检查是否有缓存的情感分析结果
    # 检查是否有缓存的情感分析结果
    # cache_file = "src/data/sentiment_cache.json"
    # os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    # 生成新闻内容的唯一标识
    news_key = "|".join([
        f"{news['title']}|{news['content'][:100]}|{news['publish_time']}"
        for news in news_list[:num_of_news]
    ])

    # # 检查缓存
    # if os.path.exists(cache_file):
    #     print("发现情感分析缓存文件")
    #     try:
    #         with open(cache_file, 'r', encoding='utf-8') as f:
    #             cache = json.load(f)
    #             if news_key in cache:
    #                 print("使用缓存的情感分析结果")
    #                 return cache[news_key]
    #             print("未找到匹配的情感分析缓存")
    #     except Exception as e:
    #         print(f"读取情感分析缓存出错: {e}")
    #         cache = {}
    # else:
    #     print("未找到情感分析缓存文件，将创建新文件")
    #     cache = {}

    # 准备系统消息
    system_message = {
        "role": "system",
        "content": """你是一个专业的美股或A股市场分析师，擅长解读新闻对股票走势的影响。你需要分析一组新闻的情感倾向，并给出一个介于-1到1之间的分数：
        - 1表示极其积极（例如：重大利好消息、超预期业绩、行业政策支持）
        - 0.5到0.9表示积极（例如：业绩增长、新项目落地、获得订单）
        - 0.1到0.4表示轻微积极（例如：小额合同签订、日常经营正常）
        - 0表示中性（例如：日常公告、人事变动、无重大影响的新闻）
        - -0.1到-0.4表示轻微消极（例如：小额诉讼、非核心业务亏损）
        - -0.5到-0.9表示消极（例如：业绩下滑、重要客户流失、行业政策收紧）
        - -1表示极其消极（例如：重大违规、核心业务严重亏损、被监管处罚）

        分析时重点关注：
        1. 业绩相关：财报、业绩预告、营收利润等
        2. 政策影响：行业政策、监管政策、地方政策等
        3. 市场表现：市场份额、竞争态势、商业模式等
        4. 资本运作：并购重组、股权激励、定增配股等
        5. 风险事件：诉讼仲裁、处罚、债务等
        6. 行业地位：技术创新、专利、市占率等
        7. 舆论环境：媒体评价、社会影响等

        请确保分析：
        1. 新闻的真实性和可靠性
        2. 新闻的时效性和影响范围
        3. 对公司基本面的实际影响
        4. A股市场的特殊反应规律"""
    }

    # 准备新闻内容
    news_content = "\n\n".join([
        f"标题：{news['title']}\n"
        f"来源：{news['source']}\n"
        f"时间：{news['publish_time']}\n"
        f"内容：{news['content']}"
        for news in news_list[:num_of_news]  # 使用指定数量的新闻
    ])

    user_message = {
        "role": "user",
        "content": f"请分析以下A股上市公司相关新闻的情感倾向：\n\n{news_content}\n\n请直接返回一个数字，范围是-1到1，无需解释。"
    }

    try:
        # 获取LLM分析结果
        result = get_chat_completion([system_message, user_message])
        if result is None:
            print("Error: PI error occurred, LLM returned None")
            return 0.0

        # 提取数字结果
        try:
            sentiment_score = float(result.strip())
        except ValueError as e:
            print(f"Error parsing sentiment score: {e}")
            print(f"Raw result: {result}")
            return 0.0

        # 确保分数在-1到1之间
        sentiment_score = max(-1.0, min(1.0, sentiment_score))

        # 缓存结果
        # cache[news_key] = sentiment_score
        # try:
        #     with open(cache_file, 'w', encoding='utf-8') as f:
        #         json.dump(cache, f, ensure_ascii=False, indent=2)
        # except Exception as e:
        #     print(f"Error writing cache: {e}")

        return sentiment_score

    except Exception as e:
        print(f"Error analyzing news sentiment: {e}")
        return 0.0  # 出错时返回中性分数

# 文件末尾添加 main 测试代码，确保 get_stock_news 已定义
if __name__ == "__main__":
    # 测试分流和字段一致性
    test_cases = [
        {"symbol": "600519", "desc": "A股-贵州茅台", "expect": "A股"},
        {"symbol": "AAPL", "desc": "美股-苹果", "expect": "美股"},
        {"symbol": "BTC", "desc": "虚拟币-BTC", "expect": "虚拟币"},
        {"symbol": "ETH", "desc": "虚拟币-ETH", "expect": "虚拟币"},
        {"symbol": "BNB", "desc": "虚拟币-BNB", "expect": "虚拟币"}
    ]
    for case in test_cases:
        print(f"\n{'='*20} {case['desc']} ({case['symbol']}) {'='*20}")
        news = get_stock_news(case["symbol"], max_news=3)
        if news:
            print(f"分流类型: {case['expect']}, 返回条数: {len(news)}")
            for i, item in enumerate(news, 1):
                # 字段一致性检查
                keys = set(item.keys())
                required = {"title", "content", "publish_time", "source", "url", "keyword"}
                if not required.issubset(keys):
                    print(f"❌ 字段不一致: {keys}")
                else:
                    print(f"✅ 字段一致: {keys}")
                print(f"--- 新闻 {i} ---")
                for k in ["title", "content", "publish_time", "source", "url", "keyword"]:
                    print(f"{k}: {item.get(k, '')[:100]+'...' if k == 'content' else item.get(k, '')}")
        else:
            print("未获取到新闻。")