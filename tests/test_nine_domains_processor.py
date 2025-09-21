"""
九域文化框架处理器测试脚本
测试完整的处理工作流程
"""

import asyncio
import logging
import json
from uuid import uuid4
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 测试数据：使用你提供的人域文化框架示例
TEST_CULTURAL_TEXT = """
人域｜六维文化框架

A. 神话与宗教
信条：链是"看不见的鞭子"，顺链得安、逆链遭殃。
神祇与机构：乡祠供奉"环祖"（九环祖像），由"乡祭"掌礼；城内设祭司分坊。
丧葬观："顺链而归"，请冥域渡链僧诵《归环文》；无链籍者草葬、不得入册。

B. 权力与法律
结构：县府（吏治）＋宗门驻坊（修治）双轨；大案须报天域巡链司。
身份：链籍黄/灰/黑三等（黄=良籍；灰=苦役；黑=罪籍）。
刑罚：逃籍/伪票→笞与流；传授断链术→加缚或链枷。
执法角色：缚司（县属）＋巡链官（巡回）＋坊内"契官"。

C. 经济与技术
产业：谷物、盐铁、陶织、驭兽农具；向宗门供童生与杂役。
金融：小额链票村社抗议。
技术：环铸法、锻链术、法则工艺传承有师承制约束。

D. 家庭与教育
婚嫁：需"环印"合证，双方家谱链印验真；跨籍联姻受限。
传承：血脉与师承双轨，血契者入魔域、断链者成荒民。
教育：童生入宗门习艺，成年考"链诀"定品阶。

E. 仪式与日常
节庆：链诞节（祭环祖）、裂世夜（避邪）、拾链礼（成人礼）。
日常：晨诵环文、午检链籍、夜祭祖灵；
禁忌：不得私藏断链术、不得伪造链票、不得亵渎环祖。

F. 艺术与娱乐
艺术：环纹雕刻、链歌吟唱、祖谱绘制。
竞技：链术比试、环器竞赛、法则辩论。
娱乐：说书唱戏多颂环祖功德，舞蹈模拟"九环连锁"。

【剧情钩子】
1. 祖灵续籍祭夜，有人盗改家谱链印，引发血脉争议。
2. 年轻人私学断链术，被发现后逃往荒域，家族链籍被降级。
3. 跨域商贸中发现伪造链票，引发人域与海域的外交纠纷。
"""


