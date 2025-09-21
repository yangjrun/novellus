#!/usr/bin/env python3
"""
快速冲突分析系统集成验证脚本
简化版本，用于快速验证系统集成状态
"""

import asyncio
import json
import sys
from pathlib import Path
import asyncpg

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'novellus',
    'user': 'postgres',
    'password': 'postgres'
}

PROJECT_ID = "29c170c5-4a3e-4829-a242-74c1acb96453"
NOVEL_ID = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"

async def quick_test():
    """快速集成测试"""
    print("🚀 裂世九域·法则链纪元冲突分析系统 - 快速集成验证")
    print("=" * 60)

    try:
        # 连接数据库
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")

        # 1. 检查基础项目数据
        project_check = await conn.fetchval(
            "SELECT name FROM projects WHERE id = $1", PROJECT_ID
        )
        novel_check = await conn.fetchval(
            "SELECT name FROM novels WHERE id = $1", NOVEL_ID
        )

        if project_check and novel_check:
            print(f"✅ 项目验证: {project_check}")
            print(f"✅ 小说验证: {novel_check}")
        else:
            print("❌ 基础项目数据不存在")
            return False

        # 2. 检查冲突分析表结构
        conflict_tables = [
            'cross_domain_conflict_matrix',
            'conflict_entities',
            'conflict_relations',
            'conflict_story_hooks',
            'network_analysis_results',
            'ai_generated_content'
        ]

        table_status = {}
        for table in conflict_tables:
            exists = await conn.fetchval(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = $1",
                table
            )
            table_status[table] = exists > 0
            status = "✅" if exists > 0 else "❌"
            print(f"{status} 表结构: {table}")

        # 3. 检查数据完整性（如果表存在）
        if all(table_status.values()):
            print("\n📊 数据完整性检查:")

            # 统计各表数据量
            for table in conflict_tables:
                count = await conn.fetchval(
                    f"SELECT COUNT(*) FROM {table} WHERE novel_id = $1",
                    NOVEL_ID
                )
                print(f"   {table}: {count} 条记录")

            # 检查冲突矩阵
            matrix_count = await conn.fetchval(
                "SELECT COUNT(*) FROM cross_domain_conflict_matrix WHERE novel_id = $1",
                NOVEL_ID
            )

            if matrix_count > 0:
                print(f"\n🎭 冲突矩阵分析 ({matrix_count} 个冲突对):")
                conflicts = await conn.fetch("""
                    SELECT domain_a, domain_b, intensity
                    FROM cross_domain_conflict_matrix
                    WHERE novel_id = $1
                    ORDER BY intensity DESC
                """, NOVEL_ID)

                for conflict in conflicts:
                    print(f"   {conflict['domain_a']} ↔ {conflict['domain_b']}: 强度 {conflict['intensity']}")

            # 检查关系网络
            relation_count = await conn.fetchval(
                "SELECT COUNT(*) FROM conflict_relations WHERE novel_id = $1",
                NOVEL_ID
            )

            if relation_count > 0:
                print(f"\n🔗 关系网络: {relation_count} 个关系")

                # 分析关系类型分布
                relation_types = await conn.fetch("""
                    SELECT relation_type, COUNT(*) as count
                    FROM conflict_relations
                    WHERE novel_id = $1
                    GROUP BY relation_type
                    ORDER BY count DESC
                """, NOVEL_ID)

                for rel_type in relation_types:
                    print(f"   {rel_type['relation_type']}: {rel_type['count']} 个")

            # 检查剧情钩子
            hook_count = await conn.fetchval(
                "SELECT COUNT(*) FROM conflict_story_hooks WHERE novel_id = $1",
                NOVEL_ID
            )

            if hook_count > 0:
                print(f"\n🎬 剧情钩子: {hook_count} 个")

                # AI生成vs人工创作统计
                ai_stats = await conn.fetchrow("""
                    SELECT
                        COUNT(CASE WHEN is_ai_generated THEN 1 END) as ai_generated,
                        COUNT(CASE WHEN NOT is_ai_generated THEN 1 END) as human_created,
                        AVG(overall_score) as avg_score
                    FROM conflict_story_hooks
                    WHERE novel_id = $1
                """, NOVEL_ID)

                print(f"   AI生成: {ai_stats['ai_generated']} 个")
                print(f"   人工创作: {ai_stats['human_created']} 个")
                print(f"   平均评分: {ai_stats['avg_score']:.2f}")

        # 4. 快速性能测试
        print(f"\n⚡ 快速性能测试:")

        # 复杂查询测试
        import time
        start_time = time.time()

        complex_result = await conn.fetch("""
            SELECT
                ce.name,
                ce.entity_type,
                ce.strategic_value,
                COUNT(cr.id) as relation_count
            FROM conflict_entities ce
            LEFT JOIN conflict_relations cr ON (ce.id = cr.source_entity_id OR ce.id = cr.target_entity_id)
            WHERE ce.novel_id = $1
            GROUP BY ce.id, ce.name, ce.entity_type, ce.strategic_value
            ORDER BY ce.strategic_value DESC, relation_count DESC
            LIMIT 10
        """, NOVEL_ID)

        query_time = time.time() - start_time
        print(f"   复杂实体关系查询: {len(complex_result)} 个结果, 耗时 {query_time:.3f}秒")

        if complex_result:
            print("   📈 核心实体排名:")
            for i, entity in enumerate(complex_result[:5], 1):
                print(f"      {i}. {entity['name']} (价值: {entity['strategic_value']}, "
                      f"关系数: {entity['relation_count']})")

        # 5. 系统状态总结
        print(f"\n📋 系统集成状态总结:")

        total_records = sum([
            matrix_count if 'matrix_count' in locals() else 0,
            await conn.fetchval(f"SELECT COUNT(*) FROM conflict_entities WHERE novel_id = $1", NOVEL_ID),
            relation_count if 'relation_count' in locals() else 0,
            hook_count if 'hook_count' in locals() else 0
        ])

        print(f"   ✅ 数据库表结构: {'完整' if all(table_status.values()) else '不完整'}")
        print(f"   ✅ 总数据量: {total_records} 条记录")
        print(f"   ✅ 查询性能: {'优秀' if query_time < 0.1 else '良好' if query_time < 0.5 else '需优化'}")

        integration_status = all(table_status.values()) and total_records > 0
        status_icon = "🎉" if integration_status else "⚠️"
        status_text = "集成成功" if integration_status else "需要完善"

        print(f"\n{status_icon} 系统集成状态: {status_text}")

        await conn.close()
        return integration_status

    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        return False

async def main():
    """主函数"""
    success = await quick_test()

    if success:
        print("\n🚀 系统已准备就绪，可以开始使用冲突分析功能！")
        print("\n💡 使用建议:")
        print("   1. 使用 conflict_integration_demo.py 运行完整演示")
        print("   2. 通过 MCP API 进行数据查询和分析")
        print("   3. 查看生成的剧情钩子和网络分析结果")
    else:
        print("\n⚠️  系统集成未完成，请检查:")
        print("   1. 数据库连接是否正常")
        print("   2. 是否已运行数据库初始化脚本")
        print("   3. 是否已导入冲突分析数据")

    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)