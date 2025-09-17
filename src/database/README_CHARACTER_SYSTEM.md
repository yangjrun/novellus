# 角色版本生命周期管理系统

## 🎯 系统概述

本系统专为跨域小说创作设计，支持角色在不同域（如人域→天域→灵域）之间的完整设定管理和演进追踪。系统采用智能化的版本管理策略，不仅存储角色数据，更深度分析角色的成长轨迹、关系演进和心理发展。

## ✨ 核心特性

### 1. **智能版本管理**
- **跨域演进**: 支持角色在不同域之间的设定变化
- **本质提取**: 自动识别角色的不变核心特征
- **表现分析**: 分析角色在不同环境中的表现形式
- **连续性追踪**: 确保角色发展的逻辑一致性

### 2. **深度数据分析**
- **变化类型识别**: 自动分类角色变化（身份、文化适应、技能演进等）
- **关系网络追踪**: 智能分析人际关系的演变
- **心理发展评估**: 评估角色心理状态的合理发展
- **成长轨迹记录**: 完整记录角色的发展历程

### 3. **混合存储架构**
- **PostgreSQL**: 结构化数据、版本链、关系索引
- **MongoDB**: 复杂嵌套数据、完整档案、分析结果
- **数据一致性**: 自动维护两个数据库间的同步

### 4. **创作支持功能**
- **版本对比**: 直观展示角色在不同版本间的变化
- **叙事洞察**: 自动生成剧情机会和发展建议
- **世界观检查**: 验证角色变化与域设定的一致性
- **发展评估**: 评估角色成长的合理性和潜力

## 📁 系统架构

```
src/database/
├── schemas/                           # 数据库结构定义
│   ├── character_management_tables.sql     # PostgreSQL 表结构
│   └── character_mongodb_collections.js    # MongoDB 集合结构
├── migrations/                        # 迁移和管理
│   ├── init_character_system.py           # 系统初始化
│   ├── character_lifecycle_manager.py     # 核心生命周期管理
│   └── test_character_system.py           # 集成测试
└── README_CHARACTER_SYSTEM.md        # 本文档
```

## 🗄️ 数据库设计

### PostgreSQL 表结构

#### 核心表扩展
- **entities** (扩展): 添加版本管理字段
  - `character_unique_id`: 跨版本唯一标识
  - `domain_code`: 当前所在域
  - `character_version`: 版本号
  - `is_current_version`: 是否为当前版本
  - `previous_version_id`: 前一版本引用

#### 专用管理表
- **character_version_history**: 版本变更历史
- **character_relationship_evolution**: 关系演进记录

### MongoDB 集合结构

#### 主要集合
- **character_profiles**: 完整角色档案
- **character_relationship_details**: 复杂关系数据
- **character_development_tracks**: 发展轨迹追踪
- **character_psychological_history**: 心理状态历史
- **character_version_insights**: 版本分析洞察

## 🚀 快速开始

### 1. 系统初始化

```python
from database.migrations import init_character_system

# 初始化角色管理系统
success = await init_character_system()
if success:
    print("系统初始化成功！")
```

### 2. 创建角色版本

```python
from database.migrations import create_character_version

# 角色数据（完整设定）
character_data = {
    "basicInfo": {
        "name": "林岚",
        "age": 18,
        "occupation": "外堂童生",
        "socialStatus": "灰籍"
    },
    "personality": {
        "coreTraits": ["坚韧", "共情强", "好奇"],
        "values": ["公义", "自由", "守诺"]
    },
    # ... 完整的角色设定
}

# 创建人域版本
success = await create_character_version(
    character_unique_id="lieshi-jiuyu-linlan-001",
    new_domain_code="ren_yu",
    new_character_data=character_data,
    transition_context={"creation_reason": "initial_setup"}
)
```

### 3. 跨域版本创建

```python
# 当角色进入天域时，提供新的完整设定
tian_yu_data = {
    "basicInfo": {
        "name": "林岚",  # 名字保持不变
        "age": 19,       # 年龄增长
        "occupation": "外域修士",  # 职业变化
        "socialStatus": "外域来客"
    },
    "personality": {
        "coreTraits": ["坚韧", "共情强", "好奇", "适应力强"],  # 新增特质
        "values": ["公义", "自由", "守诺", "天道平衡"]
    },
    # ... 天域的完整新设定
}

# 创建天域版本
success = await create_character_version(
    character_unique_id="lieshi-jiuyu-linlan-001",
    new_domain_code="tian_yu",
    new_character_data=tian_yu_data,
    transition_context={
        "creation_reason": "domain_ascension",
        "trigger_event": "通过飞升之门进入天域"
    }
)
```

### 4. 查询和分析

