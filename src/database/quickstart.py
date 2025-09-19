"""
快速开始脚本 - 展示如何使用裂世九域数据库系统
包含完整的示例操作流程
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path

from .database_init import initialize_database
from .data_access import init_database, get_global_manager, get_novel_manager
from .batch_manager import get_batch_manager
from .models import *

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def quickstart_demo():
    """快速开始演示"""
    print("=" * 60)
    print("🌟 裂世九域·法则链纪元 数据库系统演示")
    print("=" * 60)

    try:
        # 第一步：初始化数据库
        print("\n📊 步骤 1: 初始化数据库...")
        init_result = await initialize_database()
        if init_result["overall_success"]:
            print("✅ 数据库初始化成功")
        else:
            print("❌ 数据库初始化失败")
            print(f"PostgreSQL: {init_result['postgresql']['message']}")
            print(f"MongoDB: {init_result['mongodb']['message']}")
            return

        # 第二步：连接数据库
        print("\n🔗 步骤 2: 连接数据库...")
        await init_database()
        global_manager = get_global_manager()
        print("✅ 数据库连接成功")

        # 第三步：创建项目
        print("\n📝 步骤 3: 创建项目...")
        project_data = ProjectCreate(
            name="lieshipan_jiuyu",
            title="裂世九域·法则链纪元",
            description="一个以法则链为核心修炼体系的玄幻小说世界",
            author="AI创作者",
            genre="玄幻修仙"
        )

        project = await global_manager.create_project(project_data)
        print(f"✅ 项目创建成功: {project.title} (ID: {project.id})")

        # 第四步：创建小说
        print("\n📖 步骤 4: 创建小说...")
        novel_data = NovelCreate(
            project_id=project.id,
            name="volume_1",
            title="第一卷：初入九域",
            description="主角初入裂世九域的冒险故事",
            volume_number=1
        )

        novel = await global_manager.create_novel(novel_data)
        print(f"✅ 小说创建成功: {novel.title} (ID: {novel.id})")

        # 获取小说管理器
        novel_manager = get_novel_manager(novel.id)

        # 第五步：创建世界观元素
        print("\n🌍 步骤 5: 创建世界观元素...")

        # 创建域
        domain_data = DomainCreate(
            novel_id=novel.id,
            name="人域",
            domain_type=DomainType.HUMAN_DOMAIN,
            description="九域中最适合人类生存的域界，法则相对温和",
            power_level=3,
            characteristics={
                "主要特征": "法则温和，适合修炼入门",
                "环境": "山川河流，四季分明",
                "种族": "人类为主，少数异族"
            }
        )

        domain = await novel_manager.create_domain(domain_data)
        print(f"✅ 域创建成功: {domain.name}")

        # 创建法则链
        law_chain_data = LawChainCreate(
            novel_id=novel.id,
            name="基础元素链",
            chain_type="元素系",
            description="最基础的元素法则链，包含金木水火土五种基本元素",
            power_level=2,
            rarity=ItemRarity.COMMON,
            effects={
                "基础效果": "掌控基本元素力量",
                "进阶效果": "元素融合与变化"
            }
        )

        law_chain = await novel_manager.create_law_chain(law_chain_data)
        print(f"✅ 法则链创建成功: {law_chain.name}")

        # 第六步：创建角色
        print("\n👥 步骤 6: 创建角色...")
        character_data = CharacterCreate(
            novel_id=str(novel.id),
            name="林轩",
            character_type="protagonist",
            basic_info={
                "full_name": "林轩",
                "age": 18,
                "gender": "男",
                "race": "人类",
                "birthplace": "人域·青山镇",
                "current_domain": "人域"
            },
            cultivation_info={
                "current_stage": "开脉初期",
                "cultivation_method": "基础吐纳术",
                "law_chains": ["基础元素链"],
                "special_abilities": ["五行感知"]
            },
            personality={
                "traits": ["坚韧不拔", "聪慧过人", "重情重义"],
                "goals": ["成为裂世者", "保护家人", "探索九域奥秘"]
            },
            tags=["主角", "人域", "五行修炼"]
        )

        character = await novel_manager.create_character(character_data)
        print(f"✅ 角色创建成功: {character.name}")

        # 第七步：创建内容批次
        print("\n📚 步骤 7: 创建内容批次...")
        batch_manager = await get_batch_manager(novel.id)

        # 创建批次系列
        batches = await batch_manager.create_batch_series(
            series_name="开篇世界观",
            batch_type=BatchType.WORLDBUILDING,
            batch_count=3,
            description="建立基础世界观设定",
            interval_days=3
        )

        print(f"✅ 批次系列创建成功: 共 {len(batches)} 个批次")

        # 第八步：创建内容段落
        print("\n✍️ 步骤 8: 创建内容段落...")
        first_batch = batches[0]

        # 创建第一个段落
        segment_data = ContentSegmentCreate(
            batch_id=first_batch.id,
            segment_type=SegmentType.NARRATIVE,
            title="九域概述",
            content="""
            裂世九域，乃是由九个不同法则主导的世界拼接而成的庞大世界。

            人域，以人为主体，法则温和，适合初学者修炼；
            天域，法则高远，仙气缭绕，乃修仙者向往之地；
            灵域，万物有灵，妖兽横行，充满野性力量；
            魔域，魔气森然，强者为尊，弱肉强食；
            仙域，超脱凡俗，仙人居所，法则玄妙；
            神域，神灵栖息，威严不可侵犯；
            虚域，虚无缥缈，空间法则至强；
            混沌域，一切法则混乱交织；
            永恒域，传说中的不朽之境。

            而连接这九域的，正是神秘的法则链系统。每一条法则链都蕴含着不同的力量，
            修炼者通过感悟和掌控法则链，可以获得超越凡人的力量。
            """,
            sequence_order=1,
            tags=["九域", "世界观", "法则链", "设定"]
        )

        segment = await novel_manager.create_content_segment(segment_data)
        print(f"✅ 内容段落创建成功: {segment.title} (字数: {segment.word_count})")

        # 第九步：获取统计信息
        print("\n📈 步骤 9: 获取统计信息...")
        stats = await novel_manager.get_novel_statistics()
        print("📊 小说统计信息:")
        print(f"   总字数: {stats['novel_info']['total_word_count']}")
        print(f"   章节数: {stats['novel_info']['chapter_count']}")
        print(f"   总批次: {stats['content_statistics']['total_batches']}")
        print(f"   角色数: {stats['world_statistics']['character_count']}")

        # 第十步：获取批次仪表板
        print("\n📋 步骤 10: 获取批次管理仪表板...")
        dashboard = await batch_manager.get_batch_dashboard()
        print("📊 批次管理仪表板:")
        print(f"   总批次数: {dashboard['overview']['total_batches']}")
        print(f"   完成率: {dashboard['overview']['completion_rate']:.1f}%")
        print(f"   总字数: {dashboard['overview']['total_word_count']}")

        # 第十一步：搜索演示
        print("\n🔍 步骤 11: 搜索演示...")
        search_results = await novel_manager.search_content("法则链")
        print(f"搜索 '法则链' 的结果:")
        print(f"   找到段落: {len(search_results.get('segments', []))} 个")
        print(f"   找到角色: {len(search_results.get('characters', []))} 个")

        print("\n🎉 演示完成！")
        print("=" * 60)
        print("数据库系统已成功初始化并创建了示例数据。")
        print("您现在可以使用 MCP 服务器工具来管理您的小说项目了。")
        print("=" * 60)

        return {
            "success": True,
            "project_id": str(project.id),
            "novel_id": str(novel.id),
            "message": "快速开始演示完成"
        }

    except Exception as e:
        logger.error(f"快速开始演示失败: {e}")
        print(f"\n❌ 演示过程中出现错误: {e}")
        return {
            "success": False,
            "message": f"演示失败: {e}"
        }


async def cleanup_demo_data():
    """清理演示数据"""
    try:
        print("\n🧹 清理演示数据...")
        from .database_init import reset_database

        result = await reset_database()
        if result["overall_success"]:
            print("✅ 演示数据清理完成")
        else:
            print("❌ 数据清理失败")

        return result

    except Exception as e:
        logger.error(f"清理演示数据失败: {e}")
        print(f"❌ 清理过程中出现错误: {e}")
        return {"success": False, "message": str(e)}


def print_usage_examples():
    """打印使用示例"""
    examples = """
