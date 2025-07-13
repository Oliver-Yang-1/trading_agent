# Utils Module - AI Trading System Core Utilities

这个模块为AI交易系统提供核心工具和基础设施，包括日志管理、API集成、序列化、输出格式化等功能。采用分层架构设计，支持多Agent系统的协调运行。

## 📁 目录结构与架构

```
src/utils/
├── logging_config.py          # 基础日志设施 (Layer 1)
├── output_logger.py           # 输出重定向工具 (Layer 2)
├── serialization.py           # 数据序列化工具 (Layer 2)  
├── llm_clients.py             # LLM客户端抽象 (Layer 2)
├── structured_terminal.py     # 结构化终端输出 (Layer 2)
├── llm_interaction_logger.py  # LLM交互日志管理 (Layer 3)
└── api_utils.py               # API集成中心 (Layer 4)
```

### 分层依赖架构

```
Layer 4 - API集成层
└── api_utils.py (Agent API装饰器、FastAPI集成、全局状态管理)

Layer 3 - 交互记录层  
└── llm_interaction_logger.py (LLM调用跟踪、Agent执行日志、上下文管理)

Layer 2 - 专业工具层
├── llm_clients.py (多LLM客户端抽象)
├── structured_terminal.py (格式化输出)
├── serialization.py (JSON序列化)
└── output_logger.py (双重输出重定向)

Layer 1 - 基础设施层
└── logging_config.py (统一日志配置、图标系统)
```

## 🔧 核心模块详解

### 1. logging_config.py - 基础日志设施

统一的日志配置模块，为整个系统提供日志基础设施。

#### 主要功能

##### setup_logger()
```python
def setup_logger(name: str, log_dir: Optional[str] = None) -> logging.Logger
```

**功能**: 创建配置好的logger实例

**特性**:
- **双重输出**: 控制台(INFO+) + 文件(DEBUG+)
- **防重复**: 自动检测已存在的处理器
- **UTF-8编码**: 支持中文日志
- **自动目录**: 自动创建logs目录

**预定义图标**:
```python
SUCCESS_ICON = "✓"    # 成功操作
ERROR_ICON = "✗"      # 错误状态  
WAIT_ICON = "🔄"       # 等待/处理中
```

**使用示例**:
```python
from src.utils.logging_config import setup_logger, SUCCESS_ICON

logger = setup_logger('my_module')
logger.info(f"{SUCCESS_ICON} 操作成功完成")
```

### 2. llm_clients.py - LLM客户端抽象

多LLM提供商的统一客户端接口，支持Gemini和OpenAI Compatible APIs。

#### 核心设计

##### LLMClient抽象基类
```python
class LLMClient(ABC):
    @abstractmethod
    def get_completion(self, messages, **kwargs):
        """获取模型回答"""
        pass
```

##### GeminiClient实现
```python
class GeminiClient(LLMClient):
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.client = genai.Client(api_key=self.api_key)
```

**特性**:
- **指数退避重试**: `@backoff.on_exception`装饰器
- **地理位置错误检测**: 自动识别VPN需求
- **消息格式转换**: OpenAI格式 → Gemini格式

##### OpenAICompatibleClient实现
```python
class OpenAICompatibleClient(LLMClient):
    def __init__(self, api_key=None, base_url=None, model=None):
        # 支持任何OpenAI兼容的API服务
```

##### LLMClientFactory工厂类
```python
@staticmethod
def create_client(client_type="auto", **kwargs):
    """
    自动检测和创建客户端
    - "auto": 根据环境变量自动选择
    - "gemini": 强制使用Gemini
    - "openai_compatible": 强制使用OpenAI兼容API
    """
```

**使用示例**:
```python
from src.utils.llm_clients import LLMClientFactory

# 自动选择客户端
client = LLMClientFactory.create_client("auto")
response = client.get_completion([
    {"role": "user", "content": "分析这只股票"}
])
```

### 3. serialization.py - 数据序列化工具

将复杂Python对象转换为JSON可序列化格式，专门处理Agent状态数据。

#### 主要功能

