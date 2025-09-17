"""
测试数据和示例生成脚本
创建裂世九域小说的完整示例数据
"""

import asyncio
import json
from datetime import datetime
from database.data_access import init_database, get_global_manager, get_novel_manager
from database.models import *


async def create_lieshi_jiuyu_novel():
    """创建裂世九域小说项目"""
    global_manager = get_global_manager()

    novel = Novel(
        title="裂世九域·法则链纪元",
        code="lieshi_jiuyu",
        author="示例作者",
        genre="玄幻",
        world_type="cultivation",
        settings={
            "main_theme": "力量与自由的终极矛盾",
            "core_concept": "修炼即奴役，法则链束缚",
            "ultimate_goal": "打破法则链，重构世界",
            "power_system": "法则链进阶体系"
        }
    )

    novel_id = await global_manager.create_novel(novel, "cultivation_world")
    print(f"创建小说: {novel.title} (ID: {novel_id})")
    return novel_id


async def create_entity_types(novel_id: int):
    """创建实体类型"""
    novel_manager = get_novel_manager(novel_id)

    # 获取数据库连接
    async with novel_manager.pg_pool.acquire() as conn:
        # 角色实体类型
        await conn.execute("""
            INSERT INTO entity_types (novel_id, name, display_name, schema_definition) VALUES
            ($1, 'character', '角色', $2)
            ON CONFLICT (novel_id, name) DO NOTHING
        """, novel_id, json.dumps({
            "required_fields": ["name", "origin_domain", "current_realm"],
            "optional_fields": ["title", "bloodline", "power_level", "chain_binding_degree"],
            "field_types": {
                "name": "string",
                "title": "string",
                "origin_domain": "reference:category",
                "current_realm": "reference:category",
                "bloodline": "reference:category",
                "power_level": "integer",
                "chain_binding_degree": "integer",
                "is_chain_breaker": "boolean"
            }
        }))

        # 地点实体类型
        await conn.execute("""
            INSERT INTO entity_types (novel_id, name, display_name, schema_definition) VALUES
            ($1, 'location', '地点', $2)
            ON CONFLICT (novel_id, name) DO NOTHING
        """, novel_id, json.dumps({
            "required_fields": ["name", "domain", "type"],
            "optional_fields": ["controlling_organization", "law_chain_influence", "danger_level"],
            "field_types": {
                "name": "string",
                "domain": "reference:category",
                "type": "string",
                "controlling_organization": "reference:entity",
                "law_chain_influence": "integer",
                "danger_level": "integer"
            }
        }))

        # 势力实体类型
        await conn.execute("""
            INSERT INTO entity_types (novel_id, name, display_name, schema_definition) VALUES
            ($1, 'organization', '势力', $2)
            ON CONFLICT (novel_id, name) DO NOTHING
        """, novel_id, json.dumps({
            "required_fields": ["name", "type", "domain"],
            "optional_fields": ["leader", "law_chain_control", "influence_scope"],
            "field_types": {
                "name": "string",
                "type": "string",
                "domain": "reference:category",
                "leader": "reference:entity",
                "law_chain_control": "integer",
                "influence_scope": "string"
            }
        }))

    print("创建实体类型完成")


