import yfinance as yf
import requests
from newspaper import Article
import logging
from datetime import datetime
import os

# --- 配置 ---
# 设置日志记录，方便调试
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 辅助函数 ---

# --- 代理配置 ---
# 在程序启动时为所有网络库设置SOCKS5代理。
# 请将下面的地址和端口替换为你的实际代理配置。
def proxy_setting():
    PROXY_HOST = "127.0.0.1"
    PROXY_PORT = 7897  # 你的SOCKS5代理端口

    proxy_url = f"socks5h://{PROXY_HOST}:{PROXY_PORT}"

    # 1. 为 yfinance (其内部使用 curl_cffi) 设置代理
    os.environ['CURL_SOCKS5'] = proxy_url

    # 2. 为 requests (用于备用搜索和 newspaper3k) 设置代理
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url

    logging.info(f"代理已配置，所有网络请求将通过 {proxy_url}")

def _extract_article_text(url):
    """下载并从新闻文章URL中提取主要文本。"""
    if not url:
        return ''
    try:
        # 为网络请求设置超时，并对有问题的网站禁用SSL验证
        article = Article(url, request_timeout=10, verify_ssl=False)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logging.warning(f"无法从 {url} 提取文本。原因: {e}")
        return ''

def _normalize_and_add_news(raw_item, news_list, seen_links, source_type):
    """
    将来自任何来源的原始新闻项规范化，如果不是重复的，则添加到列表中。
    """
    title, link, publisher, timestamp = '', '', '', 0

    if source_type == 'stock_news':
        # 处理来自 yfinance stock.news 的嵌套 'content' 结构
        content = raw_item.get('content', {})
        title = content.get('title', '')
        link = content.get('canonicalUrl', {}).get('url', '')
        publisher = content.get('provider', {}).get('displayName', '')
        # pubDate 是一个字符串，如 '2025-07-11T21:38:42Z'，将其转换为时间戳
        pub_date_str = content.get('pubDate', '')
        if pub_date_str:
            try:
                timestamp = int(datetime.fromisoformat(pub_date_str.replace('Z', '+00:00')).timestamp())
            except ValueError:
                timestamp = 0
    elif source_type == 'search_api':
        # 处理来自搜索API的扁平结构
        title = raw_item.get('title', '')
        link = raw_item.get('link', '')
        publisher = raw_item.get('publisher', '')
        timestamp = raw_item.get('providerPublishTime', 0)

    if link and link not in seen_links:
        seen_links.add(link)
        news_list.append({
            'title': title,
            'link': link,
            'publisher': publisher,
            'time': timestamp,
            'text': _extract_article_text(link)
        })

# --- 主要功能 ---

def get_stock_news(ticker):
    """
    从多个雅虎财经来源获取股票代码的相关新闻。

    它首先尝试使用直接的 `stock.news` 属性，这个属性通常
    不可靠或受速率限制。然后，它会使用更健壮的
    关键词搜索（雅虎内部搜索API）来补充新闻。

    Args:
        ticker (str): 股票代码 (例如, 'AAPL', 'IXIC', '600519.SS').

    Returns:
        list: 新闻文章列表，每篇文章是一个字典。
              如果找不到新闻或发生错误，则返回空列表。
    """
    logging.info(f"正在为代码获取新闻: {ticker}")
    stock = yf.Ticker(ticker)
    news_list = []
    seen_links = set()

    # --- 来源 1: 直接的 `stock.news` 属性 (经常失败/受速率限制) ---
    try:
        direct_news = stock.news
        if direct_news:
            logging.info(f"从 stock.news API 找到 {len(direct_news)} 条新闻。")
            for item in direct_news:
                _normalize_and_add_news(item, news_list, seen_links, 'stock_news')
    except Exception as e:
        logging.warning(f"无法为 {ticker} 从 stock.news 获取新闻。原因: {e}。将继续使用搜索API。")

    # --- 来源 2: 关键词搜索 API (更可靠的备用/补充方案) ---
    keywords = []
    try:
        # 为主要指数定义关键词
        index_keywords = {
            'IXIC': ['Nasdaq Composite', 'Nasdaq Index', 'US stock market'],
            '^IXIC': ['Nasdaq Composite', 'Nasdaq Index', 'US stock market'],
            'GSPC': ['S&P 500', 'US stock market'],
            '^GSPC': ['S&P 500', 'US stock market'],
        }
        
        if ticker.upper() in index_keywords:
            keywords = index_keywords[ticker.upper()]
        else:
            # 对于普通股票，使用其名称作为主要关键词
            info = stock.info
            company_name = info.get('longName') or info.get('shortName')
            if company_name:
                keywords.append(company_name)
            else:
                keywords.append(ticker) # 如果找不到名称，则退回到股票代码
        
        logging.info(f"正在使用关键词进行搜索: {keywords}")

        for kw in keywords:
            try:
                url = f"https://query2.finance.yahoo.com/v1/finance/search?q={kw}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
                resp = requests.get(url, headers=headers, timeout=10)
                resp.raise_for_status() # 对错误的HTTP状态码抛出异常
                data = resp.json()
                search_news = data.get('news', [])
                if search_news:
                    logging.info(f"为关键词 '{kw}' 从搜索 API 找到 {len(search_news)} 条新闻。")
                    for item in search_news:
                        _normalize_and_add_news(item, news_list, seen_links, 'search_api')
            except requests.RequestException as e:
                logging.error(f"搜索关键词 '{kw}' 时发生网络错误: {e}")
            except Exception as e:
                logging.error(f"处理关键词 '{kw}' 的搜索结果时出错: {e}")

    except Exception as e:
        logging.error(f"为 {ticker} 生成关键词或获取股票信息失败。原因: {e}")

    logging.info(f"为 {ticker} 获取新闻结束。共找到 {len(news_list)} 篇不重复的文章。")
    return news_list

# --- 示例用法 ---
if __name__ == "__main__":
    proxy_setting()
    tickers_to_test = ["AAPL", "IXIC"]
    for code in tickers_to_test:
        print(f"\n{'='*15} News for {code} {'='*15}")
        news_articles = get_stock_news(code)
        if news_articles:
            # 只打印前3篇文章作为示例
            for i, n in enumerate(news_articles[:3], 1):
                print(f"\n--- 第 {i} 篇 ---")
                print(f"  标题: {n['title']}")
                print(f"  链接: {n['link']}")
                print(f"  发布者: {n['publisher']}")
                # 将时间戳转换为可读格式
                if n['time']:
                    print(f"  时间: {datetime.fromtimestamp(n['time'])}")
                else:
                    print("  时间: 不可用")
                # 打印正文摘要
                print(f"  正文: {n['text'][:200]}...")
        else:
            print("未找到相关新闻。")
        print("="*42)