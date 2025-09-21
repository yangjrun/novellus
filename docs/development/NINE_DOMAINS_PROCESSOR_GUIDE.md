# 九域文化框架数据处理工作流程使用指南

## 概述

本工作流程专门为"裂世九域·法则链纪元"小说的文化框架文本数据处理而设计，能够自动解析、提取、验证和存储复杂的九域六维文化设定。

## 核心功能

### 1. 文本清洗和结构化
- 解析每个域的六维文化数据（A-F维度）
- 清理格式，提取关键信息
- 识别实体、概念、关系

### 2. 实体提取和分类
- **组织机构**: 天命王朝、祭司议会、冥司殿等
- **身份等级**: 链籍分类、修炼境界等
- **文化物品**: 链票、环印、镇魂器等
- **仪式活动**: 各种节庆、仪式、禁忌
- **地理概念**: 城阙、帝都、港口等

### 3. 跨域关系分析
- 识别九域之间的文化交互、冲突和关联
- 分析贸易往来、政治关系、文化影响
- 构建域间关系网络

### 4. 数据质量验证
- 完整性检查（域覆盖、维度覆盖）
- 一致性验证（实体与域的匹配）
- 准确性校验（术语使用、格式规范）
- 自动清洗和修复

## 快速开始

### 1. 基础使用

```python
from src.etl.nine_domains_pipeline import NineDomainsPipeline
from uuid import uuid4

# 创建处理管道
pipeline = NineDomainsPipeline()

# 处理文本
result = await pipeline.process_cultural_text(
    text="你的九域文化设定文本",
    novel_id=uuid4(),
    source_info={"source": "文档名称"}
)

# 检查结果
if result["success"]:
    print(f"处理成功，提取了 {result['summary']['total_data_count']['entities']} 个实体")
else:
    print(f"处理失败: {result['error']}")
```

### 2. 文件处理

```python
from src.etl.nine_domains_pipeline import process_nine_domains_file

# 直接处理文件
result = await process_nine_domains_file(
    file_path="path/to/cultural_text.txt",
    novel_id="your-novel-id",
    config={
        "enable_validation": True,
        "enable_cross_domain_analysis": True,
        "enable_database_import": True
    }
)
```

### 3. 命令行使用

```bash
# 基础处理
python src/etl/nine_domains_pipeline.py --file cultural_text.txt --novel-id your-novel-id

# 带配置文件
python src/etl/nine_domains_pipeline.py --file cultural_text.txt --novel-id your-novel-id --config config.json --output result.json
```

## 配置选项

创建 `config.json` 文件：

```json
{
  "enable_text_cleaning": true,
  "enable_validation": true,
  "enable_cross_domain_analysis": true,
  "enable_database_import": true,
  "validation_level": "NORMAL",
  "enable_auto_fix": true,
  "max_concurrent_processing": 3,
  "chunk_size": 5000,
  "save_intermediate_results": true,
  "output_detailed_logs": true
}
```

## 输入文本格式

### 标准格式示例

```text
人域｜六维文化框架

A. 神话与宗教
信条：链是"看不见的鞭子"，顺链得安、逆链遭殃。
神祇与机构：乡祠供奉"环祖"（九环祖像），由"乡祭"掌礼；城内设祭司分坊。
丧葬观："顺链而归"，请冥域渡链僧诵《归环文》；无链籍者草葬、不得入册。

B. 权力与法律
结构：县府（吏治）＋宗门驻坊（修治）双轨；大案须报天域巡链司。
身份：链籍黄/灰/黑三等（黄=良籍；灰=苦役；黑=罪籍）。
刑罚：逃籍/伪票→笞与流；传授断链术→加缚或链枷。

C. 经济与技术
产业：谷物、盐铁、陶织、驭兽农具；向宗门供童生与杂役。
金融：小额链票村社抗议。
技术：环铸法、锻链术、法则工艺传承有师承制约束。

D. 家庭与教育
婚嫁：需"环印"合证，双方家谱链印验真；跨籍联姻受限。
传承：血脉与师承双轨，血契者入魔域、断链者成荒民。

E. 仪式与日常
节庆：链诞节（祭环祖）、裂世夜（避邪）、拾链礼（成人礼）。
日常：晨诵环文、午检链籍、夜祭祖灵；

F. 艺术与娱乐
艺术：环纹雕刻、链歌吟唱、祖谱绘制。
竞技：链术比试、环器竞赛、法则辩论。

【剧情钩子】
1. 祖灵续籍祭夜，有人盗改家谱链印，引发血脉争议。
2. 年轻人私学断链术，被发现后逃往荒域，家族链籍被降级。
```

