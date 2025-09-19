# 裂世九域·法则链纪元 文化框架分析系统

## 概述

这是一个专门为"裂世九域·法则链纪元"小说项目设计的文化框架分析工具，支持对九个域的六维文化设定进行深度分析、实体识别、关系网络构建和结构化数据输出。

## 核心功能

### 🎯 六维文化分析
- **A. 神话与宗教**: 分析各域的信仰体系、神话传说和宗教组织
- **B. 权力与法律**: 解析政治制度、法律体系和权力结构
- **C. 经济与技术**: 识别经济模式、技术水平和贸易关系
- **D. 家庭与教育**: 提取家庭结构、教育制度和社会传承
- **E. 仪式与日常**: 分析日常习俗、节日庆典和生活方式
- **F. 艺术与娱乐**: 识别艺术形式、娱乐活动和文化表达

### 🔍 智能实体识别
- **组织机构**: 王朝、议会、宗门、司殿等权力组织
- **重要概念**: 法则链、链籍、断链术等核心概念
- **文化物品**: 链票、环印、镇魂器等特色物品
- **仪式活动**: 裂世夜、归环礼、狂环月等文化仪式
- **地理位置**: 帝都、港口、城阙等重要地点

### 🌐 关系网络分析
- **跨域关系**: 分析九域之间的政治、经济、文化关系
- **实体关联**: 识别实体间的依赖、冲突、合作关系
- **权力结构**: 构建各域内部的权力层级网络
- **贸易网络**: 分析经济贸易和资源流动关系

### 📊 数据结构化输出
- **完整JSON格式**: 包含所有分析结果的结构化数据
- **实体词典**: 重要概念和术语的详细解释
- **关系图谱**: 可视化的实体关系网络数据
- **冲突分析**: 识别潜在的故事冲突点和情节线索

## 使用方法

### 1. 基础使用

```python
from cultural_framework_analyzer import CulturalFrameworkAnalyzer

# 创建分析器实例
analyzer = CulturalFrameworkAnalyzer()

# 分析文本内容
cultural_text = """
人域
A. 神话与宗教
天命信仰主导，认为链籍记录着天意...

B. 权力与法律
天命王朝统治，采用链籍等级制度...
...
"""

# 执行分析
result = await analyzer.analyze_full_text(cultural_text)

# 保存结果
analyzer.save_analysis_result(result, "analysis_result.json")
```

### 2. 单域分析

```python
from cultural_framework_analyzer import DomainType

# 分析特定域
domain_result = analyzer.parse_domain_text(domain_text, DomainType.HUMAN)

# 查看域的文化维度
print(domain_result.cultural_dimensions.mythology_religion)
print(domain_result.cultural_dimensions.power_law)
```

### 3. 实体分析

```python
# 获取特定类型的实体
organizations = [e for e in analyzer.entities if e.entity_type == EntityType.ORGANIZATION]
concepts = [e for e in analyzer.entities if e.entity_type == EntityType.CONCEPT]

# 查看高重要性实体
high_importance = [e for e in analyzer.entities if e.importance_level >= 8]
```

### 4. 关系网络分析

```python
# 分析跨域关系
relations = analyzer.analyze_cross_domain_relations()

# 查看特定域的关系
human_relations = [r for r in relations if r.from_domain == DomainType.HUMAN]
```

## 输入文本格式

### 标准格式要求

```
域名
A. 神话与宗教
详细内容描述...

B. 权力与法律
详细内容描述...

C. 经济与技术
详细内容描述...

D. 家庭与教育
详细内容描述...

E. 仪式与日常
详细内容描述...

F. 艺术与娱乐
详细内容描述...

情节钩子：
- 钩子1
- 钩子2
```

### 域名支持
- 人域、天域、荒域、冥域、魔域、虚域、海域、源域
- 支持变体：人间域、天界域、蛮荒域等

## 输出数据结构

### 完整JSON格式
```json
{
  "analysis_metadata": {
    "timestamp": "2025-01-XX",
    "total_domains": 8,
    "total_entities": 156,
    "total_relations": 23
  },
  "domain_cultures": {
    "人域": {
      "basic_info": {...},
      "cultural_dimensions": {
        "mythology_religion": {...},
        "power_law": {...},
        "economy_tech": {...},
        "family_education": {...},
        "ritual_daily": {...},
        "art_entertainment": {...}
      },
      "entities": [...],
      "plot_hooks": [...],
      "potential_conflicts": [...]
    }
  },
  "cross_domain_relations": [...],
  "concept_dictionary": {...},
  "analysis_insights": {...}
}
```

