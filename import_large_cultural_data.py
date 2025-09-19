#!/usr/bin/env python3
"""
大规模文化框架数据导入脚本
模拟导入109个实体和28个跨域关系的完整数据集
"""

import asyncio
import logging
import time
from uuid import UUID

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 项目和小说ID
PROJECT_ID = "29c170c5-4a3e-4829-a242-74c1acb96453"
NOVEL_ID = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"


def generate_large_cultural_dataset():
    """生成大规模文化数据集，模拟109个实体和28个跨域关系"""

    # 模拟九域的完整文化分析数据
    large_dataset = {
        "analysis_metadata": {
            "timestamp": "2025-01-19T10:00:00Z",
            "total_domains": 9,
            "total_entities": 109,
            "total_relations": 28,
            "average_confidence": 0.92,
            "processing_time": "45.2 seconds",
            "version": "2.0"
        },
        "domain_cultures": {},
        "cross_domain_relations": [],
        "concept_dictionary": []
    }

    # 定义九域
    domains = [
        "人域", "天域", "荒域", "冥域", "魔域", "虚域", "海域", "源域", "永恒域"
    ]

    # 定义文化维度
    dimensions = [
        "神话与宗教", "权力与法律", "经济与技术",
        "家庭与教育", "仪式与日常", "艺术与娱乐"
    ]

    # 实体类型模板
    entity_templates = {
        "组织机构": [
            "天命王朝", "祭司议会", "法则法庭", "链部", "天阁", "源议会",
            "荒族联盟", "野兽公会", "冥司殿", "灵魂议会", "断链教",
            "魔主联盟", "虚影议会", "时空守卫", "海域联邦", "深海议会"
        ],
        "重要概念": [
            "法则链", "链籍", "环印", "断链术", "源能", "链力",
            "血契", "灵链", "时链", "虚链", "海链", "永恒链"
        ],
        "文化物品": [
            "链票", "源能晶", "断链刃", "镇魂器", "时空罗盘", "海神珠",
            "野兽图腾", "冥界钥匙", "虚空石", "永恒印记"
        ],
        "仪式活动": [
            "裂世夜", "归环礼", "天启节", "源始祭", "荒猎节", "冥渡仪",
            "断链仪", "虚行礼", "海潮祭", "永恒誓"
        ],
        "身份制度": [
            "链籍三等制", "天阶序列", "荒族血统", "冥界等级", "魔印分级",
            "虚位认定", "海域品级", "源脉传承", "永恒印记"
        ],
        "货币体系": [
            "链票", "源能晶", "荒石", "冥币", "魔晶", "虚金",
            "海贝", "源币", "永恒币"
        ],
        "技术工艺": [
            "锻链术", "环铸法", "源技", "野技", "冥工", "断链技",
            "虚工", "海技", "永恒工艺"
        ]
    }

    entity_counter = 0
    all_entities = []

    # 为每个域生成文化数据
    for domain in domains:
        domain_data = {}

        for dimension in dimensions:
            entities = []
            entity_count = 2 if domain in ["源域", "永恒域"] else 3  # 部分域较少实体

            for i in range(entity_count):
                if entity_counter >= 109:
                    break

                # 选择实体类型
                entity_type = list(entity_templates.keys())[entity_counter % len(entity_templates)]
                type_templates = entity_templates[entity_type]

                # 生成实体
                entity = {
                    "name": f"{type_templates[entity_counter % len(type_templates)]}{domain}分支" if entity_counter > 20 else type_templates[entity_counter % len(type_templates)],
                    "type": entity_type,
                    "description": f"{domain}的{dimension}体系中的重要{entity_type}，承载着该域的文化传统和价值观念。",
                    "characteristics": {
                        "权威等级": f"{(entity_counter % 10) + 1}级",
                        "影响范围": domain,
                        "建立时间": f"法则历{1000 + (entity_counter * 50)}年"
                    },
                    "functions": [
                        f"维护{domain}的{dimension}秩序",
                        f"传承{domain}文化传统",
                        f"协调跨域关系"
                    ]
                }

                entities.append(entity)
                all_entities.append({**entity, "domain": domain, "dimension": dimension})
                entity_counter += 1

                if entity_counter >= 109:
                    break

            domain_data[dimension] = {
                "summary": f"{domain}的{dimension}体系深受法则链影响，形成了独特的文化传统。",
                "content": f"在{domain}中，{dimension}体系以法则链为核心，建立了完整的文化框架。该体系不仅影响着域内居民的日常生活，也与其他域保持着复杂的互动关系。",
                "key_elements": [entity["name"] for entity in entities],
                "entities": entities
            }

            if entity_counter >= 109:
                break

        large_dataset["domain_cultures"][domain] = domain_data

        if entity_counter >= 109:
            break

    # 生成28个跨域关系
    relations = [
        {"source_entity": "天命王朝", "target_entity": "祭司议会", "relationship_type": "控制", "strength": 0.9,
         "description": "天命王朝对祭司议会拥有行政控制权", "context": "政治统治关系"},
        {"source_entity": "天阁", "target_entity": "链部", "relationship_type": "合作", "strength": 0.85,
         "description": "天阁与链部在法则管理上密切合作", "context": "行政协作关系"},
        {"source_entity": "法则链", "target_entity": "链籍", "relationship_type": "包含", "strength": 0.95,
         "description": "法则链的知识被记录在链籍中", "context": "知识存储关系"},
        {"source_entity": "断链教", "target_entity": "魔主联盟", "relationship_type": "敌对", "strength": 0.8,
         "description": "断链教与魔主联盟存在根本理念冲突", "context": "意识形态对立"},
        {"source_entity": "海域联邦", "target_entity": "深海议会", "relationship_type": "包含", "strength": 0.9,
         "description": "深海议会是海域联邦的重要组成部分", "context": "组织结构关系"},
        {"source_entity": "荒族联盟", "target_entity": "野兽公会", "relationship_type": "合作", "strength": 0.75,
         "description": "荒族联盟与野兽公会在资源开发上合作", "context": "经济合作关系"},
        {"source_entity": "冥司殿", "target_entity": "灵魂议会", "relationship_type": "控制", "strength": 0.88,
         "description": "冥司殿对灵魂议会拥有管辖权", "context": "行政管理关系"},
        {"source_entity": "虚影议会", "target_entity": "时空守卫", "relationship_type": "合作", "strength": 0.82,
         "description": "虚影议会与时空守卫共同维护空间稳定", "context": "职能协作关系"}
    ]

    # 扩展到28个关系
    base_relations = len(relations)
    for i in range(28 - base_relations):
        # 随机组合实体生成更多关系
        source_entity = all_entities[i % len(all_entities)]
        target_entity = all_entities[(i + 15) % len(all_entities)]

        if source_entity != target_entity:
            relation_types = ["关联", "影响", "依赖", "相似", "竞争"]
            relation_type = relation_types[i % len(relation_types)]

            relations.append({
                "source_entity": source_entity["name"],
                "target_entity": target_entity["name"],
                "relationship_type": relation_type,
                "strength": 0.6 + (i % 4) * 0.1,
                "description": f"{source_entity['name']}与{target_entity['name']}之间存在{relation_type}关系",
                "context": f"{source_entity['domain']}-{target_entity['domain']}跨域关系"
            })

    large_dataset["cross_domain_relations"] = relations[:28]

    # 生成概念词典
    concept_dictionary = [
        {"term": "法则链", "definition": "连接世界本源的神圣纽带，修炼者的力量源泉",
         "category": "核心概念", "domain": "通用", "importance": 10},
        {"term": "链籍", "definition": "记录法则链知识的神圣文献",
         "category": "知识载体", "domain": "天域", "importance": 9},
        {"term": "环印", "definition": "标记身份和权限的神秘印记",
         "category": "身份标识", "domain": "人域", "importance": 8},
        {"term": "断链术", "definition": "破坏法则链结构的禁忌法术",
         "category": "禁忌技术", "domain": "魔域", "importance": 7},
        {"term": "源能", "definition": "法则链的原始能量形态",
         "category": "能量概念", "domain": "源域", "importance": 9}
    ]

    large_dataset["concept_dictionary"] = concept_dictionary

    logger.info(f"生成大规模数据集: {entity_counter} 个实体, {len(relations)} 个关系")
    return large_dataset


