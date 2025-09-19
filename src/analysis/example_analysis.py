# -*- coding: utf-8 -*-
"""
裂世九域·法则链纪元 文化框架分析示例
演示如何使用文化分析工具处理九域文本内容
"""

import asyncio
import json
from pathlib import Path
from cultural_framework_analyzer import (
    CulturalFrameworkAnalyzer,
    DomainType,
    EntityType,
    CulturalDimension
)


# 示例：九域文化设定文本
SAMPLE_NINE_DOMAINS_TEXT = """
人域
人域是九大域中的基础域界，是大多数凡人生活的世界，也是天命王朝直接统治的核心区域。

A. 神话与宗教
天命信仰占据主导地位，人们相信天域降下的法则链体系代表着天意的体现。链籍被视为神圣经典，记录着各种法则的奥秘。祭司议会在人域设有分部，负责解释法则含义和主持重要仪式。普通民众通过朝拜链庙、献祭链石来表达虔诚。

B. 权力与法律
天命王朝实行中央集权制，皇帝拥有至高无上的权威，下设九部分管不同事务。链籍等级制度决定了个人的社会地位，拥有高级法则链的人自动获得贵族身份。环印是身份的象征，不同颜色和材质代表不同等级。法律以《链令大典》为基础，强调维护法则秩序的重要性。

C. 经济与技术
链票是主要的货币形式，其价值与蕴含的法则能量成正比。商业贸易发达，人域是九域间贸易的中转站。技术水平适中，善于制造链器、环印等法则辅助用品。农业以种植链稻、环菜为主，这些作物能够吸收并存储微量法则之力。手工业发达，特别是链纹刺绣和环音制作技艺。

D. 家庭与教育
血脉传承极为重要，法则链能力往往具有遗传性。家族以链谱记录世代传承的法则能力。教育制度完善，设有链院教授法则理论，环校培养实践技能。成年礼为归环礼，标志着个人法则链的初步觉醒。婚姻讲究门当户对，特别是法则链等级的匹配。

E. 仪式与日常
裂世夜是最重要的节日，纪念九域的形成。归环礼是成年仪式，青年人在此时接受法则链传承。日常生活中，人们习惯用环手势打招呼，以链纹装饰衣物。链市每七日一次，是重要的社交和贸易场所。饮食文化中，链茶和环酒是常见的饮品。

F. 艺术与娱乐
链纹艺术高度发达，不同的纹路代表不同的意义和美感。环音乐器能够产生特殊的共鸣效果，是宫廷和民间都喜爱的音乐形式。说书人讲述九域传说，戏剧表演法则英雄的故事。竞技运动有链球和环舞，考验参与者的法则控制能力。

情节钩子：
- 平民少年意外获得传说级法则链，引起各方势力关注
- 天命王朝皇室内部为继承权发生分裂，不同派系寻求支持
- 人域与海域的贸易争端演变为外交危机
- 古老的链庙中发现失传的法则秘典，可能改变现有权力格局
- 祭司议会内部出现改革派，质疑传统的法则解释

天域
天域是九大域的统治中心，法则链体系的发源地，拥有最高的技术水平和文明程度。

A. 神话与宗教
天域自认为是法则的原点，创造了完整的法则链理论体系。天命神话认为天域的统治者是法则的化身，拥有解释和修改法则的神圣权力。链祖神殿是最高的宗教机构，保管着原始链典。各种法则都有对应的守护神，形成庞大的神系。

B. 权力与法律
天帝拥有绝对权威，下设天阁、链部、法司等机构。天命王朝的权力源泉就在天域，所有重大决策都从这里发出。环印制度最为严格，每一枚环印都记录着持有者的详细信息和权限。法典《天链经》是所有域法律的源头，具有不可违抗的权威性。

C. 经济与技术
拥有最先进的链技术，能够制造高级法则器具和环印。天域控制着链票的发行权，掌握九域的经济命脉。贸易以技术和知识输出为主，从其他域获取原材料和特产。城市建设融入法则技术，悬浮建筑和传送阵比比皆是。

D. 家庭与教育
血统纯正性要求极高，天域贵族只与特定家族联姻。教育体系最为完善，天链学院是九域最高学府。家族传承注重法则理论的深度研究，每个家族都有专门的研究方向。

E. 仪式与日常
天启节庆祝天域的建立，规模宏大。链冠礼是贵族成年仪式，比普通的归环礼更加隆重。日常生活高度仪式化，衣食住行都有严格的礼仪规范。天域居民以穿着绣有精美链纹的丝绸为荣。

F. 艺术与娱乐
艺术形式极其精致，链画能够展现法则的视觉化效果。天音乐器可以直接影响法则流动，是真正的法则艺术。文学以法则诗歌为最高形式，每首诗都蕴含深奥的法则原理。建筑艺术融合了法则几何学，创造出令人叹为观止的宏伟建筑。

情节钩子：
- 天帝突然神秘失踪，引发继承危机和政治动荡
- 发现了可能推翻现有法则理论的古老文献
- 天域内部出现反对天命统治的地下组织
- 与其他域的法则研究产生冲突，威胁天域的技术垄断
- 天链学院的学者意外发现了连接其他世界的法则门径

魔域
魔域是九大域中最为神秘和危险的区域，这里的法则呈现出扭曲和反常的特性。

A. 神话与宗教
魔域信奉混沌法则，认为秩序本身就是对自由的束缚。断链术被视为解放的象征，能够破坏既定的法则结构。血月教是主要的宗教组织，崇拜毁灭与重生的循环。魔域的神话故事多涉及背叛、复仇和禁忌的力量。

B. 权力与法律
魔君统治魔域，但权力结构相对松散，各大魔宗保持一定的独立性。法律以强者为尊，实力决定地位。血印替代了环印，以鲜血为媒介记录契约和身份。断链律允许在特定条件下违背或修改法则，这在其他域是绝对禁忌的。

C. 经济与技术
魔域的技术发展方向独特，专注于开发法则的破坏性和变异性。血石是重要的货币和能源，蕴含着生命力和魔性力量。贸易以禁忌知识、诅咒物品和战争器械为主。魔器制造技术高超，但往往伴随着巨大的风险和代价。

D. 家庭与教育
血脉传承注重力量而非纯正性，鼓励与强者结合以强化后代。魔学院教授断链术和禁忌法则，学习过程极其危险。成年仪式为血誓礼，需要签订血契并承受法则反噬的痛苦。

E. 仪式与日常
血月夜是重要节日，进行大规模的断链仪式。日常生活充满竞争和挑战，弱者很难生存。魔域居民以伤疤和血纹为荣，展示自己经历过的战斗和痛苦。食物多为血食，能够增强魔性力量。

F. 艺术与娱乐
血画使用鲜血和特殊颜料，能够产生诅咒效果。魔音乐器以骨骼和金属制成，音调低沉而震撼人心。角斗是最受欢迎的娱乐活动，经常有生死之战。文学作品多为悲剧和恐怖故事，探讨人性的黑暗面。

情节钩子：
- 魔君策划针对天域的大规模背叛计划
- 发现了能够永久断开所有法则链的终极禁术
- 魔域内部爆发派系斗争，威胁整个域的稳定
- 有魔族试图渗透其他域，传播断链思想
- 血月教预言了九域毁灭的启示，引发恐慌

海域
海域是九大域中的海洋世界，拥有独特的水系法则和海洋文明。

A. 神话与宗教
海域信奉潮汐神话，认为万物皆有涨落周期，法则如潮水般永恒流动。深海古神被视为法则的源泉，居住在海域最深处。珊瑚神庙遍布各个岛屿，是重要的宗教中心。海族相信死后灵魂会回到深海，与古神融为一体。

B. 权力与法律
海王统治海域，下设各岛屿的领主和船长。权力结构相对分散，各个岛屿保持较大的自治权。海律以潮汐周期为基础，不同时期有不同的法律规范。珠印是身份象征，不同的海珠代表不同的地位和能力。

C. 经济与技术
海域的财富主要来源于海洋资源和航海贸易。珍珠、珊瑚、海晶石是重要的货币和材料。造船技术高度发达，能够制造适应不同法则环境的特殊船只。海域是九域间贸易的重要中转站，控制着多条重要航线。

D. 家庭与教育
海族以氏族为单位，每个氏族都有自己的守护海兽。子女从小接受游泳和航海训练，成年礼为入海礼，需要独自在深海中生存七天。婚姻常与贸易联盟相结合，加强不同岛屿间的联系。

E. 仪式与日常
潮汐节随着月相变化，是最重要的节日。日常生活与海洋节律密切相关，作息时间跟随潮汐变化。海域居民以海产品为主食，特别是各种法则海兽的肉类。服装多用海丝和鱼鳞制成，轻便而防水。

F. 艺术与娱乐
海歌是独特的艺术形式，能够影响海洋法则和召唤海兽。珊瑚雕刻技艺精湛，作品往往具有法则效果。冲浪和赛船是流行的体育活动，考验对海洋法则的掌控能力。海域的舞蹈模仿海浪和鱼群的动作，优美而富有节奏感。

情节钩子：
- 深海中发现了古老的沉没文明，可能改变对法则起源的认知
- 海王与陆地域国发生贸易争端，威胁海域的经济利益
- 神秘的海洋灾难频发，可能与法则异常有关
- 有传说中的海兽苏醒，挑战现有的权力格局
- 发现了通往其他域的海底通道，引发探索热潮

虚域
虚域是九大域中最为虚幻和不稳定的区域，这里的现实与幻境交织。

A. 神话与宗教
虚域信奉虚无主义，认为所有的存在都是虚幻的，只有虚空才是永恒。虚空教导人们超越物质束缚，追求精神的绝对自由。幻象神殿是重要的宗教场所，但其位置和形态经常发生变化。虚域的神话充满了关于现实与虚幻边界的哲学思考。

B. 权力与法律
虚君统治虚域，但其统治方式极为特殊，更像是一种精神上的指引。法律概念在虚域相对模糊，更多依靠共识和默契。影印是身份的象征，但同样具有不稳定性，会随着持有者的精神状态发生变化。

C. 经济与技术
虚域的经济体系以精神价值为基础，知识、记忆、梦境都可以作为交易对象。幻晶是重要的货币，能够存储和传递精神能量。技术发展侧重于意识和精神领域，能够创造复杂的幻象和精神构造体。

D. 家庭与教育
家庭关系在虚域较为淡薄，更注重精神上的契合而非血缘。教育以冥想和精神修炼为主，幻学院教授如何控制和利用虚幻力量。成年仪式为破幻礼，需要学会区分现实与虚幻。

E. 仪式与日常
虚无节是重要节日，人们集体进入冥想状态，追求精神的升华。日常生活界限模糊，现实与梦境经常交织。虚域居民的衣食住行都具有不确定性，可能随时发生变化。食物多为精神食粮，能够直接滋养灵魂。

F. 艺术与娱乐
虚影艺术是独特的艺术形式，创造的作品介于存在与不存在之间。幻音乐器能够产生只有精神才能感知的音乐。虚域的文学作品探讨存在的本质和现实的意义。娱乐活动多涉及精神挑战和哲学思辨。

情节钩子：
- 虚域的现实开始崩塌，可能影响到其他域的稳定
- 发现了能够将虚幻化为现实的终极法则
- 虚君陷入永恒的冥想状态，虚域面临失控的危险
- 有人利用虚域的特性，在其他域制造大规模幻象
- 虚域与现实世界的边界开始模糊，引发存在危机
"""


