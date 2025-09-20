"""
法则链系统MCP工具接口
提供完整的法则链管理功能
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from mcp.server.fastmcp import FastMCP
from database.law_chain_manager import LawChainManager, LawChainConfig
from database.models.law_chain_models import (
    LawChainDefinition, LawChainMaster, LawChainCombination,
    FieldStrengthZone, DomainAffinity, ChainCategory,
    LearningLevel, RarityLevel, AcquisitionChannel,
    CombinationType, ChainRequirement, CombinationEffect,
    CombinationCost, TimeModifiers, ResonanceFactor,
    LocationData
)


def register_law_chain_tools(mcp: FastMCP):
    """注册法则链系统工具"""

    # =========================================================================
    # 法则链定义管理
    # =========================================================================

    @mcp.tool()
    async def create_law_chain(
        novel_id: str,
        chain_code: str,
        chain_name: str,
        chain_category: str,
        description: str,
        origin_story: Optional[str] = None,
        max_level: int = 6,
        base_rarity: int = 0,
        domain_affinity: Optional[Dict[str, float]] = None,
        special_traits: Optional[List[str]] = None
    ) -> str:
        """
        创建新的法则链定义

        Args:
            novel_id: 小说ID
            chain_code: 法则链代码（如FATE, CAUSE, SPACE等）
            chain_name: 法则链名称（如命运链、因果链等）
            chain_category: 法则链类别（命运/因果/时空/生死/混沌/权柄/名真/记忆/界域/形质/映象/共鸣）
            description: 法则链描述
            origin_story: 起源故事
            max_level: 最大等级（0-6）
            base_rarity: 基础稀有度（0-5）
            domain_affinity: 四域偏好 {"人域": 0-100, "天域": 0-100, "灵域": 0-100, "荒域": 0-100}
            special_traits: 特殊特性列表

        Returns:
            创建的法则链ID
        """
        try:
            # 构建域偏好
            affinity = DomainAffinity(
                human=domain_affinity.get("人域", 0) if domain_affinity else 0,
                heaven=domain_affinity.get("天域", 0) if domain_affinity else 0,
                spirit=domain_affinity.get("灵域", 0) if domain_affinity else 0,
                wild=domain_affinity.get("荒域", 0) if domain_affinity else 0
            )

            # 创建法则链定义
            chain_def = LawChainDefinition(
                novel_id=novel_id,
                chain_code=chain_code,
                chain_name=chain_name,
                chain_category=ChainCategory(chain_category),
                description=description,
                origin_story=origin_story,
                max_level=max_level,
                base_rarity=base_rarity,
                domain_affinity=affinity,
                special_traits=special_traits or []
            )

            async with LawChainManager() as manager:
                chain_id = await manager.create_law_chain(chain_def)

            return json.dumps({
                "success": True,
                "chain_id": chain_id,
                "message": f"成功创建法则链：{chain_name}"
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    @mcp.tool()
    async def list_law_chains(
        novel_id: str,
        category: Optional[str] = None,
        min_rarity: Optional[int] = None
    ) -> str:
        """
        列出法则链

        Args:
            novel_id: 小说ID
            category: 筛选类别（可选）
            min_rarity: 最小稀有度（可选）

        Returns:
            法则链列表
        """
        try:
            async with LawChainManager() as manager:
                chains = await manager.list_law_chains(
                    novel_id,
                    ChainCategory(category) if category else None,
                    min_rarity
                )

            result = []
            for chain in chains:
                result.append({
                    "id": chain.id,
                    "chain_code": chain.chain_code,
                    "chain_name": chain.chain_name,
                    "category": chain.chain_category.value,
                    "description": chain.description,
                    "max_level": chain.max_level,
                    "base_rarity": chain.base_rarity,
                    "domain_affinity": {
                        "人域": chain.domain_affinity.human,
                        "天域": chain.domain_affinity.heaven,
                        "灵域": chain.domain_affinity.spirit,
                        "荒域": chain.domain_affinity.wild
                    },
                    "special_traits": chain.special_traits
                })

            return json.dumps({
                "success": True,
                "total": len(result),
                "chains": result
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    # =========================================================================
    # 角色法则链管理
    # =========================================================================

    @mcp.tool()
    async def grant_chain_to_character(
        character_id: str,
        chain_id: str,
        acquisition_channel: str,
        initial_level: int = 0,
        initial_rarity: int = 0
    ) -> str:
        """
        授予角色法则链

        Args:
            character_id: 角色ID
            chain_id: 法则链ID
            acquisition_channel: 获取渠道（命格/师承/契约/器物/权柄/结界/窗口/坩埚/共鸣）
            initial_level: 初始等级（0-6）
            initial_rarity: 初始稀有度（0-5）

        Returns:
            授予结果
        """
        try:
            async with LawChainManager() as manager:
                master_id = await manager.grant_chain_to_character(
                    character_id,
                    chain_id,
                    AcquisitionChannel(acquisition_channel),
                    initial_level,
                    initial_rarity
                )

            return json.dumps({
                "success": True,
                "master_id": master_id,
                "message": f"成功授予角色法则链"
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    @mcp.tool()
    async def upgrade_chain_level(
        character_id: str,
        chain_id: str,
        target_level: int
    ) -> str:
        """
        升级法则链等级

        Args:
            character_id: 角色ID
            chain_id: 法则链ID
            target_level: 目标等级（必须高于当前等级）

        Returns:
            升级结果
        """
        try:
            async with LawChainManager() as manager:
                success = await manager.upgrade_chain_level(
                    character_id,
                    chain_id,
                    target_level
                )

            if success:
                return json.dumps({
                    "success": True,
                    "message": f"成功将法则链升级到L{target_level}"
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "success": False,
                    "message": "升级失败，请检查条件"
                }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    @mcp.tool()
    async def get_character_chains(
        character_id: str,
        min_level: Optional[int] = None
    ) -> str:
        """
        获取角色的法则链列表

        Args:
            character_id: 角色ID
            min_level: 最小等级筛选（可选）

        Returns:
            角色的法则链列表
        """
        try:
            async with LawChainManager() as manager:
                chains = await manager.list_character_chains(
                    character_id,
                    min_level
                )

            result = []
            for chain in chains:
                result.append({
                    "chain_id": chain.chain_id,
                    "current_level": chain.current_level,
                    "current_rarity": chain.current_rarity,
                    "mastery_progress": float(chain.mastery_progress),
                    "acquisition_channel": chain.acquisition_channel.value if chain.acquisition_channel else None,
                    "acquisition_date": chain.acquisition_date.isoformat(),
                    "total_uses": chain.total_uses,
                    "successful_uses": chain.successful_uses,
                    "success_rate": chain.success_rate,
                    "chain_fatigue": float(chain.chain_fatigue),
                    "pollution_level": float(chain.pollution_level),
                    "is_exhausted": chain.is_exhausted,
                    "is_polluted": chain.is_polluted,
                    "special_states": chain.special_states
                })

            return json.dumps({
                "success": True,
                "total": len(result),
                "chains": result
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    # =========================================================================
    # 法则链使用
    # =========================================================================

    @mcp.tool()
    async def use_law_chain(
        character_id: str,
        chain_id: str,
        action_type: str,
        zone_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        使用法则链

        Args:
            character_id: 角色ID
            chain_id: 法则链ID
            action_type: 行动类型
            zone_id: 场强区域ID（可选）
            parameters: 额外参数（可选）

        Returns:
            使用结果和产生的代价
        """
        try:
            async with LawChainManager() as manager:
                usage_log = await manager.use_law_chain(
                    character_id,
                    chain_id,
                    action_type,
                    zone_id,
                    parameters
                )

            return json.dumps({
                "success": True,
                "result": {
                    "success": usage_log.success,
                    "action_type": usage_log.action_type,
                    "field_strength": float(usage_log.field_strength) if usage_log.field_strength else 0,
                    "costs": {
                        "因果债": float(usage_log.costs_incurred.causal_debt),
                        "寿债": float(usage_log.costs_incurred.life_debt),
                        "污染": float(usage_log.costs_incurred.pollution),
                        "链疲劳": float(usage_log.costs_incurred.chain_fatigue),
                        "正当性风险": float(usage_log.costs_incurred.legitimacy_risk)
                    },
                    "side_effects": usage_log.side_effects,
                    "duration_ms": usage_log.duration_ms
                }
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    # =========================================================================
    # 法则链组合
    # =========================================================================

    @mcp.tool()
    async def create_chain_combination(
        novel_id: str,
        combination_name: str,
        combination_type: str,
        required_chains: List[Dict[str, Any]],
        description: Optional[str] = None,
        effects: Optional[Dict[str, Any]] = None,
        stability_rating: int = 50
    ) -> str:
        """
        创建法则链组合

        Args:
            novel_id: 小说ID
            combination_name: 组合名称
            combination_type: 组合类型（同相相长/战术联动/硬克制）
            required_chains: 所需法则链列表 [{"chain_id": "", "min_level": 0, "min_rarity": 0}]
            description: 组合描述
            effects: 组合效果 {"power_boost": 0, "range_extension": 0, "duration_bonus": 0}
            stability_rating: 稳定性评级（0-100）

        Returns:
            创建的组合ID
        """
        try:
            # 构建组合要求
            requirements = [
                ChainRequirement(
                    chain_id=rc["chain_id"],
                    min_level=rc.get("min_level", 0),
                    min_rarity=rc.get("min_rarity", 0)
                )
                for rc in required_chains
            ]

            # 构建组合效果
            combo_effects = CombinationEffect(
                power_boost=effects.get("power_boost", 0) if effects else 0,
                range_extension=effects.get("range_extension", 0) if effects else 0,
                duration_bonus=effects.get("duration_bonus", 0) if effects else 0,
                special_effects=effects.get("special_effects", []) if effects else []
            )

            # 创建组合
            combination = LawChainCombination(
                novel_id=novel_id,
                combination_name=combination_name,
                combination_type=CombinationType(combination_type),
                description=description,
                required_chains=requirements,
                effects=combo_effects,
                stability_rating=stability_rating
            )

            async with LawChainManager() as manager:
                combo_id = await manager.create_combination(combination)

            return json.dumps({
                "success": True,
                "combination_id": combo_id,
                "message": f"成功创建法则链组合：{combination_name}"
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    @mcp.tool()
    async def use_chain_combination(
        character_id: str,
        combination_id: str,
        zone_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        使用法则链组合

        Args:
            character_id: 角色ID
            combination_id: 组合ID
            zone_id: 场强区域ID（可选）
            parameters: 额外参数（可选）

        Returns:
            组合使用结果
        """
        try:
            async with LawChainManager() as manager:
                usage_log = await manager.use_combination(
                    character_id,
                    combination_id,
                    zone_id,
                    parameters
                )

            return json.dumps({
                "success": True,
                "result": {
                    "success": usage_log.success,
                    "field_strength": float(usage_log.field_strength) if usage_log.field_strength else 0,
                    "costs": {
                        "链疲劳": float(usage_log.costs_incurred.chain_fatigue),
                        "污染": float(usage_log.costs_incurred.pollution)
                    },
                    "output": usage_log.output_results
                }
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    @mcp.tool()
    async def get_combination_recommendations(
        character_id: str,
        limit: int = 5
    ) -> str:
        """
        获取组合推荐

        Args:
            character_id: 角色ID
            limit: 推荐数量限制

        Returns:
            推荐的法则链组合列表
        """
        try:
            async with LawChainManager() as manager:
                recommendations = await manager.get_combination_recommendations(
                    character_id,
                    limit
                )

            return json.dumps({
                "success": True,
                "recommendations": recommendations
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    # =========================================================================
    # 场强系统
    # =========================================================================

    @mcp.tool()
    async def create_field_zone(
        novel_id: str,
        zone_name: str,
        zone_type: str,
        base_field_strength: float,
        location_data: Optional[Dict[str, Any]] = None,
        time_modifiers: Optional[Dict[str, float]] = None,
        resonance_factors: Optional[Dict[str, Any]] = None,
        affected_chains: Optional[List[str]] = None
    ) -> str:
        """
        创建场强区域

        Args:
            novel_id: 小说ID
            zone_name: 区域名称
            zone_type: 区域类型
            base_field_strength: 基础场强（0-5）
            location_data: 位置数据 {"coordinates": [], "radius": 0, "shape": "sphere"}
            time_modifiers: 时段修正 {"dawn": 0, "morning": 0, "noon": 0, ...}
            resonance_factors: 共振因素 {"min_people": 0, "resonance_multiplier": 1.0}
            affected_chains: 受影响的法则链ID列表

        Returns:
            创建的区域ID
        """
        try:
            # 构建位置数据
            loc_data = LocationData(
                coordinates=location_data.get("coordinates") if location_data else None,
                radius=location_data.get("radius", 0) if location_data else 0,
                shape=location_data.get("shape", "sphere") if location_data else "sphere"
            )

            # 构建时段修正
            time_mods = TimeModifiers(
                dawn=time_modifiers.get("dawn", 0) if time_modifiers else 0,
                morning=time_modifiers.get("morning", 0) if time_modifiers else 0,
                noon=time_modifiers.get("noon", 0) if time_modifiers else 0,
                afternoon=time_modifiers.get("afternoon", 0) if time_modifiers else 0,
                dusk=time_modifiers.get("dusk", 0) if time_modifiers else 0,
                night=time_modifiers.get("night", 0) if time_modifiers else 0,
                midnight=time_modifiers.get("midnight", 0) if time_modifiers else 0
            )

            # 构建共振因素
            res_factors = ResonanceFactor(
                min_people=resonance_factors.get("min_people", 0) if resonance_factors else 0,
                resonance_multiplier=resonance_factors.get("resonance_multiplier", 1.0) if resonance_factors else 1.0,
                special_conditions=resonance_factors.get("special_conditions", []) if resonance_factors else []
            )

            # 创建场强区域
            zone = FieldStrengthZone(
                novel_id=novel_id,
                zone_name=zone_name,
                zone_type=zone_type,
                location_data=loc_data,
                base_field_strength=Decimal(str(base_field_strength)),
                current_field_strength=Decimal(str(base_field_strength)),
                time_modifiers=time_mods,
                resonance_factors=res_factors,
                affected_chains=affected_chains or []
            )

            async with LawChainManager() as manager:
                zone_id = await manager.create_field_zone(zone)

            return json.dumps({
                "success": True,
                "zone_id": zone_id,
                "message": f"成功创建场强区域：{zone_name}"
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    @mcp.tool()
    async def calculate_field_strength(
        zone_id: str,
        people_count: int = 0
    ) -> str:
        """
        计算当前场强

        Args:
            zone_id: 区域ID
            people_count: 当前人数

        Returns:
            场强计算结果
        """
        try:
            async with LawChainManager() as manager:
                calculation = await manager.calculate_field_strength(
                    zone_id,
                    people_count
                )

            return json.dumps({
                "success": True,
                "field_strength": float(calculation.calculated_strength),
                "details": {
                    "location_factor": float(calculation.location_factor),
                    "time_factor": float(calculation.time_factor),
                    "people_count": calculation.people_count,
                    "resonance_factor": float(calculation.resonance_factor),
                    "active_chains": calculation.active_chains
                }
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    # =========================================================================
    # 债务和恢复
    # =========================================================================

    @mcp.tool()
    async def get_character_debts(
        character_id: str,
        status: Optional[str] = None
    ) -> str:
        """
        获取角色的债务

        Args:
            character_id: 角色ID
            status: 债务状态筛选（active/partial/paid/defaulted/transferred）

        Returns:
            债务列表
        """
        try:
            async with LawChainManager() as manager:
                debts = await manager.get_character_debts(
                    character_id,
                    status
                )

            result = []
            for debt in debts:
                result.append({
                    "id": debt.id,
                    "debt_type": debt.debt_type,
                    "original_amount": float(debt.original_amount),
                    "current_amount": float(debt.current_amount),
                    "remaining_amount": float(debt.remaining_amount),
                    "interest_rate": float(debt.interest_rate),
                    "creditor_type": debt.creditor_type,
                    "status": debt.status,
                    "is_overdue": debt.is_overdue,
                    "due_date": debt.due_date.isoformat() if debt.due_date else None,
                    "source_event": debt.source_event
                })

            return json.dumps({
                "success": True,
                "total": len(result),
                "debts": result
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    @mcp.tool()
    async def recover_chain_fatigue(
        character_id: str,
        hours: float = 1.0
    ) -> str:
        """
        恢复链疲劳

        Args:
            character_id: 角色ID
            hours: 恢复时长（小时）

        Returns:
            恢复结果
        """
        try:
            async with LawChainManager() as manager:
                await manager.recover_chain_fatigue(character_id, hours)

            return json.dumps({
                "success": True,
                "message": f"成功恢复{hours}小时的链疲劳"
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    @mcp.tool()
    async def decay_pollution(
        character_id: str,
        days: float = 1.0
    ) -> str:
        """
        衰减污染

        Args:
            character_id: 角色ID
            days: 衰减天数

        Returns:
            衰减结果
        """
        try:
            async with LawChainManager() as manager:
                await manager.decay_pollution(character_id, days)

            return json.dumps({
                "success": True,
                "message": f"成功衰减{days}天的污染"
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)

    # =========================================================================
    # 统计和分析
    # =========================================================================

    @mcp.tool()
    async def get_chain_statistics(character_id: str) -> str:
        """
        获取角色的法则链统计

        Args:
            character_id: 角色ID

        Returns:
            统计数据
        """
        try:
            async with LawChainManager() as manager:
                stats = await manager.get_character_chain_stats(character_id)

            return json.dumps({
                "success": True,
                "statistics": stats
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)