#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色版本生命周期管理系统
处理角色跨域演进的完整生命周期，包括版本创建、关系演进、发展追踪等
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum

from ..connections.postgresql import postgres_db
from ..connections.mongodb import mongodb

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """变化类型"""
    CORE_IDENTITY = "core_identity"      # 核心身份变化
    CULTURAL_ADAPTATION = "cultural_adaptation"  # 文化适应
    SKILL_EVOLUTION = "skill_evolution"   # 技能演进
    RELATIONSHIP_SHIFT = "relationship_shift"  # 关系变化
    PSYCHOLOGICAL_GROWTH = "psychological_growth"  # 心理成长
    EXTERNAL_TRANSFORMATION = "external_transformation"  # 外在转变


class RelationshipTransition(Enum):
    """关系迁移类型"""
    PRESERVED = "preserved"      # 保持不变
    STRENGTHENED = "strengthened"  # 加强
    WEAKENED = "weakened"       # 削弱
    TRANSFORMED = "transformed"  # 转化为新形式
    SUSPENDED = "suspended"     # 暂时中断
    TERMINATED = "terminated"   # 彻底终止
    NEW_ESTABLISHED = "new_established"  # 新建立


@dataclass
class CharacterEssence:
    """角色本质特征（跨域不变或慢变的部分）"""
    core_personality: List[str] = field(default_factory=list)
    fundamental_values: List[str] = field(default_factory=list)
    deep_motivations: List[str] = field(default_factory=list)
    psychological_patterns: Dict[str, Any] = field(default_factory=dict)
    innate_talents: List[str] = field(default_factory=list)


@dataclass
class CharacterManifestation:
    """角色表现形式（域特定的变化部分）"""
    domain_identity: Dict[str, Any] = field(default_factory=dict)
    social_role: Dict[str, Any] = field(default_factory=dict)
    skill_expression: Dict[str, Any] = field(default_factory=dict)
    behavioral_patterns: Dict[str, Any] = field(default_factory=dict)
    relationship_network: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VersionTransition:
    """版本迁移信息"""
    from_domain: str
    to_domain: str
    transition_catalyst: str  # 迁移的故事催化剂
    anticipated_challenges: List[str]
    growth_opportunities: List[str]
    continuity_bridges: List[str]  # 连续性桥梁