async def run_comprehensive_analysis():
    """运行完整的文化框架分析示例"""

    print("🚀 启动裂世九域文化框架分析")
    print("=" * 60)

    # 创建分析器
    analyzer = CulturalFrameworkAnalyzer()

    # 分析文本
    print("📖 正在分析九域文化文本...")
    result = await analyzer.analyze_full_text(SAMPLE_NINE_DOMAINS_TEXT)

    # 显示分析概况
    metadata = result['analysis_metadata']
    print(f"\n✅ 分析完成！")
    print(f"   📊 分析域数: {metadata['total_domains']}")
    print(f"   🏷️  识别实体: {metadata['total_entities']}")
    print(f"   🔗 跨域关系: {metadata['total_relations']}")
    print(f"   📅 分析时间: {metadata['timestamp']}")

    # 显示各域基本信息
    print(f"\n🌍 九域概览:")
    for domain_name, domain_data in result['domain_cultures'].items():
        entity_count = len(domain_data['entities'])
        hook_count = len(domain_data['plot_hooks'])
        print(f"   {domain_name}: {entity_count}个实体, {hook_count}个情节钩子")

    # 显示高重要性实体
    print(f"\n⭐ 高重要性实体 (Top 10):")
    high_importance = result['entity_summary']['high_importance']
    for i, entity in enumerate(high_importance[:10], 1):
        print(f"   {i:2d}. {entity['name']} ({entity['domain']}) - 重要性: {entity['importance']}")

    # 显示跨域关系
    print(f"\n🌐 跨域关系网络:")
    for relation in result['cross_domain_relations']:
        print(f"   {relation['from_domain']} ↔ {relation['to_domain']}")
        print(f"      类型: {relation['relation_type']} | 强度: {relation['strength']} | 性质: {relation['nature']}")
        print(f"      描述: {relation['description']}")
        print()

    # 显示主要主题
    print(f"🎯 主导主题:")
    for theme in result['analysis_insights']['dominant_themes']:
        print(f"   • {theme}")

    # 显示文化冲突
    print(f"\n⚔️ 识别的文化冲突:")
    for conflict in result['analysis_insights']['cultural_conflicts']:
        print(f"   • {conflict['type']}: {conflict['description']}")

    # 显示世界观一致性检查
    print(f"\n🔍 世界观一致性检查:")
    consistency = result['analysis_insights']['world_consistency']
    print(f"   链概念一致性: {'✅' if consistency['chain_concept_consistency'] else '❌'}")
    print(f"   权力结构一致性: {'✅' if consistency['power_hierarchy_consistency'] else '❌'}")
    print(f"   文化逻辑一致性: {'✅' if consistency['cultural_logic_consistency'] else '❌'}")

    if consistency['issues']:
        print(f"   发现的问题:")
        for issue in consistency['issues']:
            print(f"      • {issue}")

    # 保存结果
    output_dir = Path("analysis_results")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "nine_domains_analysis.json"
    analyzer.save_analysis_result(result, str(output_file))
    print(f"\n💾 分析结果已保存到: {output_file}")

    # 生成专门的报告
    await generate_detailed_reports(result, output_dir)

    return result