## 输出结果结构

```json
{
  "success": true,
  "process_id": "uuid",
  "processing_time": 2.45,
  "summary": {
    "total_data_count": {
      "frameworks": 6,
      "entities": 25,
      "relations": 12,
      "plot_hooks": 3,
      "concepts": 15
    },
    "domain_distribution": {
      "人域": 6
    },
    "dimension_distribution": {
      "神话与宗教": 1,
      "权力与法律": 1,
      "经济与技术": 1,
      "家庭与教育": 1,
      "仪式与日常": 1,
      "艺术与娱乐": 1
    },
    "quality_metrics": {
      "domains_covered": 1,
      "dimensions_covered": 6,
      "avg_entity_description_length": 45.2,
      "cross_domain_relations": 2
    },
    "recommendations": [
      "域覆盖率较低，建议补充更多域的文化数据",
      "实体描述质量良好，可考虑进一步细化"
    ]
  }
}
```

## 数据库集成

### PostgreSQL 表结构

主要表：
- `cultural_frameworks`: 文化框架数据
- `cultural_entities`: 文化实体
- `cultural_relations`: 实体关系
- `plot_hooks`: 剧情钩子
- `concept_dictionary`: 概念词典

### MongoDB 集合结构

主要集合：
- `cultural_details`: 详细的文化分析数据
- `plot_hooks_detailed`: 剧情钩子详细信息
- `concepts_dictionary`: 概念词典扩展信息
- `processing_logs`: 处理日志

## 测试

运行完整测试套件：

```bash
python test_nine_domains_processor.py
```

测试包括：
- 主流程测试
- 各组件单独测试
- 实体提取详细测试
- 数据验证测试

## 高级用法

### 1. 自定义实体提取规则

```python
from src.etl.nine_domains_entity_extractor import NineDomainsEntityExtractor, ExtractionRule, EntityType

extractor = NineDomainsEntityExtractor()

# 添加自定义规则
custom_rule = ExtractionRule(
    name="custom_organizations",
    patterns=[r'([^，。！？\s]{2,8}(?:联盟|公会|商行))'],
    entity_type=EntityType.ORGANIZATION,
    confidence_boost=0.3
)

extractor.extraction_rules.append(custom_rule)
```

### 2. 自定义验证规则

```python
from src.etl.cultural_data_validator import CulturalDataValidator

validator = CulturalDataValidator()

# 修改验证标准
validator.quality_standards["min_entities_per_domain"] = 5
validator.quality_standards["min_concepts_per_novel"] = 10
```

### 3. 批量处理多个文件

```python
import asyncio
from pathlib import Path

async def batch_process_files(file_paths, novel_id):
    pipeline = NineDomainsPipeline()
    results = []

    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        result = await pipeline.process_cultural_text(
            text, novel_id, {"source_file": str(file_path)}
        )
        results.append(result)

    await pipeline.close()
    return results
```

## 故障排除

### 常见问题

1. **实体提取数量少**
   - 检查文本格式是否符合九域标准
   - 确认域名和维度标记正确
   - 增加自定义提取规则

2. **验证失败**
   - 检查必需概念是否存在
   - 确认域与实体的一致性
   - 降低验证级别到 "LOOSE"

3. **跨域关系识别不准确**
   - 确保文本中明确描述了域间关系
   - 检查域特征词汇是否正确
   - 手动添加关系描述

4. **数据库导入失败**
   - 检查数据库连接配置
   - 确认表结构是否正确
   - 查看处理日志

### 性能优化

1. **大文件处理**
   - 调整 `chunk_size` 参数
   - 启用 `max_concurrent_processing`
   - 关闭不需要的分析功能

2. **内存使用**
   - 分批处理大量数据
   - 及时关闭处理管道
   - 清理中间结果

## 扩展开发

### 添加新的文化维度

1. 在 `CulturalDimension` 枚举中添加新维度
2. 更新解析模式
3. 添加相应的验证规则
4. 更新数据库架构

### 支持新的实体类型

1. 在 `EntityType` 枚举中添加新类型
2. 设计提取规则
3. 添加验证逻辑
4. 更新UI界面

## 联系与支持

如有问题或需要扩展功能，请：
1. 查看处理日志
2. 运行测试套件
3. 检查配置文件
4. 联系开发团队

---

*九域文化框架数据处理工作流程 v1.0*
*专为"裂世九域·法则链纪元"设计*