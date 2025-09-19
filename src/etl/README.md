# 裂世九域·法则链纪元 - ETL数据处理管道

## 概述

这是一个专为"裂世九域·法则链纪元"小说项目设计的现代化ETL（Extract, Transform, Load）数据处理管道。该系统提供了完整的文本内容处理、实体识别、数据验证和流式处理功能，特别针对中文小说内容进行了优化。

## 核心功能

### 1. 批处理管道 (Pipeline Manager)
- **多内容类型支持**: 世界观、角色、情节、场景、对话
- **断点续传**: 支持从上次处理位置继续
- **并行处理**: 可配置的工作线程数
- **错误处理**: 自动重试和错误恢复机制
- **性能监控**: 实时处理速率和性能指标

### 2. 中文文本处理 (Text Processor)
- **智能分词**: 基于jieba的中文分词，支持自定义词典
- **文本清洗**: 去除冗余字符、标准化标点符号
- **繁简转换**: 支持繁体与简体中文相互转换
- **内容提取**: 自动提取对话、人名、地点、时间表达式
- **质量评估**: 可读性、连贯性和复杂度评分

### 3. 实体识别与提取 (Entity Extractor)
- **多模式识别**: 正则表达式、NLP模型、短语匹配
- **小说专用实体**: 人物、地点、修炼境界、功法、法宝、组织
- **关系提取**: 自动识别实体间的关系
- **消歧与合并**: 智能处理同一实体的不同提及
- **置信度评分**: 为每个提取的实体分配置信度

### 4. 数据质量保证 (Data Validator)
- **多层次验证**: 模式验证、内容质量、业务规则
- **质量评分**: 综合评估数据质量并给出分数
- **异常检测**: 基于历史数据检测异常模式
- **冲突解决**: 自动或手动解决数据冲突
- **一致性检查**: 跨数据库一致性验证

### 5. 流式处理 (Stream Processor)
- **多源接入**: 文件监控、HTTP Webhook、消息队列
- **时间窗口**: 基于时间的滑动窗口处理
- **背压控制**: 防止数据堆积的流量控制
- **容错机制**: 自动重试和死信队列
- **实时监控**: 流处理性能和状态监控

### 6. 增量更新 (Incremental Processor)
- **变更检测**: 基于内容哈希的智能变更检测
- **版本管理**: 完整的数据版本历史追踪
- **冲突解决**: 多种冲突解决策略
- **跨库同步**: PostgreSQL与MongoDB数据同步
- **变更审计**: 完整的变更日志和审计跟踪

## 技术架构

### 数据存储
- **PostgreSQL**: 结构化数据和关系存储
- **MongoDB**: 文档存储和灵活模式
- **双写策略**: 确保数据在两个数据库中的一致性

### 处理引擎
- **异步处理**: 基于asyncio的高性能异步处理
- **并行计算**: 多进程/多线程并行处理支持
- **内存管理**: 优化的内存使用和缓存策略

### 数据流向
```
原始文本 → 文本清洗 → 实体提取 → 数据验证 → 数据存储
                                    ↓
流式更新 → 增量检测 → 冲突解决 → 版本管理 → 同步更新
```

## 安装与配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 数据库初始化
```sql
-- 在PostgreSQL中执行
\i src/etl/db_schema.sql
```

### 3. 环境配置
```env
# .env文件
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=novellus
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=novellus
```

### 4. 中文模型下载
```bash
python -m spacy download zh_core_web_sm
```

## 使用示例

### 基本批处理
```python
from src.etl import PipelineManager, PipelineConfig, ContentType

# 配置管道
config = PipelineConfig(
    batch_size=100,
    enable_validation=True,
    enable_entity_extraction=True,
    chinese_segmentation=True
)

# 创建管道管理器
pipeline = PipelineManager(config)

# 处理世界观内容
metrics = await pipeline.process_batch(
    content_type=ContentType.WORLDVIEW,
    data_source="worldview_data.txt"
)
```

### 流式处理
```python
from src.etl import StreamProcessor

# 配置流处理器
stream_processor = StreamProcessor()

# 启动文件监控
await stream_processor.start_stream(
    content_type=ContentType.CHARACTER,
    source_config={
        'type': 'file_watcher',
        'path': './content',
        'patterns': ['*.txt']
    }
)
```

### 增量更新
```python
from src.etl import IncrementalProcessor

# 创建增量处理器
incremental = IncrementalProcessor()

# 处理更新
result = await incremental.process_incremental_update(
    content_type=ContentType.PLOT,
    record_id="plot_001",
    new_data=updated_content
)
```

## 性能特性

### 处理能力
- **批处理**: 1000-5000 记录/分钟（取决于内容复杂度）
- **流处理**: 100-500 事件/秒
- **实体提取**: 50-200 实体/秒
- **数据验证**: 500-1000 记录/秒

### 扩展性
- **水平扩展**: 支持多实例部署
- **垂直扩展**: 可配置工作线程数
- **存储扩展**: 支持分片和集群部署

### 可靠性
- **容错处理**: 自动重试和错误恢复
- **数据一致性**: ACID事务和最终一致性
- **监控告警**: 实时性能监控和异常告警

## 监控与运维

### 性能指标
- 处理速率和延迟
- 错误率和重试次数
- 内存和CPU使用率
- 数据库连接池状态

### 质量指标
- 数据验证通过率
- 实体提取准确率
- 内容质量评分分布
- 冲突解决成功率

### 运维工具
- 管道状态监控面板
- 实时日志查看
- 性能分析报告
- 数据质量报告

## 最佳实践

### 配置优化
1. **批处理大小**: 根据内存和处理能力调整batch_size
2. **工作线程**: CPU密集型任务适中配置，I/O密集型可增加
3. **缓存策略**: 合理设置缓存大小和过期时间

### 数据质量
1. **定期验证**: 定期运行全量数据验证
2. **监控异常**: 设置数据质量告警阈值
3. **人工审核**: 重要数据变更需要人工确认

### 性能调优
1. **数据库索引**: 为频繁查询字段创建索引
2. **分区策略**: 大表按时间或内容类型分区
3. **连接池**: 合理配置数据库连接池大小

## 扩展开发

### 自定义处理器
```python
from src.etl.text_processor import TextProcessor

class CustomTextProcessor(TextProcessor):
    async def custom_clean_method(self, text: str) -> str:
        # 自定义清洗逻辑
        return cleaned_text
```

### 自定义验证规则
```python
from src.etl.data_validator import DataValidator

class CustomValidator(DataValidator):
    async def custom_business_rule(self, record, content_type, entities):
        # 自定义业务规则验证
        return validation_issues
```

## 故障排除

### 常见问题
1. **内存不足**: 减少batch_size或增加系统内存
2. **数据库连接**: 检查连接配置和网络状态
3. **中文处理**: 确保jieba词典和spacy模型正确安装
4. **权限问题**: 检查数据库用户权限和文件访问权限

### 日志分析
- 查看详细错误堆栈信息
- 分析处理性能瓶颈
- 监控数据质量趋势
- 追踪数据变更历史

## 版本历史

### v1.0.0 (当前版本)
- 基础ETL管道功能
- 中文文本处理优化
- 实体识别和关系提取
- 数据质量保证机制
- 流式处理支持
- 增量更新和版本管理

### 未来计划
- 机器学习模型集成
- 分布式处理支持
- 可视化监控界面
- 更多数据源连接器
- 高级分析功能

## 技术支持

如有问题或建议，请提交Issue或联系开发团队。