async def create_categories(novel_id: int):
    """创建分类数据"""
    novel_manager = get_novel_manager(novel_id)

    async with novel_manager.pg_pool.acquire() as conn:
        # 九大域
        domains = [
            ("人域", "human", "最低等之地，血脉残缺者的聚居区", 1),
            ("天域", "heaven", "命运法则主宰之地，由天命王朝统治", 9),
            ("灵域", "spirit", "灵气丰饶，宗门林立", 7),
            ("荒域", "wasteland", "荒芜废墟，埋葬无数断链者残魂", 3),
            ("冥域", "underworld", "死亡法则执掌，生死轮回门户", 8),
            ("魔域", "demon", "链条崩坏，混乱与疯狂之地", 6),
            ("虚域", "void", "虚幻法则之域，预言与幻境", 5),
            ("海域", "ocean", "深海古族，掌控时空链片段", 8),
            ("源域", "origin", "传说中的起源地，埋葬完整法则链", 10)
        ]

        for name, code, desc, level in domains:
            await conn.execute("""
                INSERT INTO categories (novel_id, type, name, code, description, level, attributes)
                VALUES ($1, 'domain', $2, $3, $4, $5, $6)
                ON CONFLICT (novel_id, type, code) DO NOTHING
            """, novel_id, name, code, desc, level, json.dumps({"power_level": level}))

        # 修炼境界
        realms = [
            ("凡身", "mortal", "链痕未开，无法修炼", 1),
            ("开脉", "open_meridian", "激活血脉链痕，初触碎链", 2),
            ("归源", "return_source", "与法则链契合，获得稳定力量", 3),
            ("封侯", "noble_lord", "能以链之力统御一域/宗门", 4),
            ("破界", "break_boundary", "打破域壁，调用跨域法则链", 5),
            ("帝境", "emperor", "执掌域链，能操纵法则权柄", 6),
            ("裂世者", "world_splitter", "融合多条法则链，企图重构世界", 7)
        ]

        for name, code, desc, level in realms:
            await conn.execute("""
                INSERT INTO categories (novel_id, type, name, code, description, level, attributes)
                VALUES ($1, 'realm', $2, $3, $4, $5, $6)
                ON CONFLICT (novel_id, type, code) DO NOTHING
            """, novel_id, name, code, desc, level, json.dumps({
                "power_threshold": level * 10000,
                "chain_binding_degree": level * 10
            }))

        # 血脉类型
        bloodlines = [
            ("完整链痕", "complete", "天生血脉完整，修炼天才", 5),
            ("残缺链痕", "incomplete", "血脉残缺，修炼困难", 2),
            ("断裂链痕", "broken", "血脉断裂，几乎无法修炼", 1),
            ("源链血脉", "source", "传说中的源链血脉", 10)
        ]

        for name, code, desc, level in bloodlines:
            await conn.execute("""
                INSERT INTO categories (novel_id, type, name, code, description, level, attributes)
                VALUES ($1, 'bloodline', $2, $3, $4, $5, $6)
                ON CONFLICT (novel_id, type, code) DO NOTHING
            """, novel_id, name, code, desc, level, json.dumps({"talent_modifier": level}))

    print("创建分类数据完成")


async def create_sample_characters(novel_id: int):
    """创建示例角色"""
    novel_manager = get_novel_manager(novel_id)

    # 主角
    protagonist_request = CreateEntityRequest(
        novel_id=novel_id,
        entity_type_name="character",
        name="林逸",
        code="protagonist",
        attributes={
            "origin_domain": "人域",
            "current_realm": "开脉",
            "bloodline": "源链血脉",
            "power_level": 5000,
            "chain_binding_degree": 10,
            "is_chain_breaker": True
        },
        tags=["主角", "断链者", "源链血脉"],
        priority=100,
        profile={
            "identity": {
                "full_name": "林逸",
                "aliases": ["断链者", "逆天者", "源链之子"],
                "age": 18,
                "gender": "male"
            },
            "appearance": {
                "description": "身材精瘦，双眼偶现金芒",
                "height": "175cm",
                "distinctive_features": [
                    "左臂隐藏的特殊链痕",
                    "愤怒时眼中会闪过金色光芒"
                ]
            },
            "background": {
                "origin": {
                    "birthplace": "人域贫民区",
                    "family": {
                        "father": "疑似古代断链者后裔，已故",
                        "mother": "温柔善良的普通人，已故",
                        "family_secret": "祖上曾是古代断链者"
                    },
                    "childhood_trauma": "目睹父母被链枷处决"
                },
                "formative_events": [
                    {
                        "age": 7,
                        "event": "父母被处决",
                        "impact": "种下复仇种子和对法则链的恐惧"
                    },
                    {
                        "age": 16,
                        "event": "荒域遗迹奇遇",
                        "impact": "获得断链术传承，开始修炼之路"
                    }
                ]
            },
            "abilities": {
                "innate_abilities": [
                    {
                        "name": "断链视觉",
                        "description": "能看到他人身上的法则链束缚",
                        "manifestation": "双眼金芒闪烁"
                    },
                    {
                        "name": "源链共鸣",
                        "description": "体内源链碎片对完整法则链的共鸣"
                    }
                ],
                "learned_skills": [
                    {
                        "name": "碎链拳",
                        "category": "断链术",
                        "level": "入门",
                        "description": "暂时断开敌人与法则链的联系"
                    }
                ]
            }
        }
    )

    protagonist_id = await novel_manager.create_entity(protagonist_request)
    print(f"创建主角: 林逸 (ID: {protagonist_id})")

    # 神秘老者（导师）
    mentor_request = CreateEntityRequest(
        novel_id=novel_id,
        entity_type_name="character",
        name="古长风",
        code="mentor",
        attributes={
            "origin_domain": "荒域",
            "current_realm": "帝境",
            "bloodline": "断裂链痕",
            "power_level": 500000,
            "chain_binding_degree": 5,
            "is_chain_breaker": True
        },
        tags=["导师", "古代断链者", "残魂"],
        priority=80,
        profile={
            "identity": {
                "full_name": "古长风",
                "aliases": ["荒域老者", "断链宗师", "最后的反抗者"],
                "age": 1000,
                "gender": "male",
                "status": "残魂状态"
            },
            "background": {
                "origin": {
                    "era": "千年前的断链战争时代",
                    "role": "断链者联盟首领",
                    "tragedy": "最后据点被攻破，以残魂形式存活"
                },
                "achievements": [
                    "创立完整的断链术体系",
                    "领导千年前的反抗战争",
                    "保存源链传承"
                ]
            },
            "relationship_with_protagonist": {
                "role": "精神导师",
                "legacy": "传授断链术和世界真相",
                "final_gift": "源链碎片和最后的力量"
            }
        }
    )

    mentor_id = await novel_manager.create_entity(mentor_request)
    print(f"创建导师: 古长风 (ID: {mentor_id})")

    # 天域执法者队长
    enforcer_request = CreateEntityRequest(
        novel_id=novel_id,
        entity_type_name="character",
        name="司马玄",
        code="enforcer_captain",
        attributes={
            "origin_domain": "天域",
            "current_realm": "封侯",
            "bloodline": "完整链痕",
            "power_level": 80000,
            "chain_binding_degree": 80,
            "is_chain_breaker": False
        },
        tags=["反派", "执法者", "天域"],
        priority=60,
        profile={
            "identity": {
                "full_name": "司马玄",
                "titles": ["天域执法队长", "链枷执行者"],
                "age": 45,
                "gender": "male"
            },
            "personality": {
                "traits": ["冷酷无情", "绝对服从", "法则至上"],
                "motivation": "维护天域秩序，清除异端"
            },
            "role_in_story": "早期主要反派，代表法则链的压迫力量"
        }
    )

    enforcer_id = await novel_manager.create_entity(enforcer_request)
    print(f"创建反派: 司马玄 (ID: {enforcer_id})")

    return protagonist_id, mentor_id, enforcer_id