##### serialize_agent_state()
```python
def serialize_agent_state(state: Dict) -> Dict:
    """将AgentState转换为JSON友好格式"""
```

**处理的数据类型**:
- **Pandas对象**: DataFrame/Series → dict
- **LangChain消息**: 自动提取content和type
- **自定义对象**: 通过`__dict__`属性序列化
- **日期时间**: 转换为ISO格式
- **嵌套结构**: 递归处理列表和字典

**错误处理**:
```python
# 序列化失败时的优雅降级
{
    "error": "无法序列化状态: 具体错误信息",
    "serialization_error": True,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**使用示例**:
```python
from src.utils.serialization import serialize_agent_state
import pandas as pd

state = {
    "data": {"df": pd.DataFrame({"price": [100, 110]})},
    "metadata": {"timestamp": datetime.now()}
}

serialized = serialize_agent_state(state)
# 可以安全地用json.dumps()处理
```

### 4. output_logger.py - 输出重定向工具

将程序输出同时重定向到控制台和文件，用于调试和日志记录。

#### OutputLogger类
```python
class OutputLogger:
    def __init__(self, filename: str | None = None):
        """
        初始化双重输出
        - filename: 可选文件名，默认使用时间戳
        """
```

**特性**:
- **双重输出**: 同时写入控制台和文件
- **自动目录**: 自动创建logs目录
- **即时刷新**: `flush()`确保数据及时写入
- **自动清理**: `__del__`方法自动关闭文件

**使用示例**:
```python
from src.utils.output_logger import OutputLogger
import sys

# 重定向标准输出
sys.stdout = OutputLogger("debug_output.txt")
print("这条消息将同时显示在控制台和文件中")
```

### 5. structured_terminal.py - 结构化终端输出

为交易分析结果提供美观、结构化的终端显示格式。

#### 核心设计

##### StructuredTerminalOutput类
```python
class StructuredTerminalOutput:
    def __init__(self):
        self.data = {}      # Agent数据
        self.metadata = {}  # 元数据
```

**格式化组件**:
```python
SYMBOLS = {
    "border": "═", "header_left": "╔", "header_right": "╗",
    "tree_branch": "├─", "tree_last": "└─", "vertical": "║"
}

STATUS_ICONS = {
    "bearish": "📉", "bullish": "📈", "neutral": "◽",
    "buy": "🛒", "sell": "💰", "hold": "⏸️"
}

AGENT_MAP = {
    "market_data_agent": {"icon": "📊", "name": "Market Data"},
    "technical_analyst_agent": {"icon": "📈", "name": "Technical Analysis"},
    # ... 其他agent映射
}
```

##### 主要方法

###### generate_output()
生成完整的结构化报告，包括：
- 标题和股票代码
- 分析时间范围
- 各Agent分析结果（按预定义顺序）
- 特殊处理portfolio_management_agent的决策输出

###### extract_agent_data()
```python
def extract_agent_data(state: Dict[str, Any], agent_name: str) -> Any:
    """从工作流状态中提取指定agent的数据"""
```

**数据提取策略**:
1. 从`metadata.all_agent_reasoning`获取
2. 从`metadata.agent_reasoning`获取  
3. 从`messages`中按agent名称匹配
4. 尝试JSON解析消息内容

**使用示例**:
```python
from src.utils.structured_terminal import print_structured_output

# 在工作流结束后调用
print_structured_output(final_state)
```

### 6. llm_interaction_logger.py - LLM交互日志管理

提供LLM调用和Agent执行的详细日志记录，采用上下文变量管理。

#### 核心设计

##### Context Variables (线程安全)
```python
log_storage_context: ContextVar[BaseLogStorage] = ContextVar(
    "log_storage_context", default=None
)
current_agent_name_context: ContextVar[str] = ContextVar(
    "current_agent_name_context", default=None
)
current_run_id_context: ContextVar[str] = ContextVar(
    "current_run_id_context", default=None
)
```

##### OutputCapture工具类
```python
class OutputCapture:
    """捕获标准输出和日志的工具类"""
    
    def __enter__(self):
        # 捕获stdout和log到内存缓冲区
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 收集输出并恢复原始流
```

##### 核心装饰器

###### wrap_llm_call()
```python
def wrap_llm_call(original_llm_func: Callable) -> Callable:
    """包装LLM调用函数以记录交互"""
