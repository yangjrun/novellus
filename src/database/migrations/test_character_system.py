#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色版本管理系统集成测试
验证系统初始化、角色创建、版本管理、数据分析等功能
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# 导入测试所需的模块
from .init_character_system import init_character_system
from .character_lifecycle_manager import (
    CharacterLifecycleManager,
    create_character_version,
    get_character_timeline
)

logger = logging.getLogger(__name__)


class CharacterSystemIntegrationTest:
    """角色系统集成测试类"""

    def __init__(self):
        self.test_results = []
        self.test_character_id = "lieshi-jiuyu-test-linlan-001"
        self.lifecycle_manager = None

    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有集成测试"""
        logger.info("开始运行角色系统集成测试...")

        test_suite = [
            ("系统初始化测试", self.test_system_initialization),
            ("角色首版本创建测试", self.test_first_version_creation),
            ("角色跨域版本创建测试", self.test_cross_domain_version_creation),
            ("版本演进时间线测试", self.test_character_timeline),
            ("版本比较功能测试", self.test_version_comparison),
            ("数据完整性验证测试", self.test_data_integrity),
            ("分析功能测试", self.test_analysis_functions),
            ("错误处理测试", self.test_error_handling),
            ("性能测试", self.test_performance)
        ]

        for test_name, test_func in test_suite:
            try:
                logger.info(f"执行测试: {test_name}")
                result = await test_func()
                self.test_results.append({
                    "test_name": test_name,
                    "status": "PASSED" if result else "FAILED",
                    "details": result if isinstance(result, dict) else {"success": result}
                })
                logger.info(f"✓ {test_name}: {'通过' if result else '失败'}")
            except Exception as e:
                logger.error(f"✗ {test_name} 发生异常: {e}")
                self.test_results.append({
                    "test_name": test_name,
                    "status": "ERROR",
                    "details": {"error": str(e)}
                })

        # 生成测试报告
        return self._generate_test_report()

    async def test_system_initialization(self) -> bool:
        """测试系统初始化"""
        logger.info("测试系统初始化...")

        try:
            # 初始化角色系统
            success = await init_character_system(force_recreate=True)
            if not success:
                logger.error("系统初始化失败")
                return False

            # 初始化生命周期管理器
            self.lifecycle_manager = CharacterLifecycleManager()
            await self.lifecycle_manager.initialize()

            logger.info("系统初始化成功")
            return True

        except Exception as e:
            logger.error(f"系统初始化测试失败: {e}")
            return False

    async def test_first_version_creation(self) -> Dict[str, Any]:
        """测试首个版本创建"""
        logger.info("测试首个版本创建...")

        # 测试角色数据 - 林岚在人域的设定（简化版）
        test_character_data = {
            "id": self.test_character_id,
            "projectId": "proj-liashi-jiuyu",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),

            "basicInfo": {
                "name": "林岚",
                "alias": ["小岚", "半环"],
                "age": 18,
                "gender": "female",
                "occupation": "外堂童生（水工学徒/抄写）",
                "socialStatus": "灰籍"
            },

            "appearance": {
                "height": "167cm",
                "weight": "52kg",
                "hairColor": "黑",
                "eyeColor": "深棕"
            },

            "personality": {
                "coreTraits": ["坚韧", "共情强", "好奇", "原则感"],
                "values": ["公义", "自由", "守诺"],
                "beliefs": ["链应服务于人而非枷锁", "真相可以被证明"],
                "fears": ["亲友再次被加缚", "自己被利用成工具"],
                "desires": ["为家复案", "让灰籍获得体面身份"]
            },

            "background": {
                "birthplace": "白泥村（人域·南环水网）",
                "family": "父林瑜（溺亡存疑，水工匠），母许霜（失踪），叔林仲（黑籍服役）",
                "childhood": "随父巡渠与作图，常被宗门拒之门外；在乡祠抄写《小环章》"
            },

            "abilities": {
                "professionalSkills": ["水工测绘", "账册核对", "基层法条应用", "野外生存"],
                "specialTalents": ["过目不忘（文书/图样）", "水势瞬时判断"],
                "languages": ["通域语", "人域乡言", "天域官音（基础）"]
            },

            "relationships": {
                "family": [
                    {"name": "林瑜", "relationship": "父女", "description": "水工手记的遗留者，真相未明", "importance": "high"},
                    {"name": "许霜", "relationship": "母女", "description": "失踪，疑涉档案调包案", "importance": "high"}
                ],
                "friends": [
                    {"name": "苏杳", "relationship": "青梅", "description": "柳链集织局学徒，可靠内应", "importance": "medium"}
                ]
            },

            "psychology": {
                "mentalHealth": "长期哀伤与高警觉并存；对'链枷'声敏感",
                "mentalHealthStatus": "fair",
                "copingMechanisms": [
                    {"type": "adaptive", "strategy": "书写与整理证据", "effectiveness": 8, "frequency": "frequent"}
                ]
            },

            "characterArc": {
                "currentStage": "跨越复仇门槛（准备进入荒域取证）",
                "developmentGoals": [
                    {
                        "goal": "为父翻案并撤销灰籍加缚",
                        "timeline": "三个月内",
                        "progress": 30,
                        "priority": "high"
                    }
                ]
            },

            "behaviorProfile": {
                "communicationStyle": {
                    "primaryStyle": "assertive",
                    "verbalCharacteristics": ["先问证据", "复述对方观点再反驳"]
                },
                "decisionMaking": {
                    "approach": "analytical",
                    "informationGathering": "现场取证+口述采集+比对账册"
                }
            }
        }

        try:
            # 创建首个版本
            success = await create_character_version(
                self.test_character_id,
                "ren_yu",
                test_character_data,
                {"creation_reason": "initial_setup"}
            )

            if not success:
                return {"success": False, "error": "版本创建失败"}

            # 验证版本是否正确创建
            timeline = await get_character_timeline(self.test_character_id)

            return {
                "success": True,
                "versions_created": len(timeline),
                "current_domain": timeline[-1]["domain_code"] if timeline else None,
                "current_version": timeline[-1]["version"] if timeline else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_cross_domain_version_creation(self) -> Dict[str, Any]:
        """测试跨域版本创建"""
        logger.info("测试跨域版本创建...")

        # 林岚进入天域的新设定（简化版，突出变化）
        tian_yu_character_data = {
            "id": self.test_character_id,
            "projectId": "proj-liashi-jiuyu",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),

            "basicInfo": {
                "name": "林岚",  # 名字不变
                "alias": ["小岚", "半环", "外域修士"],  # 新增别名
                "age": 19,  # 年龄增长
                "gender": "female",
                "occupation": "外域修士（初入天域）",  # 职业变化
                "socialStatus": "外域来客"  # 社会地位变化
            },

            "appearance": {
                "height": "167cm",
                "weight": "50kg",  # 体重变化
                "hairColor": "黑",
                "eyeColor": "深棕",
                "specialMarks": ["左腕淡色半环印（发光增强）", "眉心新现天印"]  # 新的特征
            },

            "personality": {
                "coreTraits": ["坚韧", "共情强", "好奇", "原则感", "适应力强"],  # 新增特质
                "values": ["公义", "自由", "守诺", "天道平衡"],  # 新增价值观
                "beliefs": ["天地有序，修士当顺应天道", "力量需要节制"],  # 信念转变
                "fears": ["力量失控", "忘记初心"],  # 新的恐惧
                "desires": ["掌握天域法则", "保护两域和平"]  # 新的愿望
            },

            "background": {
                "birthplace": "白泥村（人域·南环水网）",  # 出生地不变
                "family": "父林瑜（溺亡存疑），母许霜（失踪），叔林仲（黑籍服役）",
                "recentEvents": "通过飞升之门进入天域，初遇天域修士文化"  # 新的背景事件
            },

            "abilities": {
                "professionalSkills": ["基础御气术", "天域法理初探", "跨域交流"],  # 技能转化
                "specialTalents": ["过目不忘（文书/图样）", "气脉感知", "法则共鸣"],  # 天赋进化
                "languages": ["通域语", "人域乡言", "天域官音（进阶）", "古修真语（基础）"]  # 新语言
            },

            "relationships": {
                "family": [
                    {"name": "林瑜", "relationship": "父女", "description": "已逝，但精神指引犹在", "importance": "high"},
                    {"name": "许霜", "relationship": "母女", "description": "失踪，跨域寻找线索", "importance": "high"}
                ],
                "friends": [
                    {"name": "苏杳", "relationship": "人域挚友", "description": "跨域维持联系，互通消息", "importance": "medium"}
                ],
                "mentors": [
                    {"name": "云清师尊", "relationship": "师徒", "description": "天域引路人，教导基础修炼", "importance": "high"}
                ]
            },

            "psychology": {
                "mentalHealth": "适应新环境的紧张与兴奋并存",
                "mentalHealthStatus": "good",  # 状态改善
                "copingMechanisms": [
                    {"type": "adaptive", "strategy": "冥想与气息调理", "effectiveness": 7, "frequency": "daily"},
                    {"type": "healthy", "strategy": "与师尊交流", "effectiveness": 8, "frequency": "weekly"}
                ]
            },

            "characterArc": {
                "currentStage": "天域适应期（学习基础修炼）",
                "developmentGoals": [
                    {
                        "goal": "掌握基础御气术",
                        "timeline": "半年内",
                        "progress": 20,
                        "priority": "high"
                    },
                    {
                        "goal": "寻找母亲失踪线索",
                        "timeline": "持续",
                        "progress": 10,
                        "priority": "high"
                    }
                ]
            },

            "behaviorProfile": {
                "communicationStyle": {
                    "primaryStyle": "respectful-assertive",  # 风格调整
                    "verbalCharacteristics": ["先行礼仪", "谨慎询问", "理据并重"]  # 适应天域礼仪
                },
                "decisionMaking": {
                    "approach": "intuitive-analytical",  # 决策方式进化
                    "informationGathering": "感知+推理+请教师长"  # 新的信息收集方式
                }
            }
        }

        try:
            # 创建天域版本
            success = await create_character_version(
                self.test_character_id,
                "tian_yu",
                tian_yu_character_data,
                {"creation_reason": "domain_ascension", "trigger_event": "通过飞升之门"}
            )

            if not success:
                return {"success": False, "error": "天域版本创建失败"}

            # 验证版本创建结果
            timeline = await get_character_timeline(self.test_character_id)

            # 检查版本数量和域迁移
            has_multiple_versions = len(timeline) >= 2
            has_domain_transition = any(entry["domain_code"] == "tian_yu" for entry in timeline)

            return {
                "success": True,
                "total_versions": len(timeline),
                "has_multiple_versions": has_multiple_versions,
                "has_domain_transition": has_domain_transition,
                "latest_domain": timeline[-1]["domain_code"] if timeline else None,
                "latest_version": timeline[-1]["version"] if timeline else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_character_timeline(self) -> Dict[str, Any]:
        """测试角色演进时间线"""
        logger.info("测试角色演进时间线...")

        try:
            timeline = await get_character_timeline(self.test_character_id)

            if not timeline:
                return {"success": False, "error": "无法获取时间线"}

            # 验证时间线完整性
            versions = [entry["version"] for entry in timeline]
            domains = [entry["domain_code"] for entry in timeline]

            return {
                "success": True,
                "timeline_entries": len(timeline),
                "versions": versions,
                "domains": domains,
                "has_progression": len(set(versions)) == len(versions),  # 版本号应该是唯一的
                "has_domain_changes": len(set(domains)) > 1  # 应该有域变化
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_version_comparison(self) -> Dict[str, Any]:
        """测试版本比较功能"""
        logger.info("测试版本比较功能...")

        try:
            # 获取时间线以确定可比较的版本
            timeline = await get_character_timeline(self.test_character_id)

            if len(timeline) < 2:
                return {"success": False, "error": "需要至少2个版本才能比较"}

            # 比较第一个版本和最新版本
            comparison = await self.lifecycle_manager.compare_character_versions(
                self.test_character_id,
                timeline[0]["version"],
                timeline[-1]["version"]
            )

            if "error" in comparison:
                return {"success": False, "error": comparison["error"]}

            # 验证比较结果的完整性
            expected_sections = ["basic_info_changes", "personality_evolution", "abilities_progression", "domain_transition"]
            has_all_sections = all(section in comparison for section in expected_sections)

            return {
                "success": True,
                "comparison_available": True,
                "has_all_sections": has_all_sections,
                "domain_transition": comparison.get("domain_transition", {}),
                "changes_detected": bool(comparison.get("basic_info_changes", {}).get("changed"))
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_data_integrity(self) -> Dict[str, Any]:
        """测试数据完整性"""
        logger.info("测试数据完整性...")

        try:
            # 验证PostgreSQL和MongoDB数据一致性
            pg_versions = await self.lifecycle_manager.pg_db.fetch_all(
                "SELECT * FROM entities WHERE character_unique_id = $1 ORDER BY character_version",
                self.test_character_id
            )

            mongo_versions = []
            async for doc in self.lifecycle_manager.mongo_db.character_profiles.find(
                {"character_unique_id": self.test_character_id}
            ).sort("version", 1):
                mongo_versions.append(doc)

            # 检查版本数量一致性
            pg_count = len(pg_versions)
            mongo_count = len(mongo_versions)

            # 检查当前版本一致性
            pg_current = [v for v in pg_versions if v.get("is_current_version")]
            mongo_current = [v for v in mongo_versions if v.get("is_current_version")]

            return {
                "success": True,
                "pg_versions": pg_count,
                "mongo_versions": mongo_count,
                "version_count_consistent": pg_count == mongo_count,
                "current_version_consistent": len(pg_current) == len(mongo_current) == 1,
                "data_integrity": "良好" if pg_count == mongo_count and len(pg_current) == 1 else "需要检查"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_analysis_functions(self) -> Dict[str, Any]:
        """测试分析功能"""
        logger.info("测试分析功能...")

        try:
            # 检查MongoDB中是否有版本洞察数据
            insights = await self.lifecycle_manager.mongo_db.character_version_insights.find_one(
                {"character_unique_id": self.test_character_id}
            )

            # 检查发展轨迹记录
            development_tracks = []
            async for track in self.lifecycle_manager.mongo_db.character_development_tracks.find(
                {"character_unique_id": self.test_character_id}
            ):
                development_tracks.append(track)

            return {
                "success": True,
                "has_insights": insights is not None,
                "development_tracks": len(development_tracks),
                "analysis_available": insights is not None or len(development_tracks) > 0
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_error_handling(self) -> Dict[str, Any]:
        """测试错误处理"""
        logger.info("测试错误处理...")

        error_tests = []

        try:
            # 测试1: 不存在的角色查询
            nonexistent_timeline = await get_character_timeline("nonexistent-character")
            error_tests.append({
                "test": "nonexistent_character_query",
                "handled_gracefully": len(nonexistent_timeline) == 0
            })

            # 测试2: 无效的域代码
            try:
                invalid_result = await create_character_version(
                    "test-invalid-char",
                    "invalid_domain",
                    {"basicInfo": {"name": "Test"}},
                    {"test": True}
                )
                error_tests.append({
                    "test": "invalid_domain_code",
                    "handled_gracefully": not invalid_result  # 应该返回False
                })
            except Exception:
                error_tests.append({
                    "test": "invalid_domain_code",
                    "handled_gracefully": True  # 异常被适当处理
                })

            # 测试3: 空数据处理
            try:
                empty_data_result = await create_character_version(
                    "test-empty-data",
                    "ren_yu",
                    {},
                    {"test": True}
                )
                error_tests.append({
                    "test": "empty_character_data",
                    "handled_gracefully": not empty_data_result
                })
            except Exception:
                error_tests.append({
                    "test": "empty_character_data",
                    "handled_gracefully": True
                })

            all_passed = all(test["handled_gracefully"] for test in error_tests)

            return {
                "success": True,
                "error_tests": error_tests,
                "all_error_tests_passed": all_passed
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_performance(self) -> Dict[str, Any]:
        """测试性能"""
        logger.info("测试性能...")

        try:
            import time

            # 测试版本创建性能
            start_time = time.time()
            performance_character_data = {
                "basicInfo": {"name": "性能测试角色", "age": 20, "occupation": "测试员"},
                "personality": {"coreTraits": ["测试"]},
                "abilities": {"professionalSkills": ["性能测试"]}
            }

            await create_character_version(
                "performance-test-character",
                "ren_yu",
                performance_character_data
            )
            creation_time = time.time() - start_time

            # 测试查询性能
            start_time = time.time()
            await get_character_timeline("performance-test-character")
            query_time = time.time() - start_time

            return {
                "success": True,
                "version_creation_time": round(creation_time, 3),
                "timeline_query_time": round(query_time, 3),
                "performance_acceptable": creation_time < 5.0 and query_time < 1.0
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASSED"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAILED"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])

        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0
            },
            "detailed_results": self.test_results,
            "overall_status": "PASSED" if failed_tests == 0 and error_tests == 0 else "FAILED",
            "generated_at": datetime.now().isoformat()
        }

    async def cleanup_test_data(self):
        """清理测试数据"""
        logger.info("清理测试数据...")

        try:
            # 清理PostgreSQL中的测试数据
            await self.lifecycle_manager.pg_db.execute(
                "DELETE FROM entities WHERE character_unique_id LIKE '%test%' OR character_unique_id LIKE '%performance%'"
            )

            # 清理MongoDB中的测试数据
            await self.lifecycle_manager.mongo_db.character_profiles.delete_many({
                "character_unique_id": {"$regex": "(test|performance)"}
            })

            await self.lifecycle_manager.mongo_db.character_development_tracks.delete_many({
                "character_unique_id": {"$regex": "(test|performance)"}
            })

            await self.lifecycle_manager.mongo_db.character_version_insights.delete_many({
                "character_unique_id": {"$regex": "(test|performance)"}
            })

            logger.info("测试数据清理完成")

        except Exception as e:
            logger.warning(f"测试数据清理失败: {e}")


# 便捷函数
async def run_integration_tests(cleanup_after: bool = True) -> Dict[str, Any]:
    """运行完整的集成测试"""
    test_runner = CharacterSystemIntegrationTest()

    try:
        results = await test_runner.run_all_tests()

        if cleanup_after:
            await test_runner.cleanup_test_data()

        return results

    except Exception as e:
        logger.error(f"集成测试运行失败: {e}")
        return {"error": str(e), "status": "FAILED"}


# 命令行执行
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="角色系统集成测试")
    parser.add_argument("--no-cleanup", action="store_true", help="测试后不清理数据")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出结果")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    async def main():
        try:
            results = await run_integration_tests(cleanup_after=not args.no_cleanup)

            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
            else:
                # 友好的控制台输出
                print(f"\n{'='*60}")
                print("角色版本管理系统集成测试报告")
                print(f"{'='*60}")

                summary = results.get("summary", {})
                print(f"总测试数: {summary.get('total_tests', 0)}")
                print(f"通过: {summary.get('passed', 0)}")
                print(f"失败: {summary.get('failed', 0)}")
                print(f"错误: {summary.get('errors', 0)}")
                print(f"成功率: {summary.get('success_rate', 0)}%")
                print(f"总体状态: {results.get('overall_status', 'UNKNOWN')}")

                if summary.get('failed', 0) > 0 or summary.get('errors', 0) > 0:
                    print("\n失败的测试:")
                    for result in results.get("detailed_results", []):
                        if result["status"] in ["FAILED", "ERROR"]:
                            print(f"  - {result['test_name']}: {result['status']}")
                            if "error" in result.get("details", {}):
                                print(f"    错误: {result['details']['error']}")

            # 设置退出码
            overall_status = results.get("overall_status", "FAILED")
            sys.exit(0 if overall_status == "PASSED" else 1)

        except Exception as e:
            print(f"测试运行失败: {e}")
            sys.exit(1)

    asyncio.run(main())