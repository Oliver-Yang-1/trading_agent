#!/usr/bin/env python
"""
增强版运行脚本 - 执行股票投资Agent同时启动FastAPI后端

使用方法:
    # 仅启动后端API服务（默认模式）
    poetry run python run_with_backend.py
    
    # 启动后端并立即执行分析
    poetry run python run_with_backend.py --ticker 002848 --show-reasoning
    
此脚本会:
1. 默认仅启动FastAPI后端服务在 http://localhost:8000
2. 当提供--ticker参数时，同时执行与 src/main.py 相同的功能
3. 可通过API端点访问执行过程中的详细信息
"""

import os
import sys
import argparse
import threading
import time
import uuid
import signal
import multiprocessing
from datetime import datetime, timedelta

# 导入新的API工具
from src.utils.api_utils import start_api_server
# 直接从源文件导入 workflow_run 上下文管理器
from backend.utils.context_managers import workflow_run

# 导入原始main.py的关键组件
from src.main import run_hedge_fund

# 控制后端服务停止的全局标志
stop_event = threading.Event()


def start_backend_server(host="0.0.0.0", port=8000, stop_event=None):
    """Start the FastAPI backend server."""
    print(
        f"\n🚀 Starting backend API server - Visit http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs for API documentation")
    # Use the new API server start function, set parameters so it can be interrupted properly
    start_api_server(host=host, port=port, stop_event=stop_event)


def signal_handler(sig, frame):
    """Handle termination signals."""
    print("\n\n⚠️ Received termination signal, gracefully shutting down the service...\n")
    stop_event.set()  # Set the stop flag
    time.sleep(1)  # Give the service some time to clean up
    print("👋 Service stopped")
    sys.exit(0)


def run_with_backend():
    """主程序入口函数"""
    # 创建与原始main.py相同的参数解析
    parser = argparse.ArgumentParser(
        description='运行股票投资分析系统 (带后端API服务)'
    )
    parser.add_argument('--ticker', type=str,
                        help='股票代码 (如果提供，将同时执行分析)')
    parser.add_argument('--start-date', type=str,
                        help='开始日期 (YYYY-MM-DD)，默认为结束日期前一年')
    parser.add_argument('--end-date', type=str,
                        help='结束日期 (YYYY-MM-DD)，默认为昨天')
    parser.add_argument('--show-reasoning', action='store_true',
                        help='显示每个Agent的分析推理过程')
    parser.add_argument('--num-of-news', type=int, default=5,
                        help='用于情感分析的新闻文章数量 (默认: 5)')
    parser.add_argument('--initial-capital', type=float, default=100000.0,
                        help='初始资金 (默认: 100,000)')
    parser.add_argument('--initial-position', type=int, default=0,
                        help='初始持仓数量 (默认: 0)')

    # 额外的后端服务配置参数
    parser.add_argument('--backend-host', type=str, default="0.0.0.0",
                        help='后端服务主机 (默认: 0.0.0.0)')
    parser.add_argument('--backend-port', type=int, default=8000,
                        help='后端服务端口 (默认: 8000)')

    args = parser.parse_args()

    # 打印欢迎消息
    print("\n" + "="*70)
    if args.ticker:
        print(f"🤖 A-Share Investment Agent System (with API backend) - Analyzing stock: {args.ticker}")
    else:
        print(f"🤖 A-Share Investment Agent System (API backend only mode)")
    print("="*70)

    # 启动后端服务器（在后台线程中）
    backend_thread = threading.Thread(
        target=start_backend_server,
        args=(args.backend_host, args.backend_port, stop_event),
        daemon=True  # 设为守护线程，主程序结束时自动结束
    )
    backend_thread.start()

    # 等待后端服务启动
    print("⏳ Waiting for backend server to start...")
    time.sleep(2)  # 给uvicorn一些启动时间

    run_id = None
    result = None

    # 如果提供了ticker参数，执行分析
    if args.ticker:
        # 处理日期参数，与原始main.py保持一致
        current_date = datetime.now()
        yesterday = current_date - timedelta(days=1)
        end_date = yesterday if not args.end_date else min(
            datetime.strptime(args.end_date, '%Y-%m-%d'), yesterday)

        if not args.start_date:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d')

        # 验证参数
        if start_date > end_date:
            raise ValueError("开始日期不能晚于结束日期")
        if args.num_of_news < 1:
            raise ValueError("新闻文章数量必须至少为1")
        if args.num_of_news > 100:
            raise ValueError("新闻文章数量不能超过100")

        # 初始化投资组合
        portfolio = {
            "cash": args.initial_capital,
            "stock": args.initial_position
        }

        # 生成唯一运行ID
        run_id = str(uuid.uuid4())

        # 执行对冲基金逻辑（使用workflow_run上下文管理器）
        print(f"\n📊 开始执行投资分析... (运行ID: {run_id})")
        with workflow_run(run_id):
            result = run_hedge_fund(
                ticker=args.ticker,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                portfolio=portfolio,
                show_reasoning=args.show_reasoning,
                num_of_news=args.num_of_news
            )

        # 显示结果
        print("\n🔍 最终分析结果:")
        print(result)

    # 提示API访问信息
    print("\n" + "-"*70)
    print(
        f"✅ Backend API server started - Visit http://localhost:{args.backend_port}/docs for API documentation")
    if run_id:
        print(f"📝 You can view Agent execution history and reasoning via the API")
        print(f"🆔 Current run ID: {run_id}")
    print(f"🔄 You can trigger a new stock analysis via the POST /analysis/start endpoint")
    print("-"*70)

    # Keep the program running so that the backend service continues to provide service
    print("\nPress Ctrl+C to exit...\n")

    try:
        # Use periodic checking instead of direct join for better Ctrl+C responsiveness
        while not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        # Ensure stop_event is set when KeyboardInterrupt is caught in the main thread
        stop_event.set()
        print("\n👋 Service stopped")
        sys.exit(0)


if __name__ == "__main__":
    # Set signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Special handling for CTRL_C_EVENT on Windows
    if sys.platform == 'win32':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCtrlHandler(None, False)

    # Run the main program
    try:
        run_with_backend()
    except KeyboardInterrupt:
        # Ensure we handle KeyboardInterrupt from anywhere
        stop_event.set()
        print("\n👋 Service stopped")
        sys.exit(0)