```

**功能**:
- 自动从上下文获取agent名称和run_id
- 记录请求和响应数据
- 创建`LLMInteractionLog`对象
- 存储到全局日志系统

###### log_agent_execution()
```python
def log_agent_execution(agent_name: str):
    """Agent函数装饰器，设置日志上下文"""
```

**功能**:
- 设置上下文变量（agent名称、run_id）
- 捕获执行时间和输入输出状态
- 使用`OutputCapture`收集终端输出
- 处理执行异常并记录错误日志
- 自动清理上下文变量

**使用示例**:
```python
from src.utils.llm_interaction_logger import log_agent_execution, wrap_llm_call

@log_agent_execution("technical_analyst")
def technical_analyst_agent(state):
    # Agent实现
    pass

# 包装LLM调用
get_chat_completion = wrap_llm_call(original_get_chat_completion)
```

### 7. api_utils.py - API集成中心

系统最复杂的模块，提供Agent的API集成、装饰器和全局状态管理。

#### 核心功能

##### agent_endpoint装饰器
```python
def agent_endpoint(agent_name_param: str, description: str = ""):
    """为Agent创建API端点的装饰器"""
```

**功能详解**:
1. **Agent注册**: 注册到全局API状态
2. **状态管理**: 更新Agent运行状态
3. **输入输出序列化**: 自动序列化Agent状态
4. **终端输出捕获**: 捕获stdout/stderr/logs
5. **LLM交互跟踪**: 设置上下文变量
6. **异常处理**: 完整的错误处理和日志记录
7. **性能监控**: 记录开始/结束时间

##### log_llm_interaction双模式装饰器
```python
def log_llm_interaction(state):
    """
    两种使用模式：
    1. 装饰器工厂: log_llm_interaction(state)(llm_func)
    2. 直接调用: log_llm_interaction(agent_name)(request, response)
    """
```

**装饰器模式**:
- 自动从多个来源提取agent信息
- 格式化请求和响应数据
- 与全局API状态同步
- 存储到日志系统

**直接调用模式**:
- 向后兼容现有代码
- 手动传入agent名称
- 相同的日志记录功能

##### FastAPI集成
```python
# 从backend导入FastAPI应用
from backend.main import app

def start_api_server(host="0.0.0.0", port=8000, stop_event=None):
    """启动API服务器，支持优雅关闭"""
```

**特性**:
- 与backend模块深度集成
- 支持停止事件的优雅关闭
- uvicorn服务器配置
- 线程监控机制

#### 全局状态管理
```python
# 跟踪每个agent的LLM调用
_agent_llm_calls = {}

# 临时消息日志文件
MESSAGES_LOG_FILE = "data/temp_messages_log.txt"
```

## 🏗️ 系统集成架构

### 环境变量配置体系

```env
# === LLM服务配置 ===
# Gemini API (主要)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash

# OpenAI Compatible API (备用)
OPENAI_COMPATIBLE_API_KEY=your_openai_key  
OPENAI_COMPATIBLE_BASE_URL=https://api.openai.com/v1
OPENAI_COMPATIBLE_MODEL=gpt-3.5-turbo

# === 系统配置 ===
LOG_LEVEL=INFO                # 日志级别
CACHE_ENABLED=true            # 缓存开关
```

### 依赖关系图

```
外部系统依赖:
├── Google Gemini API ────→ llm_clients.py
├── OpenAI Compatible APIs ─→ llm_clients.py  
├── FastAPI Framework ─────→ api_utils.py
└── Backend Module ────────→ api_utils.py, llm_interaction_logger.py

内部模块依赖:
logging_config.py (无依赖)
├── llm_clients.py
├── structured_terminal.py
├── output_logger.py (独立)
└── serialization.py (独立)
    ├── llm_interaction_logger.py
    └── api_utils.py (核心集成)