🚀 裂世九域数据库系统使用示例

1. 项目管理：
   - 创建项目: create_project(name="project_name", title="项目标题")
   - 创建小说: create_novel(project_id="...", name="novel_name", title="小说标题")
   - 查看项目: list_projects()

2. 批次管理：
   - 创建批次: create_content_batch(novel_id="...", batch_name="批次名", batch_type="worldbuilding")
   - 批次系列: create_batch_series(novel_id="...", series_name="系列名", batch_count=5)
   - 管理面板: get_batch_dashboard(novel_id="...")

3. 世界观管理：
   - 创建域: create_domain(novel_id="...", name="人域", domain_type="人域")
   - 创建法则链: create_law_chain(novel_id="...", name="法则链名", chain_type="类型")
   - 创建角色: create_character(novel_id="...", name="角色名", character_type="protagonist")

4. 内容管理：
   - 创建段落: create_content_segment(batch_id="...", title="标题", content="内容")
   - 搜索内容: search_novel_content(novel_id="...", query="搜索词")
   - 统计信息: get_novel_statistics(novel_id="...")

5. 系统管理：
   - 初始化数据库: initialize_database_tool()
   - 检查状态: get_database_status()

支持的批次类型：worldbuilding, characters, plot, scenes, dialogue, revision
支持的域类型：人域, 天域, 灵域, 魔域, 仙域, 神域, 虚域, 混沌域, 永恒域
支持的角色类型：protagonist, antagonist, supporting, background, mentor, love_interest
"""
    print(examples)


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='裂世九域数据库系统快速开始')
    parser.add_argument('action', choices=['demo', 'cleanup', 'examples'],
                       help='操作类型: demo=运行演示, cleanup=清理数据, examples=显示使用示例')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.action == 'demo':
        result = await quickstart_demo()
        if result["success"]:
            print(f"\n✅ 演示成功完成")
            print(f"项目ID: {result.get('project_id')}")
            print(f"小说ID: {result.get('novel_id')}")
        else:
            print(f"\n❌ 演示失败: {result['message']}")

    elif args.action == 'cleanup':
        result = await cleanup_demo_data()
        if result["success"]:
            print("✅ 数据清理完成")
        else:
            print(f"❌ 数据清理失败: {result['message']}")

    elif args.action == 'examples':
        print_usage_examples()


if __name__ == "__main__":
    asyncio.run(main())