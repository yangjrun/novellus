"""
文化框架系统完整初始化脚本
包含PostgreSQL表和MongoDB集合的初始化
"""

import asyncio
import asyncpg
from datetime import datetime
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import config


class CulturalFrameworkInitializer:
    """文化框架系统初始化器"""

    def __init__(self, pg_pool: asyncpg.Pool, mongo_db: AsyncIOMotorDatabase):
        self.pg_pool = pg_pool
        self.mongo_db = mongo_db

    async def init_cultural_dimensions(self):
        """初始化六个标准文化维度"""
        print("初始化标准文化维度...")

        dimensions = [
            {
                "code": "myth_religion",
                "name": "神话与宗教",
                "display_name": "神话与宗教维度",
                "description": "信仰体系、神话传说、宗教机构、丧葬观念等",
                "dimension_type": "cultural",
                "importance_weight": 9,
                "standard_elements": {
                    "core_beliefs": "核心信仰和教义",
                    "deities": "神祇体系",
                    "institutions": "宗教机构",
                    "rituals": "仪式和礼拜",
                    "afterlife": "死亡和来世观念",
                    "taboos": "宗教禁忌",
                    "sacred_objects": "圣物和圣地",
                    "clergy": "神职人员体系"
                },
                "sort_order": 1
            },
            {
                "code": "power_law",
                "name": "权力与法律",
                "display_name": "权力与法律维度",
                "description": "政治结构、法律制度、权力分配、社会秩序等",
                "dimension_type": "political",
                "importance_weight": 10,
                "standard_elements": {
                    "government_structure": "政府结构",
                    "legal_system": "法律体系",
                    "enforcement": "执法机构",
                    "power_distribution": "权力分配",
                    "social_hierarchy": "社会等级",
                    "identity_system": "身份制度",
                    "criminal_justice": "刑事司法",
                    "civil_rights": "公民权利"
                },
                "sort_order": 2
            },
            {
                "code": "economy_tech",
                "name": "经济与技术",
                "display_name": "经济与技术维度",
                "description": "生产方式、贸易体系、技术水平、资源分配等",
                "dimension_type": "economic",
                "importance_weight": 8,
                "standard_elements": {
                    "production": "生产方式",
                    "trade": "贸易体系",
                    "currency": "货币金融",
                    "technology": "技术水平",
                    "resources": "资源配置",
                    "infrastructure": "基础设施",
                    "innovation": "创新机制",
                    "labor": "劳动关系"
                },
                "sort_order": 3
            },
            {
                "code": "family_education",
                "name": "家庭与教育",
                "display_name": "家庭与教育维度",
                "description": "家庭结构、婚姻制度、教育体系、社会化过程等",
                "dimension_type": "social",
                "importance_weight": 7,
                "standard_elements": {
                    "family_structure": "家庭结构",
                    "marriage": "婚姻制度",
                    "education": "教育体系",
                    "socialization": "社会化过程",
                    "child_rearing": "育儿方式",
                    "coming_of_age": "成年仪式",
                    "knowledge_transfer": "知识传承",
                    "social_mobility": "社会流动"
                },
                "sort_order": 4
            },
            {
                "code": "ritual_daily",
                "name": "仪式与日常",
                "display_name": "仪式与日常维度",
                "description": "日常生活、节庆仪式、社交礼仪、生活习俗等",
                "dimension_type": "cultural",
                "importance_weight": 6,
                "standard_elements": {
                    "daily_life": "日常生活",
                    "festivals": "节庆活动",
                    "social_etiquette": "社交礼仪",
                    "customs": "生活习俗",
                    "food_culture": "饮食文化",
                    "clothing": "服饰规范",
                    "time_concepts": "时间观念",
                    "leisure": "休闲娱乐"
                },
                "sort_order": 5
            },
            {
                "code": "art_entertainment",
                "name": "艺术与娱乐",
                "display_name": "艺术与娱乐维度",
                "description": "艺术形式、娱乐活动、审美观念、文化表达等",
                "dimension_type": "cultural",
                "importance_weight": 5,
                "standard_elements": {
                    "architecture": "建筑风格",
                    "literature": "文学艺术",
                    "music_dance": "音乐舞蹈",
                    "visual_arts": "视觉艺术",
                    "crafts": "手工艺术",
                    "entertainment": "娱乐形式",
                    "aesthetics": "美学标准",
                    "sports": "体育竞技"
                },
                "sort_order": 6
            }
        ]

        async with self.pg_pool.acquire() as conn:
            for dim in dimensions:
                # 检查是否已存在
                existing = await conn.fetchrow(
                    "SELECT id FROM cultural_dimensions WHERE code = $1",
                    dim["code"]
                )

                if not existing:
                    await conn.execute("""
                        INSERT INTO cultural_dimensions
                        (code, name, display_name, description, dimension_type,
                         importance_weight, standard_elements, sort_order, is_active)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                    dim["code"], dim["name"], dim["display_name"],
                    dim["description"], dim["dimension_type"],
                    dim["importance_weight"], dim["standard_elements"],
                    dim["sort_order"], True)

                    print(f"插入维度: {dim['name']}")
                else:
                    print(f"维度已存在: {dim['name']}")

        print("标准文化维度初始化完成")

    async def init_nine_domains(self, novel_id: int = 1):
        """初始化九大域的基础数据"""
        print("初始化九大域...")

        domains = [
            {
                "name": "人域",
                "code": "ren_yu",
                "display_name": "人域 - 血脉残缺者的聚居地",
                "dominant_law": "残缺法则链",
                "ruling_power": "天域附庸",
                "power_level": 2,
                "civilization_level": 3,
                "stability_level": 4,
                "geographic_features": {
                    "terrain": "丘陵平原",
                    "climate": "温带大陆性",
                    "special_zones": ["乡祠分布区", "县府中心", "宗门驻坊"]
                },
                "resources": {
                    "agricultural": "谷物种植",
                    "mineral": "盐铁开采",
                    "manufactured": "陶织、驭兽农具",
                    "human": "向宗门供童生与杂役"
                },
                "sort_order": 1
            },
            {
                "name": "天域",
                "code": "tian_yu",
                "display_name": "天域 - 命运法则主宰之地",
                "dominant_law": "命运法则链",
                "ruling_power": "天命王朝",
                "power_level": 10,
                "civilization_level": 10,
                "stability_level": 9,
                "geographic_features": {
                    "terrain": "高原盆地",
                    "climate": "四季分明",
                    "special_zones": ["帝都", "九环观", "归环台", "链算所"]
                },
                "resources": {
                    "strategic": "链算占测",
                    "luxury": "链纤维宫织",
                    "administrative": "界核监修",
                    "cultural": "链墨抄经"
                },
                "sort_order": 2
            },
            {
                "name": "灵域",
                "code": "ling_yu",
                "display_name": "灵域 - 灵气丰饶的宗门之地",
                "dominant_law": "灵气法则链",
                "ruling_power": "各大宗门",
                "power_level": 8,
                "civilization_level": 9,
                "stability_level": 6,
                "geographic_features": {
                    "terrain": "山脉灵峰",
                    "climate": "灵气浓郁",
                    "special_zones": ["宗门山门", "灵脉节点", "试炼秘境"]
                },
                "resources": {
                    "spiritual": "灵石灵草",
                    "technical": "法器炼制",
                    "knowledge": "功法传承",
                    "services": "修炼指导"
                },
                "sort_order": 3
            },
            {
                "name": "荒域",
                "code": "huang_yu",
                "display_name": "荒域 - 断链者的废墟之地",
                "dominant_law": "破碎法则链",
                "ruling_power": "无序状态",
                "power_level": 4,
                "civilization_level": 2,
                "stability_level": 1,
                "geographic_features": {
                    "terrain": "废墟戈壁",
                    "climate": "恶劣多变",
                    "special_zones": ["古战场", "断链遗迹", "部落营地"]
                },
                "resources": {
                    "mining": "链矿走带",
                    "survival": "荒脊放牧",
                    "knowledge": "断链术残卷",
                    "mercenary": "战士雇佣"
                },
                "sort_order": 4
            },
            {
                "name": "冥域",
                "code": "ming_yu",
                "display_name": "冥域 - 死亡法则的轮回门户",
                "dominant_law": "死亡法则链",
                "ruling_power": "冥王殿",
                "power_level": 9,
                "civilization_level": 8,
                "stability_level": 10,
                "geographic_features": {
                    "terrain": "冥河谷地",
                    "climate": "阴冷肃穆",
                    "special_zones": ["冥司殿", "渡魂桥", "轮回池", "镇魂塔"]
                },
                "resources": {
                    "ritual": "葬服镇魂器",
                    "spiritual": "冥盐炼制",
                    "administrative": "轮回账册",
                    "services": "渡度服务"
                },
                "sort_order": 5
            },
            {
                "name": "魔域",
                "code": "mo_yu",
                "display_name": "魔域 - 链条崩坏的混沌之地",
                "dominant_law": "混沌法则链",
                "ruling_power": "魔皇",
                "power_level": 7,
                "civilization_level": 4,
                "stability_level": 2,
                "geographic_features": {
                    "terrain": "裂谷深渊",
                    "climate": "链崩区域",
                    "special_zones": ["魔皇城", "血契市", "乱阵禁地"]
                },
                "resources": {
                    "chaotic": "碎链材料",
                    "dangerous": "血契能量",
                    "unstable": "链崩器",
                    "forbidden": "乱术残片"
                },
                "sort_order": 6
            },
            {
                "name": "虚域",
                "code": "xu_yu",
                "display_name": "虚域 - 虚幻法则的预言之境",
                "dominant_law": "虚幻法则链",
                "ruling_power": "虚空议会",
                "power_level": 8,
                "civilization_level": 8,
                "stability_level": 5,
                "geographic_features": {
                    "terrain": "虚实交错",
                    "climate": "梦境变幻",
                    "special_zones": ["链算院", "回响塔", "梦境广场"]
                },
                "resources": {
                    "information": "回响记录",
                    "prediction": "因果推演",
                    "memory": "梦境存储",
                    "legal": "虚证仲裁"
                },
                "sort_order": 7
            },
            {
                "name": "海域",
                "code": "hai_yu",
                "display_name": "海域 - 深海古族的时空之域",
                "dominant_law": "时空法则链",
                "ruling_power": "海皇族",
                "power_level": 9,
                "civilization_level": 7,
                "stability_level": 7,
                "geographic_features": {
                    "terrain": "无垠海洋",
                    "climate": "潮汐变化",
                    "special_zones": ["海皇宫", "潮汐港", "时空漩涡"]
                },
                "resources": {
                    "navigation": "海图链印",
                    "trade": "跨域贸易",
                    "temporal": "时空技术",
                    "marine": "深海资源"
                },
                "sort_order": 8
            },
            {
                "name": "源域",
                "code": "yuan_yu",
                "display_name": "源域 - 完整法则链的起源之地",
                "dominant_law": "完整法则链(源链)",
                "ruling_power": "未知",
                "power_level": 10,
                "civilization_level": 10,
                "stability_level": 8,
                "geographic_features": {
                    "terrain": "神秘禁地",
                    "climate": "源力涌动",
                    "special_zones": ["源心", "守源会驻地", "古链遗迹"]
                },
                "resources": {
                    "ultimate": "完整源链",
                    "knowledge": "古谱抄本",
                    "spiritual": "源力净化",
                    "temporal": "原始记忆"
                },
                "sort_order": 9
            }
        ]

        async with self.pg_pool.acquire() as conn:
            for domain in domains:
                # 检查是否已存在
                existing = await conn.fetchrow(
                    "SELECT id FROM domains WHERE novel_id = $1 AND code = $2",
                    novel_id, domain["code"]
                )

                if not existing:
                    domain_id = await conn.fetchval("""
                        INSERT INTO domains
                        (novel_id, name, code, display_name, dominant_law, ruling_power,
                         power_level, civilization_level, stability_level,
                         geographic_features, resources, sort_order, is_active)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                        RETURNING id
                    """,
                    novel_id, domain["name"], domain["code"], domain["display_name"],
                    domain["dominant_law"], domain["ruling_power"],
                    domain["power_level"], domain["civilization_level"], domain["stability_level"],
                    domain["geographic_features"], domain["resources"],
                    domain["sort_order"], True)

                    print(f"插入域: {domain['name']} (ID: {domain_id})")
                else:
                    print(f"域已存在: {domain['name']}")

        print("九大域初始化完成")

    async def create_sample_frameworks(self, novel_id: int = 1):
        """创建示例文化框架"""
        print("创建示例文化框架...")

        async with self.pg_pool.acquire() as conn:
            # 获取人域和天域的ID
            ren_yu_id = await conn.fetchval(
                "SELECT id FROM domains WHERE novel_id = $1 AND code = 'ren_yu'",
                novel_id
            )
            tian_yu_id = await conn.fetchval(
                "SELECT id FROM domains WHERE novel_id = $1 AND code = 'tian_yu'",
                novel_id
            )

            # 获取维度ID
            dimensions = await conn.fetch(
                "SELECT id, code FROM cultural_dimensions ORDER BY sort_order"
            )

            if ren_yu_id and tian_yu_id:
                # 为人域和天域创建所有六个维度的框架
                for dim in dimensions:
                    for domain_id, domain_code in [(ren_yu_id, "ren_yu"), (tian_yu_id, "tian_yu")]:
                        domain_name = "人域" if domain_code == "ren_yu" else "天域"

                        existing = await conn.fetchrow(
                            "SELECT id FROM cultural_frameworks WHERE novel_id = $1 AND domain_id = $2 AND dimension_id = $3",
                            novel_id, domain_id, dim['id']
                        )

                        if not existing:
                            framework_name = f"{domain_name}{dim['name']}框架"

                            framework_id = await conn.fetchval("""
                                INSERT INTO cultural_frameworks
                                (novel_id, domain_id, dimension_id, framework_name, version, completeness_score)
                                VALUES ($1, $2, $3, $4, '1.0', 30)
                                RETURNING id
                            """, novel_id, domain_id, dim['id'], framework_name)

                            print(f"创建框架: {framework_name} (ID: {framework_id})")

        print("示例文化框架创建完成")

    async def insert_sample_cultural_elements(self, novel_id: int = 1):
        """插入示例文化要素"""
        print("插入示例文化要素...")

        async with self.pg_pool.acquire() as conn:
            # 获取人域神话宗教框架
            framework = await conn.fetchrow("""
                SELECT cf.id, d.code as domain_code, cd.code as dimension_code
                FROM cultural_frameworks cf
                JOIN domains d ON cf.domain_id = d.id
                JOIN cultural_dimensions cd ON cf.dimension_id = cd.id
                WHERE cf.novel_id = $1 AND d.code = 'ren_yu' AND cd.code = 'myth_religion'
            """, novel_id)

            if framework:
                # 人域神话宗教要素
                elements = [
                    {
                        "element_type": "belief",
                        "name": "链是看不见的鞭子",
                        "code": "chain_whip_doctrine",
                        "category": "core_doctrine",
                        "attributes": {
                            "teaching": "顺链得安、逆链遭殃",
                            "implications": "命运由链决定，反抗无用",
                            "enforcement": "通过日常教化和仪式强化"
                        },
                        "importance": 10,
                        "tags": ["核心信条", "命运观", "顺从教育"]
                    },
                    {
                        "element_type": "institution",
                        "name": "乡祠",
                        "code": "village_shrine",
                        "category": "local_temple",
                        "attributes": {
                            "function": "祭祀、链籍管理、社区仲裁",
                            "deities": "环祖（九环祖像）",
                            "officials": "乡祭掌礼",
                            "jurisdiction": "村落级别"
                        },
                        "importance": 8,
                        "tags": ["宗教机构", "基层管理", "社区中心"]
                    },
                    {
                        "element_type": "ritual",
                        "name": "归环葬礼",
                        "code": "return_ring_funeral",
                        "category": "death_ritual",
                        "attributes": {
                            "procedure": "请冥域渡链僧诵《归环文》",
                            "discrimination": "无链籍者草葬、不得入册",
                            "meaning": "确保亡魂顺链归位",
                            "social_function": "强化身份等级"
                        },
                        "importance": 7,
                        "tags": ["丧葬仪式", "身份歧视", "来世观念"]
                    },
                    {
                        "element_type": "symbol",
                        "name": "九环祖像",
                        "code": "nine_ring_ancestor",
                        "category": "sacred_object",
                        "attributes": {
                            "appearance": "九个相连的环形图案",
                            "symbolism": "完整链条的理想状态",
                            "location": "各乡祠中心位置",
                            "worship": "日常祭拜和重大仪式"
                        },
                        "importance": 9,
                        "tags": ["神圣象征", "祖先崇拜", "链条理念"]
                    }
                ]

                for element in elements:
                    existing = await conn.fetchrow(
                        "SELECT id FROM cultural_elements WHERE framework_id = $1 AND code = $2",
                        framework['id'], element["code"]
                    )

                    if not existing:
                        element_id = await conn.fetchval("""
                            INSERT INTO cultural_elements
                            (novel_id, framework_id, element_type, name, code, category,
                             attributes, importance, influence_scope, status, tags)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'local', 'active', $9)
                            RETURNING id
                        """,
                        novel_id, framework['id'], element["element_type"],
                        element["name"], element["code"], element["category"],
                        element["attributes"], element["importance"], element["tags"])

                        print(f"插入要素: {element['name']} (ID: {element_id})")

        print("示例文化要素插入完成")

    async def insert_sample_plot_hooks(self, novel_id: int = 1):
        """插入示例剧情钩子"""
        print("插入示例剧情钩子...")

        async with self.pg_pool.acquire() as conn:
            # 获取人域ID
            ren_yu_id = await conn.fetchval(
                "SELECT id FROM domains WHERE novel_id = $1 AND code = 'ren_yu'",
                novel_id
            )

            if ren_yu_id:
                hooks = [
                    {
                        "title": "秋试链筵伪票案",
                        "description": "年度秋试链筵上揭出大规模伪造链票案，牵涉官商勾结和籍等造假",
                        "hook_type": "crisis",
                        "drama_level": 8,
                        "scope": "regional",
                        "urgency_level": 4,
                        "involved_entities": [],
                        "required_capabilities": ["调查能力", "政治敏感度", "链票识别"],
                        "potential_outcomes": {
                            "exposure": "揭露更大的腐败网络",
                            "cover_up": "被权势压制，真相掩埋",
                            "reform": "推动籍等制度改革"
                        }
                    },
                    {
                        "title": "宗门抢选童生风波",
                        "description": "宗门外堂强制抢选有潜力的童生，引发村社民众抗议和家庭分离",
                        "hook_type": "conflict",
                        "drama_level": 7,
                        "scope": "local",
                        "urgency_level": 3,
                        "involved_entities": [],
                        "required_capabilities": ["外交斡旋", "武力对抗", "民心号召"],
                        "potential_outcomes": {
                            "negotiation": "达成妥协，建立公平选拔机制",
                            "confrontation": "暴力冲突，激化矛盾",
                            "resistance": "地下组织兴起，长期对抗"
                        }
                    },
                    {
                        "title": "祖灵续籍祭夜盗谱案",
                        "description": "祖灵续籍祭夜有人盗改家谱链印，试图伪造血脉记录改变身份等级",
                        "hook_type": "mystery",
                        "drama_level": 6,
                        "scope": "local",
                        "urgency_level": 2,
                        "involved_entities": [],
                        "required_capabilities": ["链印鉴定", "族谱研究", "夜间潜行"],
                        "potential_outcomes": {
                            "detection": "发现更大的身份造假网络",
                            "success": "成功改变某些人的命运",
                            "punishment": "严厉制裁，加强管控"
                        }
                    }
                ]

                for hook in hooks:
                    existing = await conn.fetchrow(
                        "SELECT id FROM plot_hooks WHERE novel_id = $1 AND title = $2",
                        novel_id, hook["title"]
                    )

                    if not existing:
                        hook_id = await conn.fetchval("""
                            INSERT INTO plot_hooks
                            (novel_id, domain_id, title, description, hook_type,
                             drama_level, scope, urgency_level, involved_entities,
                             required_capabilities, potential_outcomes, status)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 'available')
                            RETURNING id
                        """,
                        novel_id, ren_yu_id, hook["title"], hook["description"],
                        hook["hook_type"], hook["drama_level"], hook["scope"],
                        hook["urgency_level"], hook["involved_entities"],
                        hook["required_capabilities"], hook["potential_outcomes"])

                        print(f"插入剧情钩子: {hook['title']} (ID: {hook_id})")

        print("示例剧情钩子插入完成")

    async def initialize_complete_system(self, novel_id: int = 1):
        """完整初始化文化框架系统"""
        print("开始完整文化框架系统初始化...")

        try:
            await self.init_cultural_dimensions()
            await self.init_nine_domains(novel_id)
            await self.create_sample_frameworks(novel_id)
            await self.insert_sample_cultural_elements(novel_id)
            await self.insert_sample_plot_hooks(novel_id)

            print("文化框架系统完整初始化成功完成!")

        except Exception as e:
            print(f"初始化过程中发生错误: {e}")
            raise


async def init_cultural_framework_system():
    """初始化文化框架系统的主函数"""
    try:
        # 连接PostgreSQL
        pg_pool = await asyncpg.create_pool(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password,
            min_size=1,
            max_size=10
        )
        print("PostgreSQL 连接成功")

        # 连接MongoDB
        mongo_client = AsyncIOMotorClient(config.mongodb_url)
        mongo_db = mongo_client[config.mongodb_db]
        await mongo_client.admin.command('ping')
        print("MongoDB 连接成功")

        # 初始化系统
        initializer = CulturalFrameworkInitializer(pg_pool, mongo_db)
        await initializer.initialize_complete_system()

        # 同时初始化MongoDB文化内容
        from init_cultural_mongodb import CulturalMongoDBInitializer
        mongo_initializer = CulturalMongoDBInitializer(mongo_db)
        await mongo_initializer.initialize_cultural_system()

        await pg_pool.close()
        mongo_client.close()

        return True

    except Exception as e:
        print(f"文化框架系统初始化失败: {e}")
        return False


async def main():
    """主函数"""
    success = await init_cultural_framework_system()
    if success:
        print("文化框架系统初始化成功!")
    else:
        print("文化框架系统初始化失败!")


if __name__ == "__main__":
    asyncio.run(main())