"""
API数据模型

这个模块定义了API使用的请求和响应数据模型
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, TypeVar, Generic
from datetime import datetime, UTC

# 类型定义
T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """API响应的标准格式"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgentInfo(BaseModel):
    """Agent信息模型"""
    name: str
    description: str
    state: str = "idle"  # idle, running, completed, error
    last_run: Optional[datetime] = None


class RunInfo(BaseModel):
    """运行信息模型"""
    run_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str  # "running", "completed", "error"
    agents: List[str] = []


class StockAnalysisRequest(BaseModel):
    """股票分析请求模型"""
    ticker: str = Field(
        ...,
        description="股票代码，例如：'002848'",
        example="002848"
    )
    show_reasoning: bool = Field(
        True,
        description="是否显示分析推理过程",
        example=True
    )
    num_of_news: int = Field(
        5,
        description="用于情感分析的新闻文章数量（1-100）",
        ge=1,
        le=100,
        example=5
    )
    initial_capital: float = Field(
        100000.0,
        description="初始资金",
        gt=0,
        example=100000.0
    )
    initial_position: int = Field(
        0,
        description="初始持仓数量",
        ge=0,
        example=0
    )

    class Config:
        schema_extra = {
            "example": {
                "ticker": "002848",
                "show_reasoning": True,
                "num_of_news": 5,
                "initial_capital": 100000.0,
                "initial_position": 0
            }
        }


class StockAnalysisResponse(BaseModel):
    """股票分析响应模型

    用于表示股票分析任务的响应信息，包含运行ID、状态和时间戳等
    """
    run_id: str = Field(..., description="分析任务唯一标识符")
    ticker: str = Field(..., description="股票代码")
    status: str = Field(..., description="任务状态：running, completed, error")
    message: str = Field(..., description="状态描述信息")
    submitted_at: datetime = Field(..., description="任务提交时间")
    completed_at: Optional[datetime] = Field(None, description="任务完成时间")

    class Config:
        schema_extra = {
            "example": {
                "run_id": "550e8400-e29b-41d4-a716-446655440000",
                "ticker": "002848",
                "status": "running",
                "message": "分析任务已启动",
                "submitted_at": "2023-03-15T12:30:45.123Z",
                "completed_at": None
            }
        }
