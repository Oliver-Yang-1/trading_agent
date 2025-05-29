"""
API工具模块 - 提供Agent共享的API功能组件

此模块定义了全局FastAPI应用实例和路由注册机制，
为各个Agent提供统一的API暴露方式。

注意: 大部分功能已被重构到backend目录，此模块仅为向后兼容性而保留。
"""

from fastapi import APIRouter
from backend.main import app  # Restore this import
import json
import logging
import functools
# import uuid # Unused
import threading  # Used for server stop event
import time  # Used for server stop event
import inspect  # Used in log_llm_interaction (decorator mode)
from typing import Dict, List, Any, Optional, Callable, TypeVar  # Keep needed types
from datetime import datetime, UTC  # Keep needed datetime objects
# from contextlib import contextmanager # Unused
# from concurrent.futures import ThreadPoolExecutor, Future # Unused
import uvicorn  # Used in start_api_server
# from functools import wraps # Redundant, imported via functools
# import builtins # Unused
import sys
import io
import os # <--- 添加 os 导入

# 导入重构后的模块
from backend.models.api_models import (
    # ApiResponse, AgentInfo, # Potentially unused
    RunInfo,  # Keep
    # StockAnalysisRequest, StockAnalysisResponse # Potentially unused
)
from backend.state import api_state
from backend.utils.api_utils import (
    # serialize_for_api, # Unused
    safe_parse_json,  # Keep
    format_llm_request,  # Keep
    format_llm_response  # Keep
)
# from backend.utils.context_managers import workflow_run # Unused
# from backend.services import execute_stock_analysis # Unused
from backend.schemas import LLMInteractionLog  # Keep
from backend.schemas import AgentExecutionLog  # Keep
from src.utils.serialization import serialize_agent_state  # Keep

# 导入日志记录器
try:
    # log_agent_execution is no longer needed here
    from src.utils.llm_interaction_logger import set_global_log_storage  # Keep
    from backend.dependencies import get_log_storage
    _has_log_system = True
except ImportError:
    _has_log_system = False
    # Define a dummy set_global_log_storage if import fails

    def set_global_log_storage(storage):
        pass
    # Define a dummy get_log_storage if import fails

    def get_log_storage():
        return None

# 统一在此处定义 logger，无论 _has_log_system 如何
logger = logging.getLogger("api_utils")

# 设置全局日志存储器
if _has_log_system:
    try:
        storage = get_log_storage()
        if storage: # 确保 storage 不是 None
            set_global_log_storage(storage)
    except Exception as e:
        # logger 此时必定已定义
        logger.warning(f"设置全局日志存储器失败: {str(e)}")

# 类型定义
T = TypeVar('T')

# 增加一个全局字典用于跟踪每个agent的LLM调用
_agent_llm_calls = {}

# --- Temporary Messages Logging File ---
# 获取项目根目录 (假设此文件在 src/utils/ 目录下)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MESSAGES_LOG_FILE = os.path.join(PROJECT_ROOT, "data", "temp_messages_log.txt")
# 确保 data 目录存在
if not os.path.exists(os.path.join(PROJECT_ROOT, "data")):
    os.makedirs(os.path.join(PROJECT_ROOT, "data"), exist_ok=True)
# --- End Temporary Messages Logging File ---


# -----------------------------------------------------------------------------
# FastAPI应用
# -----------------------------------------------------------------------------

# 从backend中导入FastAPI应用

# 这些路由器不再使用，仅为向后兼容性保留定义
agents_router = APIRouter(tags=["Agents"])
runs_router = APIRouter(tags=["Runs"])
workflow_router = APIRouter(tags=["Workflow"])

# -----------------------------------------------------------------------------
# 装饰器和工具函数
# -----------------------------------------------------------------------------