### 核心数据字段

#### 实体信息
- `name`: 实体名称
- `entity_type`: 实体类型（组织、概念、物品等）
- `domain`: 所属域
- `dimension`: 所属文化维度
- `importance_level`: 重要性等级（1-10）
- `related_entities`: 相关实体列表
- `attributes`: 实体属性字典

#### 域关系
- `from_domain` / `to_domain`: 关系双方
- `relation_type`: 关系类型（政治、经济、文化等）
- `strength`: 关系强度（1-10）
- `nature`: 关系性质（友好、敌对、中立等）
- `description`: 关系描述

## 高级功能

### 1. 世界观一致性检查
```python
consistency = result['analysis_insights']['world_consistency']
if not consistency['chain_concept_consistency']:
    print("发现链概念不一致问题")
    print(consistency['issues'])
```

### 2. 主题识别
```python
themes = result['analysis_insights']['dominant_themes']
for theme in themes:
    print(f"主要主题: {theme}")
```

### 3. 冲突分析
```python
conflicts = result['analysis_insights']['cultural_conflicts']
for conflict in conflicts:
    print(f"冲突类型: {conflict['type']}")
    print(f"冲突描述: {conflict['description']}")
```

### 4. 权力结构分析
```python
power_analysis = result['analysis_insights']['power_structure_analysis']
print(f"权力集中度: {power_analysis['power_concentration']}")
```

## 预定义概念词典

系统内置了法则链相关的核心概念：

- **链籍**: 法则记录，天域管理
- **法则链**: 修炼基础，所有域通用
- **断链术**: 禁忌法术，虚域/魔域
- **链票**: 货币工具，人域/天域
- **环印**: 身份标识，天域权力象征
- **镇魂器**: 冥域法器，灵魂控制

## 扩展和定制

### 1. 添加新实体类型
```python
class EntityType(Enum):
    # 现有类型...
    NEW_TYPE = "新类型"

# 更新识别模式
analyzer.entity_patterns[EntityType.NEW_TYPE] = [r'新模式正则']
```

### 2. 自定义域关系
```python
# 在 _analyze_domain_pair_relation 方法中添加新的预定义关系
known_relations = {
    (DomainType.CUSTOM1, DomainType.CUSTOM2): {
        'type': '自定义关系',
        'strength': 8,
        'nature': '复杂',
        'description': '自定义关系描述'
    }
}
```

### 3. 扩展文化维度
虽然当前支持六维标准，但可以通过修改 `CulturalDimension` 枚举和相关解析逻辑来支持更多维度。

## 性能优化

### 1. 大文本处理
- 支持异步处理
- 分段解析避免内存溢出
- 智能缓存提高重复分析效率

### 2. 并行分析
```python
import asyncio

# 并行分析多个域
tasks = [analyzer.parse_domain_text(text, domain) for domain, text in domain_texts.items()]
results = await asyncio.gather(*tasks)
```

## 故障排除

### 常见问题

1. **实体识别不准确**
   - 检查文本格式是否符合标准
   - 调整正则表达式模式
   - 验证文化维度标记（A-F）

2. **关系分析缺失**
   - 确保域名正确标识
   - 检查实体关联描述
   - 验证预定义关系配置

3. **输出格式问题**
   - 检查JSON序列化兼容性
   - 验证Unicode编码
   - 确认文件写入权限

### 调试技巧
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看中间结果
print(f"识别到的实体: {len(analyzer.entities)}")
for entity in analyzer.entities[:5]:  # 显示前5个
    print(f"- {entity.name} ({entity.entity_type.value})")
```

## 示例项目

查看 `example_analysis.py` 文件了解完整的使用示例，包括：
- 真实文本分析案例
- 结果可视化方法
- 与数据库集成示例
- 批量处理工作流

## 许可证

本工具采用MIT许可证，可自由使用和修改。

---

更多详细信息请参考源码注释和API文档。