async def import_large_cultural_data():
    """导入大规模文化数据"""

    start_time = time.time()
    logger.info("开始大规模文化数据导入...")

    try:
        # 初始化系统组件
        from src.database.connection_manager import DatabaseManager
        from src.database.cultural_batch_manager import CulturalDataBatchManager
        from src.database.repositories.cultural_framework_repository import CulturalFrameworkRepository

        # 建立数据库连接
        connection_manager = DatabaseManager()
        await connection_manager.initialize()

        # 初始化仓库和批量管理器
        repository = CulturalFrameworkRepository(connection_manager)
        await repository.initialize()

        batch_manager = CulturalDataBatchManager(repository)

        # 生成大规模数据集
        logger.info("生成大规模文化数据集...")
        dataset = generate_large_cultural_dataset()

        # 执行批量导入
        logger.info("开始批量导入数据...")
        task_id = await batch_manager.import_cultural_framework_analysis(
            novel_id=UUID(NOVEL_ID),
            analysis_data=dataset,
            task_name="大规模文化数据导入 - 109实体28关系"
        )

        # 获取导入统计
        stats = batch_manager.get_processing_statistics()
        import_time = time.time() - start_time

        # 输出结果
        logger.info("="*60)
        logger.info("大规模文化数据导入完成")
        logger.info("="*60)
        logger.info(f"任务ID: {task_id}")
        logger.info(f"总用时: {import_time:.2f} 秒")
        logger.info(f"导入统计:")
        logger.info(f"  - 总处理数: {stats['total_processed']}")
        logger.info(f"  - 成功数: {stats['successful']}")
        logger.info(f"  - 失败数: {stats['failed']}")
        logger.info(f"  - 警告数: {len(stats['warnings'])}")
        logger.info(f"  - 文化框架创建: {stats.get('frameworks_created', 0)}")
        logger.info(f"  - 实体创建: {sum(stats.get('entities_by_type', {}).values())}")
        logger.info(f"  - 关系创建: {stats.get('relations_created', 0)}")

        if stats['warnings']:
            logger.info("警告信息:")
            for warning in stats['warnings']:
                logger.info(f"  - {warning}")

        # 验证导入结果
        logger.info("\n验证导入结果...")
        novel_stats = await repository.get_novel_statistics(UUID(NOVEL_ID))

        pg_stats = novel_stats["postgresql_stats"]
        logger.info("PostgreSQL统计:")
        logger.info(f"  - 文化框架: {pg_stats['framework_count']}")
        logger.info(f"  - 文化实体: {pg_stats['entity_count']}")
        logger.info(f"  - 实体关系: {pg_stats['relation_count']}")
        logger.info(f"  - 跨域关系: {pg_stats['cross_domain_relations']}")
        logger.info(f"  - 平均实体置信度: {pg_stats['avg_entity_confidence']:.3f}")

        # 关闭连接
        await connection_manager.close()

        return {
            "success": True,
            "import_time": import_time,
            "statistics": stats,
            "novel_statistics": novel_stats
        }

    except Exception as e:
        logger.error(f"大规模数据导入失败: {e}")
        if 'connection_manager' in locals():
            await connection_manager.close()
        raise


async def main():
    """主函数"""
    try:
        result = await import_large_cultural_data()

        if result["success"]:
            print(f"\n✅ 大规模文化数据导入成功!")
            print(f"导入用时: {result['import_time']:.2f} 秒")
            print(f"成功导入: {result['statistics']['successful']} 项")
            print(f"实体总数: {sum(result['statistics'].get('entities_by_type', {}).values())}")
            print(f"关系总数: {result['statistics'].get('relations_created', 0)}")
        else:
            print(f"\n❌ 数据导入失败")

    except Exception as e:
        print(f"\n❌ 导入过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())