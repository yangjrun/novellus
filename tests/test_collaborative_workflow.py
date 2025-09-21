#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试人工协作创作工作流
"""

import asyncio
import json
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.collaborative_workflow import (
    HumanAICollaborativeWorkflow,
    CreationSessionManager,
    ContentAnalyzer,
    UserInteractionInterface
)


async def test_workflow():
    """测试完整的人工协作工作流"""

    print("=" * 60)
    print("Novellus 人工协作创作工作流测试")
    print("=" * 60)

    # 测试数据
    novel_id = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"
    chapter_number = 17

    # 创建工作流实例（使用模拟的数据库管理器）
    workflow = HumanAICollaborativeWorkflow(novel_id)

    print("\n1. 生成创作Prompt")
    print("-" * 40)

    # 生成prompt
    formatted_prompt, prompt_components = await workflow.generate_prompt_for_user(
        chapter_number=chapter_number,
        scene_type="breakthrough",
        focus_characters=["林潜", "炎无极"],
        target_length=2000,
        style_preferences={
            "temperature": 0.85,
            "notes": "戏剧性强烈，描写细腻"
        }
    )

    print("生成的Prompt：")
    print(formatted_prompt[:500] + "...")  # 只显示前500字符

    print("\n" + "=" * 60)
    print("2. 模拟用户在Claude生成的内容")
    print("-" * 40)

    # 模拟生成的内容
    mock_content = """
    时间法则的力量在林潜体内疯狂涌动，如同万千银河倒卷，每一缕法则之力都在撕裂着他的经脉。

    "坚持住！"炎无极的声音从远处传来，但在林潜的感知中，这声音仿佛跨越了无数个纪元才抵达他的耳畔。

    时间，在这一刻变得混乱。

    林潜能清晰地感受到，自己的身体正在经历着诡异的变化——左手在急速衰老，皮肤如枯树皮般褶皱；右手却在逆转时光，变得如婴儿般稚嫩。这是时间法则失控的征兆！

    "不行，必须找到平衡点！"林潜咬紧牙关，神识深入法则本源。

    就在这千钧一发之际，他突然想起了师尊曾经说过的话："法则并非独立存在，时间与空间本为一体，分则两伤，合则共生。"

    对了，空间法则！

    林潜毫不犹豫地引动体内潜藏的空间法则之力。刹那间，两股截然不同却又相辅相成的力量在他的丹田处碰撞。

    轰！

    一声只有林潜自己能听到的巨响在识海中炸开。时间与空间，这两条本该在大乘期才能同时掌控的法则链，竟然在这一刻开始了融合。

    "这不可能！"远处观战的几位长老同时惊呼。

    但林潜已经没有退路了。他能感觉到，第三条法则链正在成型——那是一条前所未有的时空法则链，银色与紫色的光芒交织缠绕，形成了一条璀璨夺目的锁链虚影。

    "给我……凝！"

    随着林潜一声怒吼，所有的异象瞬间收敛。当光芒散去，他缓缓睁开双眼，眼中闪过一丝时空错乱的奇异光芒。

    成功了。

    他成为了九域历史上第一个在化神期就掌握时空融合法则的修士。
    """

    print(f"模拟内容长度：{len(mock_content)} 字")
    print("内容预览：")
    print(mock_content[:300] + "...")

    print("\n" + "=" * 60)
    print("3. 创建会话并分析内容")
    print("-" * 40)

    # 创建会话管理器
    session_manager = CreationSessionManager(None)
    session_id = await session_manager.create_session(
        novel_id=novel_id,
        chapter_number=chapter_number,
        session_name="测试创作会话"
    )

    print(f"创建会话ID: {session_id}")

    # 分析内容
    formatted_report, analysis = await workflow.analyze_user_content(
        session_id=session_id,
        generated_content=mock_content,
        user_satisfaction=7,
        prompt_used=prompt_components
    )

    print("\n分析报告：")
    print(formatted_report)

    print("\n" + "=" * 60)
    print("4. 生成改进建议")
    print("-" * 40)

    suggestions = await workflow.suggest_improvements(
        session_id=session_id,
        analysis_result=analysis,
        user_feedback="希望加入更多内心独白和环境描写"
    )

    print("改进建议：")
    print(json.dumps(suggestions, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("5. 优化Prompt")
    print("-" * 40)

    # 基于反馈优化prompt
    issues = ["内心活动描写不足", "环境描写较少"]
    improvements = ["增加心理描写", "丰富环境细节", "加强感官描写"]

    optimized_formatted, optimized_components = await workflow.optimize_prompt_iteration(
        session_id=session_id,
        original_prompt=prompt_components,
        issues_found=issues,
        desired_improvements=improvements
    )

    print("优化后的Prompt：")
    print(optimized_formatted[:500] + "...")

    print("\n" + "=" * 60)
    print("6. 模拟第二次生成（改进后）")
    print("-" * 40)

    improved_content = mock_content + """

    【第二次迭代增加的内容】

    林潜的意识仿佛被撕裂成了无数片段，每一片都在经历着不同的时间流速。

    在某个片段中，他看到了自己儿时练剑的场景，竹剑划破空气的声音清晰可闻；在另一个片段里，他窥见了未来的某个瞬间，满头白发的自己正在传授弟子时空法则的奥秘。

    "这就是时空法则的真谛吗？"林潜的内心震撼不已，"过去、现在、未来，原来从来都不是线性的存在……"

    突破之地的空间开始扭曲，地面的青石板呈现出诡异的波纹状，仿佛水面的涟漪。空气中弥漫着一股奇特的气息，那是时间与空间交织产生的混沌之力。

    远处的山峰在视线中忽远忽近，天空的云朵时而静止，时而倒流。整个世界都在为这次前所未有的突破而震颤。
    """

    # 分析改进后的内容
    formatted_report2, analysis2 = await workflow.analyze_user_content(
        session_id=session_id,
        generated_content=improved_content,
        user_satisfaction=9,
        prompt_used=optimized_components
    )

    print(f"改进后内容长度：{len(improved_content)} 字")
    print(f"用户满意度提升：7 -> 9")
    print(f"质量评分提升：{analysis.overall_score:.2f} -> {analysis2.overall_score:.2f}")

    print("\n" + "=" * 60)
    print("7. 获取会话统计")
    print("-" * 40)

    stats = await session_manager.get_session_statistics(session_id)
    print("会话统计：")
    print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

    # 测试UI界面格式化功能
    ui = UserInteractionInterface()

    print("\n附加测试：会话摘要格式化")
    print("-" * 40)
    summary = ui.format_session_summary(stats)
    print(summary)


async def test_analyzer():
    """单独测试内容分析器"""

    print("\n" + "=" * 60)
    print("内容分析器功能测试")
    print("=" * 60)

    analyzer = ContentAnalyzer(None)

    # 测试内容
    test_content = """
    "法则链的力量，远超你的想象。"林潜缓缓开口，声音虽然平静，却蕴含着惊天动地的威压。

    他轻轻抬手，时间法则瞬间发动。整个空间的时间流速骤然放缓，飞舞的落叶凝固在半空，如同琥珀中的昆虫。

    炎无极震惊地发现，自己的动作变得无比缓慢，仿佛陷入了泥沼之中。这就是时间法则的恐怖之处——当对手还在思考的时候，掌控者已经可以发动无数次攻击。

    空气中弥漫着淡淡的法则波动，那是只有化神期以上的修士才能感知到的力量。
    """

    print("测试各项分析功能：")

    # 1. 长度分析
    length_analysis = analyzer._analyze_length(test_content)
    print(f"\n1. 长度分析：")
    print(f"   - 字符数：{length_analysis['character_count']}")
    print(f"   - 段落数：{length_analysis['paragraph_count']}")

    # 2. 结构分析
    structure = analyzer._analyze_structure(test_content)
    print(f"\n2. 结构分析：")
    print(f"   - 包含对话：{structure['has_dialogue']}")
    print(f"   - 包含动作：{structure['has_action']}")

    # 3. 叙事流畅度
    flow = analyzer._evaluate_narrative_flow(test_content)
    print(f"\n3. 叙事流畅度：")
    print(f"   - 流畅度评分：{flow['flow_score']:.2f}")
    print(f"   - 过渡词数量：{flow['transition_count']}")

    # 4. 对话质量
    dialogue = analyzer._evaluate_dialogue(test_content)
    print(f"\n4. 对话质量：")
    print(f"   - 对话数量：{dialogue['dialogue_count']}")
    print(f"   - 质量评分：{dialogue.get('quality_score', 0):.2f}")

    # 5. 场景生动性
    scene = analyzer._evaluate_scene_description(test_content)
    print(f"\n5. 场景生动性：")
    print(f"   - 感官丰富度：{scene['sensory_richness_score']:.2f}")
    print(f"   - 视觉元素：{scene['visual_elements']}")

    # 6. 法则链使用
    law_chain = analyzer._check_law_chain_usage(test_content)
    print(f"\n6. 法则链系统：")
    print(f"   - 提及的法则链：{law_chain['mentioned_law_chains']}")
    print(f"   - 使用评分：{law_chain['usage_score']:.2f}")


async def main():
    """主测试函数"""

    try:
        # 运行工作流测试
        await test_workflow()

        # 运行分析器测试
        await test_analyzer()

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("人工协作创作工作流运行正常")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试出错：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())