async def test_nine_domains_processor():
    """测试九域处理器"""
    print("=== 九域文化框架处理器测试 ===\n")

    try:
        # 导入处理管道
        from src.etl.nine_domains_pipeline import NineDomainsPipeline

        # 创建测试配置
        test_config = {
            "enable_text_cleaning": True,
            "enable_validation": True,
            "enable_cross_domain_analysis": True,
            "enable_database_import": False,  # 测试时不导入数据库
            "validation_level": "NORMAL",
            "enable_auto_fix": True,
            "output_detailed_logs": True
        }

        # 创建处理管道
        pipeline = NineDomainsPipeline(test_config)
        print("+ 处理管道初始化成功")

        # 生成测试小说ID
        test_novel_id = uuid4()
        print(f"+ 测试小说ID: {test_novel_id}")

        # 处理文本
        print("\n--- 开始处理文化框架文本 ---")
        result = await pipeline.process_cultural_text(
            TEST_CULTURAL_TEXT,
            test_novel_id,
            {"source": "test_data", "description": "人域六维文化框架测试"}
        )

        # 检查结果
        if result.get("success"):
            print("+ 文化框架处理成功!")

            # 打印处理摘要
            summary = result.get("summary", {})
            print(f"\n--- 处理摘要 ---")
            print(f"处理时间: {summary.get('processing_time_seconds', 0):.2f}秒")

            data_counts = summary.get('total_data_count', {})
            print(f"提取数据:")
            print(f"  - 文化框架: {data_counts.get('frameworks', 0)}")
            print(f"  - 文化实体: {data_counts.get('entities', 0)}")
            print(f"  - 实体关系: {data_counts.get('relations', 0)}")
            print(f"  - 剧情钩子: {data_counts.get('plot_hooks', 0)}")
            print(f"  - 概念词典: {data_counts.get('concepts', 0)}")

            # 打印质量指标
            quality_metrics = summary.get('quality_metrics', {})
            print(f"\n质量指标:")
            print(f"  - 域覆盖: {quality_metrics.get('domains_covered', 0)}")
            print(f"  - 维度覆盖: {quality_metrics.get('dimensions_covered', 0)}")
            print(f"  - 平均实体描述长度: {quality_metrics.get('avg_entity_description_length', 0):.1f}")
            print(f"  - 跨域关系数: {quality_metrics.get('cross_domain_relations', 0)}")

            # 打印建议
            recommendations = summary.get('recommendations', [])
            if recommendations:
                print(f"\n改进建议:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")

            # 打印验证结果
            if result.get("postprocessing", {}).get("validation_result"):
                validation = result["postprocessing"]["validation_result"]
                print(f"\n--- 数据验证结果 ---")
                print(f"验证通过: {'是' if validation.is_valid else '否'}")
                print(f"质量分数: {validation.quality_score:.2f}")
                print(f"问题数量: {len(validation.issues)}")

                if validation.issues:
                    print("主要问题:")
                    for issue in validation.issues[:5]:  # 只显示前5个问题
                        print(f"  - [{issue.issue_type.value}] {issue.message}")

        else:
            print("X 文化框架处理失败:")
            print(f"错误: {result.get('error')}")

        # 关闭资源
        await pipeline.close()
        print("\n+ 测试完成，资源已清理")

    except Exception as e:
        print(f"X 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_individual_components():
    """测试各个组件"""
    print("\n=== 组件单独测试 ===\n")

    try:
        # 测试文化处理器
        print("1. 测试九域文化处理器...")
        from src.etl.nine_domains_cultural_processor import NineDomainsCulturalProcessor

        processor = NineDomainsCulturalProcessor()
        batch_data = await processor.process_nine_domains_text(TEST_CULTURAL_TEXT, uuid4())

        print(f"   + 提取框架: {len(batch_data.frameworks)}")
        print(f"   + 提取实体: {len(batch_data.entities)}")
        print(f"   + 提取关系: {len(batch_data.relations)}")

        # 测试实体提取器
        print("\n2. 测试实体提取器...")
        from src.etl.nine_domains_entity_extractor import NineDomainsEntityExtractor

        entity_extractor = NineDomainsEntityExtractor()
        entities = entity_extractor.extract_entities(TEST_CULTURAL_TEXT)

        print(f"   + 提取实体: {len(entities)}")
        if entities:
            print(f"   示例实体: {entities[0].text} ({entities[0].entity_type.value})")

        # 测试跨域分析器
        print("\n3. 测试跨域关系分析器...")
        from src.etl.cross_domain_analyzer import CrossDomainAnalyzer

        cross_analyzer = CrossDomainAnalyzer()
        cross_result = cross_analyzer.analyze_cross_domain_relationships(TEST_CULTURAL_TEXT, batch_data.entities)

        cross_relations = cross_result.get("cross_domain_relations", [])
        print(f"   + 跨域关系: {len(cross_relations)}")

        # 测试数据验证器
        print("\n4. 测试数据验证器...")
        from src.etl.cultural_data_validator import CulturalDataValidator

        validator = CulturalDataValidator()
        validation_result = validator.validate_cultural_batch(batch_data)

        print(f"   + 验证通过: {'是' if validation_result.is_valid else '否'}")
        print(f"   + 质量分数: {validation_result.quality_score:.2f}")
        print(f"   + 问题数量: {len(validation_result.issues)}")

        print("\n+ 所有组件测试完成")

    except Exception as e:
        print(f"X 组件测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_sample_entities():
    """测试样本实体提取"""
    print("\n=== 实体提取详细测试 ===\n")

    try:
        from src.etl.nine_domains_entity_extractor import NineDomainsEntityExtractor

        extractor = NineDomainsEntityExtractor()
        entities = extractor.extract_entities(TEST_CULTURAL_TEXT)

        print(f"总共提取到 {len(entities)} 个实体:")

        # 按类型分组显示
        entity_groups = {}
        for entity in entities:
            entity_type = entity.entity_type.value
            if entity_type not in entity_groups:
                entity_groups[entity_type] = []
            entity_groups[entity_type].append(entity)

        for entity_type, group_entities in entity_groups.items():
            print(f"\n{entity_type} ({len(group_entities)}个):")
            for entity in group_entities[:3]:  # 只显示前3个
                print(f"  - {entity.text}")
                print(f"    域: {entity.domain.value if entity.domain else '未知'}")
                print(f"    置信度: {entity.confidence:.2f}")
                print(f"    上下文: {entity.context[:50]}...")

        # 显示统计信息
        stats = extractor.get_extraction_statistics(entities)
        print(f"\n提取统计:")
        print(f"  - 平均置信度: {stats['average_confidence']:.2f}")
        print(f"  - 高置信度实体: {stats['by_confidence']['high']}")
        print(f"  - 中置信度实体: {stats['by_confidence']['medium']}")
        print(f"  - 低置信度实体: {stats['by_confidence']['low']}")

    except Exception as e:
        print(f"X 实体提取测试失败: {e}")


def save_test_results(results: dict, filename: str = "test_results.json"):
    """保存测试结果"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"+ 测试结果已保存到: {filename}")
    except Exception as e:
        print(f"X 保存测试结果失败: {e}")


async def main():
    """主测试函数"""
    print("九域文化框架处理器 - 完整测试套件")
    print("=" * 50)

    # 运行主要测试
    await test_nine_domains_processor()

    # 运行组件测试
    await test_individual_components()

    # 运行实体提取详细测试
    await test_sample_entities()

    print("\n" + "=" * 50)
    print("测试套件执行完成!")
    print("\n如需测试完整的数据库集成，请:")
    print("1. 确保数据库连接配置正确")
    print("2. 在配置中启用 'enable_database_import': True")
    print("3. 运行: python test_nine_domains_processor.py")


if __name__ == "__main__":
    asyncio.run(main())