async def create_sample_locations(novel_id: int):
    """创建示例地点"""
    novel_manager = get_novel_manager(novel_id)

    # 人域贫民区
    slum_request = CreateEntityRequest(
        novel_id=novel_id,
        entity_type_name="location",
        name="人域贫民区",
        code="human_slum",
        attributes={
            "domain": "人域",
            "type": "居住区",
            "danger_level": 2,
            "law_chain_influence": 1
        },
        tags=["贫民区", "主角出身地"],
        priority=70,
        profile={
            "description": {
                "overview": "人域最底层的居住区域",
                "conditions": "破旧不堪，生活条件恶劣",
                "population": "血脉残缺者和他们的后代",
                "atmosphere": "压抑、绝望，被社会遗弃"
            },
            "significance": "主角的出生地，见证了血脉歧视的残酷"
        }
    )

    slum_id = await novel_manager.create_entity(slum_request)
    print(f"创建地点: 人域贫民区 (ID: {slum_id})")

    # 荒域遗迹
    ruins_request = CreateEntityRequest(
        novel_id=novel_id,
        entity_type_name="location",
        name="荒域古战场遗迹",
        code="wasteland_ruins",
        attributes={
            "domain": "荒域",
            "type": "古战场",
            "danger_level": 8,
            "law_chain_influence": 3
        },
        tags=["遗迹", "传承地", "断链者"],
        priority=80,
        profile={
            "description": {
                "overview": "千年前断链战争的最后战场",
                "remains": "断裂的石柱、残破的法阵、古老的血迹",
                "atmosphere": "死寂中蕴含着不屈的意志",
                "hidden_secrets": "断链术传承和源链碎片"
            },
            "historical_significance": "断链者最后的据点，古长风的藏身之所"
        }
    )

    ruins_id = await novel_manager.create_entity(ruins_request)
    print(f"创建地点: 荒域古战场遗迹 (ID: {ruins_id})")

    return slum_id, ruins_id


