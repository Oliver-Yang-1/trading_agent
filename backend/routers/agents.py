"""
Agent相关路由模块

此模块提供与Agent状态、信息和数据相关的API端点
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
import logging

from ..models.api_models import ApiResponse, AgentInfo
from ..state import api_state
from ..utils.api_utils import serialize_for_api

logger = logging.getLogger("agents_router")

# 创建路由器
router = APIRouter(prefix="/api/agents", tags=["Agents"])


@router.get("/", response_model=List[AgentInfo])
async def list_agents():
    """获取所有Agent列表"""
    agents = api_state.get_all_agents()
    return agents


@router.get("/{agent_name}", response_model=ApiResponse[Dict])
async def get_agent_info(agent_name: str):
    """获取指定Agent的信息"""
    info = api_state.get_agent_info(agent_name)
    if not info:
        return ApiResponse(
            success=False,
            message=f"Agent '{agent_name}' 不存在",
            data=None
        )
    return ApiResponse(data=info)


@router.get("/{agent_name}/latest_input", response_model=ApiResponse[Dict])
async def get_latest_input(agent_name: str):
    """获取Agent的最新输入状态"""
    data = api_state.get_agent_data(agent_name, "input_state")
    return ApiResponse(data=serialize_for_api(data))


@router.get("/{agent_name}/latest_output", response_model=ApiResponse[Dict])
async def get_latest_output(agent_name: str):
    """获取Agent的最新输出状态"""
    data = api_state.get_agent_data(agent_name, "output_state")
    return ApiResponse(data=serialize_for_api(data))


@router.get("/{agent_name}/reasoning", response_model=ApiResponse[Dict])
async def get_reasoning(agent_name: str):
    """获取Agent的推理详情"""
    try:
        # 获取数据
        data = api_state.get_agent_data(agent_name, "reasoning")

        # 如果数据不存在
        if data is None:
            return ApiResponse(
                success=False,
                message=f"没有找到{agent_name}的推理记录",
                data={"message": f"Agent {agent_name} 没有推理数据"}
            )

        # 尝试解析和序列化数据
        serialized_data = serialize_for_api(data)

        # 确保结果是字典类型
        if not isinstance(serialized_data, dict):
            # 如果不是字典，包装为字典返回
            return ApiResponse(
                data={"content": serialized_data, "type": "raw_content"}
            )

        return ApiResponse(data=serialized_data)
    except Exception as e:
        # 记录错误并返回友好的错误信息
        logger.error(f"序列化{agent_name}的推理数据时出错: {str(e)}")
        return ApiResponse(
            success=False,
            message=f"无法处理{agent_name}的推理数据: {str(e)}",
            data={"error": str(e), "original_type": str(type(data))}
        )


@router.get("/{agent_name}/latest_llm_request", response_model=ApiResponse[Dict])
async def get_latest_llm_request(agent_name: str):
    """获取Agent的最新LLM请求"""
    try:
        data = api_state.get_agent_data(agent_name, "llm_request")

        # 确保返回有意义的数据
        if data is None:
            return ApiResponse(
                success=True,
                message=f"没有找到{agent_name}的LLM请求记录",
                data={"message": f"没有找到{agent_name}的LLM请求记录"}
            )

        # 尝试解析和序列化数据
        serialized_data = serialize_for_api(data)

        # 确保结果是字典类型
        if not isinstance(serialized_data, dict):
            # 如果不是字典，包装为字典返回
            serialized_data = {
                "content": serialized_data, "type": "raw_content"}

        return ApiResponse(data=serialized_data)
    except Exception as e:
        logger.error(f"处理{agent_name}的LLM请求数据时出错: {str(e)}")
        return ApiResponse(
            success=False,
            message=f"无法处理{agent_name}的LLM请求数据: {str(e)}",
            data={"error": str(e)}
        )


@router.get("/{agent_name}/latest_llm_response", response_model=ApiResponse[Dict])
async def get_latest_llm_response(agent_name: str):
    """获取Agent的最新LLM响应"""
    try:
        data = api_state.get_agent_data(agent_name, "llm_response")

        # 确保返回有意义的数据
        if data is None:
            return ApiResponse(
                success=True,
                message=f"没有找到{agent_name}的LLM响应记录",
                data={"message": f"没有找到{agent_name}的LLM响应记录"}
            )

        # 尝试解析和序列化数据
        serialized_data = serialize_for_api(data)

        # 确保结果是字典类型
        if not isinstance(serialized_data, dict):
            # 如果不是字典，包装为字典返回
            serialized_data = {
                "content": serialized_data, "type": "raw_content"}

        return ApiResponse(data=serialized_data)
    except Exception as e:
        logger.error(f"处理{agent_name}的LLM响应数据时出错: {str(e)}")
        return ApiResponse(
            success=False,
            message=f"无法处理{agent_name}的LLM响应数据: {str(e)}",
            data={"error": str(e)}
        )