async def generate_detailed_reports(result: dict, output_dir: Path):
    """生成详细的分析报告"""

    print("\n📋 正在生成详细报告...")

    # 1. 实体分类报告
    entity_report = {
        "总览": result['entity_summary'],
        "按类型分类": {},
        "按域分类": {},
        "详细列表": []
    }

    # 按类型整理实体
    for domain_name, domain_data in result['domain_cultures'].items():
        for entity in domain_data['entities']:
            entity_type = entity['type']
            if entity_type not in entity_report["按类型分类"]:
                entity_report["按类型分类"][entity_type] = []

            entity_report["按类型分类"][entity_type].append({
                "名称": entity['name'],
                "域": domain_name,
                "重要性": entity['importance'],
                "描述": entity['description']
            })

            # 详细列表
            entity_report["详细列表"].append({
                "名称": entity['name'],
                "类型": entity['type'],
                "域": domain_name,
                "维度": entity['dimension'],
                "重要性": entity['importance'],
                "描述": entity['description'],
                "属性": entity['attributes'],
                "相关实体": entity['related_entities']
            })

    # 保存实体报告
    with open(output_dir / "entity_analysis_report.json", 'w', encoding='utf-8') as f:
        json.dump(entity_report, f, ensure_ascii=False, indent=2)

    # 2. 文化维度分析报告
    cultural_report = {
        "六维分析概览": {},
        "各域文化对比": {}
    }

    dimensions = ["mythology_religion", "power_law", "economy_tech",
                 "family_education", "ritual_daily", "art_entertainment"]
    dimension_names = ["神话与宗教", "权力与法律", "经济与技术",
                      "家庭与教育", "仪式与日常", "艺术与娱乐"]

    for i, dim in enumerate(dimensions):
        cultural_report["六维分析概览"][dimension_names[i]] = {}

        for domain_name, domain_data in result['domain_cultures'].items():
            dim_data = domain_data['cultural_dimensions'].get(dim, {})
            if dim_data:
                cultural_report["六维分析概览"][dimension_names[i]][domain_name] = {
                    "标题": dim_data.get('title', ''),
                    "关键要素数量": len(dim_data.get('key_elements', [])),
                    "组织数量": len(dim_data.get('organizations', [])),
                    "概念数量": len(dim_data.get('concepts', [])),
                    "物品数量": len(dim_data.get('items', [])),
                    "实践数量": len(dim_data.get('practices', []))
                }

    # 保存文化报告
    with open(output_dir / "cultural_dimensions_report.json", 'w', encoding='utf-8') as f:
        json.dump(cultural_report, f, ensure_ascii=False, indent=2)

    # 3. 情节钩子汇总
    plot_hooks_report = {
        "总数统计": {},
        "按域分类": {},
        "全部钩子": []
    }

    total_hooks = 0
    for domain_name, domain_data in result['domain_cultures'].items():
        hooks = domain_data['plot_hooks']
        plot_hooks_report["按域分类"][domain_name] = hooks
        plot_hooks_report["全部钩子"].extend([f"[{domain_name}] {hook}" for hook in hooks])
        total_hooks += len(hooks)

    plot_hooks_report["总数统计"]["总数"] = total_hooks
    plot_hooks_report["总数统计"]["平均每域"] = round(total_hooks / len(result['domain_cultures']), 2)

    # 保存情节钩子报告
    with open(output_dir / "plot_hooks_report.json", 'w', encoding='utf-8') as f:
        json.dump(plot_hooks_report, f, ensure_ascii=False, indent=2)

    # 4. 概念词典
    concept_dict = result['concept_dictionary']
    with open(output_dir / "concept_dictionary.json", 'w', encoding='utf-8') as f:
        json.dump(concept_dict, f, ensure_ascii=False, indent=2)

    print(f"   ✅ 实体分析报告: entity_analysis_report.json")
    print(f"   ✅ 文化维度报告: cultural_dimensions_report.json")
    print(f"   ✅ 情节钩子报告: plot_hooks_report.json")
    print(f"   ✅ 概念词典: concept_dictionary.json")


