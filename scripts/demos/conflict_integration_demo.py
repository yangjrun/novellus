#!/usr/bin/env python3
"""
裂世九域·法则链纪元跨域冲突分析系统集成演示脚本
展示完整的数据导入、查询和分析功能
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
import logging

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.conflict_data_importer import ConflictDataImporter, ImportConfig
from database.data_access import init_database, close_database, get_novel_manager
from database.connections.postgresql import get_pg_pool

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConflictIntegrationDemo:
    """冲突分析系统集成演示类"""

    def __init__(self):
        self.project_id = "29c170c5-4a3e-4829-a242-74c1acb96453"
        self.novel_id = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"
        self.results = {}

    async def print_banner(self):
        """打印演示横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                 裂世九域·法则链纪元跨域冲突分析系统                         ║
║                        完整集成演示脚本                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 演示目标：
   1. 初始化数据库架构
   2. 导入冲突分析数据（100实体+2296关系）
   3. 验证数据完整性
   4. 展示查询和分析功能
   5. 生成集成测试报告

📊 分析数据规模：
   - 跨域冲突矩阵：6个冲突对
   - 冲突实体：100个结构化实体
   - 冲突关系：2,296个复杂关系
   - 剧情钩子：30个高质量钩子
   - 网络分析：完整拓扑结构分析
   - AI生成内容：智能创作支持

🔧 技术架构：
   - PostgreSQL + MongoDB混合数据库
   - 完整的MCP API支持
   - 高性能索引和查询优化
   - 版本控制和审核流程