```python
from database.migrations import get_character_timeline, CharacterLifecycleManager

# 获取角色演进时间线
timeline = await get_character_timeline("lieshi-jiuyu-linlan-001")

# 版本比较
manager = CharacterLifecycleManager()
await manager.initialize()

comparison = await manager.compare_character_versions(
    "lieshi-jiuyu-linlan-001",
    "1.0",  # 人域版本
    "2.0"   # 天域版本
)
```

## 🔧 高级功能

### 智能变化分析

系统自动分析角色变化类型：

- **CORE_IDENTITY**: 核心身份变化
- **CULTURAL_ADAPTATION**: 文化适应
- **SKILL_EVOLUTION**: 技能演进
- **RELATIONSHIP_SHIFT**: 关系变化
- **PSYCHOLOGICAL_GROWTH**: 心理成长
- **EXTERNAL_TRANSFORMATION**: 外在转变

### 关系网络演进

追踪关系状态变化：

- **PRESERVED**: 保持不变
- **STRENGTHENED**: 关系加强
- **WEAKENED**: 关系削弱
- **TRANSFORMED**: 转化为新形式
- **SUSPENDED**: 暂时中断
- **TERMINATED**: 彻底终止
- **NEW_ESTABLISHED**: 新建立

### 发展一致性评估

系统评估角色发展的逻辑一致性：

- **心理健康状态**: 合理的心理发展轨迹
- **应对机制**: 应对策略的进化
- **创伤处理**: 创伤的连续性和治愈过程
- **价值观演进**: 核心价值观的保持与发展

## 🧪 测试和验证

### 运行集成测试

```bash
# 完整测试套件
python -m database.migrations.test_character_system

# JSON格式输出
python -m database.migrations.test_character_system --json

# 保留测试数据
python -m database.migrations.test_character_system --no-cleanup
```

### 测试覆盖范围

- ✅ 系统初始化
- ✅ 首版本创建
- ✅ 跨域版本创建
- ✅ 版本演进时间线
- ✅ 版本比较功能
- ✅ 数据完整性验证
- ✅ 分析功能测试
- ✅ 错误处理测试
- ✅ 性能测试

## 📊 数据模型示例

### 角色本质特征 (CharacterEssence)
```python
essence = CharacterEssence(
    core_personality=["坚韧", "共情强", "好奇"],
    fundamental_values=["公义", "自由", "守诺"],
    deep_motivations=["为家复案", "保护弱者"],
    psychological_patterns={
        "coping_style": ["理性分析", "行动导向"],
        "emotional_patterns": ["克制表达", "内化处理"]
    },
    innate_talents=["过目不忘", "水势判断"]
)
```

### 角色表现形式 (CharacterManifestation)
```python
manifestation = CharacterManifestation(
    domain_identity={
        "domain": "tian_yu",
        "occupation": "外域修士",
        "social_status": "外域来客"
    },
    social_role={
        "primary_role": "学习者",
        "influence_scope": "外域修士圈"
    },
    skill_expression={
        "professional_skills": ["基础御气术", "法理初探"],
        "domain_specific_abilities": ["气脉感知", "法则共鸣"]
    }
)
```

## 🎯 使用场景

### 1. 小说创作场景
- **剧情推进**: 角色进入新域时，系统帮助分析合理的变化方向
- **一致性检查**: 确保角色发展符合既定人设和世界观
- **灵感激发**: 通过版本对比发现新的剧情可能性

### 2. 世界观管理
- **文化适应**: 分析角色如何适应不同域的文化环境
- **技能转化**: 追踪技能在不同域中的表现形式
- **关系维护**: 管理跨域关系的维持和发展

### 3. 角色发展规划
- **成长轨迹**: 规划角色的长期发展路径
- **能力进阶**: 设计合理的能力提升过程
- **心理健康**: 关注角色的心理发展和创伤治愈

## ⚠️ 注意事项

### 数据安全
- 定期备份 PostgreSQL 和 MongoDB 数据
- 测试环境与生产环境隔离
- 重要操作前建议先在测试环境验证

### 性能优化
- 大量数据时考虑分页查询
- 定期维护数据库索引
- 监控 MongoDB 集合大小

### 扩展建议
- 可根据具体世界观扩展域特定的分析逻辑
- 可添加更多的角色特征提取规则
- 可集成AI模型进行更智能的分析

## 🔄 版本历史

### v2.0 (当前版本)
- ✨ 重新设计为智能生命周期管理系统
- ✨ 添加深度变化分析功能
- ✨ 实现关系网络演进追踪
- ✨ 集成完整的测试框架
- 🗑️ 移除过于复杂的迁移逻辑

### v1.0 (已弃用)
- 基础的数据迁移功能
- 简单的版本管理

## 📞 支持

如有问题或建议，请：

1. 查看集成测试结果确认系统状态
2. 检查日志文件获取详细错误信息
3. 运行数据完整性验证
4. 参考本文档的使用示例

---

*这个系统专为复杂的跨域小说世界观设计，旨在帮助作者更好地管理和发展角色，确保故事的连贯性和深度。*