# Database 目录结构说明

## 📁 整理后的目录结构

```
src/database/
├── __init__.py                    # 数据库模块主入口
├── data_access.py                 # 数据访问层API
├── DIRECTORY_STRUCTURE.md         # 本文档
│
├── connections/                   # 数据库连接管理
│   ├── __init__.py               # 连接模块导出
│   ├── postgresql.py             # PostgreSQL连接管理
│   └── mongodb.py                # MongoDB连接管理
│
├── models/                       # 数据模型定义
│   ├── __init__.py               # 模型模块导出
│   ├── models.py                 # 基础数据模型
│   └── cultural_models.py        # 文化框架模型
│
├── schemas/                      # 数据库表结构定义
│   ├── __init__.py               # 模式定义导出
│   ├── init_postgresql.sql       # PostgreSQL基础表
│   └── cultural_framework_tables.sql  # 文化框架表
│
├── migrations/                   # 数据库迁移和初始化
│   ├── __init__.py               # 迁移模块导出
│   └── init_mongodb.py           # MongoDB基础初始化
│
├── cultural_framework/           # 文化框架系统
│   ├── __init__.py               # 文化框架模块导出
│   ├── init_cultural_mongodb.py  # 文化框架MongoDB初始化
│   └── init_cultural_framework.py # 完整文化框架初始化
│
├── utils/                        # 工具和辅助功能
│   ├── __init__.py               # 工具模块导出
│   └── sample_data.py            # 示例数据生成
│
└── __pycache__/                  # Python缓存目录
```

## 🎯 模块职责划分

### 📦 connections/ - 数据库连接管理
- **PostgreSQL连接**: 连接池管理、异步连接
- **MongoDB连接**: 客户端管理、数据库实例获取
- **向后兼容**: 保持原有API不变

### 🏗️ models/ - 数据模型定义
- **基础模型**: 小说、实体、关系、事件等核心模型
- **文化框架模型**: 域、维度、框架、要素等文化相关模型
- **请求响应模型**: API交互的数据传输对象
- **类型定义**: 枚举类型和约束定义

### 🗃️ schemas/ - 数据库表结构
- **PostgreSQL表**: SQL文件定义表结构、索引、触发器
- **版本控制**: 表结构变更的版本管理
- **约束定义**: 外键、检查约束、唯一约束

### 🔄 migrations/ - 数据库迁移
- **初始化脚本**: 新环境的数据库初始化
- **迁移脚本**: 数据库结构升级脚本
- **种子数据**: 基础数据和示例数据

### 🎭 cultural_framework/ - 文化框架系统
- **MongoDB初始化**: 文化内容集合和索引
- **完整初始化**: PostgreSQL + MongoDB 联合初始化
- **六维框架**: 标准文化维度的定义和实现
- **九域配置**: 各域的文化特征配置

### 🛠️ utils/ - 工具辅助
- **示例数据**: 测试和演示用的数据生成
- **数据验证**: 数据完整性检查工具
- **导入导出**: 数据备份和恢复工具

## 🚀 使用指南

### 基础使用
```python
# 导入数据库模块
from database import init_database, get_novel_manager

# 初始化数据库
await init_database()

# 获取小说管理器
novel_manager = get_novel_manager(novel_id=1)
```

### 文化框架使用
```python
# 导入文化框架初始化
from database.cultural_framework import init_cultural_framework_system

# 初始化文化框架系统
await init_cultural_framework_system()
```

### 模型使用
```python
# 导入模型
from database.models import Novel, Domain, CulturalFramework

# 创建模型实例
novel = Novel(title="裂世九域", code="lieshi_jiuyu")
```

## 📋 迁移指南

### 从旧结构迁移
1. **导入路径更新**: 无需更改，保持向后兼容
2. **新功能使用**: 使用新的文化框架功能
3. **逐步迁移**: 可以逐步将代码迁移到新结构

### 添加新功能
1. **模型定义**: 在 `models/` 中添加新模型
2. **表结构**: 在 `schemas/` 中添加SQL文件
3. **初始化**: 在 `migrations/` 中添加初始化脚本
4. **导出**: 在对应的 `__init__.py` 中导出新功能

## ⚠️ 注意事项

### 导入路径
- 主要功能从 `database` 模块导入
- 子模块功能从对应子包导入
- 保持向后兼容性

### 文件组织
- 按功能职责分类存放
- 每个目录都有 `__init__.py`
- 明确的模块导出定义

### 开发建议
- 新功能优先放在对应的子模块中
- 保持文件命名的一致性
- 添加适当的文档说明

## 🔄 版本控制

### 当前版本: v2.0
- ✅ 重新组织目录结构
- ✅ 添加文化框架系统
- ✅ 保持向后兼容
- ✅ 完善模块划分

### 下一版本计划
- [ ] 添加数据库迁移工具
- [ ] 完善测试覆盖
- [ ] 性能优化工具
- [ ] 数据导入导出工具