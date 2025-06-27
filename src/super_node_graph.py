"""
Interactive Super Node Graph - 交互式超级节点图

这个Graph是一个通用的任务执行agent，提供交互式体验：
1. AI 抛出初始问题，询问用户想要执行什么任务
2. 用户输入任意查询或任务
3. Super Node 进行 ReAct 分析和任务执行
4. 用户可以继续提问或执行其他任务

使用方式:
python src/super_node_graph.py
"""

import sys
import argparse
import uuid
import threading
import uvicorn
from datetime import datetime, timedelta
from typing import Annotated, Any, Dict, Sequence, TypedDict

from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage, AIMessage
import operator

# --- Agent Imports ---
from src.agents.super_node import super_node_agent
from src.agents.state import AgentState
from src.tools.openrouter_config import get_chat_completion
from src.utils.logging_config import setup_logger
from src.utils.api_utils import log_llm_interaction

# --- Backend Imports ---
from backend.dependencies import get_log_storage
from backend.main import app as fastapi_app
from src.utils.llm_interaction_logger import set_global_log_storage

# --- Initialize Logging ---
log_storage = get_log_storage()
set_global_log_storage(log_storage)
logger = setup_logger('super_node_graph')

# --- Interactive State Definition ---
class InteractiveState(TypedDict):
    """交互式状态，扩展了AgentState以支持用户交互"""
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    data: Annotated[Dict[str, Any], lambda a, b: {**a, **b}]
    metadata: Annotated[Dict[str, Any], lambda a, b: {**a, **b}]
    current_input: str  # 用户当前输入
    conversation_active: bool  # 对话是否继续
    iteration_count: int  # 交互轮次


def ai_initiator_node(state: InteractiveState) -> InteractiveState:
    """AI初始化节点 - 抛出初始问题"""
    logger.info("🤖 AI Initiator: 开始对话")
    
    # AI的初始问候和问题
    initial_message = """你好！我是您的智能任务助手。

我可以帮您执行各种任务和分析，包括但不限于：

📊 股票分析 - 财务指标、技术分析、市场情绪
📈 数据分析 - 数据处理、统计分析、可视化
🔍 信息查询 - 新闻搜集、信息整理、内容分析
💼 业务分析 - 市场研究、竞争分析、趋势预测
🧮 计算任务 - 数学计算、公式推导、逻辑推理
📝 文档处理 - 内容生成、格式转换、信息提取

请告诉我您想要执行什么任务？我将使用ReAct模式为您提供智能分析。

您的任务是："""

    print("\n" + "="*60)
    print("🤖 AI助手：")
    print(initial_message)
    print("="*60)
    
    # 创建AI消息
    ai_message = AIMessage(
        content=initial_message,
        name="ai_initiator"
    )
    
    return {
        "messages": [ai_message],
        "data": state["data"],
        "metadata": state["metadata"],
        "current_input": "",
        "conversation_active": True,
        "iteration_count": state.get("iteration_count", 0)
    }


def user_input_node(state: InteractiveState) -> InteractiveState:
    """用户输入节点 - 获取用户输入"""
    logger.info("👤 User Input: 等待用户输入")
    
    # 获取用户输入
    try:
        print("\n📝 请输入您的任务或问题 (输入 'quit' 或 'exit' 退出)：")
        user_input = input("👤 您：").strip()
        
        if user_input.lower() in ['quit', 'exit', '退出', 'q']:
            print("\n👋 感谢使用，再见！")
            return {
                "messages": state["messages"],
                "data": state["data"],
                "metadata": state["metadata"],
                "current_input": user_input,
                "conversation_active": False,
                "iteration_count": state.get("iteration_count", 0)
            }
        
        if not user_input:
            user_input = "请介绍你的功能"  # 默认请求
             
        print(f"\n✅ 收到您的任务：{user_input}")
        
    except KeyboardInterrupt:
        print("\n\n👋 检测到退出信号，再见！")
        return {
            "messages": state["messages"],
            "data": state["data"],
            "metadata": state["metadata"],
            "current_input": "",
            "conversation_active": False,
            "iteration_count": state.get("iteration_count", 0)
        }
    
    # 创建用户消息
    user_message = HumanMessage(
        content=user_input,
        name="user"
    )
    
    return {
        "messages": state["messages"] + [user_message],
        "data": state["data"],
        "metadata": state["metadata"],
        "current_input": user_input,
        "conversation_active": True,
        "iteration_count": state.get("iteration_count", 0) + 1
    }


def super_node_wrapper(state: InteractiveState) -> InteractiveState:
    """Super Node包装器 - 调用ReAct分析"""
    logger.info("🧠 Super Node: 开始ReAct分析")
    
    print("\n🔍 开始智能分析...")
    print("⚡ ReAct模式启动中...")
    
    # 构建AgentState用于super_node
    agent_state = {
        "messages": state["messages"],
        "data": state["data"],
        "metadata": {
            **state["metadata"],
            "user_query": state.get("current_input", ""),
            "show_reasoning": True  # 显示推理过程
        }
    }
    
    # 调用super_node_agent
    try:
        result_state = super_node_agent(agent_state)
        
        # 提取分析结果
        analysis_message = result_state["messages"][-1] if result_state["messages"] else None
        
        if analysis_message:
            print("\n🎯 分析完成！")
            print("\n" + "="*60)
            print("📊 分析结果：")
            
            # 解析并显示结果
            try:
                import json
                result_content = json.loads(analysis_message.content)
                final_answer = result_content.get("reasoning", "分析完成")
                print(final_answer)
            except:
                print(analysis_message.content)
            
            print("="*60)
        
        return {
            "messages": state["messages"] + result_state["messages"],
            "data": result_state["data"],
            "metadata": result_state["metadata"],
            "current_input": "",
            "conversation_active": True,
            "iteration_count": state.get("iteration_count", 0)
        }
        
    except Exception as e:
        logger.error(f"Super Node分析出错: {e}")
        error_message = AIMessage(
            content=f"抱歉，分析过程中遇到问题：{str(e)}",
            name="super_node_error"
        )
        
        print(f"\n❌ 分析出错：{str(e)}")
        
        return {
            "messages": state["messages"] + [error_message],
            "data": state["data"],
            "metadata": state["metadata"],
            "current_input": "",
            "conversation_active": True,
            "iteration_count": state.get("iteration_count", 0)
        }


