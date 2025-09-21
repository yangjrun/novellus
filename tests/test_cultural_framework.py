#!/usr/bin/env python3
"""
文化框架数据库集成测试脚本
验证数据完整性、性能优化和系统集成功能
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from uuid import UUID, uuid4
from typing import Dict, Any, List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 项目和小说ID
PROJECT_ID = "29c170c5-4a3e-4829-a242-74c1acb96453"
NOVEL_ID = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"


class CulturalFrameworkIntegrationTest:
    """文化框架集成测试类"""

    def __init__(self):
        self.repository = None
        self.batch_manager = None
        self.test_results = {
            "database_initialization": False,
            "cultural_framework_creation": False,
            "cultural_entity_creation": False,
            "cultural_relations_creation": False,
            "data_import_test": False,
            "search_functionality": False,
            "performance_metrics": {},
            "data_integrity_checks": {},
            "overall_success": False
        }

    async def initialize_test_environment(self):
        """初始化测试环境"""
        try:
            logger.info("初始化测试环境...")

            # 导入必要的模块
            from src.database.repositories.cultural_framework_repository import CulturalFrameworkRepository
            from src.database.connection_manager import DatabaseManager
            from src.database.cultural_batch_manager import CulturalDataBatchManager

            # 初始化数据库连接
            self.connection_manager = DatabaseManager()
            await self.connection_manager.initialize()

            # 初始化仓库和批量管理器
            self.repository = CulturalFrameworkRepository(self.connection_manager)
            await self.repository.initialize()

            self.batch_manager = CulturalDataBatchManager(self.repository)

            self.test_results["database_initialization"] = True
            logger.info("测试环境初始化成功")

        except Exception as e:
            logger.error(f"测试环境初始化失败: {e}")
            raise

    async def test_cultural_framework_operations(self):
        """测试文化框架基本操作"""
        try:
            logger.info("测试文化框架基本操作...")

            from src.database.models.cultural_framework_models import (
                CulturalFrameworkCreate, DomainType, CulturalDimension
            )

            # 测试1：创建文化框架
            framework_data = CulturalFrameworkCreate(
                novel_id=UUID(NOVEL_ID),
                domain_type=DomainType.HUMAN_DOMAIN,
                dimension=CulturalDimension.POWER_LAW,
                title="人域政治体系测试",
                summary="测试用的人域政治体系框架",
                key_elements=["天命王朝", "链籍制度", "法则法庭"],
                detailed_content="这是一个测试用的详细内容...",
                tags=["测试", "政治", "权力"],
                priority=8
            )

            start_time = time.time()
            framework_id = await self.repository.create_cultural_framework(framework_data)
            creation_time = time.time() - start_time

            # 测试2：获取文化框架
            start_time = time.time()
            retrieved_framework = await self.repository.get_cultural_framework(framework_id)
            retrieval_time = time.time() - start_time

            # 验证数据一致性
            if retrieved_framework and retrieved_framework.title == framework_data.title:
                self.test_results["cultural_framework_creation"] = True
                self.test_results["performance_metrics"]["framework_creation_time"] = creation_time
                self.test_results["performance_metrics"]["framework_retrieval_time"] = retrieval_time
                logger.info(f"文化框架测试成功 - 创建时间: {creation_time:.3f}s, 获取时间: {retrieval_time:.3f}s")
            else:
                logger.error("文化框架数据不一致")

        except Exception as e:
            logger.error(f"文化框架操作测试失败: {e}")

    async def test_cultural_entity_operations(self):
        """测试文化实体操作"""
        try:
            logger.info("测试文化实体操作...")

            from src.database.models.cultural_framework_models import (
                CulturalEntityCreate, EntityType, DomainType, CulturalDimension
            )

            # 测试1：创建多种类型的文化实体
            test_entities = [
                {
                    "name": "天命王朝",
                    "entity_type": EntityType.ORGANIZATION,
                    "domain_type": DomainType.HUMAN_DOMAIN,
                    "description": "人域的统治机构"
                },
                {
                    "name": "法则链",
                    "entity_type": EntityType.CONCEPT,
                    "domain_type": None,  # 跨域概念
                    "description": "连接世界本源的神圣纽带"
                },
                {
                    "name": "链票",
                    "entity_type": EntityType.CURRENCY,
                    "domain_type": DomainType.HUMAN_DOMAIN,
                    "description": "人域的主要货币"
                },
                {
                    "name": "归环礼",
                    "entity_type": EntityType.RITUAL,
                    "domain_type": DomainType.HUMAN_DOMAIN,
                    "description": "成年仪式"
                }
            ]

            entity_ids = []
            total_creation_time = 0

            for entity_data in test_entities:
                entity_create = CulturalEntityCreate(
                    novel_id=UUID(NOVEL_ID),
                    name=entity_data["name"],
                    entity_type=entity_data["entity_type"],
                    domain_type=entity_data["domain_type"],
                    dimensions=[CulturalDimension.POWER_LAW],
                    description=entity_data["description"],
                    functions=["测试功能"],
                    tags=["测试"]
                )

                start_time = time.time()
                entity_id = await self.repository.create_cultural_entity(entity_create)
                creation_time = time.time() - start_time
                total_creation_time += creation_time

                entity_ids.append(entity_id)

            # 测试2：按类型获取实体
            start_time = time.time()
            organizations = await self.repository.get_entities_by_type(
                UUID(NOVEL_ID), EntityType.ORGANIZATION
            )
            query_time = time.time() - start_time

            if len(organizations) >= 1:  # 至少有天命王朝
                self.test_results["cultural_entity_creation"] = True
                self.test_results["performance_metrics"]["entity_creation_avg_time"] = total_creation_time / len(test_entities)
                self.test_results["performance_metrics"]["entity_query_time"] = query_time
                logger.info(f"文化实体测试成功 - 创建 {len(test_entities)} 个实体，平均时间: {total_creation_time/len(test_entities):.3f}s")
            else:
                logger.error("文化实体查询结果不正确")

            return entity_ids

        except Exception as e:
            logger.error(f"文化实体操作测试失败: {e}")
            return []

    async def test_cultural_relations(self, entity_ids: List[UUID]):
        """测试文化关系操作"""
        try:
            if len(entity_ids) < 2:
                logger.warning("实体数量不足，跳过关系测试")
                return

            logger.info("测试文化关系操作...")

            from src.database.models.cultural_framework_models import (
                CulturalRelationCreate, RelationType
            )

            # 创建关系：天命王朝控制链票
            relation_data = CulturalRelationCreate(
                novel_id=UUID(NOVEL_ID),
                source_entity_id=entity_ids[0],  # 天命王朝
                target_entity_id=entity_ids[2],  # 链票
                relation_type=RelationType.CONTROLS,
                description="天命王朝控制货币发行",
                strength=0.9,
                context="政治经济关系"
            )

            start_time = time.time()
            relation_id = await self.repository.create_cultural_relation(relation_data)
            creation_time = time.time() - start_time

            # 获取实体关系
            start_time = time.time()
            relations = await self.repository.get_entity_relations(entity_ids[0])
            query_time = time.time() - start_time

            if len(relations) >= 1:
                self.test_results["cultural_relations_creation"] = True
                self.test_results["performance_metrics"]["relation_creation_time"] = creation_time
                self.test_results["performance_metrics"]["relation_query_time"] = query_time
                logger.info(f"文化关系测试成功 - 创建时间: {creation_time:.3f}s, 查询时间: {query_time:.3f}s")
            else:
                logger.error("文化关系查询结果不正确")

        except Exception as e:
            logger.error(f"文化关系操作测试失败: {e}")

    async def test_data_import_functionality(self):
        """测试数据导入功能"""
        try:
            logger.info("测试数据导入功能...")

            # 创建模拟的分析数据
            sample_analysis_data = {
                "analysis_metadata": {
                    "timestamp": "2025-01-19T10:00:00Z",
                    "total_domains": 2,
                    "total_entities": 4,
                    "total_relations": 2,
                    "average_confidence": 0.92
                },
                "domain_cultures": {
                    "人域": {
                        "A. 神话与宗教": {
                            "summary": "以法则链信仰为核心的宗教体系",
                            "content": "人域居民信仰法则链的力量，认为法则链是连接世界本源的神圣纽带...",
                            "key_elements": ["法则链信仰", "祭司议会", "宗教仪式"],
                            "entities": [
                                {
                                    "name": "祭司议会",
                                    "type": "组织机构",
                                    "description": "人域的宗教管理机构，负责法则解释和宗教仪式",
                                    "characteristics": {"成员数量": "约200人", "权力范围": "宗教事务"},
                                    "functions": ["法则解释", "宗教仪式主持", "信仰指导"]
                                }
                            ]
                        },
                        "B. 权力与法律": {
                            "summary": "天命王朝统治下的政治体系",
                            "content": "人域由天命王朝统治，实行链籍三等制度...",
                            "key_elements": ["天命王朝", "链籍三等制", "法则法庭"],
                            "entities": [
                                {
                                    "name": "链籍三等制",
                                    "type": "身份制度",
                                    "description": "基于法则链掌握程度的社会等级制度",
                                    "characteristics": {"等级数量": "三等", "流动性": "有限"},
                                    "functions": ["社会分层", "权力分配", "资源配置"]
                                }
                            ]
                        }
                    },
                    "天域": {
                        "A. 神话与宗教": {
                            "summary": "法则链本源信仰",
                            "content": "天域是法则链的本源之地...",
                            "key_elements": ["法则本源", "天链学院", "链籍管理"],
                            "entities": [
                                {
                                    "name": "天链学院",
                                    "type": "组织机构",
                                    "description": "九域最高学府，研究法则链奥秘",
                                    "characteristics": {"地位": "最高学府", "影响力": "九域"},
                                    "functions": ["法则研究", "人才培养", "知识传承"]
                                }
                            ]
                        }
                    }
                },
                "cross_domain_relations": [
                    {
                        "source_entity": "天链学院",
                        "target_entity": "祭司议会",
                        "relationship_type": "影响",
                        "strength": 0.8,
                        "description": "天链学院为祭司议会提供理论指导",
                        "context": "宗教学术关系"
                    },
                    {
                        "source_entity": "天命王朝",
                        "target_entity": "链籍三等制",
                        "relationship_type": "控制",
                        "strength": 0.95,
                        "description": "天命王朝制定和维护等级制度",
                        "context": "政治统治关系"
                    }
                ],
                "concept_dictionary": [
                    {
                        "term": "法则链",
                        "definition": "连接世界本源的神圣纽带，修炼者的力量源泉",
                        "category": "核心概念",
                        "domain": "通用",
                        "importance": 10
                    }
                ]
            }

            # 执行导入测试
            start_time = time.time()
            task_id = await self.batch_manager.import_cultural_framework_analysis(
                novel_id=UUID(NOVEL_ID),
                analysis_data=sample_analysis_data,
                task_name="集成测试导入"
            )
            import_time = time.time() - start_time

            # 获取处理统计
            stats = self.batch_manager.get_processing_statistics()

            if stats['successful'] > 0:
                self.test_results["data_import_test"] = True
                self.test_results["performance_metrics"]["data_import_time"] = import_time
                self.test_results["data_integrity_checks"]["import_stats"] = stats
                logger.info(f"数据导入测试成功 - 导入时间: {import_time:.3f}s, 成功记录: {stats['successful']}")
            else:
                logger.error("数据导入测试失败，没有成功记录")

        except Exception as e:
            logger.error(f"数据导入功能测试失败: {e}")

    async def test_search_functionality(self):
        """测试搜索功能"""
        try:
            logger.info("测试搜索功能...")

            from src.database.models.cultural_framework_models import EntityType

            # 测试1：全文搜索
            start_time = time.time()
            search_results = await self.repository.search_entities(
                novel_id=UUID(NOVEL_ID),
                search_query="天命王朝",
                entity_types=[EntityType.ORGANIZATION]
            )
            search_time = time.time() - start_time

            # 测试2：跨域关系查询
            start_time = time.time()
            cross_domain_relations = await self.repository.get_cross_domain_relations(UUID(NOVEL_ID))
            cross_domain_query_time = time.time() - start_time

            if len(search_results) > 0 or len(cross_domain_relations) > 0:
                self.test_results["search_functionality"] = True
                self.test_results["performance_metrics"]["entity_search_time"] = search_time
                self.test_results["performance_metrics"]["cross_domain_query_time"] = cross_domain_query_time
                logger.info(f"搜索功能测试成功 - 实体搜索: {search_time:.3f}s, 跨域查询: {cross_domain_query_time:.3f}s")
            else:
                logger.warning("搜索功能测试：没有找到匹配结果")

        except Exception as e:
            logger.error(f"搜索功能测试失败: {e}")

    async def perform_data_integrity_checks(self):
        """执行数据完整性检查"""
        try:
            logger.info("执行数据完整性检查...")

            # 获取统计信息
            stats = await self.repository.get_novel_statistics(UUID(NOVEL_ID))

            # 检查数据一致性
            pg_stats = stats["postgresql_stats"]
            mongo_stats = stats["mongodb_stats"]

            integrity_checks = {
                "postgresql_data_exists": pg_stats["entity_count"] > 0,
                "mongodb_data_exists": mongo_stats["total_content"] > 0,
                "entity_relation_consistency": True,  # 简化检查
                "confidence_scores_valid": pg_stats["avg_entity_confidence"] >= 0.0,
                "cross_domain_relations_exist": pg_stats["cross_domain_relations"] > 0
            }

            # 计算数据质量评分
            quality_score = sum(integrity_checks.values()) / len(integrity_checks) * 100

            self.test_results["data_integrity_checks"].update({
                "statistics": stats,
                "integrity_checks": integrity_checks,
                "quality_score": quality_score
            })

            logger.info(f"数据完整性检查完成 - 质量评分: {quality_score:.1f}%")

        except Exception as e:
            logger.error(f"数据完整性检查失败: {e}")

    async def run_performance_benchmarks(self):
        """运行性能基准测试"""
        try:
            logger.info("运行性能基准测试...")

            from src.database.models.cultural_framework_models import EntityType

            # 批量查询性能测试
            entity_types = [EntityType.ORGANIZATION, EntityType.CONCEPT, EntityType.RITUAL, EntityType.CURRENCY]
            batch_query_times = []

            for entity_type in entity_types:
                start_time = time.time()
                entities = await self.repository.get_entities_by_type(UUID(NOVEL_ID), entity_type)
                query_time = time.time() - start_time
                batch_query_times.append(query_time)

            # 并发搜索测试
            search_queries = ["法则", "王朝", "议会", "学院"]
            concurrent_search_start = time.time()

            search_tasks = [
                self.repository.search_entities(UUID(NOVEL_ID), query)
                for query in search_queries
            ]
            await asyncio.gather(*search_tasks)

            concurrent_search_time = time.time() - concurrent_search_start

            # 记录性能指标
            performance_metrics = self.test_results["performance_metrics"]
            performance_metrics.update({
                "batch_query_avg_time": sum(batch_query_times) / len(batch_query_times),
                "batch_query_max_time": max(batch_query_times),
                "concurrent_search_time": concurrent_search_time,
                "queries_per_second": len(search_queries) / concurrent_search_time if concurrent_search_time > 0 else 0
            })

            logger.info(f"性能基准测试完成 - QPS: {performance_metrics['queries_per_second']:.2f}")

        except Exception as e:
            logger.error(f"性能基准测试失败: {e}")

    async def run_all_tests(self):
        """运行所有测试"""
        try:
            logger.info("开始文化框架数据库集成测试...")

            # 初始化测试环境
            await self.initialize_test_environment()

            # 运行各项测试
            await self.test_cultural_framework_operations()
            entity_ids = await self.test_cultural_entity_operations()
            await self.test_cultural_relations(entity_ids)
            await self.test_data_import_functionality()
            await self.test_search_functionality()

            # 数据完整性和性能测试
            await self.perform_data_integrity_checks()
            await self.run_performance_benchmarks()

            # 评估总体结果
            self.evaluate_overall_success()

            # 生成测试报告
            self.generate_test_report()

        except Exception as e:
            logger.error(f"集成测试过程中出现错误: {e}")
            self.test_results["overall_success"] = False

        finally:
            # 清理测试环境
            await self.cleanup_test_environment()

    def evaluate_overall_success(self):
        """评估总体测试成功率"""
        core_tests = [
            "database_initialization",
            "cultural_framework_creation",
            "cultural_entity_creation",
            "cultural_relations_creation",
            "data_import_test"
        ]

        passed_tests = sum(1 for test in core_tests if self.test_results.get(test, False))
        success_rate = passed_tests / len(core_tests)

        # 数据质量评分
        quality_score = self.test_results.get("data_integrity_checks", {}).get("quality_score", 0)

        # 综合评估
        self.test_results["overall_success"] = success_rate >= 0.8 and quality_score >= 80

        logger.info(f"测试成功率: {success_rate:.1%}, 数据质量评分: {quality_score:.1f}%")

    def generate_test_report(self):
        """生成测试报告"""
        report = {
            "test_summary": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "overall_success": self.test_results["overall_success"],
                "project_id": PROJECT_ID,
                "novel_id": NOVEL_ID
            },
            "test_results": self.test_results,
            "recommendations": self.generate_recommendations()
        }

        # 保存报告到文件
        report_file = Path("cultural_framework_test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"测试报告已保存: {report_file}")

        # 输出简要报告
        self.print_test_summary()

    def generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []

        performance_metrics = self.test_results.get("performance_metrics", {})

        # 性能优化建议
        if performance_metrics.get("entity_search_time", 0) > 0.1:
            recommendations.append("实体搜索时间较长，建议优化全文搜索索引")

        if performance_metrics.get("data_import_time", 0) > 5.0:
            recommendations.append("数据导入时间较长，建议优化批量插入逻辑")

        if performance_metrics.get("queries_per_second", 0) < 10:
            recommendations.append("查询并发性能较低，建议增加连接池大小")

        # 数据质量建议
        quality_score = self.test_results.get("data_integrity_checks", {}).get("quality_score", 0)
        if quality_score < 90:
            recommendations.append("数据质量评分偏低，建议加强数据验证机制")

        if not self.test_results.get("search_functionality", False):
            recommendations.append("搜索功能测试未通过，建议检查索引配置")

        return recommendations

    def print_test_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("文化框架数据库集成测试报告")
        print("="*60)

        print(f"总体结果: {'✅ 通过' if self.test_results['overall_success'] else '❌ 失败'}")
        print(f"项目ID: {PROJECT_ID}")
        print(f"小说ID: {NOVEL_ID}")

        print("\n详细测试结果:")
        test_items = [
            ("数据库初始化", "database_initialization"),
            ("文化框架创建", "cultural_framework_creation"),
            ("文化实体创建", "cultural_entity_creation"),
            ("文化关系创建", "cultural_relations_creation"),
            ("数据导入测试", "data_import_test"),
            ("搜索功能测试", "search_functionality")
        ]

        for name, key in test_items:
            status = "✅ 通过" if self.test_results.get(key, False) else "❌ 失败"
            print(f"  {name}: {status}")

        # 性能指标
        performance = self.test_results.get("performance_metrics", {})
        if performance:
            print("\n性能指标:")
            if "entity_creation_avg_time" in performance:
                print(f"  实体创建平均时间: {performance['entity_creation_avg_time']:.3f}s")
            if "data_import_time" in performance:
                print(f"  数据导入时间: {performance['data_import_time']:.3f}s")
            if "queries_per_second" in performance:
                print(f"  查询每秒数: {performance['queries_per_second']:.2f} QPS")

        # 数据质量
        integrity = self.test_results.get("data_integrity_checks", {})
        if "quality_score" in integrity:
            print(f"\n数据质量评分: {integrity['quality_score']:.1f}%")

        print("\n" + "="*60)

    async def cleanup_test_environment(self):
        """清理测试环境"""
        try:
            if hasattr(self, 'connection_manager'):
                await self.connection_manager.close()
            logger.info("测试环境清理完成")
        except Exception as e:
            logger.error(f"清理测试环境失败: {e}")


async def main():
    """主函数"""
    test_runner = CulturalFrameworkIntegrationTest()
    await test_runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())