```

### 日志系统分层架构

```
Layer 4 - API集成日志
├── Agent执行日志 (开始/结束时间、输入输出状态)
├── LLM交互日志 (请求/响应数据)
└── 终端输出捕获 (stdout/stderr/logs)

Layer 3 - 交互记录日志  
├── 上下文变量管理 (agent名称、run_id)
├── 输出捕获器 (OutputCapture)
└── 存储抽象层 (BaseLogStorage)

Layer 2 - 专业日志工具
├── 双重输出重定向 (控制台+文件)
├── 结构化格式化 (美化显示)
└── 序列化支持 (复杂对象处理)

Layer 1 - 基础日志设施
├── 统一Logger配置 (控制台INFO+、文件DEBUG+)
├── 自动目录管理 (logs/目录)
└── 图标系统 (SUCCESS_ICON, ERROR_ICON等)
```

### 错误处理与容错机制

#### 分层异常处理
```python
# Level 1 - 配置异常
if not self.api_key:
    logger.error(f"{ERROR_ICON} 未找到 API KEY")
    raise ValueError("API KEY not found")

# Level 2 - 网络异常 (重试机制)
@backoff.on_exception(backoff.expo, Exception, max_tries=5, max_time=300)
def api_call_with_retry():
    # 指数退避重试

# Level 3 - 序列化异常 (优雅降级)
try:
    return _convert_to_serializable(state)
except Exception as e:
    return {"error": f"序列化失败: {str(e)}", "serialization_error": True}

# Level 4 - 日志异常 (不影响主流程)
try:
    log_storage.add_log(log_entry)
except Exception as log_err:
    logger.warning(f"日志存储失败: {str(log_err)}")
    # 继续执行，不中断主要业务流程
```

## 🔄 使用指南

### 基础使用模式

#### 1. 日志系统集成
```python
from src.utils.logging_config import setup_logger, SUCCESS_ICON, ERROR_ICON

# 创建模块专用logger
logger = setup_logger('my_module')

# 标准日志记录
logger.info(f"{SUCCESS_ICON} 操作成功")
logger.error(f"{ERROR_ICON} 操作失败: {error_msg}")

# 自动文件输出: logs/my_module.log
```

#### 2. LLM客户端使用
```python
from src.utils.llm_clients import LLMClientFactory

# 自动选择最佳客户端
client = LLMClientFactory.create_client("auto")

# 标准化消息格式
messages = [
    {"role": "system", "content": "你是专业的股票分析师"},
    {"role": "user", "content": "分析这只股票的技术面"}
]

# 获取回复（自动重试、错误处理）
response = client.get_completion(messages)
```

#### 3. Agent装饰器集成
```python
from src.utils.api_utils import agent_endpoint, log_llm_interaction

@agent_endpoint("technical_analyst", "技术分析师，负责技术指标分析")
def technical_analyst_agent(state):
    """技术分析Agent"""
    
    # LLM调用会自动记录
    @log_llm_interaction(state)
    def get_analysis():
        return get_chat_completion(messages)
    
    analysis = get_analysis()
    
    # 自动序列化和API暴露
    return {
        "messages": state["messages"] + [new_message],
        "data": {**state["data"], "technical_analysis": analysis},
        "metadata": state["metadata"]
    }
```

#### 4. 结构化输出使用
```python
from src.utils.structured_terminal import print_structured_output

# 在工作流完成后
def main():
    # ... 执行工作流
    final_state = workflow.invoke(initial_state)
    
    # 打印美化的分析报告
    print_structured_output(final_state)
```

### 高级使用模式

#### 1. 自定义LLM客户端
```python
from src.utils.llm_clients import LLMClient

class CustomLLMClient(LLMClient):
    def get_completion(self, messages, **kwargs):
        # 自定义实现
        pass

# 注册到工厂
LLMClientFactory.register_client("custom", CustomLLMClient)
```

#### 2. 输出捕获和重定向
```python
from src.utils.output_logger import OutputLogger
from src.utils.llm_interaction_logger import OutputCapture