async def create_sample_organizations(novel_id: int):
    """创建示例势力"""
    novel_manager = get_novel_manager(novel_id)

    # 天命王朝
    dynasty_request = CreateEntityRequest(
        novel_id=novel_id,
        entity_type_name="organization",
        name="天命王朝",
        code="heavenly_dynasty",
        attributes={
            "type": "帝国",
            "domain": "天域",
            "law_chain_control": 10,
            "influence_scope": "多域"
        },
        tags=["帝国", "统治者", "命运法则"],
        priority=90,
        profile={
            "description": {
                "nature": "以命运法则链为核心的统治体系",
                "power_source": "命运链操控",
                "governance": "血脉等级制度"
            },
            "characteristics": [
                "操控众生命运",
                "维持血脉歧视体系",
                "垄断法则链资源"
            ],
            "role_in_story": "主要反派势力，代表压迫和束缚"
        }
    )

    dynasty_id = await novel_manager.create_entity(dynasty_request)
    print(f"创建势力: 天命王朝 (ID: {dynasty_id})")

    # 裂世反叛军
    rebels_request = CreateEntityRequest(
        novel_id=novel_id,
        entity_type_name="organization",
        name="裂世反叛军",
        code="world_splitter_rebels",
        attributes={
            "type": "反叛组织",
            "domain": "隐秘",
            "law_chain_control": 2,
            "influence_scope": "地下"
        },
        tags=["反叛军", "断链者", "自由"],
        priority=70,
        profile={
            "description": {
                "nature": "古代断链者的后继组织",
                "goal": "推翻法则链统治，重获自由",
                "methods": "断链术传承，秘密活动"
            },
            "current_status": "几乎被消灭，只剩零星传承",
            "hope": "主角的觉醒带来新的希望"
        }
    )

    rebels_id = await novel_manager.create_entity(rebels_request)
    print(f"创建势力: 裂世反叛军 (ID: {rebels_id})")

    return dynasty_id, rebels_id


async def create_sample_relationships(novel_id: int, protagonist_id: int, mentor_id: int,
                                    enforcer_id: int, dynasty_id: int):
    """创建示例关系"""
    novel_manager = get_novel_manager(novel_id)

    # 主角 - 导师关系
    mentor_rel_id = await novel_manager.create_relationship(
        mentor_id, protagonist_id, "传承",
        strength=10,
        attributes={
            "type": "师父-弟子",
            "legacy": "断链术",
            "emotional_bond": "深度信任和敬重"
        }
    )
    print(f"创建关系: 导师传承主角 (ID: {mentor_rel_id})")

    # 主角 - 反派关系
    enemy_rel_id = await novel_manager.create_relationship(
        protagonist_id, enforcer_id, "仇恨",
        strength=8,
        attributes={
            "type": "杀父仇人",
            "origin": "执法者杀害主角父母",
            "future": "必有一战"
        }
    )
    print(f"创建关系: 主角仇恨反派 (ID: {enemy_rel_id})")

    # 反派 - 天命王朝关系
    loyalty_rel_id = await novel_manager.create_relationship(
        enforcer_id, dynasty_id, "效忠",
        strength=9,
        attributes={
            "type": "忠诚下属",
            "role": "执法队长",
            "duty": "清除异端"
        }
    )
    print(f"创建关系: 反派效忠王朝 (ID: {loyalty_rel_id})")


async def create_sample_events(novel_id: int, protagonist_id: int, mentor_id: int, enforcer_id: int):
    """创建示例事件"""
    novel_manager = get_novel_manager(novel_id)

    # 灭门事件
    tragedy_event = Event(
        novel_id=novel_id,
        name="血夜灭门",
        event_type="悲剧",
        sequence_order=1,
        impact_level=10,
        scope="personal",
        description="天域执法者处决主角父母，主角目睹惨剧",
        attributes={
            "emotional_impact": "种下复仇种子",
            "world_building": "展现法则链压迫",
            "character_development": "主角觉醒的起点"
        }
    )

    tragedy_id = await novel_manager.create_event(tragedy_event, [protagonist_id, enforcer_id])
    print(f"创建事件: 血夜灭门 (ID: {tragedy_id})")

    # 传承事件
    inheritance_event = Event(
        novel_id=novel_id,
        name="荒域传承",
        event_type="觉醒",
        sequence_order=2,
        impact_level=9,
        scope="personal",
        description="主角在荒域遗迹中遇到古长风，获得断链术传承",
        attributes={
            "power_gain": "断链术入门",
            "knowledge_gain": "世界真相",
            "identity_discovery": "源链血脉觉醒"
        }
    )

    inheritance_id = await novel_manager.create_event(inheritance_event, [protagonist_id, mentor_id])
    print(f"创建事件: 荒域传承 (ID: {inheritance_id})")