async def demonstrate_specific_analysis():
    """演示特定分析功能"""

    print("\n" + "=" * 60)
    print("🔬 演示特定分析功能")
    print("=" * 60)

    analyzer = CulturalFrameworkAnalyzer()

    # 1. 单域分析演示
    print("\n1️⃣ 单域分析演示 - 人域")
    human_domain_text = """
    人域是九大域中的基础域界...
    A. 神话与宗教
    天命信仰占据主导地位...
    """

    # 这里使用示例文本的人域部分
    human_text = SAMPLE_NINE_DOMAINS_TEXT.split("天域")[0].split("人域")[1].strip()
    human_culture = analyzer.parse_domain_text(human_text, DomainType.HUMAN)

    print(f"   域名: {human_culture.domain_name}")
    print(f"   实体数量: {len(human_culture.entities)}")
    print(f"   情节钩子: {len(human_culture.plot_hooks)}")
    print(f"   潜在冲突: {len(human_culture.potential_conflicts)}")

    # 显示神话宗教维度详情
    myth_rel = human_culture.cultural_dimensions.mythology_religion
    if myth_rel:
        print(f"   神话宗教要素: {len(myth_rel.get('key_elements', []))}")
        if myth_rel.get('organizations'):
            print(f"   宗教组织: {', '.join(myth_rel['organizations'])}")

    # 2. 实体关系分析
    print("\n2️⃣ 实体关系分析")
    organizations = [e for e in analyzer.entities if e.entity_type == EntityType.ORGANIZATION]
    concepts = [e for e in analyzer.entities if e.entity_type == EntityType.CONCEPT]

    print(f"   组织机构: {len(organizations)}")
    for org in organizations[:3]:  # 显示前3个
        print(f"      • {org.name} ({org.domain.value}) - 重要性: {org.importance_level}")

    print(f"   重要概念: {len(concepts)}")
    for concept in concepts[:3]:  # 显示前3个
        print(f"      • {concept.name} ({concept.domain.value}) - 重要性: {concept.importance_level}")

    # 3. 跨域关系构建
    print("\n3️⃣ 跨域关系构建")
    # 首先需要分析完整文本来构建关系
    await analyzer.analyze_full_text(SAMPLE_NINE_DOMAINS_TEXT)
    relations = analyzer.analyze_cross_domain_relations()

    print(f"   发现关系: {len(relations)}")
    for relation in relations[:3]:  # 显示前3个
        print(f"      • {relation.from_domain.value} → {relation.to_domain.value}")
        print(f"        类型: {relation.relation_type}, 强度: {relation.strength}")

    # 4. 概念词典构建
    print("\n4️⃣ 概念词典构建")
    concept_dict = analyzer.build_concept_dictionary()
    print(f"   概念总数: {len(concept_dict)}")

    # 显示预定义的链概念
    chain_concepts = {k: v for k, v in concept_dict.items() if k in analyzer.chain_concepts}
    print(f"   预定义链概念: {len(chain_concepts)}")
    for name, info in list(chain_concepts.items())[:3]:
        print(f"      • {name}: {info.get('function', '未知功能')}")