# 方式1: 全局重定向
sys.stdout = OutputLogger("analysis_output.txt")

# 方式2: 上下文捕获
with OutputCapture() as capture:
    print("这些输出会被捕获")
    logger.info("日志也会被捕获")

# 获取捕获的内容
terminal_outputs = capture.outputs
```

#### 3. 序列化定制
```python
from src.utils.serialization import serialize_agent_state

# 处理复杂状态
complex_state = {
    "data": {
        "dataframe": pd.DataFrame({"price": [100, 110]}),
        "timestamp": datetime.now(),
        "custom_obj": MyCustomObject()
    },
    "metadata": {"show_reasoning": True}
}

# 自动处理所有复杂对象
serialized = serialize_agent_state(complex_state)
json.dumps(serialized)  # 安全的JSON序列化
```

## ⚠️ 重要注意事项

### 架构设计问题

1. **循环依赖风险**: api_utils导入其他utils模块，存在潜在循环引用
2. **强耦合问题**: src/utils与backend模块强耦合，违反分层原则
3. **资源管理**: 缺乏日志文件轮转和内存清理机制

### 性能考虑

1. **日志文件大小**: 无自动轮转，长期运行会产生大文件
2. **内存占用**: LLM交互日志在内存累积，需要清理机制
3. **序列化性能**: 深度递归可能影响大对象处理速度

### 安全注意事项

1. **API密钥保护**: 确保.env文件不被提交到版本控制
2. **日志敏感信息**: 避免在日志中记录API密钥或敏感数据  
3. **文件权限**: 日志文件应设置适当的访问权限

### 使用建议

1. **模块导入**: 避免在模块顶层导入api_utils，使用延迟导入
2. **日志级别**: 生产环境建议使用INFO级别，开发时使用DEBUG
3. **资源清理**: 定期清理logs目录和临时文件
4. **监控告警**: 监控日志文件大小和内存使用情况

## 🔄 维护与扩展

### 定期维护任务

**周度检查**:
- [ ] 检查日志文件大小，手动清理过大文件
- [ ] 监控内存使用情况，重启长时间运行的服务
- [ ] 验证LLM API连接状态和配额使用

**月度更新**:
- [ ] 更新第三方库版本（backoff, openai, google-generativeai）
- [ ] 检查环境变量配置的有效性
- [ ] 优化日志配置和输出格式

**季度优化**:
- [ ] 重构循环依赖和强耦合问题
- [ ] 实现日志轮转和自动清理机制
- [ ] 性能基准测试和优化

### 扩展开发指南

#### 添加新的LLM客户端
```python
# 1. 实现LLMClient接口
class NewLLMClient(LLMClient):
    def get_completion(self, messages, **kwargs):
        # 实现具体逻辑
        pass

# 2. 注册到工厂类
def create_client(client_type="auto", **kwargs):
    if client_type == "new_llm":
        return NewLLMClient(**kwargs)
    # ... 现有逻辑
```

#### 扩展日志功能
```python
# 1. 扩展OutputCapture类
class AdvancedOutputCapture(OutputCapture):
    def capture_metrics(self):
        # 添加性能指标捕获
        pass

# 2. 添加新的日志装饰器
def log_performance(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        logger.info(f"性能: {func.__name__} 耗时 {duration:.2f}s")
        return result
    return wrapper
```

#### 优化建议实现
```python
# 1. 依赖注入模式
class UtilsManager:
    def __init__(self, log_storage, llm_factory):
        self.log_storage = log_storage
        self.llm_factory = llm_factory
    
    def get_configured_logger(self, name):
        return setup_logger(name, self.log_storage.get_log_dir())

# 2. 配置中心模式
class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config = self.load_config(config_file)
    
    def get_llm_config(self):
        return self.config.get("llm", {})
```

---

💡 **开发建议**: 这个utils模块体系设计相对完善，但在模块解耦和资源管理方面还有改进空间。建议优先解决架构耦合问题，然后逐步优化性能和资源管理机制。