#!/usr/bin/env python3
"""
文化框架数据完整性验证脚本
验证导入的114个实体和关系网络的完整性
"""

import asyncio
import logging
from uuid import UUID

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

NOVEL_ID = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"


async def verify_cultural_data_integrity():
    """验证文化数据完整性"""

    logger.info("开始验证文化数据完整性和关系网络...")

    try:
        # 初始化系统组件
        from src.database.connection_manager import DatabaseManager
        from src.database.repositories.cultural_framework_repository import CulturalFrameworkRepository

        # 建立数据库连接
        connection_manager = DatabaseManager()
        await connection_manager.initialize()

        repository = CulturalFrameworkRepository(connection_manager)
        await repository.initialize()

        verification_results = {
            "novel_statistics": {},
            "domain_distribution": {},
            "entity_type_distribution": {},
            "relation_network_analysis": {},
            "data_quality_metrics": {},
            "cross_domain_analysis": {},
            "integrity_checks": {}
        }

        # 1. 获取总体统计
        logger.info("1. 获取数据总体统计...")
        novel_stats = await repository.get_novel_statistics(UUID(NOVEL_ID))
        verification_results["novel_statistics"] = novel_stats

        pg_stats = novel_stats["postgresql_stats"]
        logger.info(f"   - 文化框架总数: {pg_stats['framework_count']}")
        logger.info(f"   - 文化实体总数: {pg_stats['entity_count']}")
        logger.info(f"   - 实体关系总数: {pg_stats['relation_count']}")
        logger.info(f"   - 跨域关系数: {pg_stats['cross_domain_relations']}")

        # 2. 域分布分析
        logger.info("2. 分析域分布...")
        async with connection_manager.postgres.get_connection() as conn:
            domain_distribution = await conn.fetch("""
                SELECT domain_type, COUNT(*) as entity_count
                FROM cultural_entities
                WHERE novel_id = $1 AND domain_type IS NOT NULL
                GROUP BY domain_type
                ORDER BY entity_count DESC
            """, UUID(NOVEL_ID))

            verification_results["domain_distribution"] = {
                row['domain_type']: row['entity_count']
                for row in domain_distribution
            }

            logger.info("   域分布:")
            for domain, count in verification_results["domain_distribution"].items():
                logger.info(f"     - {domain}: {count} 个实体")

        # 3. 实体类型分布
        logger.info("3. 分析实体类型分布...")
        async with connection_manager.postgres.get_connection() as conn:
            entity_type_distribution = await conn.fetch("""
                SELECT entity_type, COUNT(*) as count
                FROM cultural_entities
                WHERE novel_id = $1
                GROUP BY entity_type
                ORDER BY count DESC
            """, UUID(NOVEL_ID))

            verification_results["entity_type_distribution"] = {
                row['entity_type']: row['count']
                for row in entity_type_distribution
            }

            logger.info("   实体类型分布:")
            for entity_type, count in verification_results["entity_type_distribution"].items():
                logger.info(f"     - {entity_type}: {count} 个")

        # 4. 关系网络分析
        logger.info("4. 分析关系网络...")
        async with connection_manager.postgres.get_connection() as conn:
            # 关系类型分布
            relation_type_dist = await conn.fetch("""
                SELECT relation_type, COUNT(*) as count
                FROM cultural_relations
                WHERE novel_id = $1
                GROUP BY relation_type
                ORDER BY count DESC
            """, UUID(NOVEL_ID))

            # 实体连接度分析（出度和入度）
            entity_connectivity = await conn.fetch("""
                WITH outgoing_connections AS (
                    SELECT source_entity_id as entity_id, COUNT(*) as out_degree
                    FROM cultural_relations
                    WHERE novel_id = $1
                    GROUP BY source_entity_id
                ),
                incoming_connections AS (
                    SELECT target_entity_id as entity_id, COUNT(*) as in_degree
                    FROM cultural_relations
                    WHERE novel_id = $1
                    GROUP BY target_entity_id
                ),
                all_entities AS (
                    SELECT id as entity_id, name
                    FROM cultural_entities
                    WHERE novel_id = $1
                )
                SELECT
                    e.name,
                    COALESCE(o.out_degree, 0) as out_degree,
                    COALESCE(i.in_degree, 0) as in_degree,
                    COALESCE(o.out_degree, 0) + COALESCE(i.in_degree, 0) as total_degree
                FROM all_entities e
                LEFT JOIN outgoing_connections o ON e.entity_id = o.entity_id
                LEFT JOIN incoming_connections i ON e.entity_id = i.entity_id
                ORDER BY total_degree DESC
                LIMIT 20
            """, UUID(NOVEL_ID))

            verification_results["relation_network_analysis"] = {
                "relation_types": {row['relation_type']: row['count'] for row in relation_type_dist},
                "top_connected_entities": [
                    {
                        "name": row['name'],
                        "out_degree": row['out_degree'],
                        "in_degree": row['in_degree'],
                        "total_degree": row['total_degree']
                    } for row in entity_connectivity
                ]
            }

            logger.info("   关系类型分布:")
            for rel_type, count in verification_results["relation_network_analysis"]["relation_types"].items():
                logger.info(f"     - {rel_type}: {count} 个关系")

            logger.info("   连接度最高的实体 (Top 10):")
            for entity in verification_results["relation_network_analysis"]["top_connected_entities"][:10]:
                logger.info(f"     - {entity['name']}: 总连接度 {entity['total_degree']} (出: {entity['out_degree']}, 入: {entity['in_degree']})")

        # 5. 跨域关系分析
        logger.info("5. 分析跨域关系...")
        async with connection_manager.postgres.get_connection() as conn:
            cross_domain_relations = await conn.fetch("""
                SELECT
                    r.source_domain,
                    r.target_domain,
                    r.relation_type,
                    COUNT(*) as count,
                    AVG(r.strength) as avg_strength
                FROM cultural_relations r
                WHERE r.novel_id = $1 AND r.is_cross_domain = true
                GROUP BY r.source_domain, r.target_domain, r.relation_type
                ORDER BY count DESC
            """, UUID(NOVEL_ID))

            verification_results["cross_domain_analysis"] = {
                "relations": [
                    {
                        "source_domain": row['source_domain'],
                        "target_domain": row['target_domain'],
                        "relation_type": row['relation_type'],
                        "count": row['count'],
                        "avg_strength": float(row['avg_strength']) if row['avg_strength'] else 0.0
                    } for row in cross_domain_relations
                ]
            }

            logger.info("   跨域关系:")
            for rel in verification_results["cross_domain_analysis"]["relations"]:
                logger.info(f"     - {rel['source_domain']} -> {rel['target_domain']} ({rel['relation_type']}): {rel['count']} 个关系")

        # 6. 数据质量检查
        logger.info("6. 执行数据质量检查...")
        async with connection_manager.postgres.get_connection() as conn:
            # 检查空值和异常数据
            quality_checks = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_entities,
                    COUNT(CASE WHEN name IS NULL OR name = '' THEN 1 END) as empty_names,
                    COUNT(CASE WHEN description IS NULL OR description = '' THEN 1 END) as empty_descriptions,
                    COUNT(CASE WHEN domain_type IS NULL THEN 1 END) as null_domains,
                    AVG(confidence_score) as avg_confidence,
                    MIN(confidence_score) as min_confidence,
                    MAX(confidence_score) as max_confidence
                FROM cultural_entities
                WHERE novel_id = $1
            """, UUID(NOVEL_ID))

            # 检查关系完整性
            relation_integrity = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_relations,
                    COUNT(CASE WHEN source_entity_id IS NULL OR target_entity_id IS NULL THEN 1 END) as invalid_relations,
                    COUNT(CASE WHEN description IS NULL OR description = '' THEN 1 END) as empty_descriptions,
                    AVG(strength) as avg_strength,
                    COUNT(CASE WHEN is_cross_domain = true THEN 1 END) as cross_domain_count
                FROM cultural_relations
                WHERE novel_id = $1
            """, UUID(NOVEL_ID))

            verification_results["data_quality_metrics"] = {
                "entity_quality": {
                    "total_entities": quality_checks['total_entities'],
                    "empty_names": quality_checks['empty_names'],
                    "empty_descriptions": quality_checks['empty_descriptions'],
                    "null_domains": quality_checks['null_domains'],
                    "avg_confidence": float(quality_checks['avg_confidence']) if quality_checks['avg_confidence'] else 0.0,
                    "min_confidence": float(quality_checks['min_confidence']) if quality_checks['min_confidence'] else 0.0,
                    "max_confidence": float(quality_checks['max_confidence']) if quality_checks['max_confidence'] else 0.0
                },
                "relation_quality": {
                    "total_relations": relation_integrity['total_relations'],
                    "invalid_relations": relation_integrity['invalid_relations'],
                    "empty_descriptions": relation_integrity['empty_descriptions'],
                    "avg_strength": float(relation_integrity['avg_strength']) if relation_integrity['avg_strength'] else 0.0,
                    "cross_domain_count": relation_integrity['cross_domain_count']
                }
            }

            entity_quality = verification_results["data_quality_metrics"]["entity_quality"]
            relation_quality = verification_results["data_quality_metrics"]["relation_quality"]

            logger.info("   实体数据质量:")
            logger.info(f"     - 实体总数: {entity_quality['total_entities']}")
            logger.info(f"     - 空名称: {entity_quality['empty_names']}")
            logger.info(f"     - 空描述: {entity_quality['empty_descriptions']}")
            logger.info(f"     - 空域信息: {entity_quality['null_domains']}")
            logger.info(f"     - 平均置信度: {entity_quality['avg_confidence']:.3f}")

            logger.info("   关系数据质量:")
            logger.info(f"     - 关系总数: {relation_quality['total_relations']}")
            logger.info(f"     - 无效关系: {relation_quality['invalid_relations']}")
            logger.info(f"     - 平均强度: {relation_quality['avg_strength']:.3f}")
            logger.info(f"     - 跨域关系数: {relation_quality['cross_domain_count']}")

        # 7. 完整性检查
        logger.info("7. 执行完整性检查...")
        integrity_checks = {
            "has_entities": entity_quality['total_entities'] > 0,
            "has_relations": relation_quality['total_relations'] > 0,
            "has_cross_domain_relations": relation_quality['cross_domain_count'] > 0,
            "entities_have_names": entity_quality['empty_names'] == 0,
            "relations_are_valid": relation_quality['invalid_relations'] == 0,
            "good_confidence_scores": entity_quality['avg_confidence'] > 0.5,
            "has_multiple_domains": len(verification_results["domain_distribution"]) >= 3,
            "has_multiple_entity_types": len(verification_results["entity_type_distribution"]) >= 5
        }

        verification_results["integrity_checks"] = integrity_checks

        # 计算总体质量评分
        passed_checks = sum(integrity_checks.values())
        total_checks = len(integrity_checks)
        quality_score = (passed_checks / total_checks) * 100

        verification_results["overall_quality_score"] = quality_score

        logger.info("   完整性检查结果:")
        for check, passed in integrity_checks.items():
            status = "通过" if passed else "失败"
            logger.info(f"     - {check}: {status}")

        logger.info(f"\n总体质量评分: {quality_score:.1f}% ({passed_checks}/{total_checks} 检查通过)")

        # 关闭连接
        await connection_manager.close()

        return verification_results

    except Exception as e:
        logger.error(f"数据完整性验证失败: {e}")
        if 'connection_manager' in locals():
            await connection_manager.close()
        raise


async def main():
    """主函数"""
    try:
        results = await verify_cultural_data_integrity()

        print(f"\n文化数据完整性验证完成!")
        print(f"总体质量评分: {results['overall_quality_score']:.1f}%")
        print(f"实体总数: {results['data_quality_metrics']['entity_quality']['total_entities']}")
        print(f"关系总数: {results['data_quality_metrics']['relation_quality']['total_relations']}")
        print(f"跨域关系数: {results['data_quality_metrics']['relation_quality']['cross_domain_count']}")
        print(f"域覆盖数: {len(results['domain_distribution'])}")

    except Exception as e:
        print(f"验证过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())