import pytest
from datetime import datetime, timedelta
from src.tools.algogene_client import get_algogene_price_history
import logging

logger = logging.getLogger(__name__)

def test_get_btcusd_price_history():
    """
    测试获取BTCUSD的历史价格数据
    测试不同的时间间隔和数据点数量
    """
    # 获取当前时间作为时间戳，使用UTC时间
    current_time = datetime.utcnow()
    # 向前偏移一天，确保有数据
    timestamp = (current_time - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    
    # 测试用例1: 获取1分钟级别的数据
    response_1min = get_algogene_price_history(
        count=10,
        instrument="BTCUSD",
        interval="M",  # 使用"M"表示分钟级别
        timestamp=timestamp
    )
    
    # 检查是否有错误返回
    if "error" in response_1min:
        logger.error(f"获取1分钟数据失败: {response_1min['error']}")
        pytest.skip(f"API调用失败: {response_1min['error']}")
    
    # 基本数据结构验证
    assert isinstance(response_1min, dict), "返回值应该是字典类型"
    assert "res" in response_1min, "返回值应该包含'res'键"
    assert "count" in response_1min, "返回值应该包含'count'键"
    
    # 数据内容验证
    assert len(response_1min["res"]) > 0, "返回的数据列表不应为空"
    first_candle = response_1min["res"][0]
    
    # 验证K线数据结构
    required_fields = ["t", "o", "h", "l", "c", "v", "instrument"]
    for field in required_fields:
        assert field in first_candle, f"K线数据缺少必要字段: {field}"
    
    # 验证数据类型
    assert isinstance(first_candle["o"], (int, float)), "开盘价应该是数字类型"
    assert isinstance(first_candle["h"], (int, float)), "最高价应该是数字类型"
    assert isinstance(first_candle["l"], (int, float)), "最低价应该是数字类型"
    assert isinstance(first_candle["c"], (int, float)), "收盘价应该是数字类型"
    assert isinstance(first_candle["v"], (int, float)), "成交量应该是数字类型"
    
    # 验证价格逻辑
    assert first_candle["h"] >= first_candle["l"], "最高价应该大于等于最低价"
    assert first_candle["h"] >= first_candle["o"], "最高价应该大于等于开盘价"
    assert first_candle["h"] >= first_candle["c"], "最高价应该大于等于收盘价"
    assert first_candle["l"] <= first_candle["o"], "最低价应该小于等于开盘价"
    assert first_candle["l"] <= first_candle["c"], "最低价应该小于等于收盘价"
    
    # 测试用例2: 获取日线级别的数据
    response_daily = get_algogene_price_history(
        count=5,
        instrument="BTCUSD",
        interval="D",  # 使用"D"表示日线级别
        timestamp=timestamp
    )
    
    if "error" in response_daily:
        logger.error(f"获取日线数据失败: {response_daily['error']}")
        pytest.skip(f"API调用失败: {response_daily['error']}")
    
    # 验证日线数据
    assert isinstance(response_daily, dict), "返回值应该是字典类型"
    assert len(response_daily["res"]) > 0, "返回的数据列表不应为空"
    
    # 测试用例3: 测试数据点数量限制
    response_limit = get_algogene_price_history(
        count=100,  # 测试较大的数据点数量
        instrument="BTCUSD",
        interval="H",  # 使用"H"表示小时级别
        timestamp=timestamp
    )
    
    if "error" in response_limit:
        logger.error(f"获取小时数据失败: {response_limit['error']}")
        pytest.skip(f"API调用失败: {response_limit['error']}")
    
    assert isinstance(response_limit, dict), "返回值应该是字典类型"
    assert len(response_limit["res"]) > 0, "返回的数据列表不应为空"
    
    print("\n测试结果摘要:")
    print(f"1分钟级别数据点数量: {len(response_1min['res'])}")
    print(f"日线级别数据点数量: {len(response_daily['res'])}")
    print(f"小时级别数据点数量: {len(response_limit['res'])}")
    
if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    pytest.main(["-v", __file__]) 