def should_continue(state: InteractiveState) -> str:
    """条件路由 - 决定是否继续对话"""
    if not state.get("conversation_active", True):
        logger.info("🔚 对话结束")
        return "end"
    
    iteration = state.get("iteration_count", 0)
    if iteration >= 10:  # 最大10轮对话
        print("\n⏰ 已达到最大对话轮次，会话结束。")
        return "end"
    
    logger.info(f"🔄 继续对话 (第{iteration}轮)")
    return "continue"


def farewell_node(state: InteractiveState) -> InteractiveState:
    """告别节点"""
    logger.info("👋 Farewell: 结束对话")
    
    farewell_message = """

🎉 任务会话结束！

感谢您使用AI智能任务助手。如果您需要执行更多任务，请随时重新启动程序。

💡 小贴士：
- 我可以帮您执行各种分析和任务
- 使用 --show-reasoning 查看详细的推理过程  
- 支持连续对话，让任务执行更高效
- 每次启动都是全新的会话

期待再次为您服务！ 🚀✨
"""
    
    print(farewell_message)
    
    farewell_ai_message = AIMessage(
        content=farewell_message,
        name="farewell"
    )
    
    return {
        "messages": state["messages"] + [farewell_ai_message],
        "data": state["data"],
        "metadata": state["metadata"],
        "current_input": "",
        "conversation_active": False,
        "iteration_count": state.get("iteration_count", 0)
    }


# --- 创建交互式Graph ---
def create_interactive_graph():
    """创建交互式Graph"""
    workflow = StateGraph(InteractiveState)
    
    # 添加节点
    workflow.add_node("ai_initiator", ai_initiator_node)
    workflow.add_node("user_input", user_input_node)
    workflow.add_node("super_node_analysis", super_node_wrapper)
    workflow.add_node("farewell", farewell_node)
    
    # 设置入口点
    workflow.set_entry_point("ai_initiator")
    
    # 添加边
    workflow.add_edge("ai_initiator", "user_input")
    workflow.add_edge("user_input", "super_node_analysis")
    
    # 条件边：分析完成后，检查是否继续
    workflow.add_conditional_edges(
        "super_node_analysis",
        should_continue,
        {
            "continue": "user_input",
            "end": "farewell"
        }
    )
    
    # 结束边
    workflow.add_edge("farewell", END)
    
    return workflow.compile()


# --- FastAPI Background Task ---
def run_fastapi():
    """后台运行FastAPI服务器"""
    logger.info("🚀 Starting FastAPI server in background (port 8000)")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_config=None)


# --- 主运行函数 ---
def run_interactive_session(show_reasoning: bool = True):
    """运行交互式会话"""
    print("\n🚀 启动智能任务助手...")
    print("🤖 准备为您执行各种任务...")
    
    # 生成运行ID
    run_id = str(uuid.uuid4())
    logger.info(f"🆔 Session ID: {run_id}")
    
    # 设置初始状态 - 通用数据结构
    initial_state = {
        "messages": [],
        "data": {
            # 通用数据存储，根据用户任务动态填充
            "task_context": {},
            "session_info": {
                "start_time": datetime.now().isoformat(),
                "session_type": "interactive"
            }
        },
        "metadata": {
            "show_reasoning": show_reasoning,
            "run_id": run_id,
            "session_type": "interactive",
        },
        "current_input": "",
        "conversation_active": True,
        "iteration_count": 0
    }
    
    # 创建并运行Graph
    app = create_interactive_graph()
    
    try:
        final_state = app.invoke(initial_state)
        logger.info("✅ 交互会话成功完成")
        return final_state
    except KeyboardInterrupt:
        print("\n\n👋 会话被用户中断，再见！")
        return None
    except Exception as e:
        logger.error(f"❌ 交互会话出错: {e}")
        print(f"\n❌ 会话出现错误：{str(e)}")
        return None


# --- 主程序入口 ---
if __name__ == "__main__":
    # 启动FastAPI后台服务
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='智能任务助手 - 可执行任意分析和任务')
    parser.add_argument('--show-reasoning', action='store_true', default=True,
                        help='显示详细推理过程 (默认: True)')
    parser.add_argument('--no-reasoning', action='store_true',
                        help='不显示推理过程')
    
    args = parser.parse_args()
    
    # 处理推理显示设置
    show_reasoning = args.show_reasoning and not args.no_reasoning
    
    try:
        # 运行交互式会话
        run_interactive_session(
            show_reasoning=show_reasoning
        )
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断，再见！")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        print(f"\n❌ 程序出现错误：{str(e)}") 