async def demonstrate_advanced_features():
    """演示高级功能"""

    print("\n" + "=" * 60)
    print("🚀 演示高级功能")
    print("=" * 60)

    analyzer = CulturalFrameworkAnalyzer()
    result = await analyzer.analyze_full_text(SAMPLE_NINE_DOMAINS_TEXT)

    # 1. 主题识别
    print("\n1️⃣ 主题识别")
    themes = analyzer._identify_dominant_themes()
    for theme in themes:
        print(f"   • {theme}")

    # 2. 权力结构分析
    print("\n2️⃣ 权力结构分析")
    power_analysis = analyzer._analyze_power_structures()
    print(f"   组织总数: {power_analysis['total_organizations']}")
    print(f"   权力集中度: {power_analysis['power_concentration']}")

    if power_analysis['by_domain']:
        print("   各域组织分布:")
        for domain, orgs in power_analysis['by_domain'].items():
            print(f"      {domain}: {len(orgs)}个组织")

    # 3. 文化冲突识别
    print("\n3️⃣ 文化冲突识别")
    conflicts = analyzer._identify_cultural_conflicts()
    for conflict in conflicts:
        print(f"   • {conflict.get('type', '未知类型')}: {conflict.get('description', '无描述')}")

    # 4. 世界观一致性检查
    print("\n4️⃣ 世界观一致性检查")
    consistency = analyzer._check_world_consistency()

    checks = [
        ("链概念一致性", consistency['chain_concept_consistency']),
        ("权力层级一致性", consistency['power_hierarchy_consistency']),
        ("文化逻辑一致性", consistency['cultural_logic_consistency'])
    ]

    for check_name, is_consistent in checks:
        status = "✅ 通过" if is_consistent else "❌ 问题"
        print(f"   {check_name}: {status}")

    if consistency['issues']:
        print("   发现的问题:")
        for issue in consistency['issues']:
            print(f"      • {issue}")


async def main():
    """主函数 - 运行所有示例"""

    print("🎉 欢迎使用裂世九域文化框架分析系统")
    print("这个示例将演示系统的各种功能和特性")

    try:
        # 运行综合分析
        result = await run_comprehensive_analysis()

        # 演示特定功能
        await demonstrate_specific_analysis()

        # 演示高级功能
        await demonstrate_advanced_features()

        print("\n" + "=" * 60)
        print("🎊 所有示例运行完成！")
        print("📁 查看 analysis_results/ 目录获取详细报告")
        print("📖 参考 README.md 了解更多使用方法")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 运行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())