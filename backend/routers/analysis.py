"""
股票分析相关路由模块

此模块提供与股票分析任务相关的API端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
import uuid
import logging
from datetime import datetime, UTC
from typing import Dict, Optional

from ..models.api_models import (
    ApiResponse, StockAnalysisRequest, StockAnalysisResponse
)
from ..state import api_state
from ..services import execute_stock_analysis
from ..utils.api_utils import serialize_for_api, safe_parse_json
from backend.storage.base import BaseLogStorage
from backend.dependencies import get_log_storage

logger = logging.getLogger("analysis_router")

# 创建路由器
router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.post("/start", response_model=ApiResponse[StockAnalysisResponse])
async def start_stock_analysis(request: StockAnalysisRequest):
    """开始股票分析任务

    此API端点允许前端触发新的股票分析。分析将在后台进行，
    前端可通过返回的run_id查询分析状态和结果。

    参数说明:
    - ticker: 股票代码，如"002848"（必填）
    - show_reasoning: 是否显示分析推理过程，默认为true
    - num_of_news: 用于情感分析的新闻数量(1-100)，默认为5
    - initial_capital: 初始资金，默认为100000
    - initial_position: 初始持仓数量，默认为0

    分析日期说明:
    - 系统会自动使用最近一年的数据进行分析，无需手动指定日期范围

    示例请求:
    ```json
    {
        "ticker": "002848",
        "show_reasoning": true,
        "num_of_news": 5,
        "initial_capital": 100000.0,
        "initial_position": 0
    }
    ```

    简化请求(仅提供必填参数):
    ```json
    {
        "ticker": "002848"
    }
    ```
    """
    # 生成唯一ID
    run_id = str(uuid.uuid4())

    # 将任务提交到线程池
    future = api_state._executor.submit(
        execute_stock_analysis,
        request=request,
        run_id=run_id
    )

    # 注册任务
    api_state.register_analysis_task(run_id, future)

    # 注册运行
    api_state.register_run(run_id)

    # 创建响应对象
    response = StockAnalysisResponse(
        run_id=run_id,
        ticker=request.ticker,
        status="running",
        message="分析任务已启动",
        submitted_at=datetime.now(UTC)
    )

    # 使用ApiResponse包装返回
    return ApiResponse(
        success=True,
        message="分析任务已成功启动",
        data=response
    )


@router.get("/{run_id}/status", response_model=ApiResponse[Dict])
async def get_analysis_status(run_id: str):
    """获取股票分析任务的状态"""
    task = api_state.get_analysis_task(run_id)
    run_info = api_state.get_run(run_id)

    if not run_info:
        return ApiResponse(
            success=False,
            message=f"分析任务 '{run_id}' 不存在",
            data=None
        )

    status_data = {
        "run_id": run_id,
        "status": run_info.status,
        "start_time": run_info.start_time,
        "end_time": run_info.end_time,
    }

    if task:
        if task.done():
            if task.exception():
                status_data["error"] = str(task.exception())
            status_data["is_complete"] = True
        else:
            status_data["is_complete"] = False

    return ApiResponse(data=status_data)


@router.get("/{run_id}/result", response_model=ApiResponse[Dict])
async def get_analysis_result(run_id: str):
    """获取股票分析任务的结果数据

    此接口返回最终的投资决策结果以及各个Agent的分析数据摘要。
    分析必须已经完成才能获取结果。
    """
    try:
        task = api_state.get_analysis_task(run_id)
        run_info = api_state.get_run(run_id)

        if not run_info:
            return ApiResponse(
                success=False,
                message=f"分析任务 '{run_id}' 不存在",
                data=None
            )

        # 检查任务是否完成
        if run_info.status != "completed":
            return ApiResponse(
                success=False,
                message=f"分析任务尚未完成或已失败，当前状态: {run_info.status}",
                data={"status": run_info.status}
            )

        # 收集所有参与此运行的Agent数据
        agent_results = {}
        ticker = ""
        for agent_name in run_info.agents:
            agent_data = api_state.get_agent_data(agent_name)
            if agent_data and "reasoning" in agent_data:
                # 尝试解析和序列化推理数据
                reasoning_data = safe_parse_json(agent_data["reasoning"])
                agent_results[agent_name] = serialize_for_api(reasoning_data)

            # 尝试从market_data_agent获取ticker
            if agent_name == "market_data" and agent_data and "output_state" in agent_data:
                try:
                    output = agent_data["output_state"]
                    if "data" in output and "ticker" in output["data"]:
                        ticker = output["data"]["ticker"]
                except Exception:
                    pass

        # 尝试获取portfolio_management的最终决策
        final_decision = None
        portfolio_data = api_state.get_agent_data("portfolio_management")
        if portfolio_data and "output_state" in portfolio_data:
            try:
                output = portfolio_data["output_state"]
                messages = output.get("messages", [])
                # 获取最后一个消息
                if messages:
                    last_message = messages[-1]
                    if hasattr(last_message, "content"):
                        # 尝试解析content，可能是JSON字符串
                        final_decision = safe_parse_json(last_message.content)
            except Exception as e:
                logger.error(f"解析最终决策时出错: {str(e)}")

        result_data = {
            "run_id": run_id,
            "ticker": ticker,
            "completion_time": run_info.end_time,
            "final_decision": serialize_for_api(final_decision),
            "agent_results": agent_results
        }

        return ApiResponse(data=result_data)
    except Exception as e:
        logger.error(f"获取分析结果时出错: {str(e)}")
        return ApiResponse(
            success=False,
            message=f"获取分析结果时出错: {str(e)}",
            data={"error": str(e)}
        )


@router.get("/{run_id}/structured_log", response_model=ApiResponse)
async def get_structured_log(
    run_id: str = Path(..., description="Analysis run ID"),
    storage: BaseLogStorage = Depends(get_log_storage)
):
    """Get the structured log for a specific analysis run."""
    try:
        # Get all agent logs for this run
        agent_logs = storage.get_agent_logs(run_id=run_id)
        if not agent_logs:
            raise HTTPException(
                status_code=404,
                detail=f"No logs found for run ID {run_id}"
            )

        # Format the logs into a structured report
        report = format_structured_report(agent_logs)
        
        return ApiResponse(
            success=True,
            data={"content": report}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get structured log: {str(e)}"
        )

def format_structured_report(agent_logs: list) -> str:
    """Format agent logs into a structured report."""
    report_lines = []
    
    # Add header
    report_lines.append("=" * 80)
    report_lines.append(f"Investment Analysis Report for Ticker: {agent_logs[0].input_state.get('ticker', 'Unknown')}")
    report_lines.append("=" * 80)
    
    # Add analysis period if available
    if agent_logs[0].input_state.get('start_date') and agent_logs[0].input_state.get('end_date'):
        report_lines.append(f"Analysis Period: {agent_logs[0].input_state['start_date']} to {agent_logs[0].input_state['end_date']}")
    report_lines.append("")
    
    # Process each agent's output
    for log in agent_logs:
        if log.reasoning_details:
            # Add agent section header
            report_lines.append(f"╔{'═' * 40} 📊 {log.agent_name.replace('_', ' ').title()} {'═' * 40}╗")
            
            # Add agent's reasoning
            if isinstance(log.reasoning_details, dict):
                for key, value in log.reasoning_details.items():
                    if isinstance(value, dict):
                        report_lines.append(f"║ {key}:")
                        for subkey, subvalue in value.items():
                            report_lines.append(f"║   ├─ {subkey}: {subvalue}")
                    else:
                        report_lines.append(f"║ {key}: {value}")
            else:
                report_lines.append(f"║ {log.reasoning_details}")
            
            report_lines.append(f"╚{'═' * 80}╝")
            report_lines.append("")
    
    return "\n".join(report_lines)