async def create_sample_story_content(novel_id: int):
    """创建示例故事内容"""
    novel_manager = get_novel_manager(novel_id)

    # 第一章故事内容
    chapter1_content = {
        "novel_id": novel_id,
        "novel_code": "lieshi_jiuyu",
        "story_node_id": 1,
        "content": {
            "chapter_info": {
                "volume": "第一卷：九域觉醒",
                "chapter": "第一章：被压迫者",
                "scene": "血夜灭门",
                "sequence": 1
            },
            "narrative": {
                "setting": {
                    "time": {
                        "period": "深夜时分",
                        "weather": "血月当空",
                        "season": "寒冬",
                        "world_time": "法则链纪元三千年"
                    },
                    "location": {
                        "name": "人域贫民区小院",
                        "description": "破旧的小院，被高墙环绕",
                        "atmosphere": "压抑、绝望、死寂"
                    }
                },
                "key_moments": [
                    {
                        "moment": "天域执法者降临",
                        "description": "数十名黑甲执法者从天而降，包围小院",
                        "impact": "命运的审判即将开始"
                    },
                    {
                        "moment": "链枷降下",
                        "description": "金色的巨大锁链在空中盘旋，父母被束缚",
                        "impact": "主角内心种下对法则链的恐惧和仇恨"
                    }
                ],
                "dialogue": [
                    {
                        "speaker": "执法者队长",
                        "content": "残缺血脉者，胆敢私藏禁忌传承！",
                        "tone": "冷酷无情",
                        "subtext": "代表天域的绝对权威"
                    },
                    {
                        "speaker": "主角父亲",
                        "content": "大人明鉴，我们只是普通人...",
                        "tone": "恐惧中带着绝望",
                        "subtext": "最后的挣扎和保护欲"
                    }
                ]
            },
            "world_building_reveals": [
                {
                    "concept": "血脉歧视制度",
                    "explanation": "天域以血脉完整性划分等级，残缺者被视为低等",
                    "evidence": "执法者的轻蔑态度和处决理由"
                }
            ]
        },
        "impact": {
            "character_development": {
                "protagonist": {
                    "before": "无忧无虑的孩子",
                    "after": "背负仇恨的孤儿",
                    "key_change": "从天真转向坚韧"
                }
            }
        },
        "metadata": {
            "word_count": 3500,
            "themes": ["压迫与反抗", "命运与自由", "亲情与复仇"],
            "mood": "悲剧性的开端"
        }
    }

    await novel_manager.mongo_db.story_content.insert_one(chapter1_content)
    print("创建故事内容: 第一章血夜灭门")


async def create_sample_data():
    """创建完整的示例数据"""
    print("开始创建裂世九域示例数据...")

    # 初始化数据库
    await init_database()

    # 创建小说项目
    novel_id = await create_lieshi_jiuyu_novel()

    # 创建基础数据
    await create_entity_types(novel_id)
    await create_categories(novel_id)

    # 创建实体
    protagonist_id, mentor_id, enforcer_id = await create_sample_characters(novel_id)
    slum_id, ruins_id = await create_sample_locations(novel_id)
    dynasty_id, rebels_id = await create_sample_organizations(novel_id)

    # 创建关系
    await create_sample_relationships(novel_id, protagonist_id, mentor_id, enforcer_id, dynasty_id)

    # 创建事件
    await create_sample_events(novel_id, protagonist_id, mentor_id, enforcer_id)

    # 创建故事内容
    await create_sample_story_content(novel_id)

    print(f"\n裂世九域示例数据创建完成!")
    print(f"小说ID: {novel_id}")
    print(f"主角ID: {protagonist_id}")
    print(f"可以使用MCP工具进行查询和管理")

    return {
        "novel_id": novel_id,
        "characters": {
            "protagonist": protagonist_id,
            "mentor": mentor_id,
            "enforcer": enforcer_id
        },
        "locations": {
            "slum": slum_id,
            "ruins": ruins_id
        },
        "organizations": {
            "dynasty": dynasty_id,
            "rebels": rebels_id
        }
    }


if __name__ == "__main__":
    asyncio.run(create_sample_data())