# -*- coding: utf-8 -*-
"""
简化的文化框架分析测试脚本
"""

import asyncio
import json
from cultural_framework_analyzer import CulturalFrameworkAnalyzer, DomainType

# 测试文本
TEST_TEXT = """
人域
人域是九大域中的基础域界，是大多数凡人生活的世界。

A. 神话与宗教
天命信仰占据主导地位，人们相信法则链体系代表着天意的体现。祭司议会在人域设有分部。

B. 权力与法律
天命王朝实行中央集权制，皇帝拥有至高无上的权威。环印是身份的象征。

C. 经济与技术
链票是主要的货币形式，其价值与蕴含的法则能量成正比。

D. 家庭与教育
血脉传承极为重要，法则链能力往往具有遗传性。成年礼为归环礼。

E. 仪式与日常
裂世夜是最重要的节日。链市每七日一次，是重要的社交和贸易场所。

F. 艺术与娱乐
链纹艺术高度发达，环音乐器能够产生特殊的共鸣效果。

情节钩子：
- 平民少年意外获得传说级法则链，引起各方势力关注
- 天命王朝皇室内部为继承权发生分裂

天域
天域是九大域的统治中心，法则链体系的发源地。

A. 神话与宗教
天域自认为是法则的原点，创造了完整的法则链理论体系。

B. 权力与法律
天帝拥有绝对权威，下设天阁、链部、法司等机构。

C. 经济与技术
拥有最先进的链技术，能够制造高级法则器具和环印。

D. 家庭与教育
血统纯正性要求极高，天链学院是九域最高学府。

E. 仪式与日常
天启节庆祝天域的建立，规模宏大。

F. 艺术与娱乐
艺术形式极其精致，链画能够展现法则的视觉化效果。

情节钩子：
- 天帝突然神秘失踪，引发继承危机和政治动荡
- 发现了可能推翻现有法则理论的古老文献
"""


async def test_basic_analysis():
    """测试基础分析功能"""
    print("开始测试文化框架分析器...")

    analyzer = CulturalFrameworkAnalyzer()

    # 测试完整文本分析
    try:
        result = await analyzer.analyze_full_text(TEST_TEXT)

        print(f"✅ 分析完成")
        print(f"   - 识别域数: {result['analysis_metadata']['total_domains']}")
        print(f"   - 识别实体: {result['analysis_metadata']['total_entities']}")
        print(f"   - 跨域关系: {result['analysis_metadata']['total_relations']}")

        # 显示各域信息
        for domain_name, domain_data in result['domain_cultures'].items():
            print(f"\n🌍 {domain_name}:")
            print(f"   实体数量: {len(domain_data['entities'])}")
            print(f"   情节钩子: {len(domain_data['plot_hooks'])}")

            # 显示前3个实体
            if domain_data['entities']:
                print("   主要实体:")
                for entity in domain_data['entities'][:3]:
                    print(f"     • {entity['name']} ({entity['type']})")

        # 保存结果
        with open("test_result.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n💾 结果已保存到 test_result.json")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_entity_patterns():
    """测试实体识别模式"""
    print("\n测试实体识别模式...")

    analyzer = CulturalFrameworkAnalyzer()

    test_cases = [
        ("天命王朝", "组织机构"),
        ("祭司议会", "组织机构"),
        ("法则链", "重要概念"),
        ("链票", "文化物品"),
        ("环印", "文化物品"),
        ("裂世夜", "仪式活动"),
        ("归环礼", "仪式活动")
    ]

    for entity_name, expected_type in test_cases:
        # 简单的模式匹配测试
        found = False
        for entity_type, patterns in analyzer.entity_patterns.items():
            for pattern in patterns:
                import re
                if re.search(pattern, entity_name):
                    print(f"✅ {entity_name} -> {entity_type.value}")
                    found = True
                    break
            if found:
                break

        if not found:
            print(f"❌ 未识别: {entity_name}")

def test_concept_dictionary():
    """测试概念词典"""
    print("\n测试概念词典...")

    analyzer = CulturalFrameworkAnalyzer()
    concepts = analyzer.chain_concepts

    print(f"预定义概念数量: {len(concepts)}")
    for name, info in concepts.items():
        print(f"  • {name}: {info['function']} ({info['type']})")

def main():
    """主测试函数"""
    print("=" * 50)
    print("裂世九域文化框架分析器测试")
    print("=" * 50)

    # 测试实体模式
    test_entity_patterns()

    # 测试概念词典
    test_concept_dictionary()

    # 测试完整分析
    success = asyncio.run(test_basic_analysis())

    if success:
        print("\n🎉 所有测试通过!")
    else:
        print("\n❌ 测试失败，请检查错误信息")

if __name__ == "__main__":
    main()