class CharacterLifecycleManager:
    """角色版本生命周期管理器"""

    def __init__(self):
        self.pg_db = postgres_db
        self.mongo_db = None

    async def initialize(self):
        """初始化管理器"""
        mongo_client = await mongodb.get_client()
        self.mongo_db = mongo_client.get_database()

    async def create_new_version(
        self,
        character_unique_id: str,
        new_domain_code: str,
        new_character_data: Dict[str, Any],
        transition_context: Dict[str, Any] = None
    ) -> bool:
        """
        创建角色新版本（智能化版本管理）

        Args:
            character_unique_id: 角色唯一ID
            new_domain_code: 新域代码
            new_character_data: 新的完整角色设定
            transition_context: 迁移上下文信息

        Returns:
            bool: 创建是否成功
        """
        try:
            logger.info(f"为角色 {character_unique_id} 创建新版本，目标域: {new_domain_code}")

            # 1. 获取当前版本信息
            current_version = await self._get_current_version_info(character_unique_id)

            # 2. 深度分析角色变化
            change_analysis = await self._analyze_character_evolution(
                current_version, new_character_data, new_domain_code
            )

            # 3. 提取角色本质和表现形式
            essence = self._extract_character_essence(new_character_data)
            manifestation = self._extract_character_manifestation(new_character_data, new_domain_code)

            # 4. 分析关系网络变化
            relationship_transitions = await self._analyze_relationship_transitions(
                character_unique_id, current_version, new_character_data
            )

            # 5. 创建版本链记录
            new_version_info = await self._create_version_chain(
                current_version, new_domain_code, change_analysis, essence, manifestation
            )

            # 6. 存储完整档案
            await self._store_complete_profile(
                character_unique_id, new_version_info, new_character_data, essence, manifestation
            )

            # 7. 更新关系网络
            await self._update_relationship_network(
                character_unique_id, new_domain_code, relationship_transitions
            )

            # 8. 记录发展轨迹
            await self._record_development_trajectory(
                character_unique_id, new_version_info, change_analysis
            )

            # 9. 生成版本洞察
            insights = await self._generate_version_insights(
                character_unique_id, current_version, new_version_info, change_analysis
            )

            logger.info(f"✓ 角色 {character_unique_id} 版本创建完成，版本: {new_version_info['version']}")
            return True

        except Exception as e:
            logger.error(f"✗ 角色版本创建失败: {e}")
            return False

    async def _get_current_version_info(self, character_unique_id: str) -> Optional[Dict[str, Any]]:
        """获取当前版本的完整信息"""
        # PostgreSQL 结构化数据
        pg_query = """
        SELECT e.*, et.name as entity_type_name
        FROM entities e
        JOIN entity_types et ON e.entity_type_id = et.id
        WHERE e.character_unique_id = $1 AND e.is_current_version = true
        """

        pg_data = await self.pg_db.fetch_one(pg_query, character_unique_id)
        if not pg_data:
            return None

        # MongoDB 详细档案
        mongo_data = await self.mongo_db.character_profiles.find_one({
            "character_unique_id": character_unique_id,
            "is_current_version": True
        })

        return {
            "pg_data": dict(pg_data) if pg_data else None,
            "mongo_data": mongo_data,
            "version": pg_data["character_version"] if pg_data else "1.0",
            "domain_code": pg_data["domain_code"] if pg_data else None
        }

    async def _analyze_character_evolution(
        self,
        current_version: Optional[Dict[str, Any]],
        new_data: Dict[str, Any],
        new_domain: str
    ) -> Dict[str, Any]:
        """深度分析角色演进"""

        if not current_version or not current_version.get("mongo_data"):
            return {"type": "initial_creation", "changes": []}

        old_data = current_version["mongo_data"]
        old_domain = current_version["domain_code"]

        analysis = {
            "transition_type": self._determine_transition_type(old_domain, new_domain),
            "core_changes": [],
            "surface_changes": [],
            "continuity_elements": [],
            "growth_indicators": [],
            "adaptation_challenges": [],
            "development_consistency": 0.0  # 0-1 评分
        }

        # 核心身份分析
        old_basic = old_data.get("basic_info", {})
        new_basic = new_data.get("basicInfo", {})

        # 分析身份变化
        if old_basic.get("occupation") != new_basic.get("occupation"):
            analysis["core_changes"].append({
                "type": ChangeType.CORE_IDENTITY,
                "description": f"职业转换: {old_basic.get('occupation')} → {new_basic.get('occupation')}",
                "impact_level": self._assess_occupation_change_impact(
                    old_basic.get("occupation"), new_basic.get("occupation"), old_domain, new_domain
                )
            })

        # 社会地位变化
        if old_basic.get("social_status") != new_basic.get("socialStatus"):
            analysis["core_changes"].append({
                "type": ChangeType.CULTURAL_ADAPTATION,
                "description": f"社会地位变化: {old_basic.get('social_status')} → {new_basic.get('socialStatus')}",
                "adaptation_required": True
            })

        # 性格深度分析
        old_personality = old_data.get("personality", {})
        new_personality = new_data.get("personality", {})

        personality_continuity = self._analyze_personality_continuity(old_personality, new_personality)
        analysis["continuity_elements"].extend(personality_continuity["preserved"])
        analysis["growth_indicators"].extend(personality_continuity["evolved"])

        # 技能体系演进分析
        skills_evolution = self._analyze_skills_evolution(
            old_data.get("abilities", {}), new_data.get("abilities", {}), old_domain, new_domain
        )
        analysis["surface_changes"].extend(skills_evolution)

        # 心理发展一致性评估
        psychology_consistency = self._assess_psychological_consistency(
            old_data.get("psychology", {}), new_data.get("psychology", {})
        )
        analysis["development_consistency"] = psychology_consistency

        return analysis

    def _determine_transition_type(self, old_domain: str, new_domain: str) -> str:
        """确定迁移类型"""
        domain_transitions = {
            ("ren_yu", "tian_yu"): "ascension",  # 人域到天域是修炼提升
            ("tian_yu", "ling_yu"): "spiritual_evolution",  # 天域到灵域是精神进化
            # 可以根据世界观扩展更多类型
        }
        return domain_transitions.get((old_domain, new_domain), "cross_domain_journey")

    def _assess_occupation_change_impact(self, old_job: str, new_job: str, old_domain: str, new_domain: str) -> int:
        """评估职业变化的影响程度 (1-10)"""
        if not old_job or not new_job:
            return 5

        # 基于域和职业的映射关系评估影响
        # 这里可以构建更复杂的评估逻辑
        if old_domain != new_domain:
            return 8  # 跨域职业变化通常影响较大
        elif old_job == new_job:
            return 1  # 职业不变影响最小
        else:
            return 5  # 同域内职业变化中等影响

    def _analyze_personality_continuity(self, old_personality: Dict, new_personality: Dict) -> Dict[str, List]:
        """分析性格连续性"""
        result = {"preserved": [], "evolved": [], "transformed": []}

        old_traits = set(old_personality.get("coreTraits", []))
        new_traits = set(new_personality.get("coreTraits", []))

        # 保持的特质
        preserved = old_traits & new_traits
        result["preserved"] = [f"保持核心特质: {trait}" for trait in preserved]

        # 新发展的特质
        evolved = new_traits - old_traits
        result["evolved"] = [f"发展新特质: {trait}" for trait in evolved]

        # 价值观连续性分析
        old_values = set(old_personality.get("values", []))
        new_values = set(new_personality.get("values", []))

        preserved_values = old_values & new_values
        result["preserved"].extend([f"保持核心价值观: {value}" for value in preserved_values])

        return result

    def _analyze_skills_evolution(
        self, old_abilities: Dict, new_abilities: Dict, old_domain: str, new_domain: str
    ) -> List[Dict]:
        """分析技能演进"""
        evolutions = []

        old_skills = set(old_abilities.get("professionalSkills", []))
        new_skills = set(new_abilities.get("professionalSkills", []))

        # 技能转化分析
        preserved_skills = old_skills & new_skills
        new_skills_only = new_skills - old_skills
        lost_skills = old_skills - new_skills

        if preserved_skills:
            evolutions.append({
                "type": ChangeType.SKILL_EVOLUTION,
                "description": f"技能在新域延续: {', '.join(list(preserved_skills)[:3])}{'等' if len(preserved_skills) > 3 else ''}",
                "evolution_pattern": "continuity"
            })

        if new_skills_only:
            evolutions.append({
                "type": ChangeType.SKILL_EVOLUTION,
                "description": f"新域获得技能: {', '.join(list(new_skills_only)[:3])}{'等' if len(new_skills_only) > 3 else ''}",
                "evolution_pattern": "acquisition"
            })

        if lost_skills:
            evolutions.append({
                "type": ChangeType.SKILL_EVOLUTION,
                "description": f"技能在新域转化/淡化: {', '.join(list(lost_skills)[:3])}{'等' if len(lost_skills) > 3 else ''}",
                "evolution_pattern": "transformation"
            })

        return evolutions

    def _assess_psychological_consistency(self, old_psychology: Dict, new_psychology: Dict) -> float:
        """评估心理发展的一致性 (0-1)"""
        if not old_psychology or not new_psychology:
            return 0.5

        consistency_score = 0.0
        factors_checked = 0

        # 心理健康状态的合理发展
        old_status = old_psychology.get("mentalHealthStatus")
        new_status = new_psychology.get("mentalHealthStatus")
        if old_status and new_status:
            # 可以建立心理状态转换的合理性评估
            consistency_score += 0.3  # 简化评估
            factors_checked += 1

        # 应对机制的演进
        old_coping = old_psychology.get("copingMechanisms", [])
        new_coping = new_psychology.get("copingMechanisms", [])
        if len(new_coping) >= len(old_coping):  # 应对机制应该是积累和进化的
            consistency_score += 0.4
        factors_checked += 1

        # 创伤处理的连续性
        old_trauma = old_psychology.get("trauma", [])
        new_trauma = new_psychology.get("trauma", [])
        # 创伤不应该凭空消失，应该有处理过程
        if len(new_trauma) >= len(old_trauma) * 0.7:  # 允许部分创伤得到治愈
            consistency_score += 0.3
        factors_checked += 1

        return consistency_score / factors_checked if factors_checked > 0 else 0.5

    def _extract_character_essence(self, character_data: Dict[str, Any]) -> CharacterEssence:
        """提取角色本质特征"""
        personality = character_data.get("personality", {})
        psychology = character_data.get("psychology", {})
        abilities = character_data.get("abilities", {})

        return CharacterEssence(
            core_personality=personality.get("coreTraits", []),
            fundamental_values=personality.get("values", []),
            deep_motivations=personality.get("desires", []),
            psychological_patterns={
                "coping_style": psychology.get("copingMechanisms", []),
                "emotional_patterns": psychology.get("emotionalPatterns", []),
                "defense_mechanisms": psychology.get("psychologicalDefenses", [])
            },
            innate_talents=abilities.get("specialTalents", [])
        )

    def _extract_character_manifestation(self, character_data: Dict[str, Any], domain_code: str) -> CharacterManifestation:
        """提取角色表现形式"""
        basic_info = character_data.get("basicInfo", {})
        lifestyle = character_data.get("lifestyle", {})
        abilities = character_data.get("abilities", {})
        behavior = character_data.get("behaviorProfile", {})
        relationships = character_data.get("relationships", {})

        return CharacterManifestation(
            domain_identity={
                "domain": domain_code,
                "occupation": basic_info.get("occupation"),
                "social_status": basic_info.get("socialStatus"),
                "reputation": lifestyle.get("economicStatus")
            },
            social_role={
                "primary_role": basic_info.get("occupation"),
                "social_circles": relationships.get("socialCircle", []),
                "influence_scope": lifestyle.get("residence")
            },
            skill_expression={
                "professional_skills": abilities.get("professionalSkills", []),
                "practical_skills": abilities.get("practicalSkills", []),
                "domain_specific_abilities": []  # 可以根据域特征填充
            },
            behavioral_patterns=behavior,
            relationship_network=relationships
        )

    async def _analyze_relationship_transitions(
        self,
        character_unique_id: str,
        current_version: Optional[Dict[str, Any]],
        new_data: Dict[str, Any]
    ) -> Dict[str, RelationshipTransition]:
        """分析关系网络变化"""
        transitions = {}

        if not current_version or not current_version.get("mongo_data"):
            return transitions

        old_relationships = current_version["mongo_data"].get("relationships", {})
        new_relationships = new_data.get("relationships", {})

        # 分析各类关系的变化
        for relation_type in ["family", "friends", "enemies", "mentors", "lovers"]:
            old_relations = {rel.get("name") for rel in old_relationships.get(relation_type, [])}
            new_relations = {rel.get("name") for rel in new_relationships.get(relation_type, [])}

            # 保持的关系
            preserved = old_relations & new_relations
            for name in preserved:
                transitions[f"{relation_type}:{name}"] = RelationshipTransition.PRESERVED

            # 新建立的关系
            new_only = new_relations - old_relations
            for name in new_only:
                transitions[f"{relation_type}:{name}"] = RelationshipTransition.NEW_ESTABLISHED

            # 失去的关系
            lost = old_relations - new_relations
            for name in lost:
                transitions[f"{relation_type}:{name}"] = RelationshipTransition.SUSPENDED  # 默认为暂时中断

        return transitions

    async def _create_version_chain(
        self,
        current_version: Optional[Dict[str, Any]],
        new_domain_code: str,
        change_analysis: Dict[str, Any],
        essence: CharacterEssence,
        manifestation: CharacterManifestation
    ) -> Dict[str, Any]:
        """创建版本链记录"""

        if current_version and current_version.get("pg_data"):
            current_pg = current_version["pg_data"]

            # 计算新版本号
            current_version_str = current_pg.get("character_version", "1.0")
            try:
                major, minor = map(int, current_version_str.split('.'))
                new_version = f"{major}.{minor + 1}"
            except ValueError:
                new_version = "2.0"

            # 将当前版本设置为非当前
            await self.pg_db.execute(
                "UPDATE entities SET is_current_version = false WHERE character_unique_id = $1",
                current_pg["character_unique_id"]
            )

            previous_version_id = current_pg["id"]
            novel_id = current_pg["novel_id"]
            character_name = current_pg["name"]
            character_unique_id = current_pg["character_unique_id"]
        else:
            new_version = "1.0"
            previous_version_id = None
            # 需要从新数据中提取基础信息
            novel_id = 1  # 这里应该从某处获取正确的 novel_id
            character_name = new_data.get("basicInfo", {}).get("name", "Unknown")
            character_unique_id = f"lieshi-jiuyu-{character_name.lower()}-001"  # 简化的ID生成

        # 构建新版本的属性数据
        new_attributes = {
            "basicInfo": manifestation.domain_identity,
            "essence": {
                "corePersonality": essence.core_personality,
                "fundamentalValues": essence.fundamental_values,
                "deepMotivations": essence.deep_motivations
            },
            "versionMetadata": {
                "transitionType": change_analysis.get("transition_type"),
                "majorChanges": [change["description"] for change in change_analysis.get("core_changes", [])],
                "continuityElements": change_analysis.get("continuity_elements", []),
                "developmentConsistency": change_analysis.get("development_consistency", 0.5)
            }
        }

        # 插入新版本记录
        insert_query = """
        INSERT INTO entities (
            novel_id, entity_type_id, name, code, character_unique_id,
            domain_code, character_version, previous_version_id,
            is_current_version, attributes, status
        ) VALUES (
            $1, (SELECT id FROM entity_types WHERE novel_id = $1 AND name = 'character' LIMIT 1),
            $2, $3, $4, $5, $6, $7, true, $8, 'active'
        ) RETURNING id
        """

        result = await self.pg_db.fetch_one(
            insert_query,
            novel_id,
            character_name,
            character_unique_id,
            character_unique_id,
            new_domain_code,
            new_version,
            previous_version_id,
            json.dumps(new_attributes)
        )

        return {
            "entity_id": result["id"],
            "version": new_version,
            "domain_code": new_domain_code,
            "previous_version_id": previous_version_id,
            "attributes": new_attributes
        }

    async def _store_complete_profile(
        self,
        character_unique_id: str,
        version_info: Dict[str, Any],
        character_data: Dict[str, Any],
        essence: CharacterEssence,
        manifestation: CharacterManifestation
    ):
        """存储完整的角色档案到MongoDB"""

        # 获取小说信息
        novel_info = await self.pg_db.fetch_one(
            "SELECT code FROM novels WHERE id = (SELECT novel_id FROM entities WHERE id = $1)",
            version_info["entity_id"]
        )
        novel_code = novel_info["code"] if novel_info else "unknown"

        # 构建完整的MongoDB文档
        profile_document = {
            "character_unique_id": character_unique_id,
            "character_name": character_data.get("basicInfo", {}).get("name", ""),
            "novel_id": 1,  # 简化处理
            "novel_code": novel_code,
            "domain_code": version_info["domain_code"],
            "version": version_info["version"],

            # 完整的角色数据
            **{k: v for k, v in character_data.items()},

            # 提取的本质和表现
            "character_essence": {
                "core_personality": essence.core_personality,
                "fundamental_values": essence.fundamental_values,
                "deep_motivations": essence.deep_motivations,
                "psychological_patterns": essence.psychological_patterns,
                "innate_talents": essence.innate_talents
            },

            "character_manifestation": {
                "domain_identity": manifestation.domain_identity,
                "social_role": manifestation.social_role,
                "skill_expression": manifestation.skill_expression,
                "behavioral_patterns": manifestation.behavioral_patterns,
                "relationship_network": manifestation.relationship_network
            },

            # 版本元数据
            "version_metadata": version_info["attributes"]["versionMetadata"],

            # 系统字段
            "metadata": {
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "created_by": "lifecycle_manager",
                "processing_version": "2.0"
            },

            "is_current_version": True,
            "is_archived": False
        }

        # 设置其他版本为非当前
        await self.mongo_db.character_profiles.update_many(
            {"character_unique_id": character_unique_id},
            {"$set": {"is_current_version": False}}
        )

        # 插入新版本
        await self.mongo_db.character_profiles.insert_one(profile_document)

    async def _update_relationship_network(
        self,
        character_unique_id: str,
        new_domain_code: str,
        relationship_transitions: Dict[str, RelationshipTransition]
    ):
        """更新关系网络"""

        # 获取新的entity_id
        new_entity = await self.pg_db.fetch_one(
            "SELECT id, novel_id FROM entities WHERE character_unique_id = $1 AND is_current_version = true",
            character_unique_id
        )

        if not new_entity:
            return

        # 记录关系变化
        for relationship_key, transition_type in relationship_transitions.items():
            relation_type, target_name = relationship_key.split(":", 1)

            # 插入关系演进记录
            await self.pg_db.execute("""
                INSERT INTO character_relationship_evolution (
                    novel_id, source_character_id, target_character_id, domain_code, version,
                    current_relationship_type, change_reason, impact_level
                ) VALUES ($1, $2, $3, $4, '2.0', $5, $6, 5)
            """,
                new_entity["novel_id"],
                character_unique_id,
                target_name,  # 简化处理，实际应该是目标角色的ID
                new_domain_code,
                relation_type,
                f"Domain transition: {transition_type.value}"
            )

    async def _record_development_trajectory(
        self,
        character_unique_id: str,
        version_info: Dict[str, Any],
        change_analysis: Dict[str, Any]
    ):
        """记录发展轨迹"""

        trajectory_document = {
            "character_unique_id": character_unique_id,
            "novel_id": 1,
            "track_type": "domain_transition",

            "development_data": {
                "track_name": f"Domain Transition to {version_info['domain_code']}",
                "transition_analysis": change_analysis,
                "version": version_info["version"],
                "consistency_score": change_analysis.get("development_consistency", 0.5)
            },

            "development_history": [{
                "timestamp": datetime.now(timezone.utc),
                "domain_code": version_info["domain_code"],
                "change_description": f"Version {version_info['version']} created",
                "impact_assessment": {
                    "core_changes_count": len(change_analysis.get("core_changes", [])),
                    "surface_changes_count": len(change_analysis.get("surface_changes", [])),
                    "continuity_elements_count": len(change_analysis.get("continuity_elements", []))
                }
            }],

            "metadata": {
                "created_at": datetime.now(timezone.utc),
                "is_active": True,
                "priority_level": 8  # 域迁移是高优先级的发展轨迹
            }
        }

        await self.mongo_db.character_development_tracks.insert_one(trajectory_document)

    async def _generate_version_insights(
        self,
        character_unique_id: str,
        current_version: Optional[Dict[str, Any]],
        new_version_info: Dict[str, Any],
        change_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成版本洞察"""

        insights = {
            "character_development_assessment": {
                "consistency_score": change_analysis.get("development_consistency", 0.5),
                "growth_potential": self._assess_growth_potential(change_analysis),
                "adaptation_challenges": change_analysis.get("adaptation_challenges", [])
            },
            "narrative_opportunities": self._identify_narrative_opportunities(change_analysis),
            "relationship_implications": self._analyze_relationship_implications(change_analysis),
            "world_building_consistency": self._check_world_building_consistency(
                new_version_info["domain_code"], change_analysis
            )
        }

        # 存储洞察到数据库
        insight_document = {
            "character_unique_id": character_unique_id,
            "version": new_version_info["version"],
            "insights": insights,
            "generated_at": datetime.now(timezone.utc),
            "insight_version": "1.0"
        }

        # 可以存储到专门的洞察集合中
        try:
            await self.mongo_db.character_version_insights.insert_one(insight_document)
        except Exception as e:
            logger.warning(f"Failed to store insights: {e}")

        return insights

    def _assess_growth_potential(self, change_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """评估成长潜力"""
        growth_indicators = change_analysis.get("growth_indicators", [])
        core_changes = change_analysis.get("core_changes", [])

        return {
            "potential_score": min(len(growth_indicators) * 0.3 + len(core_changes) * 0.2, 1.0),
            "growth_areas": [indicator for indicator in growth_indicators[:5]],
            "development_risks": [change["description"] for change in core_changes if change.get("impact_level", 0) > 7]
        }

    def _identify_narrative_opportunities(self, change_analysis: Dict[str, Any]) -> List[str]:
        """识别叙事机会"""
        opportunities = []

        # 基于变化类型识别机会
        for change in change_analysis.get("core_changes", []):
            change_type = change.get("type")
            if change_type == ChangeType.CORE_IDENTITY:
                opportunities.append(f"身份冲突与重新定位: {change['description']}")
            elif change_type == ChangeType.CULTURAL_ADAPTATION:
                opportunities.append(f"文化冲击与适应过程: {change['description']}")

        # 基于连续性元素识别机会
        continuity = change_analysis.get("continuity_elements", [])
        if continuity:
            opportunities.append(f"核心特质的新环境表现: {continuity[0] if continuity else ''}")

        return opportunities[:5]  # 限制数量

    def _analyze_relationship_implications(self, change_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析关系影响"""
        return {
            "relationship_stability_risk": "medium",  # 可以基于变化分析计算
            "new_relationship_potential": "high",     # 新域通常有新关系机会
            "cross_domain_relationship_challenges": [
                "原域关系的维持困难",
                "新域社会规则的适应",
                "身份变化对关系动态的影响"
            ]
        }

    def _check_world_building_consistency(self, domain_code: str, change_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """检查世界观一致性"""
        # 这里可以基于域的文化框架进行检查
        return {
            "consistency_score": 0.8,  # 简化评估
            "potential_conflicts": [],
            "suggestions": [
                f"确保角色变化符合{domain_code}域的文化特征",
                "检查技能转化的合理性",
                "验证社会地位变化的逻辑"
            ]
        }

    # 查询和分析方法
    async def get_character_evolution_timeline(self, character_unique_id: str) -> List[Dict[str, Any]]:
        """获取角色演进时间线"""
        timeline = []

        # 从PostgreSQL获取版本历史
        versions = await self.pg_db.fetch_all("""
            SELECT e.*, cvh.transition_reason, cvh.transition_date
            FROM entities e
            LEFT JOIN character_version_history cvh ON e.id = cvh.character_entity_id
            WHERE e.character_unique_id = $1
            ORDER BY e.character_version
        """, character_unique_id)

        for version in versions:
            # 获取对应的MongoDB详细数据
            mongo_data = await self.mongo_db.character_profiles.find_one({
                "character_unique_id": character_unique_id,
                "version": version["character_version"]
            })

            timeline.append({
                "version": version["character_version"],
                "domain_code": version["domain_code"],
                "created_at": version["created_at"],
                "transition_reason": version.get("transition_reason"),
                "basic_info": mongo_data.get("basic_info", {}) if mongo_data else {},
                "version_metadata": mongo_data.get("version_metadata", {}) if mongo_data else {}
            })

        return timeline

    async def compare_character_versions(
        self, character_unique_id: str, version1: str, version2: str
    ) -> Dict[str, Any]:
        """比较角色版本"""
        # 获取两个版本的完整数据
        v1_data = await self.mongo_db.character_profiles.find_one({
            "character_unique_id": character_unique_id,
            "version": version1
        })

        v2_data = await self.mongo_db.character_profiles.find_one({
            "character_unique_id": character_unique_id,
            "version": version2
        })

        if not v1_data or not v2_data:
            return {"error": "One or both versions not found"}

        # 进行详细对比
        comparison = {
            "basic_info_changes": self._compare_dicts(
                v1_data.get("basic_info", {}), v2_data.get("basic_info", {})
            ),
            "personality_evolution": self._compare_dicts(
                v1_data.get("personality", {}), v2_data.get("personality", {})
            ),
            "abilities_progression": self._compare_dicts(
                v1_data.get("abilities", {}), v2_data.get("abilities", {})
            ),
            "domain_transition": {
                "from": v1_data.get("domain_code"),
                "to": v2_data.get("domain_code"),
                "transition_type": v2_data.get("version_metadata", {}).get("transitionType")
            }
        }

        return comparison

    def _compare_dicts(self, dict1: Dict, dict2: Dict) -> Dict[str, Any]:
        """比较两个字典的差异"""
        changes = {
            "added": {},
            "removed": {},
            "changed": {},
            "unchanged": {}
        }

        all_keys = set(dict1.keys()) | set(dict2.keys())

        for key in all_keys:
            if key in dict1 and key in dict2:
                if dict1[key] != dict2[key]:
                    changes["changed"][key] = {"from": dict1[key], "to": dict2[key]}
                else:
                    changes["unchanged"][key] = dict1[key]
            elif key in dict1:
                changes["removed"][key] = dict1[key]
            else:
                changes["added"][key] = dict2[key]

        return changes


# 便捷函数
async def create_character_version(
    character_unique_id: str,
    new_domain_code: str,
    new_character_data: Dict[str, Any],
    transition_context: Dict[str, Any] = None
) -> bool:
    """便捷的角色版本创建函数"""
    manager = CharacterLifecycleManager()
    await manager.initialize()

    return await manager.create_new_version(
        character_unique_id, new_domain_code, new_character_data, transition_context
    )


async def get_character_timeline(character_unique_id: str) -> List[Dict[str, Any]]:
    """获取角色演进时间线"""
    manager = CharacterLifecycleManager()
    await manager.initialize()

    return await manager.get_character_evolution_timeline(character_unique_id)


# 命令行执行
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="角色版本生命周期管理")
    parser.add_argument("--character-id", required=True, help="角色唯一ID")
    parser.add_argument("--timeline", action="store_true", help="显示演进时间线")
    parser.add_argument("--compare", nargs=2, help="比较两个版本")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    async def main():
        if args.timeline:
            timeline = await get_character_timeline(args.character_id)
            print(f"角色 {args.character_id} 演进时间线:")
            for entry in timeline:
                print(f"  版本 {entry['version']} - 域: {entry['domain_code']} - {entry['created_at']}")

        elif args.compare:
            manager = CharacterLifecycleManager()
            await manager.initialize()
            comparison = await manager.compare_character_versions(
                args.character_id, args.compare[0], args.compare[1]
            )
            print(f"版本比较结果:")
            print(json.dumps(comparison, indent=2, ensure_ascii=False))

    asyncio.run(main())