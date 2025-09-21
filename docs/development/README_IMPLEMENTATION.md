# 网络小说世界观管理系统 - 实现说明

## 系统概述

本系统是一个支持多小说的通用世界观管理平台，基于MCP(Model Control Protocol)架构，使用PostgreSQL + MongoDB混合数据库设计。

## 核心特性

### 🎯 多小说支持
- 完全的数据隔离：每个小说项目的数据独立管理
- 模板化设计：支持不同类型小说的快速创建
- 灵活扩展：通用实体系统支持自定义字段和属性

### 📊 混合数据库架构
- **PostgreSQL**: 存储结构化数据（实体、关系、事件、分类）
- **MongoDB**: 存储内容描述数据（档案、故事、世界观配置）
- **数据协作**: 通过ID关联实现跨库查询和数据同步

### 🔧 MCP服务器接口
- RESTful风格的工具接口
- 完整的CRUD操作支持
- JSON格式的数据交换
- 详细的错误处理和响应

## 文件结构

```
src/
├── database/
│   ├── __init__.py              # 数据库包初始化
│   ├── init_postgresql.sql      # PostgreSQL数据库初始化脚本
│   ├── init_mongodb.py          # MongoDB集合初始化脚本
│   ├── models.py                # 数据模型定义
│   ├── data_access.py           # 数据访问层API
│   ├── postgresql.py            # PostgreSQL连接管理（兼容性）
│   ├── mongodb.py               # MongoDB连接管理（兼容性）
│   └── sample_data.py           # 示例数据生成脚本
├── mcp_server.py                # MCP服务器主程序
└── config.py                    # 配置管理
```

## 数据库设计

### PostgreSQL 表结构

#### 核心管理表
- `novels`: 小说项目管理
- `novel_templates`: 小说类型模板
- `entity_types`: 实体类型定义

#### 通用数据表
- `entities`: 通用实体表（角色、地点、势力等）
- `entity_relationships`: 实体关系
- `categories`: 分类系统（域、境界、等级）
- `events`: 事件和时间线

#### 辅助表
- `schema_versions`: 版本管理
- `audit_logs`: 审计日志

### MongoDB 集合结构

- `novel_worldbuilding`: 世界观配置
- `entity_profiles`: 实体详细档案
- `story_content`: 故事内容
- `scene_descriptions`: 场景描述
- `novel_templates`: 小说模板
- `cross_novel_analysis`: 跨小说分析

## 快速开始

### 1. 环境准备

确保已安装并配置：
- Python 3.8+
- PostgreSQL 12+
- MongoDB 4.4+
- 必要的Python依赖包

### 2. 数据库初始化

```bash
# 初始化PostgreSQL
psql -U postgres -d your_database -f src/database/init_postgresql.sql

# 初始化MongoDB
uv run python src/database/init_mongodb.py
```

### 3. 启动MCP服务器

```bash
uv run python src/mcp_server.py
```

### 4. 创建示例数据

```bash
uv run python src/database/sample_data.py
```

## MCP工具接口

### 小说项目管理

#### `create_novel`
创建新的小说项目
```
参数:
- title: 小说标题
- code: 小说代码标识
- author: 作者（可选）
- genre: 类型（可选）
- world_type: 世界观类型（可选）
- template_code: 模板代码（可选）
```

#### `list_novels`
获取小说列表
```
参数:
- status: 状态过滤（可选）
```

#### `get_novel_summary`
获取小说摘要信息
```
参数:
- novel_id: 小说ID
```

### 实体管理

#### `create_entity`
创建实体（角色、地点、势力等）
```
参数:
- novel_id: 小说ID
- entity_type_name: 实体类型名称
- name: 实体名称
- code: 实体代码（可选）
- attributes: 属性JSON字符串（可选）
- tags: 标签JSON数组（可选）
- priority: 优先级（可选）
- profile: 详细档案JSON（可选）
```

#### `get_entity`
获取实体详细信息
```
参数:
- novel_id: 小说ID
- entity_id: 实体ID
- include_profile: 是否包含详细档案（可选）
```

#### `search_entities`
搜索实体
```
参数:
- novel_id: 小说ID
- filters: 过滤条件JSON（可选）
- sort: 排序字段（可选）
- limit: 限制数量（可选）
- offset: 偏移量（可选）
```