def log_llm_interaction(state): # type: ignore
    """记录LLM交互的装饰器函数

    这个函数可以以两种方式使用：
    1. 作为装饰器工厂：log_llm_interaction(state)(llm_func)
    2. 作为直接调用函数：用于已有的log_llm_interaction兼容模式
    """
    # 检查是否是直接函数调用模式（向后兼容）
    if isinstance(state, str) and len(state) > 0:
        # 兼容原有直接调用方式
        agent_name = state  # 第一个参数是agent_name

        def direct_logger(request_data, response_data): # type: ignore
            # 保存格式化的请求和响应
            formatted_request = format_llm_request(request_data)
            formatted_response = format_llm_response(response_data)

            timestamp = datetime.now(UTC)

            # 获取当前运行ID
            run_id = api_state.current_run_id

            api_state.update_agent_data(
                agent_name, "llm_request", formatted_request)
            api_state.update_agent_data(
                agent_name, "llm_response", formatted_response)

            # 记录交互的时间戳
            api_state.update_agent_data(
                agent_name, "llm_timestamp", timestamp.isoformat())

            # 同时保存到BaseLogStorage (解决/logs端点返回空问题)
            try:
                # 获取log_storage实例
                if _has_log_system:
                    log_storage = get_log_storage()
                    if log_storage: # <--- 添加检查 log_storage 是否为 None
                        # 创建LLMInteractionLog对象
                        log_entry = LLMInteractionLog( # type: ignore
                            agent_name=agent_name,
                            run_id=run_id,
                            request_data=formatted_request,
                            response_data=formatted_response,
                            timestamp=timestamp
                        )
                        # 添加到存储
                        log_storage.add_log(log_entry)
                        logger.debug(f"已将直接调用的LLM交互保存到日志存储: {agent_name}")
            except Exception as log_err:
                logger.warning(f"保存直接调用的LLM交互到日志存储失败: {str(log_err)}")

            return response_data

        return direct_logger

    # 装饰器工厂模式
    def decorator(llm_func): # type: ignore
        @functools.wraps(llm_func)
        def wrapper(*args, **kwargs): # type: ignore
            # 获取函数调用信息，以便更好地记录请求
            caller_frame = inspect.currentframe().f_back # type: ignore
            caller_info = {
                "function": llm_func.__name__,
                "file": caller_frame.f_code.co_filename, # type: ignore
                "line": caller_frame.f_lineno # type: ignore
            }

            # 执行原始函数获取结果
            result = llm_func(*args, **kwargs)

            # 从state中提取agent_name和run_id
            agent_name_from_state = None # type: ignore
            run_id_from_state = None # type: ignore

            # 尝试从state参数中提取 (这里的 state 是 log_llm_interaction 的参数，不是 agent 的 state)
            current_agent_state_dict = None
            # Check if 'state' (the decorator parameter) is a dict and has metadata
            if isinstance(state, dict) and "metadata" in state:
                 current_agent_state_dict = state
            elif args and isinstance(args[0], dict) and "metadata" in args[0]: # 假设第一个参数是 AgentState
                 current_agent_state_dict = args[0]
            elif 'state' in kwargs and isinstance(kwargs['state'], dict) and "metadata" in kwargs['state']:
                 current_agent_state_dict = kwargs['state']


            if current_agent_state_dict:
                agent_name_from_state = current_agent_state_dict.get("metadata", {}).get(
                    "current_agent_name")
                run_id_from_state = current_agent_state_dict.get("metadata", {}).get("run_id")


            # 如果state中没有，尝试从上下文变量中获取
            if not agent_name_from_state:
                try:
                    from src.utils.llm_interaction_logger import current_agent_name_context, current_run_id_context
                    agent_name_from_state = current_agent_name_context.get()
                    run_id_from_state = current_run_id_context.get()
                except (ImportError, AttributeError, LookupError):
                    pass

            final_agent_name = agent_name_from_state
            final_run_id = run_id_from_state

            if not final_agent_name and hasattr(api_state, "current_agent_name"):
                final_agent_name = api_state.current_agent_name
                final_run_id = api_state.current_run_id


            if final_agent_name:
                timestamp = datetime.now(UTC)

                messages_arg = None
                if "messages" in kwargs:
                    messages_arg = kwargs["messages"]
                elif args and len(args) > 0 and isinstance(args[0], list):
                    messages_arg = args[0]
                elif args and len(args) > 1 and isinstance(args[1], list):
                    messages_arg = args[1]


                model_arg = kwargs.get("model")
                if not model_arg and args and len(args) > 0 and isinstance(args[0], str):
                    model_arg = args[0]

                client_type_arg = kwargs.get("client_type", "auto")

                formatted_request = {
                    "caller": caller_info,
                    "messages": messages_arg,
                    "model": model_arg,
                    "client_type": client_type_arg,
                    "arguments": format_llm_request(args),
                    "kwargs": format_llm_request(kwargs) if kwargs else {}
                }
                formatted_response = format_llm_response(result)

                api_state.update_agent_data(
                    final_agent_name, "llm_request", formatted_request)
                api_state.update_agent_data(
                    final_agent_name, "llm_response", formatted_response)
                api_state.update_agent_data(
                    final_agent_name, "llm_timestamp", timestamp.isoformat())

                try:
                    if _has_log_system:
                        log_storage = get_log_storage()
                        if log_storage: # <--- 添加检查 log_storage 是否为 None
                            log_entry = LLMInteractionLog( # type: ignore
                                agent_name=final_agent_name,
                                run_id=final_run_id,
                                request_data=formatted_request,
                                response_data=formatted_response,
                                timestamp=timestamp
                            )
                            log_storage.add_log(log_entry)
                            logger.debug(f"已将装饰器捕获的LLM交互保存到日志存储: {final_agent_name}")
                except Exception as log_err:
                    logger.warning(f"保存装饰器捕获的LLM交互到日志存储失败: {str(log_err)}")
            return result
        return wrapper
    if callable(state):
        return decorator(state)
    return decorator


