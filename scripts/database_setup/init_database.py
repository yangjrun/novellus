#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化和项目创建脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.database_init import initialize_database
from database.data_access import init_database, get_global_manager, close_database
from database.models import ProjectCreate, NovelCreate, DomainCreate, DomainType
from uuid import UUID


async def setup_database_and_project():
    """初始化数据库并创建裂世九域项目"""

    print("=" * 60)
    print("🚀 开始初始化数据库和创建裂世九域项目")
    print("=" * 60)

    # 1. 初始化数据库结构
    print("\n📊 步骤1: 初始化数据库结构...")
    result = await initialize_database()

    if result["overall_success"]:
        print("✅ 数据库初始化成功！")
        print(f"  - PostgreSQL: {result['postgresql']['message']}")
        print(f"  - MongoDB: {result['mongodb']['message']}")
    else:
        print("❌ 数据库初始化失败")
        print(f"  - PostgreSQL: {result['postgresql']['message']}")
        print(f"  - MongoDB: {result['mongodb']['message']}")
        return

    # 2. 初始化数据库连接
    print("\n🔗 步骤2: 建立数据库连接...")
    await init_database()
    print("✅ 数据库连接成功！")

    # 3. 创建项目
    print("\n📚 步骤3: 创建裂世九域项目...")
    global_manager = get_global_manager()

    project_data = ProjectCreate(
        name="rift-nine-domains",
        title="裂世九域·法则链纪元",
        description="远古时代，世界本为一体，由完整的法则链运转。后因'裂世大劫'，法则链断裂成九段，化为九大域。",
        author="系统管理员",
        genre="东方玄幻"
    )

    project = await global_manager.create_project(project_data)
    print(f"✅ 项目创建成功！")
    print(f"  - 项目ID: {project.id}")
    print(f"  - 项目名称: {project.title}")

    # 4. 创建小说
    print("\n📖 步骤4: 创建小说实例...")
    novel_data = NovelCreate(
        project_id=project.id,
        name="main-story",
        title="裂世九域·主线",
        description="主角从人域奴籍觉醒，踏上打破法则链枷锁的道路",
        volume_number=1
    )

    novel = await global_manager.create_novel(novel_data)
    print(f"✅ 小说创建成功！")
    print(f"  - 小说ID: {novel.id}")
    print(f"  - 小说标题: {novel.title}")

    # 5. 初始化九大域数据
    print("\n🌍 步骤5: 初始化九大域...")
    from database.data_access import get_novel_manager
    novel_manager = get_novel_manager(str(novel.id))

    domains = [
        ("人域", DomainType.HUMAN_DOMAIN, "最低等之地，血脉残缺者的聚居区。主角出身之地", 1),
        ("天域", DomainType.HEAVEN_DOMAIN, "命运法则主宰之地，由'天命王朝'统治", 9),
        ("灵域", DomainType.SPIRIT_DOMAIN, "灵气丰饶，宗门林立，以'契链'为唯一通路", 7),
        ("荒域", DomainType.VOID_DOMAIN, "荒芜废墟，埋葬了无数'断链者'的残魂", 3),
        ("冥域", DomainType.IMMORTAL_DOMAIN, "死亡法则执掌，生死轮回的门户", 8),
        ("魔域", DomainType.DEMON_DOMAIN, "链条崩坏，孕育混乱与疯狂之地", 6),
        ("虚域", DomainType.GOD_DOMAIN, "与未来/幻象相关的链条之域。预言与幻境", 5),
        ("海域", DomainType.CHAOS_DOMAIN, "深海古族，掌控时空链片段", 4),
        ("源域", DomainType.ETERNAL_DOMAIN, "传说中的起源地，埋葬'完整法则链'", 10),
    ]

    for name, domain_type, description, power_level in domains:
        domain_data = DomainCreate(
            novel_id=novel.id,
            name=name,
            domain_type=domain_type,
            description=description,
            power_level=power_level
        )
        domain = await novel_manager.create_domain(domain_data)
        print(f"  ✅ {name} 创建成功 (力量等级: {power_level})")

    # 6. 关闭数据库连接
    await close_database()

    print("\n" + "=" * 60)
    print("🎉 初始化完成！裂世九域项目已成功创建！")
    print("=" * 60)
    print(f"\n📝 项目信息:")
    print(f"  - 项目ID: {project.id}")
    print(f"  - 小说ID: {novel.id}")
    print(f"  - 九大域: 已全部创建")
    print(f"\n下一步: 你可以开始导入更多文本内容了！")


if __name__ == "__main__":
    asyncio.run(setup_database_and_project())