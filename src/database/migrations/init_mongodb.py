"""
MongoDB 集合初始化脚本
创建索引和初始化数据
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import config


class MongoDBInitializer:
    """MongoDB 初始化器"""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database

    async def create_indexes(self):
        """创建所有必要的索引"""
        print("创建 MongoDB 索引...")

        # novel_worldbuilding 集合索引
        await self.database.novel_worldbuilding.create_index([
            ("novel_id", 1)
        ])
        await self.database.novel_worldbuilding.create_index([
            ("novel_code", 1)
        ])
        await self.database.novel_worldbuilding.create_index([
            ("novel_id", 1),
            ("config_type", 1)
        ])

        # entity_profiles 集合索引
        await self.database.entity_profiles.create_index([
            ("novel_id", 1),
            ("entity_id", 1)
        ], unique=True)
        await self.database.entity_profiles.create_index([
            ("novel_code", 1)
        ])
        await self.database.entity_profiles.create_index([
            ("entity_type", 1)
        ])
        await self.database.entity_profiles.create_index([
            ("novel_id", 1),
            ("entity_type", 1)
        ])

        # story_content 集合索引
        await self.database.story_content.create_index([
            ("novel_id", 1),
            ("story_node_id", 1)
        ])
        await self.database.story_content.create_index([
            ("novel_code", 1)
        ])
        await self.database.story_content.create_index([
            ("content.chapterInfo.sequence", 1)
        ])

        # scene_descriptions 集合索引
        await self.database.scene_descriptions.create_index([
            ("novel_id", 1),
            ("location_id", 1)
        ])
        await self.database.scene_descriptions.create_index([
            ("scene_type", 1)
        ])

        # dialogue_records 集合索引
        await self.database.dialogue_records.create_index([
            ("novel_id", 1),
            ("scene_id", 1)
        ])
        await self.database.dialogue_records.create_index([
            ("participants", 1)
        ])

        # cross_novel_analysis 集合索引
        await self.database.cross_novel_analysis.create_index([
            ("analysis_type", 1)
        ])
        await self.database.cross_novel_analysis.create_index([
            ("scope.novel_ids", 1)
        ])
        await self.database.cross_novel_analysis.create_index([
            ("generated_at", -1)
        ])

        # novel_templates 集合索引
        await self.database.novel_templates.create_index([
            ("template_code", 1)
        ], unique=True)
        await self.database.novel_templates.create_index([
            ("category", 1)
        ])

        print("MongoDB 索引创建完成")

    async def insert_default_templates(self):
        """插入默认的小说模板"""
        print("插入默认小说模板...")

        templates = [
            {
                "template_name": "修仙世界观模板",
                "template_code": "cultivation_world",
                "category": "fantasy",
                "description": "传统修仙小说的世界观模板，包含境界体系、宗门势力等",
                "default_config": {
                    "power_system": {
                        "type": "cultivation",
                        "common_realms": [
                            {"name": "练气", "level": 1, "description": "初入修仙门槛"},
                            {"name": "筑基", "level": 2, "description": "奠定修仙基础"},
                            {"name": "金丹", "level": 3, "description": "凝聚金丹，寿命大增"},
                            {"name": "元婴", "level": 4, "description": "元婴出窍，神通广大"},
                            {"name": "化神", "level": 5, "description": "化神期，接触天地法则"},
                            {"name": "炼虚", "level": 6, "description": "炼虚合道，虚实相间"},
                            {"name": "合体", "level": 7, "description": "合体期，法力通天"},
                            {"name": "大乘", "level": 8, "description": "大乘期，准备飞升"},
                            {"name": "渡劫", "level": 9, "description": "渡劫飞升，成就真仙"}
                        ],
                        "power_source": "灵气修炼",
                        "advancement": "境界突破",
                        "special_mechanics": {
                            "spiritual_roots": ["金", "木", "水", "火", "土", "变异"],
                            "techniques": ["功法", "神通", "秘术"],
                            "treasures": ["法宝", "丹药", "材料"]
                        }
                    },
                    "world_structure": {
                        "type": "hierarchical",
                        "levels": ["下界", "中界", "上界", "仙界"],
                        "governance": "宗门势力",
                        "common_locations": ["宗门", "秘境", "坊市", "洞府"]
                    },
                    "social_system": {
                        "organizations": ["宗门", "家族", "散修联盟", "商会"],
                        "relationships": ["师父", "师兄弟", "道侣", "仇敌"]
                    }
                },
                "entity_templates": {
                    "character": {
                        "required_fields": ["name", "realm", "sect_affiliation"],
                        "optional_fields": ["spiritual_root", "techniques", "treasures", "background"],
                        "profile_structure": {
                            "identity": ["name", "aliases", "age", "gender"],
                            "cultivation": ["realm", "spiritual_root", "techniques"],
                            "background": ["origin", "family", "major_events"],
                            "relationships": ["master", "disciples", "friends", "enemies"],
                            "goals": ["short_term", "long_term", "ultimate"]
                        }
                    },
                    "location": {
                        "required_fields": ["name", "type", "controlling_sect"],
                        "optional_fields": ["spiritual_energy", "resources", "dangers"],
                        "types": ["宗门", "城市", "秘境", "洞府", "险地"]
                    },
                    "organization": {
                        "required_fields": ["name", "type", "territory"],
                        "optional_fields": ["founder", "specialties", "allies", "enemies"],
                        "types": ["宗门", "家族", "商会", "联盟"]
                    }
                },
                "variants": [
                    {
                        "name": "现代修仙",
                        "modifications": {
                            "setting": "现代都市",
                            "hidden_world": True,
                            "technology": "灵科融合"
                        }
                    },
                    {
                        "name": "洪荒修仙",
                        "modifications": {
                            "setting": "洪荒时代",
                            "mythology": True,
                            "saints_system": True
                        }
                    }
                ],
                "created_at": datetime.utcnow()
            },

            {
                "template_name": "西方魔幻模板",
                "template_code": "western_fantasy",
                "category": "fantasy",
                "description": "西方魔幻世界观模板，包含魔法体系、种族职业等",
                "default_config": {
                    "magic_system": {
                        "type": "elemental",
                        "elements": ["火", "水", "土", "风", "光", "暗"],
                        "advancement": "法术掌握度",
                        "classes": [
                            {"name": "法师", "focus": "元素魔法"},
                            {"name": "牧师", "focus": "神圣魔法"},
                            {"name": "术士", "focus": "血脉魔法"},
                            {"name": "德鲁伊", "focus": "自然魔法"}
                        ]
                    },
                    "world_structure": {
                        "type": "kingdom_based",
                        "governance": "王室议会",
                        "races": ["人类", "精灵", "矮人", "兽人", "龙族"],
                        "common_locations": ["王国", "魔法学院", "教会", "冒险者公会"]
                    }
                },
                "entity_templates": {
                    "character": {
                        "required_fields": ["name", "race", "class", "level"],
                        "optional_fields": ["spells", "equipment", "background"]
                    },
                    "location": {
                        "required_fields": ["name", "type", "kingdom"],
                        "optional_fields": ["magic_level", "population", "ruler"]
                    }
                },
                "created_at": datetime.utcnow()
            },

            {
                "template_name": "现代都市模板",
                "template_code": "modern_urban",
                "category": "contemporary",
                "description": "现代都市背景小说模板",
                "default_config": {
                    "setting": {
                        "time_period": "contemporary",
                        "technology_level": "current",
                        "social_structure": "modern_society"
                    },
                    "themes": ["商战", "都市情感", "职场", "家庭"],
                    "common_backgrounds": ["商业", "金融", "娱乐", "教育", "医疗"]
                },
                "entity_templates": {
                    "character": {
                        "required_fields": ["name", "occupation", "age"],
                        "optional_fields": ["education", "family", "goals"]
                    },
                    "location": {
                        "required_fields": ["name", "type", "district"],
                        "optional_fields": ["description", "owner"]
                    },
                    "organization": {
                        "required_fields": ["name", "type", "industry"],
                        "optional_fields": ["size", "reputation", "competitors"]
                    }
                },
                "created_at": datetime.utcnow()
            }
        ]

        # 清空现有模板（如果需要重新初始化）
        # await self.database.novel_templates.delete_many({})

        # 插入模板（如果不存在）
        for template in templates:
            existing = await self.database.novel_templates.find_one({
                "template_code": template["template_code"]
            })
            if not existing:
                await self.database.novel_templates.insert_one(template)
                print(f"插入模板: {template['template_name']}")
            else:
                print(f"模板已存在: {template['template_name']}")

        print("默认模板插入完成")

    async def insert_sample_worldbuilding(self):
        """插入示例世界观配置"""
        print("插入示例世界观配置...")

        # 裂世九域的世界观配置
        lieshi_worldbuilding = {
            "novel_id": 1,  # 假设裂世九域的ID是1
            "novel_code": "lieshi_jiuyu",
            "config_type": "complete_worldbuilding",
            "version": "1.0",
            "content": {
                "world_origin": {
                    "name": "裂世大劫",
                    "description": "远古时代，世界本为一体，由完整的法则链运转。后因裂世大劫，法则链断裂成九段，化为九大域。",
                    "impact": "世界分裂，法则链断裂，众生修炼本质改变"
                },
                "core_concept": {
                    "power_paradox": "力量与枷锁合一：越契合法则链，力量越强，但命运越被控制",
                    "cultivation_slavery": "修炼即奴役：修士通过契合法则链获得力量，但契合越深，法则链越能控制其思想、性格与命运",
                    "ultimate_contradiction": "是成为法则的奴隶，还是打破链条？破链者，必遭天命之罚"
                },
                "power_system": {
                    "name": "法则链进阶体系",
                    "realms": [
                        {
                            "name": "凡身",
                            "level": 1,
                            "description": "链痕未开，无法修炼",
                            "characteristics": ["无法感知法则链", "普通人状态"],
                            "advancement": "激活血脉链痕"
                        },
                        {
                            "name": "开脉",
                            "level": 2,
                            "description": "激活血脉链痕，初触碎链",
                            "characteristics": ["能感知法则链", "开始修炼"],
                            "advancement": "与法则链契合"
                        },
                        {
                            "name": "归源",
                            "level": 3,
                            "description": "与法则链契合，获得稳定力量",
                            "characteristics": ["稳定的法则链连接", "基础超凡能力"],
                            "advancement": "统御一域或宗门"
                        },
                        {
                            "name": "封侯",
                            "level": 4,
                            "description": "能以链之力统御一域/宗门",
                            "characteristics": ["领导能力", "区域影响力"],
                            "advancement": "打破域壁限制"
                        },
                        {
                            "name": "破界",
                            "level": 5,
                            "description": "打破域壁，调用跨域法则链",
                            "characteristics": ["跨域传送", "异域法则调用"],
                            "advancement": "执掌域链权柄"
                        },
                        {
                            "name": "帝境",
                            "level": 6,
                            "description": "执掌域链，能操纵法则的权柄",
                            "characteristics": ["域级控制权", "法则操纵"],
                            "advancement": "融合多条法则链"
                        },
                        {
                            "name": "裂世者",
                            "level": 7,
                            "description": "融合多条法则链，企图重构世界",
                            "characteristics": ["世界级影响力", "法则重构"],
                            "advancement": "重塑世界秩序"
                        }
                    ],
                    "special_mechanics": {
                        "chain_marks": {
                            "description": "血脉链痕，决定修炼天赋",
                            "types": ["完整", "残缺", "断裂", "特殊"],
                            "impact": "天才是天生链痕完整，凡人则链痕残缺"
                        },
                        "chain_breaking": {
                            "description": "断链术，禁忌的反抗力量",
                            "abilities": ["暂时切断法则控制", "抵抗天命"],
                            "consequences": "天命之罚"
                        },
                        "source_chain": {
                            "description": "源链，传说中的完整法则链",
                            "power": "融合并重构一切法则链",
                            "location": "源域深处"
                        }
                    }
                },
                "world_structure": {
                    "domains": [
                        {
                            "name": "人域",
                            "description": "最低等之地，血脉残缺者的聚居区。主角出身。",
                            "dominant_law": "残缺法则链",
                            "characteristics": ["血脉歧视", "修炼困难", "社会底层"],
                            "ruler": "天域附庸"
                        },
                        {
                            "name": "天域",
                            "description": "命运法则主宰之地，由天命王朝统治。",
                            "dominant_law": "命运法则链",
                            "characteristics": ["命运操控", "血脉等级制", "绝对权威"],
                            "ruler": "天命王朝"
                        },
                        {
                            "name": "灵域",
                            "description": "灵气丰饶，宗门林立，以契链为唯一通路。",
                            "dominant_law": "灵气法则链",
                            "characteristics": ["宗门林立", "修炼圣地", "竞争激烈"],
                            "ruler": "各大宗门"
                        },
                        {
                            "name": "荒域",
                            "description": "荒芜废墟，埋葬了无数断链者的残魂。",
                            "dominant_law": "破碎法则链",
                            "characteristics": ["废墟遗迹", "断链者传承", "危险重重"],
                            "ruler": "无序状态"
                        },
                        {
                            "name": "冥域",
                            "description": "死亡法则执掌，生死轮回的门户。",
                            "dominant_law": "死亡法则链",
                            "characteristics": ["生死轮回", "亡魂聚集", "冥王统治"],
                            "ruler": "冥王殿"
                        },
                        {
                            "name": "魔域",
                            "description": "链条崩坏，孕育混乱与疯狂之地。",
                            "dominant_law": "混沌法则链",
                            "characteristics": ["法则崩坏", "混沌疯狂", "魔物横行"],
                            "ruler": "魔皇"
                        },
                        {
                            "name": "虚域",
                            "description": "与未来/幻象相关的链条之域。预言与幻境。",
                            "dominant_law": "虚幻法则链",
                            "characteristics": ["预言幻境", "时空错乱", "虚实难分"],
                            "ruler": "虚空议会"
                        },
                        {
                            "name": "海域",
                            "description": "深海古族，掌控时空链片段。",
                            "dominant_law": "时空法则链",
                            "characteristics": ["深海古族", "时空控制", "神秘强大"],
                            "ruler": "海皇族"
                        },
                        {
                            "name": "源域",
                            "description": "传说中的起源地，埋葬完整法则链。",
                            "dominant_law": "完整法则链(源链)",
                            "characteristics": ["起源之地", "终极秘密", "极度危险"],
                            "ruler": "未知"
                        }
                    ]
                },
                "power_organizations": {
                    "天命王朝": {
                        "type": "empire",
                        "domain": "天域",
                        "power_source": "命运链操控",
                        "characteristics": ["命运操控", "血脉体系", "绝对统治"]
                    },
                    "法则宗门": {
                        "type": "religious_organization",
                        "domain": "各域",
                        "power_source": "法则链片段",
                        "characteristics": ["垄断修炼资源", "传承守护"]
                    },
                    "祭司议会": {
                        "type": "judicial_organization",
                        "domain": "跨域",
                        "power_source": "链痕解读",
                        "characteristics": ["裁定生死", "命运合法性"]
                    },
                    "裂世反叛军": {
                        "type": "rebel_organization",
                        "domain": "隐秘",
                        "power_source": "断链术传承",
                        "characteristics": ["逆天者残党", "反抗精神"]
                    }
                }
            },
            "metadata": {
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "tags": ["核心世界观", "法则链体系", "九域格局"],
                "version_history": []
            }
        }

        # 检查是否已存在
        existing = await self.database.novel_worldbuilding.find_one({
            "novel_id": 1,
            "config_type": "complete_worldbuilding"
        })

        if not existing:
            await self.database.novel_worldbuilding.insert_one(lieshi_worldbuilding)
            print("插入裂世九域世界观配置")
        else:
            print("裂世九域世界观配置已存在")

        print("示例世界观配置插入完成")

    async def create_collections(self):
        """创建所有需要的集合"""
        print("创建 MongoDB 集合...")

        collections = [
            "novel_worldbuilding",
            "entity_profiles",
            "story_content",
            "scene_descriptions",
            "dialogue_records",
            "cross_novel_analysis",
            "novel_templates"
        ]

        existing_collections = await self.database.list_collection_names()

        for collection_name in collections:
            if collection_name not in existing_collections:
                await self.database.create_collection(collection_name)
                print(f"创建集合: {collection_name}")
            else:
                print(f"集合已存在: {collection_name}")

        print("MongoDB 集合创建完成")

    async def initialize_all(self):
        """完整初始化"""
        print("开始 MongoDB 初始化...")

        await self.create_collections()
        await self.create_indexes()
        await self.insert_default_templates()
        await self.insert_sample_worldbuilding()

        print("MongoDB 初始化完成!")


async def init_mongodb():
    """初始化 MongoDB 数据库"""
    try:
        # 连接 MongoDB
        client = AsyncIOMotorClient(config.mongodb_url)
        database = client[config.mongodb_db]

        # 测试连接
        await client.admin.command('ping')
        print(f"成功连接到 MongoDB: {config.mongodb_db}")

        # 初始化
        initializer = MongoDBInitializer(database)
        await initializer.initialize_all()

        return database

    except Exception as e:
        print(f"MongoDB 初始化失败: {e}")
        raise


async def main():
    """主函数"""
    try:
        await init_mongodb()
        print("MongoDB 初始化成功完成!")
    except Exception as e:
        print(f"初始化过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())