def agent_endpoint(agent_name_param: str, description: str = ""): # Renamed agent_name to agent_name_param
    """
    为Agent创建API端点的装饰器

    用法:
    @agent_endpoint("sentiment")
    def sentiment_agent(state: AgentState) -> AgentState:
        ...
    """
    def decorator(agent_func: Callable): # type: ignore
        # 注册Agent
        api_state.register_agent(agent_name_param, description)

        # 初始化此agent的LLM调用跟踪
        _agent_llm_calls[agent_name_param] = False

        @functools.wraps(agent_func)
        def wrapper(state: Dict[str, Any]): # type: ignore
            current_agent_name_for_run = agent_name_param

            api_state.update_agent_state(current_agent_name_for_run, "running")

            if "metadata" not in state:
                state["metadata"] = {}
            state["metadata"]["current_agent_name"] = current_agent_name_for_run
            run_id = state.get("metadata", {}).get("run_id")
            if not run_id:
                logger.warning(f"run_id not found in state metadata for agent {current_agent_name_for_run}. Logging may be affected.")


            timestamp_start = datetime.now(UTC)
            serialized_input = serialize_agent_state(state)
            api_state.update_agent_data(
                current_agent_name_for_run, "input_state", serialized_input)

            output_state = None
            error_details = None
            terminal_outputs: List[str] = []

            old_stdout = sys.stdout
            old_stderr = sys.stderr
            log_stream = io.StringIO()
            
            # 使用 agent_name_param 确保日志处理器名称的唯一性
            agent_specific_logger_name = f"agent_stream.{current_agent_name_for_run}"
            agent_specific_logger = logging.getLogger(agent_specific_logger_name)
            agent_specific_logger.handlers.clear() # 清除旧的处理器
            agent_specific_logger.propagate = False # 防止传播到root logger
            log_handler = logging.StreamHandler(log_stream)
            log_handler.setLevel(logging.INFO) 
            # 可以为这个handler设置特定的格式
            # log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            # log_handler.setFormatter(log_formatter)
            agent_specific_logger.addHandler(log_handler)


            redirect_stdout = io.StringIO()
            redirect_stderr = io.StringIO()
            sys.stdout = redirect_stdout
            sys.stderr = redirect_stderr

            try:
                if _has_log_system:
                    from src.utils.llm_interaction_logger import current_agent_name_context, current_run_id_context
                    current_agent_name_context.set(current_agent_name_for_run)
                    current_run_id_context.set(run_id) # type: ignore

                output_state = agent_func(state)
                timestamp_end = datetime.now(UTC)

            except Exception as e:
                timestamp_end = datetime.now(UTC)
                error_details = str(e)
                logger.error(f"Error during execution of agent {current_agent_name_for_run}: {error_details}", exc_info=True)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                agent_specific_logger.removeHandler(log_handler) # 从特定logger移除
                log_handler.close()


                stdout_content = redirect_stdout.getvalue()
                stderr_content = redirect_stderr.getvalue()
                log_capture_content = log_stream.getvalue() # 从特定logger的stream获取

                if stdout_content:
                    terminal_outputs.append(f"--- STDOUT for {current_agent_name_for_run} ---\n{stdout_content}")
                if stderr_content:
                    terminal_outputs.append(f"--- STDERR for {current_agent_name_for_run} ---\n{stderr_content}")
                if log_capture_content:
                    terminal_outputs.append(f"--- LOGS for {current_agent_name_for_run} ---\n{log_capture_content}")

                if _has_log_system:
                    from src.utils.llm_interaction_logger import current_agent_name_context, current_run_id_context
                    current_agent_name_context.set(None) # type: ignore
                    current_run_id_context.set(None) # type: ignore


            serialized_output_for_log = None
            reasoning_details_for_log = None

            if error_details:
                api_state.update_agent_state(current_agent_name_for_run, "error")
                api_state.update_agent_data(current_agent_name_for_run, "error", error_details)
                serialized_output_for_log = {"error": error_details}
            else:
                if output_state: # 确保 output_state 不是 None
                    serialized_output_for_log = serialize_agent_state(output_state)
                    api_state.update_agent_data(
                        current_agent_name_for_run, "output_state", serialized_output_for_log)

                    if output_state.get("metadata", {}).get("show_reasoning", False):
                        if "agent_reasoning" in output_state.get("metadata", {}):
                            reasoning_details_for_log = output_state["metadata"]["agent_reasoning"]
                            api_state.update_agent_data(
                                current_agent_name_for_run,
                                "reasoning",
                                reasoning_details_for_log
                            )
                    api_state.update_agent_state(current_agent_name_for_run, "completed")


            # --- Temporary Messages Logging ---
            if not error_details and output_state and "messages" in output_state and isinstance(output_state["messages"], list):
                sender_names = [msg.name for msg in output_state["messages"] if hasattr(msg, 'name')]
                log_entry_msg_content = f"{current_agent_name_for_run}: {sender_names}\n"
                try:
                    with open(MESSAGES_LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(log_entry_msg_content)
                except Exception as log_e:
                    logger.error(f"Failed to write to temp messages log for {current_agent_name_for_run}: {log_e}")
            # --- End Temporary Messages Logging ---


            try:
                if _has_log_system:
                    log_storage = get_log_storage()
                    if log_storage:
                        log_entry_agent = AgentExecutionLog( # type: ignore
                            agent_name=current_agent_name_for_run,
                            run_id=run_id, # type: ignore
                            timestamp_start=timestamp_start,
                            timestamp_end=timestamp_end,
                            input_state=serialized_input,
                            output_state=serialized_output_for_log,
                            reasoning_details=reasoning_details_for_log,
                            terminal_outputs=terminal_outputs
                        )
                        log_storage.add_agent_log(log_entry_agent)
                        logger.debug(
                            f"已将Agent执行日志保存到存储: {current_agent_name_for_run}, run_id: {run_id}")
                    else:
                        logger.warning(
                            f"无法获取日志存储实例，跳过Agent执行日志记录: {current_agent_name_for_run}")
            except Exception as log_err:
                logger.error(
                    f"保存Agent执行日志到存储失败: {current_agent_name_for_run}, {str(log_err)}")

            if error_details:
                raise Exception(f"Agent {current_agent_name_for_run} failed: {error_details}") # Re-raise

            return output_state # type: ignore

        return wrapper
    return decorator


# 启动API服务器的函数
def start_api_server(host="0.0.0.0", port=8000, stop_event=None): # type: ignore
    """在独立线程中启动API服务器"""
    if stop_event:
        config = uvicorn.Config( # type: ignore
            app=app, 
            host=host,
            port=port,
            log_config=None, 
            use_colors=True 
        )
        server = uvicorn.Server(config) # type: ignore

        def check_stop_event(): # type: ignore
            while not stop_event.is_set():
                time.sleep(0.5)
            logger.info("收到停止信号，正在关闭API服务器...")
            server.should_exit = True

        stop_monitor = threading.Thread(
            target=check_stop_event,
            daemon=True
        )
        stop_monitor.start()
        try:
            server.run()
        except KeyboardInterrupt:
            if stop_event: 
                stop_event.set()
        logger.info("API服务器已关闭")
    else:
        uvicorn.run(app, host=host, port=port, log_config=None) # type: ignore
