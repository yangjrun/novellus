"""
MongoDB 文化框架集合初始化脚本
用于存储详细的文化内容和描述
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import config


class CulturalMongoDBInitializer:
    """文化框架 MongoDB 初始化器"""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database

    async def create_cultural_indexes(self):
        """创建文化框架相关的索引"""
        print("创建文化框架 MongoDB 索引...")

        # domain_cultures 集合索引
        await self.database.domain_cultures.create_index([
            ("novel_id", 1),
            ("domain_code", 1)
        ], unique=True)
        await self.database.domain_cultures.create_index([
            ("novel_code", 1)
        ])
        await self.database.domain_cultures.create_index([
            ("power_level", -1)
        ])

        # cultural_contents 集合索引
        await self.database.cultural_contents.create_index([
            ("novel_id", 1),
            ("domain_code", 1),
            ("dimension_code", 1)
        ])
        await self.database.cultural_contents.create_index([
            ("content_type", 1)
        ])
        await self.database.cultural_contents.create_index([
            ("framework_id", 1)
        ])
        await self.database.cultural_contents.create_index([
            ("tags", 1)
        ])

        # cultural_practices 集合索引
        await self.database.cultural_practices.create_index([
            ("novel_id", 1),
            ("domain_code", 1)
        ])
        await self.database.cultural_practices.create_index([
            ("practice_type", 1)
        ])
        await self.database.cultural_practices.create_index([
            ("importance_level", -1)
        ])

        # cultural_narratives 集合索引
        await self.database.cultural_narratives.create_index([
            ("novel_id", 1),
            ("narrative_type", 1)
        ])
        await self.database.cultural_narratives.create_index([
            ("involved_domains", 1)
        ])

        # plot_hook_details 集合索引
        await self.database.plot_hook_details.create_index([
            ("novel_id", 1),
            ("hook_id", 1)
        ], unique=True)
        await self.database.plot_hook_details.create_index([
            ("domain_code", 1)
        ])
        await self.database.plot_hook_details.create_index([
            ("drama_level", -1)
        ])

        # cultural_evolution_records 集合索引
        await self.database.cultural_evolution_records.create_index([
            ("novel_id", 1),
            ("domain_code", 1)
        ])
        await self.database.cultural_evolution_records.create_index([
            ("timeline.period", 1)
        ])

        print("文化框架 MongoDB 索引创建完成")

    async def insert_cultural_dimensions_template(self):
        """插入六维文化框架模板"""
        print("插入六维文化框架模板...")

        dimensions_template = {
            "template_name": "六维文化框架模板",
            "version": "1.0",
            "description": "标准的六维文化分析框架，适用于所有域的文化分析",
            "dimensions": [
                {
                    "code": "myth_religion",
                    "name": "神话与宗教",
                    "description": "信仰体系、神话传说、宗教机构、丧葬观念等",
                    "key_elements": [
                        "信条与教义", "神祇体系", "宗教机构", "仪式礼拜",
                        "丧葬观念", "禁忌戒律", "圣地圣物", "神职人员"
                    ],
                    "analysis_focus": [
                        "世界观构建", "精神支撑", "社会控制", "文化传承"
                    ]
                },
                {
                    "code": "power_law",
                    "name": "权力与法律",
                    "description": "政治结构、法律制度、权力分配、社会秩序等",
                    "key_elements": [
                        "政治结构", "法律体系", "执法机构", "权力分配",
                        "社会等级", "身份制度", "司法程序", "刑罚体系"
                    ],
                    "analysis_focus": [
                        "社会秩序", "权力制衡", "法理基础", "统治合法性"
                    ]
                },
                {
                    "code": "economy_tech",
                    "name": "经济与技术",
                    "description": "生产方式、贸易体系、技术水平、资源分配等",
                    "key_elements": [
                        "产业结构", "贸易网络", "货币金融", "技术水平",
                        "资源配置", "生产工具", "交通运输", "信息传播"
                    ],
                    "analysis_focus": [
                        "生产力水平", "经济模式", "技术限制", "财富分配"
                    ]
                },
                {
                    "code": "family_education",
                    "name": "家庭与教育",
                    "description": "家庭结构、婚姻制度、教育体系、社会化过程等",
                    "key_elements": [
                        "家庭结构", "婚姻制度", "教育体系", "成长仪式",
                        "社会化", "知识传承", "技能培训", "价值观教育"
                    ],
                    "analysis_focus": [
                        "社会再生产", "文化传承", "人才培养", "社会流动"
                    ]
                },
                {
                    "code": "ritual_daily",
                    "name": "仪式与日常",
                    "description": "日常生活、节庆仪式、社交礼仪、生活习俗等",
                    "key_elements": [
                        "日常作息", "饮食文化", "服饰规范", "节庆活动",
                        "社交礼仪", "生活禁忌", "休闲娱乐", "时间观念"
                    ],
                    "analysis_focus": [
                        "生活质量", "文化特色", "社会凝聚", "身份认同"
                    ]
                },
                {
                    "code": "art_entertainment",
                    "name": "艺术与娱乐",
                    "description": "艺术形式、娱乐活动、审美观念、文化表达等",
                    "key_elements": [
                        "建筑风格", "文学艺术", "音乐舞蹈", "体育竞技",
                        "手工艺术", "美学标准", "娱乐形式", "文化象征"
                    ],
                    "analysis_focus": [
                        "文化表达", "审美追求", "精神娱乐", "创新能力"
                    ]
                }
            ],
            "usage_guidelines": {
                "analysis_depth": "每个维度应包含3-5个核心要素的详细描述",
                "cross_dimension": "注意维度间的相互影响和内在联系",
                "cultural_specificity": "突出该域独有的文化特色",
                "narrative_integration": "与小说剧情和世界观保持一致"
            },
            "created_at": datetime.utcnow()
        }

        # 检查是否已存在
        existing = await self.database.cultural_framework_templates.find_one({
            "template_name": "六维文化框架模板"
        })

        if not existing:
            await self.database.cultural_framework_templates.insert_one(dimensions_template)
            print("插入六维文化框架模板")
        else:
            print("六维文化框架模板已存在")

    async def insert_sample_domain_cultures(self):
        """插入九域文化示例数据"""
        print("插入九域文化示例数据...")

        # 人域文化示例
        ren_yu_culture = {
            "novel_id": 1,
            "novel_code": "lieshi_jiuyu",
            "domain_code": "ren_yu",
            "domain_name": "人域",
            "cultural_profile": {
                "overview": {
                    "description": "最低等之地，血脉残缺者的聚居区，主角出身地",
                    "dominant_traits": ["血脉歧视", "修炼困难", "社会底层"],
                    "core_conflicts": ["等级固化", "资源稀缺", "希望渺茫"],
                    "unique_features": ["链籍制度", "环祖崇拜", "顺链文化"]
                },
                "power_dynamics": {
                    "ruling_class": "天域委派官员",
                    "local_authority": "县府吏治 + 宗门驻坊",
                    "enforcement": "缚司、巡链官、契官",
                    "resistance": "隐秘的断链传承"
                },
                "social_stratification": {
                    "hierarchy": [
                        {"level": 1, "name": "黄籍", "description": "良籍，少数有完整链痕者"},
                        {"level": 2, "name": "灰籍", "description": "苦役，链痕残缺但可修补"},
                        {"level": 3, "name": "黑籍", "description": "罪籍，链痕断裂或无链痕"}
                    ],
                    "mobility": "极其困难，需要巨大代价或奇遇"
                },
                "cultural_symbols": {
                    "sacred": ["九环祖像", "链印", "环石"],
                    "taboo": ["断骨羹", "逆链行为", "伪造链票"],
                    "architectural": ["环窗", "环渠", "祭司分坊"]
                }
            },
            "detailed_frameworks": {
                "myth_religion": {
                    "core_beliefs": {
                        "chain_doctrine": "链是'看不见的鞭子'，顺链得安、逆链遭殃",
                        "fate_acceptance": "命运由链决定，反抗无用",
                        "afterlife": "顺链而归，入环为安"
                    },
                    "institutions": {
                        "local_shrines": {
                            "name": "乡祠",
                            "deities": "环祖（九环祖像）",
                            "officials": "乡祭掌礼",
                            "functions": ["祭祀", "链籍管理", "社区仲裁"]
                        },
                        "urban_temples": {
                            "name": "祭司分坊",
                            "hierarchy": "隶属天域祭司议会",
                            "functions": ["宗教指导", "链测", "丧葬服务"]
                        }
                    },
                    "practices": {
                        "funeral_rites": {
                            "procedure": "请冥域渡链僧诵《归环文》",
                            "discrimination": "无链籍者草葬、不得入册",
                            "meaning": "确保亡魂顺链归位"
                        },
                        "daily_worship": {
                            "morning": "对环石默念链经",
                            "evening": "向祖像汇报一日善行",
                            "monthly": "乡祠集体祭祀"
                        }
                    }
                },
                "power_law": {
                    "government_structure": {
                        "dual_system": "县府（吏治）+ 宗门驻坊（修治）",
                        "oversight": "天域巡链司监督",
                        "coordination": "重大案件必须报告天域"
                    },
                    "identity_system": {
                        "chain_registration": {
                            "yellow": "链籍黄等 - 良籍",
                            "gray": "链籍灰等 - 苦役",
                            "black": "链籍黑等 - 罪籍"
                        },
                        "mobility_rules": "越级通婚需赎籍，功勋可改籍"
                    },
                    "legal_framework": {
                        "crimes": {
                            "escape_registration": "逃籍/伪票 → 笞与流",
                            "forbidden_knowledge": "传授断链术 → 加缚或链枷",
                            "rebellion": "聚众抗链 → 全族连坐"
                        },
                        "enforcement": {
                            "county_level": "缚司负责日常执法",
                            "circuit_level": "巡链官巡回审理",
                            "community_level": "坊内契官维持秩序"
                        }
                    }
                }
            },
            "plot_seeds": [
                {
                    "title": "秋试链筵伪票案",
                    "setup": "年度秋试链筵上揭出伪造链票案",
                    "implications": ["官商勾结", "籍等造假", "社会动荡"],
                    "potential_developments": ["主角被卷入", "更大阴谋浮现", "籍等制度质疑"]
                },
                {
                    "title": "宗门抢选风波",
                    "setup": "宗门外堂抢选童生，引发村社抗议",
                    "implications": ["人才流失", "家庭分离", "反抗情绪"],
                    "potential_developments": ["暴力冲突", "制度改革压力", "地下组织活跃"]
                }
            ],
            "metadata": {
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "version": "1.0",
                "completeness": 85,
                "tags": ["基础域", "主角出身", "底层社会", "等级制度"]
            }
        }

        # 天域文化示例
        tian_yu_culture = {
            "novel_id": 1,
            "novel_code": "lieshi_jiuyu",
            "domain_code": "tian_yu",
            "domain_name": "天域",
            "cultural_profile": {
                "overview": {
                    "description": "命运法则主宰之地，由天命王朝统治的核心域",
                    "dominant_traits": ["命运操控", "血脉等级制", "绝对权威"],
                    "core_conflicts": ["权力斗争", "血脉纯化", "秩序维护"],
                    "unique_features": ["三权合一", "链算所", "御环台"]
                },
                "power_dynamics": {
                    "supreme_authority": "天命王朝",
                    "power_structure": "王朝（政）+ 祭司（教）+ 宗门（术）",
                    "enforcement": "御环台终审，巡链司执行",
                    "legitimacy": "血脉纯度 + 链之眷顾"
                }
            },
            "detailed_frameworks": {
                "myth_religion": {
                    "orthodox_theology": {
                        "fundamental_doctrine": "链=天道，链合即德、断链即罪",
                        "sacred_texts": "《环典石经》为至高教律",
                        "divine_mandate": "王朝承天命而治理万域"
                    },
                    "institutional_hierarchy": {
                        "imperial_authority": "天命王朝主政",
                        "religious_authority": "祭司议会释链定法",
                        "ceremonial_center": "御前九环观主持国礼"
                    },
                    "afterlife_system": {
                        "imperial_capital": "归环台集体渡魂",
                        "nobility": "贵族专享金环葬",
                        "commoners": "标准环葬流程"
                    }
                },
                "power_law": {
                    "trinity_system": {
                        "political": "王朝负责行政管理",
                        "religious": "祭司负责法理解释",
                        "technical": "宗门负责链技应用",
                        "integration": "三权互为表里，制衡统一"
                    },
                    "legal_codes": {
                        "chain_registration_law": "链籍法 - 身份认定与管理",
                        "contract_law": "链契令 - 契约与交易规范",
                        "seal_law": "环印律 - 权力象征与使用"
                    },
                    "social_mobility": {
                        "merit_promotion": "功勋可'赎籍加缚'",
                        "marriage_rules": "越级通婚需'三印合奏'",
                        "career_paths": "观法→御史→缚司→巡链司→御环台"
                    }
                }
            },
            "metadata": {
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "version": "1.0",
                "completeness": 75,
                "tags": ["统治核心", "权力中心", "正统文化", "等级森严"]
            }
        }

        # 插入文化数据
        domain_cultures = [ren_yu_culture, tian_yu_culture]

        for culture in domain_cultures:
            existing = await self.database.domain_cultures.find_one({
                "novel_id": culture["novel_id"],
                "domain_code": culture["domain_code"]
            })

            if not existing:
                await self.database.domain_cultures.insert_one(culture)
                print(f"插入 {culture['domain_name']} 文化数据")
            else:
                print(f"{culture['domain_name']} 文化数据已存在")

    async def create_cultural_collections(self):
        """创建文化框架相关的MongoDB集合"""
        print("创建文化框架 MongoDB 集合...")

        collections = [
            "cultural_framework_templates",  # 文化框架模板
            "domain_cultures",              # 域文化总览
            "cultural_contents",            # 详细文化内容
            "cultural_practices",           # 文化实践与习俗
            "cultural_narratives",          # 文化叙述与故事
            "plot_hook_details",            # 剧情钩子详情
            "cultural_evolution_records",   # 文化变迁记录
            "cross_domain_interactions"     # 跨域文化交互
        ]

        existing_collections = await self.database.list_collection_names()

        for collection_name in collections:
            if collection_name not in existing_collections:
                await self.database.create_collection(collection_name)
                print(f"创建集合: {collection_name}")
            else:
                print(f"集合已存在: {collection_name}")

        print("文化框架 MongoDB 集合创建完成")

    async def initialize_cultural_system(self):
        """完整初始化文化框架系统"""
        print("开始文化框架系统初始化...")

        await self.create_cultural_collections()
        await self.create_cultural_indexes()
        await self.insert_cultural_dimensions_template()
        await self.insert_sample_domain_cultures()

        print("文化框架系统初始化完成!")


async def init_cultural_mongodb():
    """初始化文化框架 MongoDB 数据库"""
    try:
        # 连接 MongoDB
        client = AsyncIOMotorClient(config.mongodb_url)
        database = client[config.mongodb_db]

        # 测试连接
        await client.admin.command('ping')
        print(f"成功连接到 MongoDB: {config.mongodb_db}")

        # 初始化文化框架系统
        initializer = CulturalMongoDBInitializer(database)
        await initializer.initialize_cultural_system()

        return database

    except Exception as e:
        print(f"文化框架 MongoDB 初始化失败: {e}")
        raise


async def main():
    """主函数"""
    try:
        await init_cultural_mongodb()
        print("文化框架 MongoDB 初始化成功完成!")
    except Exception as e:
        print(f"初始化过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())