#### `update_entity`
更新实体信息
```
参数:
- novel_id: 小说ID
- entity_id: 实体ID
- name: 新名称（可选）
- code: 新代码（可选）
- status: 新状态（可选）
- attributes: 新属性JSON（可选）
- tags: 新标签JSON（可选）
- priority: 新优先级（可选）
- profile: 新档案JSON（可选）
```

### 关系管理

#### `create_relationship`
创建实体间关系
```
参数:
- novel_id: 小说ID
- source_entity_id: 源实体ID
- target_entity_id: 目标实体ID
- relationship_type: 关系类型
- strength: 关系强度（可选）
- attributes: 关系属性JSON（可选）
```

#### `get_entity_relationships`
获取实体的所有关系
```
参数:
- novel_id: 小说ID
- entity_id: 实体ID
```

### 事件管理

#### `create_event`
创建剧情事件
```
参数:
- novel_id: 小说ID
- name: 事件名称
- event_type: 事件类型（可选）
- description: 事件描述（可选）
- impact_level: 影响级别（可选）
- scope: 影响范围（可选）
- participants: 参与者ID列表JSON（可选）
```

#### `get_story_timeline`
获取故事时间线
```
参数:
- novel_id: 小说ID
- limit: 限制数量（可选）
```

## 示例用法

### 创建裂世九域小说项目

```json
{
  "tool": "create_novel",
  "parameters": {
    "title": "裂世九域·法则链纪元",
    "code": "lieshi_jiuyu",
    "author": "示例作者",
    "genre": "玄幻",
    "world_type": "cultivation",
    "template_code": "cultivation_world"
  }
}
```

### 创建主角角色

```json
{
  "tool": "create_entity",
  "parameters": {
    "novel_id": 1,
    "entity_type_name": "character",
    "name": "林逸",
    "code": "protagonist",
    "attributes": "{\"origin_domain\": \"人域\", \"current_realm\": \"开脉\", \"bloodline\": \"源链血脉\"}",
    "tags": "[\"主角\", \"断链者\", \"源链血脉\"]",
    "priority": 100,
    "profile": "{\"identity\": {\"full_name\": \"林逸\", \"age\": 18}, \"background\": {\"tragedy\": \"目睹父母被链枷处决\"}}"
  }
}
```

### 搜索角色实体

```json
{
  "tool": "search_entities",
  "parameters": {
    "novel_id": 1,
    "filters": "{\"entity_type\": \"character\", \"tags\": [\"主角\"]}",
    "limit": 10
  }
}
```

## 扩展指南

### 添加新的实体类型

1. 在数据库中创建实体类型记录
2. 定义schema_definition配置字段结构
3. 在MongoDB中配置对应的档案模板

### 创建自定义小说模板

1. 在MongoDB的novel_templates集合中添加模板
2. 定义default_config和entity_templates
3. 在创建小说时指定template_code

### 扩展MCP工具

1. 在mcp_server.py中添加新的@mcp.tool()函数
2. 实现相应的数据访问逻辑
3. 添加适当的错误处理和响应格式

## 安全考虑

- **数据隔离**: 每个小说的数据完全隔离，通过novel_id强制过滤
- **输入验证**: 所有用户输入都经过验证和净化
- **错误处理**: 详细的错误信息帮助调试，但不暴露敏感信息
- **审计日志**: 记录所有数据变更操作

## 性能优化

- **索引优化**: 关键查询字段都创建了适当的索引
- **分页查询**: 大量数据查询支持分页，防止内存溢出
- **连接池**: 数据库连接池管理，提高并发性能
- **缓存策略**: 热点数据可以添加缓存层

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查配置文件中的数据库连接信息
   - 确保数据库服务正在运行
   - 验证用户权限

2. **MCP工具调用失败**
   - 检查参数格式是否正确
   - 验证JSON字符串的语法
   - 查看服务器日志获取详细错误信息

3. **数据查询返回空结果**
   - 确认novel_id是否正确
   - 检查数据是否已正确创建
   - 验证过滤条件是否过于严格

### 日志分析

系统使用Python标准logging模块，日志级别设置为INFO。关键操作都会记录日志，包括：
- 数据库连接状态
- 实体创建/更新操作
- 错误信息和异常堆栈

## 开发计划

### 下一步功能
- [ ] 用户权限管理
- [ ] 数据导入/导出功能
- [ ] 图形化界面支持
- [ ] 实时协作功能
- [ ] AI辅助世界观生成

### 性能优化
- [ ] 查询结果缓存
- [ ] 数据库读写分离
- [ ] 异步任务队列
- [ ] 分布式部署支持