# 裂世九域·法则链纪元 数据库架构文档

## 概述

本项目为"裂世九域·法则链纪元"小说项目构建了一个完整的数据库管理系统，支持PostgreSQL + MongoDB双数据库架构，专门优化了多批次文本内容的渐进式管理。

## 核心特性

### 🏗️ 双数据库架构
- **PostgreSQL**: 存储结构化数据（项目、小说、批次、段落、世界观核心数据）
- **MongoDB**: 存储复杂文档数据（角色详情、地点信息、物品、事件、知识库）

### 📝 渐进式内容管理
- 支持分批次创建和管理文本内容
- 批次工作流管理（草稿→大纲→写作→审阅→修订→完成）
- 自动调度和进度追踪

### 🌍 世界观管理
- 九大域系统管理
- 法则链和链痕系统
- 修炼体系和权力组织
- 角色关系网络

## 架构组件

### 数据库层
```
src/database/
├── __init__.py              # 模块入口
├── connection_manager.py    # 数据库连接管理
├── data_access.py          # 数据访问层统一接口
├── batch_manager.py        # 批次管理系统
├── database_init.py        # 数据库初始化
├── quickstart.py           # 快速开始示例
├── models/                 # 数据模型定义
│   ├── __init__.py
│   ├── core_models.py      # 核心模型（项目、小说、批次）
│   ├── worldbuilding_models.py  # 世界观模型
│   ├── character_models.py # 角色模型
│   └── content_models.py   # 内容模型
├── repositories/           # 数据仓库层
│   ├── __init__.py
│   ├── postgresql_repository.py
│   └── mongodb_repository.py
└── schemas/               # 数据库架构定义
    ├── init_postgresql.sql
    └── init_mongodb.js
```

### 核心数据模型

#### PostgreSQL 表结构
- **projects**: 项目管理
- **novels**: 小说管理
- **content_batches**: 内容批次
- **content_segments**: 内容段落
- **domains**: 九大域
- **cultivation_systems**: 修炼体系
- **law_chains**: 法则链
- **power_organizations**: 权力组织

#### MongoDB 集合结构
- **characters**: 角色详细信息
- **locations**: 地点和场景
- **items**: 物品和法宝
- **events**: 事件和情节
- **knowledge_base**: 知识库

## 使用指南

### 1. 初始化系统

```python
# 运行快速开始演示
python src/database/quickstart.py demo

# 或者手动初始化
from database.database_init import initialize_database
result = await initialize_database()
```

### 2. 基本操作流程

#### 创建项目和小说
```python
from database.data_access import get_global_manager
from database.models import ProjectCreate, NovelCreate

global_manager = get_global_manager()

# 创建项目
project = await global_manager.create_project(ProjectCreate(
    name="lieshipan_jiuyu",
    title="裂世九域·法则链纪元",
    description="玄幻修仙小说",
    author="作者名"
))

# 创建小说
novel = await global_manager.create_novel(NovelCreate(
    project_id=project.id,
    name="volume_1",
    title="第一卷：初入九域"
))
```

#### 批次管理
```python
from database.batch_manager import get_batch_manager
from database.models import BatchType

batch_manager = await get_batch_manager(novel.id)

# 创建批次系列
batches = await batch_manager.create_batch_series(
    series_name="开篇章节",
    batch_type=BatchType.PLOT,
    batch_count=5,
    interval_days=7
)

# 获取仪表板
dashboard = await batch_manager.get_batch_dashboard()
```

#### 世界观管理
```python
from database.models import DomainCreate, DomainType

novel_manager = get_novel_manager(novel.id)

# 创建域
domain = await novel_manager.create_domain(DomainCreate(
    novel_id=novel.id,
    name="人域",
    domain_type=DomainType.HUMAN_DOMAIN,
    power_level=3
))
```

### 3. MCP服务器工具

系统提供了丰富的MCP工具，可以通过Claude客户端直接调用：

- `initialize_database_tool()`: 初始化数据库
- `create_project()`: 创建项目
- `create_novel()`: 创建小说
- `create_content_batch()`: 创建批次
- `create_character()`: 创建角色
- `search_novel_content()`: 搜索内容
- `get_novel_statistics()`: 获取统计信息

## 技术特性

### 异步支持
- 全异步数据库操作
- 连接池管理
- 事务支持

### 数据验证
- Pydantic模型验证
- 数据类型安全
- 输入数据清理

### 错误处理
- 统一异常处理
- 详细错误日志
- 优雅降级

### 性能优化
- 数据库索引优化
- 连接池复用
- 批量操作支持

## 配置说明

### 环境变量配置 (.env)
```env
# PostgreSQL配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=novellus
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# MongoDB配置
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=novellus
MONGODB_USER=
MONGODB_PASSWORD=
```

### 依赖要求
- Python 3.8+
- PostgreSQL 12+
- MongoDB 4.4+
- asyncpg
- motor
- pydantic

## 扩展性

### 添加新的内容类型
1. 在`models/`中定义新的数据模型
2. 在对应的repository中实现数据访问方法
3. 在`data_access.py`中添加管理接口
4. 在MCP服务器中添加对应的工具函数

### 自定义批次类型
1. 扩展`BatchType`枚举
2. 在批次管理器中添加对应的逻辑
3. 更新工作流状态机

### 世界观元素扩展
1. 在PostgreSQL schema中添加新表
2. 创建对应的Pydantic模型
3. 实现CRUD操作接口

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否运行
   - 验证连接配置
   - 确认防火墙设置

2. **初始化失败**
   - 检查数据库权限
   - 确认schema文件存在
   - 查看详细错误日志

3. **性能问题**
   - 检查索引使用情况
   - 监控连接池状态
   - 优化查询语句

### 日志配置
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 编写测试用例
4. 提交Pull Request

## 许可证

本项目采用MIT许可证。

---

📚 更多详细信息请参考源码注释和示例代码。