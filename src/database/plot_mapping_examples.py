"""
剧情功能映射系统使用示例
展示如何查询和使用地理实体的剧情功能
"""

import asyncio
from typing import List, Dict, Any
from .geographic_service import geographic_service
from .models.plot_mapping_models import (
    PlotFunctionQuery, FunctionCategory,
    CreatePlotMappingRequest, RecordPlotUsageRequest
)


class PlotMappingExamples:
    """剧情映射使用示例"""

    @staticmethod
    async def example_1_find_conflict_scenes():
        """示例1: 查找适合冲突的场景"""
        print("=== 示例1: 查找适合冲突的场景 ===")

        query = PlotFunctionQuery(
            novel_id=1,
            categories=[FunctionCategory.CONFLICT],  # 冲突类型
            min_drama_level=7,  # 高戏剧性
            domain_codes=["ren_yu", "tian_yu"],  # 人域和天域
            unused_only=True,  # 只要未使用的
            limit=10
        )

        response = await geographic_service.query_plot_functions(query)

        print(f"找到 {len(response.items)} 个适合冲突的场景:")
        for item in response.items[:5]:  # 显示前5个
            print(f"  • {item.entity_name} ({item.entity_type})")
            print(f"    功能: {', '.join(item.function_codes)}")
            print(f"    钩子: {item.hook_title}")
            print(f"    戏剧性: {item.hook_drama_level}/10")
            print()

        print(f"功能分布: {response.function_distribution}")
        print()

    @staticmethod
    async def example_2_plan_character_arc():
        """示例2: 按节点规划角色成长弧线"""
        print("=== 示例2: 按节点规划角色成长弧线 ===")

        # 查找起源节点的场景
        origin_query = PlotFunctionQuery(
            novel_id=1,
            node_codes=["①"],  # 起源节点
            domain_codes=["ren_yu"],  # 人域
            limit=5
        )

        origin_response = await geographic_service.query_plot_functions(origin_query)
        print("起源场景:")
        for item in origin_response.items:
            print(f"  • {item.entity_name}: {item.hook_title}")

        # 查找试炼节点的场景
        trial_query = PlotFunctionQuery(
            novel_id=1,
            node_codes=["③"],  # 试炼节点
            min_difficulty=3,
            limit=5
        )

        trial_response = await geographic_service.query_plot_functions(trial_query)
        print("\n试炼场景:")
        for item in trial_response.items:
            print(f"  • {item.entity_name}: {item.hook_title}")

        # 查找最终试炼节点的场景
        final_query = PlotFunctionQuery(
            novel_id=1,
            node_codes=["⑥"],  # 最终试炼节点
            min_drama_level=8,
            limit=5
        )

        final_response = await geographic_service.query_plot_functions(final_query)
        print("\n最终试炼场景:")
        for item in final_response.items:
            print(f"  • {item.entity_name}: {item.hook_title}")
        print()

    @staticmethod
    async def example_3_find_by_function():
        """示例3: 按功能类型查找场景"""
        print("=== 示例3: 按功能类型查找场景 ===")

        # 查找仪式触发器场景 (F1)
        ritual_query = PlotFunctionQuery(
            novel_id=1,
            function_codes=["F1"],  # 仪式触发器
            sort_by="hook_drama_level",
            sort_desc=True,
            limit=5
        )

        ritual_response = await geographic_service.query_plot_functions(ritual_query)
        print("仪式触发器场景:")
        for item in ritual_response.items:
            print(f"  • {item.entity_name} ({item.domain_code})")
            print(f"    钩子: {item.hook_title}")
            print(f"    戏剧性: {item.hook_drama_level}/10")

        # 查找资源据点场景 (F4)
        resource_query = PlotFunctionQuery(
            novel_id=1,
            function_codes=["F4"],  # 资源据点
            sort_by="difficulty_level",
            limit=5
        )

        resource_response = await geographic_service.query_plot_functions(resource_query)
        print("\n资源据点场景:")
        for item in resource_response.items:
            print(f"  • {item.entity_name}: {item.hook_title}")

        print()

    @staticmethod
    async def example_4_cross_domain_analysis():
        """示例4: 跨域分析"""
        print("=== 示例4: 跨域剧情功能分析 ===")

        domains = ["ren_yu", "tian_yu", "ling_yu", "huang_yu"]
        domain_names = {"ren_yu": "人域", "tian_yu": "天域", "ling_yu": "灵域", "huang_yu": "荒域"}

        for domain_code in domains:
            query = PlotFunctionQuery(
                novel_id=1,
                domain_codes=[domain_code],
                limit=100  # 获取该域的所有场景
            )

            response = await geographic_service.query_plot_functions(query)

            print(f"{domain_names[domain_code]}:")
            print(f"  总场景数: {response.total}")
            print(f"  平均戏剧性: {response.avg_drama_level}")
            print(f"  平均难度: {response.avg_difficulty_level}")

            # 分析功能分布
            top_functions = sorted(
                response.function_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

            print("  主要功能:")
            for func_code, count in top_functions:
                print(f"    {func_code}: {count}个场景")
            print()

    @staticmethod
    async def example_5_record_usage():
        """示例5: 记录剧情使用情况"""
        print("=== 示例5: 记录剧情使用情况 ===")

        # 首先查找一个场景
        query = PlotFunctionQuery(
            novel_id=1,
            entity_types=["landmark"],
            hook_urgency=[5],
            limit=1
        )

        response = await geographic_service.query_plot_functions(query)

        if response.items:
            # 模拟使用这个场景
            scene = response.items[0]
            print(f"使用场景: {scene.entity_name}")
            print(f"钩子: {scene.hook_title}")

            # 记录使用情况
            usage_request = RecordPlotUsageRequest(
                novel_id=1,
                mapping_id=scene.entity_id,  # 这里应该是mapping_id，示例中简化处理
                used_in_chapter="第三章",
                function_codes_used=scene.function_codes[:2],  # 使用前两个功能
                node_codes_used=scene.node_codes[:1],  # 使用第一个节点
                player_choices={
                    "choice_1": "选择直面冲突",
                    "choice_2": "采用智取策略"
                },
                outcome_achieved="成功化解危机",
                impact_level=4,
                session_id="session_001",
                notes="玩家表现出色，创造性地解决了问题"
            )

            result = await geographic_service.record_plot_usage(usage_request)
            if result.success:
                print("✓ 使用记录已保存")
            else:
                print(f"✗ 记录失败: {result.error}")
        print()

    @staticmethod
    async def example_6_stats_analysis():
        """示例6: 获取统计分析"""
        print("=== 示例6: 剧情功能使用统计 ===")

        stats_result = await geographic_service.get_plot_function_stats(novel_id=1)

        if stats_result.success:
            stats = stats_result.data
            print("功能使用统计:")
            print(f"{'功能代码':<6} {'功能名称':<12} {'场景数':<6} {'平均戏剧性':<8} {'使用次数':<6}")
            print("-" * 60)

            for stat in stats[:10]:  # 显示前10个
                print(f"{stat['function_code']:<6} {stat['function_name']:<12} "
                      f"{stat['entity_count']:<6} {stat['avg_drama_level']:<8.1f} "
                      f"{stat['total_usage_count']:<6}")
        print()

    @staticmethod
    async def example_7_create_custom_mapping():
        """示例7: 创建自定义剧情映射"""
        print("=== 示例7: 创建自定义剧情映射 ===")

        # 为一个新场景创建映射
        create_request = CreatePlotMappingRequest(
            novel_id=1,
            entity_id=1,  # 假设的实体ID
            function_codes=["F6", "F7"],  # 试炼场+盟友集散地
            node_codes=["③"],  # 试炼节点
            hook_title="新手村试炼",
            hook_description="主角在新手村接受基础训练，结识第一批伙伴",
            hook_urgency=2,
            hook_drama_level=4,
            difficulty_level=2,
            conflict_types=["技能考验", "社交挑战"],
            emotional_tags=["成长", "友谊"],
            background_context="这是主角踏出家门后的第一次正式试炼",
            escalation_paths={
                "success": "获得村民认可，解锁新区域",
                "failure": "需要额外训练，延迟进度"
            },
            resolution_options={
                "direct": "直接参加试炼",
                "preparation": "先做准备任务",
                "social": "通过社交关系获得帮助"
            }
        )

        result = await geographic_service.create_plot_mapping(create_request)
        if result.success:
            print(f"✓ 成功创建映射，ID: {result.data['mapping_id']}")
        else:
            print(f"✗ 创建失败: {result.error}")
        print()


async def run_all_examples():
    """运行所有示例"""
    print("剧情功能映射系统使用示例")
    print("=" * 50)
    print()

    examples = PlotMappingExamples()

    try:
        await examples.example_1_find_conflict_scenes()
        await examples.example_2_plan_character_arc()
        await examples.example_3_find_by_function()
        await examples.example_4_cross_domain_analysis()
        await examples.example_5_record_usage()
        await examples.example_6_stats_analysis()
        await examples.example_7_create_custom_mapping()

        print("所有示例运行完成！")

    except Exception as e:
        print(f"运行示例时出错: {str(e)}")


if __name__ == "__main__":
    asyncio.run(run_all_examples())