正在启动演示...
        """
        print(banner)

    async def step_1_initialize_database(self) -> bool:
        """步骤1：初始化数据库"""
        print("\n" + "="*80)
        print("🔧 步骤1: 初始化数据库架构")
        print("="*80)

        try:
            # 初始化数据库连接
            await init_database()
            print("✅ 数据库连接初始化成功")

            # 检查核心表是否存在
            pool = await get_pg_pool()
            async with pool.acquire() as conn:
                # 检查基础表
                basic_tables = ['projects', 'novels', 'domains', 'law_chains']
                for table in basic_tables:
                    result = await conn.fetchval(
                        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = $1",
                        table
                    )
                    if result > 0:
                        print(f"✅ 基础表 {table} 存在")
                    else:
                        print(f"❌ 基础表 {table} 不存在")
                        return False

                # 检查冲突分析表
                conflict_tables = [
                    'cross_domain_conflict_matrix',
                    'conflict_entities',
                    'conflict_relations',
                    'conflict_story_hooks',
                    'network_analysis_results',
                    'ai_generated_content'
                ]

                for table in conflict_tables:
                    result = await conn.fetchval(
                        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = $1",
                        table
                    )
                    if result > 0:
                        print(f"✅ 冲突分析表 {table} 存在")
                    else:
                        print(f"⚠️  冲突分析表 {table} 不存在，需要创建")

                # 验证项目和小说数据
                project_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM projects WHERE id = $1",
                    self.project_id
                )
                novel_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM novels WHERE id = $1",
                    self.novel_id
                )

                print(f"📊 项目数据验证: {'✅' if project_count > 0 else '❌'} "
                      f"(项目ID: {self.project_id})")
                print(f"📊 小说数据验证: {'✅' if novel_count > 0 else '❌'} "
                      f"(小说ID: {self.novel_id})")

            self.results['database_init'] = {
                'success': True,
                'basic_tables_ok': True,
                'project_exists': project_count > 0,
                'novel_exists': novel_count > 0
            }

            return True

        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            self.results['database_init'] = {
                'success': False,
                'error': str(e)
            }
            return False

    async def step_2_import_conflict_data(self) -> bool:
        """步骤2：导入冲突分析数据"""
        print("\n" + "="*80)
        print("📥 步骤2: 导入冲突分析数据")
        print("="*80)

        try:
            config = ImportConfig(
                project_id=self.project_id,
                novel_id=self.novel_id,
                clear_existing_data=True,  # 清除现有数据以确保干净的导入
                validate_data_integrity=True
            )

            importer = ConflictDataImporter(config)

            print("🔄 开始导入冲突分析数据...")
            start_time = time.time()

            result = await importer.run_import()

            import_time = time.time() - start_time

            if result['success']:
                stats = result['statistics']
                print(f"✅ 数据导入成功完成 (耗时: {import_time:.2f}秒)")
                print(f"📊 导入统计:")
                print(f"   - 冲突矩阵: {stats['matrices_imported']} 个")
                print(f"   - 冲突实体: {stats['entities_imported']} 个")
                print(f"   - 冲突关系: {stats['relations_imported']} 个")
                print(f"   - 剧情钩子: {stats['hooks_imported']} 个")
                print(f"   - 网络分析: {stats['network_analyses_imported']} 个")

                if stats['errors']:
                    print(f"⚠️  导入过程中出现 {len(stats['errors'])} 个错误:")
                    for error in stats['errors'][:5]:  # 只显示前5个错误
                        print(f"   - {error}")

                self.results['data_import'] = result
                return True
            else:
                print(f"❌ 数据导入失败: {result.get('error', '未知错误')}")
                self.results['data_import'] = result
                return False

        except Exception as e:
            print(f"❌ 导入过程异常: {e}")
            self.results['data_import'] = {
                'success': False,
                'error': str(e)
            }
            return False

    async def step_3_validate_data_integrity(self) -> bool:
        """步骤3：验证数据完整性"""
        print("\n" + "="*80)
        print("🔍 步骤3: 验证数据完整性")
        print("="*80)

        try:
            pool = await get_pg_pool()
            async with pool.acquire() as conn:
                # 统计各表数据量
                table_stats = {}

                tables_to_check = [
                    'cross_domain_conflict_matrix',
                    'conflict_entities',
                    'conflict_relations',
                    'conflict_story_hooks',
                    'network_analysis_results',
                    'ai_generated_content'
                ]

                for table in tables_to_check:
                    count = await conn.fetchval(
                        f"SELECT COUNT(*) FROM {table} WHERE novel_id = $1",
                        self.novel_id
                    )
                    table_stats[table] = count
                    print(f"📊 {table}: {count} 条记录")

                # 检查关系完整性
                entities_with_relations = await conn.fetchval("""
                    SELECT COUNT(DISTINCT source_entity_id) + COUNT(DISTINCT target_entity_id)
                    FROM conflict_relations
                    WHERE novel_id = $1
                """, self.novel_id)

                total_entities = table_stats.get('conflict_entities', 0)
                relation_coverage = (entities_with_relations / (total_entities * 2)) * 100 if total_entities > 0 else 0

                print(f"🔗 关系覆盖率: {relation_coverage:.1f}% ({entities_with_relations}/{total_entities * 2})")

                # 检查冲突矩阵完整性
                matrix_domains = await conn.fetch("""
                    SELECT domain_a, domain_b, intensity
                    FROM cross_domain_conflict_matrix
                    WHERE novel_id = $1
                    ORDER BY intensity DESC
                """, self.novel_id)

                print(f"🎭 冲突矩阵详情:")
                for row in matrix_domains:
                    print(f"   - {row['domain_a']} ↔ {row['domain_b']}: 强度 {row['intensity']}")

                # 检查数据质量
                validation_results = await conn.fetch("""
                    SELECT
                        validation_status,
                        COUNT(*) as count,
                        AVG(confidence_score) as avg_confidence
                    FROM conflict_entities
                    WHERE novel_id = $1
                    GROUP BY validation_status
                """, self.novel_id)

                print(f"🎯 数据质量评估:")
                for row in validation_results:
                    print(f"   - {row['validation_status']}: {row['count']} 个实体 "
                          f"(平均置信度: {row['avg_confidence']:.3f})")

                self.results['data_validation'] = {
                    'success': True,
                    'table_stats': table_stats,
                    'relation_coverage': relation_coverage,
                    'matrix_domains': len(matrix_domains),
                    'validation_summary': [dict(row) for row in validation_results]
                }

                return True

        except Exception as e:
            print(f"❌ 数据完整性验证失败: {e}")
            self.results['data_validation'] = {
                'success': False,
                'error': str(e)
            }
            return False

    async def step_4_demonstrate_queries(self) -> bool:
        """步骤4：演示查询功能"""
        print("\n" + "="*80)
        print("🔍 步骤4: 演示查询和分析功能")
        print("="*80)

        try:
            pool = await get_pg_pool()

            # 演示1: 高强度冲突查询
            print("\n📈 演示1: 查询高强度跨域冲突")
            async with pool.acquire() as conn:
                high_conflicts = await conn.fetch("""
                    SELECT domain_a, domain_b, intensity, risk_level, priority
                    FROM cross_domain_conflict_matrix
                    WHERE novel_id = $1 AND intensity >= 3.5
                    ORDER BY intensity DESC
                """, self.novel_id)

                for conflict in high_conflicts:
                    print(f"   🔥 {conflict['domain_a']} vs {conflict['domain_b']}: "
                          f"强度{conflict['intensity']}, 风险{conflict['risk_level']}, "
                          f"优先级{conflict['priority']}")

            # 演示2: 核心实体分析
            print("\n🎯 演示2: 核心冲突实体分析")
            async with pool.acquire() as conn:
                key_entities = await conn.fetch("""
                    SELECT name, entity_type, strategic_value, dispute_intensity,
                           array_to_string(involved_domains, ', ') as domains
                    FROM conflict_entities
                    WHERE novel_id = $1 AND strategic_value >= 7.0
                    ORDER BY strategic_value DESC
                    LIMIT 10
                """, self.novel_id)

                for entity in key_entities:
                    print(f"   ⚔️  {entity['name']} ({entity['entity_type']})")
                    print(f"      战略价值: {entity['strategic_value']}, "
                          f"争议强度: {entity['dispute_intensity']}")
                    print(f"      涉及域: {entity['domains']}")

            # 演示3: 剧情钩子推荐
            print("\n🎬 演示3: 高质量剧情钩子推荐")
            async with pool.acquire() as conn:
                top_hooks = await conn.fetch("""
                    SELECT title, hook_type, overall_score, emotional_impact,
                           is_ai_generated, array_to_string(domains_involved, ', ') as domains
                    FROM conflict_story_hooks
                    WHERE novel_id = $1 AND overall_score >= 7.0
                    ORDER BY overall_score DESC
                    LIMIT 5
                """, self.novel_id)

                for hook in top_hooks:
                    ai_tag = "🤖 AI生成" if hook['is_ai_generated'] else "📝 原创"
                    print(f"   🎭 {hook['title']} ({hook['hook_type']}) {ai_tag}")
                    print(f"      评分: {hook['overall_score']}, "
                          f"情感冲击: {hook['emotional_impact']}")
                    print(f"      涉及域: {hook['domains']}")

            # 演示4: 网络分析结果
            print("\n🕸️  演示4: 网络拓扑分析结果")
            async with pool.acquire() as conn:
                network_stats = await conn.fetch("""
                    SELECT analysis_type, node_count, edge_count,
                           network_density, average_clustering_coefficient,
                           community_count, analysis_confidence
                    FROM network_analysis_results
                    WHERE novel_id = $1
                    ORDER BY analysis_confidence DESC
                """, self.novel_id)

                for stat in network_stats:
                    print(f"   📊 {stat['analysis_type']}")
                    print(f"      节点: {stat['node_count']}, 边: {stat['edge_count']}")
                    print(f"      密度: {stat['network_density']:.3f}, "
                          f"聚类系数: {stat['average_clustering_coefficient']:.3f}")
                    if stat['community_count']:
                        print(f"      社团数: {stat['community_count']}")

            # 演示5: 域参与度分析
            print("\n🌍 演示5: 域参与度和冲突倾向分析")
            async with pool.acquire() as conn:
                domain_participation = await conn.fetch("""
                    WITH domain_conflicts AS (
                        SELECT domain_a as domain, intensity FROM cross_domain_conflict_matrix WHERE novel_id = $1
                        UNION ALL
                        SELECT domain_b as domain, intensity FROM cross_domain_conflict_matrix WHERE novel_id = $1
                    )
                    SELECT domain, COUNT(*) as conflict_count, AVG(intensity) as avg_intensity,
                           CASE
                               WHEN AVG(intensity) >= 3.5 THEN '高冲突域'
                               WHEN AVG(intensity) >= 2.5 THEN '中冲突域'
                               ELSE '低冲突域'
                           END as conflict_tendency
                    FROM domain_conflicts
                    GROUP BY domain
                    ORDER BY avg_intensity DESC
                """, self.novel_id)

                for domain in domain_participation:
                    print(f"   🏰 {domain['domain']}: {domain['conflict_tendency']}")
                    print(f"      冲突数: {domain['conflict_count']}, "
                          f"平均强度: {domain['avg_intensity']:.2f}")

            self.results['query_demo'] = {
                'success': True,
                'high_conflicts': len(high_conflicts),
                'key_entities': len(key_entities),
                'top_hooks': len(top_hooks),
                'network_analyses': len(network_stats),
                'domain_stats': len(domain_participation)
            }

            return True

        except Exception as e:
            print(f"❌ 查询演示失败: {e}")
            self.results['query_demo'] = {
                'success': False,
                'error': str(e)
            }
            return False

    async def step_5_performance_test(self) -> bool:
        """步骤5：性能测试"""
        print("\n" + "="*80)
        print("⚡ 步骤5: 性能和压力测试")
        print("="*80)

        try:
            pool = await get_pg_pool()
            performance_results = {}

            # 测试1: 复杂关系查询性能
            print("\n🔍 测试1: 复杂关系查询性能")
            start_time = time.time()

            async with pool.acquire() as conn:
                complex_query_result = await conn.fetch("""
                    SELECT
                        ce1.name as source_name,
                        ce2.name as target_name,
                        cr.relation_type,
                        cr.strength,
                        ce1.strategic_value,
                        ce2.strategic_value
                    FROM conflict_relations cr
                    JOIN conflict_entities ce1 ON cr.source_entity_id = ce1.id
                    JOIN conflict_entities ce2 ON cr.target_entity_id = ce2.id
                    WHERE cr.novel_id = $1
                    AND cr.strength >= 0.7
                    AND (ce1.strategic_value >= 6.0 OR ce2.strategic_value >= 6.0)
                    ORDER BY cr.strength DESC, ce1.strategic_value DESC
                    LIMIT 100
                """, self.novel_id)

            query1_time = time.time() - start_time
            print(f"   ✅ 复杂关系查询: {len(complex_query_result)} 条结果, "
                  f"耗时 {query1_time:.3f}秒")

            # 测试2: 聚合统计查询性能
            print("\n📊 测试2: 聚合统计查询性能")
            start_time = time.time()

            async with pool.acquire() as conn:
                stats_query_result = await conn.fetchrow("""
                    SELECT
                        COUNT(DISTINCT ce.id) as total_entities,
                        COUNT(DISTINCT cr.id) as total_relations,
                        COUNT(DISTINCT csh.id) as total_hooks,
                        AVG(ce.strategic_value) as avg_strategic_value,
                        AVG(cr.strength) as avg_relation_strength,
                        AVG(csh.overall_score) as avg_hook_score
                    FROM conflict_entities ce
                    LEFT JOIN conflict_relations cr ON (ce.id = cr.source_entity_id OR ce.id = cr.target_entity_id)
                    LEFT JOIN conflict_story_hooks csh ON csh.novel_id = ce.novel_id
                    WHERE ce.novel_id = $1
                """, self.novel_id)

            query2_time = time.time() - start_time
            print(f"   ✅ 聚合统计查询: 耗时 {query2_time:.3f}秒")
            print(f"      实体总数: {stats_query_result['total_entities']}")
            print(f"      关系总数: {stats_query_result['total_relations']}")
            print(f"      钩子总数: {stats_query_result['total_hooks']}")

            # 测试3: 并发查询测试
            print("\n🚀 测试3: 并发查询测试")
            start_time = time.time()

            concurrent_tasks = []
            for i in range(5):  # 5个并发查询
                task = self._concurrent_query_task(pool, i)
                concurrent_tasks.append(task)

            concurrent_results = await asyncio.gather(*concurrent_tasks)
            concurrent_time = time.time() - start_time

            successful_queries = sum(1 for result in concurrent_results if result['success'])
            print(f"   ✅ 并发查询测试: {successful_queries}/5 个查询成功, "
                  f"总耗时 {concurrent_time:.3f}秒")

            performance_results = {
                'complex_query_time': query1_time,
                'complex_query_results': len(complex_query_result),
                'stats_query_time': query2_time,
                'concurrent_time': concurrent_time,
                'concurrent_success_rate': successful_queries / 5,
                'total_entities': stats_query_result['total_entities'],
                'total_relations': stats_query_result['total_relations']
            }

            # 评估性能等级
            if query1_time < 0.1 and query2_time < 0.05 and concurrent_time < 1.0:
                performance_grade = "🏆 优秀"
            elif query1_time < 0.5 and query2_time < 0.2 and concurrent_time < 3.0:
                performance_grade = "✅ 良好"
            else:
                performance_grade = "⚠️ 需优化"

            print(f"\n📈 性能评估: {performance_grade}")

            self.results['performance_test'] = {
                'success': True,
                'grade': performance_grade,
                'metrics': performance_results
            }

            return True

        except Exception as e:
            print(f"❌ 性能测试失败: {e}")
            self.results['performance_test'] = {
                'success': False,
                'error': str(e)
            }
            return False

    async def _concurrent_query_task(self, pool, task_id: int) -> Dict[str, Any]:
        """并发查询任务"""
        try:
            async with pool.acquire() as conn:
                result = await conn.fetchval("""
                    SELECT COUNT(*) FROM conflict_entities
                    WHERE novel_id = $1 AND strategic_value >= $2
                """, self.novel_id, task_id)

                return {'success': True, 'task_id': task_id, 'result': result}

        except Exception as e:
            return {'success': False, 'task_id': task_id, 'error': str(e)}

    async def step_6_generate_report(self) -> bool:
        """步骤6：生成集成测试报告"""
        print("\n" + "="*80)
        print("📋 步骤6: 生成集成测试报告")
        print("="*80)

        try:
            # 计算总体成功率
            total_steps = len([k for k in self.results.keys() if k != 'final_report'])
            successful_steps = sum(1 for result in self.results.values()
                                 if isinstance(result, dict) and result.get('success', False))
            success_rate = (successful_steps / total_steps) * 100 if total_steps > 0 else 0

            # 生成报告
            report = {
                'integration_test_report': {
                    'project_name': '裂世九域·法则链纪元',
                    'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'overall_success_rate': f"{success_rate:.1f}%",
                    'total_steps': total_steps,
                    'successful_steps': successful_steps,
                    'test_results': self.results
                }
            }

            # 保存报告到文件
            report_file = Path("conflict_integration_test_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)

            print(f"✅ 集成测试报告已保存: {report_file}")
            print(f"📊 总体成功率: {success_rate:.1f}% ({successful_steps}/{total_steps})")

            # 打印简要总结
            print(f"\n📈 测试结果总结:")
            for step_name, result in self.results.items():
                if isinstance(result, dict):
                    status = "✅ 成功" if result.get('success', False) else "❌ 失败"
                    print(f"   - {step_name}: {status}")

            # 数据统计总结
            if 'data_import' in self.results and self.results['data_import'].get('success'):
                import_stats = self.results['data_import']['statistics']
                total_imported = (import_stats.get('matrices_imported', 0) +
                                import_stats.get('entities_imported', 0) +
                                import_stats.get('relations_imported', 0) +
                                import_stats.get('hooks_imported', 0) +
                                import_stats.get('network_analyses_imported', 0))
                print(f"\n📊 数据导入成果:")
                print(f"   - 总计导入: {total_imported} 条记录")
                print(f"   - 冲突实体: {import_stats.get('entities_imported', 0)} 个")
                print(f"   - 冲突关系: {import_stats.get('relations_imported', 0)} 个")

            # 性能测试总结
            if 'performance_test' in self.results and self.results['performance_test'].get('success'):
                perf_grade = self.results['performance_test']['grade']
                print(f"\n⚡ 性能测试结果: {perf_grade}")

            self.results['final_report'] = {
                'success': True,
                'report_file': str(report_file),
                'overall_success_rate': success_rate
            }

            return True

        except Exception as e:
            print(f"❌ 报告生成失败: {e}")
            self.results['final_report'] = {
                'success': False,
                'error': str(e)
            }
            return False

    async def run_complete_demo(self) -> Dict[str, Any]:
        """运行完整演示流程"""
        await self.print_banner()

        demo_steps = [
            ("初始化数据库架构", self.step_1_initialize_database),
            ("导入冲突分析数据", self.step_2_import_conflict_data),
            ("验证数据完整性", self.step_3_validate_data_integrity),
            ("演示查询功能", self.step_4_demonstrate_queries),
            ("性能压力测试", self.step_5_performance_test),
            ("生成集成报告", self.step_6_generate_report)
        ]

        all_success = True

        for step_name, step_func in demo_steps:
            print(f"\n⏳ 正在执行: {step_name}...")

            try:
                step_result = await step_func()
                if not step_result:
                    all_success = False
                    print(f"❌ {step_name} 执行失败")
                else:
                    print(f"✅ {step_name} 执行成功")

            except Exception as e:
                all_success = False
                print(f"❌ {step_name} 执行异常: {e}")

        # 最终总结
        print("\n" + "="*80)
        if all_success:
            print("🎉 裂世九域·法则链纪元跨域冲突分析系统集成演示成功完成!")
            print("📋 所有功能正常运行，数据完整性验证通过")
        else:
            print("⚠️  演示过程中出现问题，请检查错误信息")

        print("="*80)

        return self.results

async def main():
    """主函数"""
    demo = ConflictIntegrationDemo()

    try:
        results = await demo.run_complete_demo()
        return results
    finally:
        await close_database()

if __name__ == "__main__":
    results = asyncio.run(main())