"""
法则链系统管理器
提供法则链的核心业务逻辑和管理功能
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import asyncpg
import json
import math
import random
from dataclasses import dataclass

from .models.law_chain_models import (
    LawChainDefinition, LawChainLevel, LawChainMaster,
    LawChainCombination, CharacterChainCombination,
    LawChainCost, CausalDebt, FieldStrengthZone,
    FieldStrengthCalculation, LawChainUsageLog,
    ChainCategory, LearningLevel, RarityLevel,
    AcquisitionChannel, CombinationType, CostType,
    DomainType, ChainRequirement, CostRecord
)
from .connections.postgresql import postgres_db


# =============================================================================
# 辅助类和配置
# =============================================================================

@dataclass
class LawChainConfig:
    """法则链系统配置"""
    # 疲劳恢复速率（每小时恢复百分比）
    fatigue_recovery_rate: float = 10.0

    # 污染衰减速率（每天衰减百分比）
    pollution_decay_rate: float = 5.0

    # 基础成功率
    base_success_rate: float = 70.0

    # 场强影响系数
    field_strength_multiplier: float = 0.2

    # 稀有度成功率修正
    rarity_success_modifiers: Dict[int, float] = None

    # 等级成功率修正
    level_success_modifiers: Dict[int, float] = None

    # 组合稳定性阈值
    combination_stability_threshold: float = 30.0

    # 代价计算系数
    cost_multipliers: Dict[str, float] = None

    def __post_init__(self):
        if self.rarity_success_modifiers is None:
            self.rarity_success_modifiers = {
                0: 1.0,   # R0 普适
                1: 0.95,  # R1 常见
                2: 0.85,  # R2 进阶
                3: 0.70,  # R3 稀有
                4: 0.50,  # R4 至稀
                5: 0.30   # R5 禁忌
            }

        if self.level_success_modifiers is None:
            self.level_success_modifiers = {
                0: 0.5,   # L0 感知
                1: 0.7,   # L1 安全操作
                2: 0.85,  # L2 接口熟练
                3: 0.95,  # L3 低风险组合
                4: 1.0,   # L4 标准化
                5: 1.05,  # L5 枢轴权
                6: 1.1    # L6 受控极限
            }

        if self.cost_multipliers is None:
            self.cost_multipliers = {
                "因果债": 1.0,
                "寿债": 1.5,
                "污染": 0.8,
                "链疲劳": 0.5,
                "正当性风险": 2.0
            }


# =============================================================================
# 法则链管理器
# =============================================================================

class LawChainManager:
    """法则链系统核心管理器"""

    def __init__(self, config: Optional[LawChainConfig] = None):
        self.config = config or LawChainConfig()
        self._connection: Optional[asyncpg.Connection] = None

    async def __aenter__(self):
        self._connection = await postgres_db.get_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            await self._connection.close()

    # =========================================================================
    # 法则链定义管理
    # =========================================================================

    async def create_law_chain(self, chain_data: LawChainDefinition) -> str:
        """创建新的法则链定义"""
        query = """
        INSERT INTO law_chain_definitions (
            id, novel_id, chain_code, chain_name, chain_category,
            description, origin_story, max_level, base_rarity,
            domain_affinity, base_attributes, special_traits, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        RETURNING id
        """

        result = await self._connection.fetchval(
            query,
            chain_data.id,
            chain_data.novel_id,
            chain_data.chain_code,
            chain_data.chain_name,
            chain_data.chain_category.value,
            chain_data.description,
            chain_data.origin_story,
            chain_data.max_level,
            chain_data.base_rarity,
            json.dumps(chain_data.domain_affinity.model_dump()),
            json.dumps(chain_data.base_attributes),
            chain.dumps(chain_data.special_traits),
            json.dumps(chain_data.metadata)
        )

        # 创建默认等级
        await self._create_default_levels(result, chain_data.max_level)

        return result

    async def _create_default_levels(self, chain_id: str, max_level: int):
        """创建法则链的默认等级"""
        level_names = {
            0: "感知",
            1: "安全操作",
            2: "接口熟练",
            3: "低风险组合",
            4: "标准化",
            5: "枢轴权",
            6: "受控极限"
        }

        for level_num in range(max_level + 1):
            query = """
            INSERT INTO law_chain_levels (
                chain_id, level_code, level_number, level_name, description
            ) VALUES ($1, $2, $3, $4, $5)
            """

            await self._connection.execute(
                query,
                chain_id,
                f"L{level_num}",
                level_num,
                level_names[level_num],
                f"法则链{level_names[level_num]}阶段"
            )

    async def get_law_chain(self, chain_id: str) -> Optional[LawChainDefinition]:
        """获取法则链定义"""
        query = """
        SELECT * FROM law_chain_definitions WHERE id = $1
        """

        row = await self._connection.fetchrow(query, chain_id)
        if row:
            return LawChainDefinition(**dict(row))
        return None

    async def list_law_chains(
        self,
        novel_id: str,
        category: Optional[ChainCategory] = None,
        min_rarity: Optional[int] = None
    ) -> List[LawChainDefinition]:
        """列出法则链"""
        query = """
        SELECT * FROM law_chain_definitions
        WHERE novel_id = $1
        """
        params = [novel_id]

        if category:
            query += f" AND chain_category = ${len(params) + 1}"
            params.append(category.value)

        if min_rarity is not None:
            query += f" AND base_rarity >= ${len(params) + 1}"
            params.append(min_rarity)

        query += " ORDER BY chain_category, base_rarity"

        rows = await self._connection.fetch(query, *params)
        return [LawChainDefinition(**dict(row)) for row in rows]

    # =========================================================================
    # 角色法则链管理
    # =========================================================================

    async def grant_chain_to_character(
        self,
        character_id: str,
        chain_id: str,
        acquisition_channel: AcquisitionChannel,
        initial_level: int = 0,
        initial_rarity: int = 0
    ) -> str:
        """授予角色法则链"""
        query = """
        INSERT INTO law_chain_masters (
            character_id, chain_id, current_level, current_rarity,
            acquisition_channel, acquisition_date, acquisition_details
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (character_id, chain_id) DO UPDATE
        SET current_level = GREATEST(law_chain_masters.current_level, $3),
            current_rarity = GREATEST(law_chain_masters.current_rarity, $4)
        RETURNING id
        """

        result = await self._connection.fetchval(
            query,
            character_id,
            chain_id,
            initial_level,
            initial_rarity,
            acquisition_channel.value,
            datetime.now(),
            json.dumps({"method": acquisition_channel.value})
        )

        return result

    async def upgrade_chain_level(
        self,
        character_id: str,
        chain_id: str,
        target_level: int
    ) -> bool:
        """升级法则链等级"""
        # 检查当前等级
        current = await self.get_character_chain(character_id, chain_id)
        if not current:
            return False

        if current.current_level >= target_level:
            return False

        # 检查升级要求
        level_info = await self._get_level_info(chain_id, target_level)
        if not await self._check_level_requirements(character_id, level_info):
            return False

        # 执行升级
        query = """
        UPDATE law_chain_masters
        SET current_level = $1,
            mastery_progress = 0,
            updated_at = CURRENT_TIMESTAMP
        WHERE character_id = $2 AND chain_id = $3
        """

        await self._connection.execute(query, target_level, character_id, chain_id)

        # 记录升级事件
        await self._log_chain_event(
            character_id,
            chain_id,
            "LEVEL_UPGRADE",
            {"from_level": current.current_level, "to_level": target_level}
        )

        return True

    async def get_character_chain(
        self,
        character_id: str,
        chain_id: str
    ) -> Optional[LawChainMaster]:
        """获取角色的法则链信息"""
        query = """
        SELECT * FROM law_chain_masters
        WHERE character_id = $1 AND chain_id = $2
        """

        row = await self._connection.fetchrow(query, character_id, chain_id)
        if row:
            return LawChainMaster(**dict(row))
        return None

    async def list_character_chains(
        self,
        character_id: str,
        min_level: Optional[int] = None
    ) -> List[LawChainMaster]:
        """列出角色的所有法则链"""
        query = """
        SELECT * FROM law_chain_masters
        WHERE character_id = $1
        """
        params = [character_id]

        if min_level is not None:
            query += f" AND current_level >= ${len(params) + 1}"
            params.append(min_level)

        query += " ORDER BY current_level DESC, mastery_progress DESC"

        rows = await self._connection.fetch(query, *params)
        return [LawChainMaster(**dict(row)) for row in rows]

    # =========================================================================
    # 法则链使用和计算
    # =========================================================================

    async def use_law_chain(
        self,
        character_id: str,
        chain_id: str,
        action_type: str,
        zone_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> LawChainUsageLog:
        """使用法则链"""
        start_time = datetime.now()

        # 获取角色的法则链信息
        chain_master = await self.get_character_chain(character_id, chain_id)
        if not chain_master:
            raise ValueError(f"角色 {character_id} 未掌握法则链 {chain_id}")

        # 检查疲劳度
        if chain_master.is_exhausted:
            raise ValueError("法则链疲劳过度，无法使用")

        # 获取场强
        field_strength = Decimal("0")
        if zone_id:
            field_calc = await self.calculate_field_strength(zone_id)
            field_strength = field_calc.calculated_strength

        # 计算成功率
        success_rate = await self._calculate_success_rate(
            chain_master,
            field_strength,
            action_type
        )

        # 判定是否成功
        success = random.random() * 100 < float(success_rate)

        # 计算代价
        costs = await self._calculate_costs(
            chain_master,
            action_type,
            success,
            field_strength
        )

        # 更新角色状态
        await self._update_chain_master_after_use(
            character_id,
            chain_id,
            success,
            costs
        )

        # 记录代价
        await self._record_costs(character_id, chain_id, costs)

        # 创建使用日志
        end_time = datetime.now()
        usage_log = LawChainUsageLog(
            character_id=character_id,
            chain_id=chain_id,
            action_type=action_type,
            action_description=f"使用法则链执行{action_type}",
            input_parameters=parameters or {},
            field_strength=field_strength,
            zone_id=zone_id,
            success=success,
            output_results={"success_rate": float(success_rate)},
            costs_incurred=costs,
            started_at=start_time,
            completed_at=end_time,
            duration_ms=int((end_time - start_time).total_seconds() * 1000)
        )

        # 保存日志
        await self._save_usage_log(usage_log)

        return usage_log

    async def _calculate_success_rate(
        self,
        chain_master: LawChainMaster,
        field_strength: Decimal,
        action_type: str
    ) -> Decimal:
        """计算法则链使用成功率"""
        # 基础成功率
        base_rate = Decimal(str(self.config.base_success_rate))

        # 等级修正
        level_mod = Decimal(str(
            self.config.level_success_modifiers.get(
                chain_master.current_level,
                1.0
            )
        ))

        # 稀有度修正
        rarity_mod = Decimal(str(
            self.config.rarity_success_modifiers.get(
                chain_master.current_rarity,
                1.0
            )
        ))

        # 场强加成
        field_bonus = field_strength * Decimal(str(self.config.field_strength_multiplier))

        # 疲劳惩罚
        fatigue_penalty = chain_master.chain_fatigue / Decimal("200")

        # 污染惩罚
        pollution_penalty = chain_master.pollution_level / Decimal("300")

        # 熟练度加成
        proficiency_bonus = chain_master.mastery_progress / Decimal("200")

        # 计算最终成功率
        final_rate = base_rate * level_mod * rarity_mod
        final_rate = final_rate + field_bonus + proficiency_bonus
        final_rate = final_rate - fatigue_penalty - pollution_penalty

        # 限制在0-100之间
        return max(Decimal("0"), min(Decimal("100"), final_rate))

    async def _calculate_costs(
        self,
        chain_master: LawChainMaster,
        action_type: str,
        success: bool,
        field_strength: Decimal
    ) -> CostRecord:
        """计算使用法则链的代价"""
        costs = CostRecord()

        # 基础代价
        base_fatigue = Decimal("10")
        base_pollution = Decimal("2")

        # 失败惩罚
        failure_multiplier = Decimal("1.5") if not success else Decimal("1")

        # 计算链疲劳
        costs.chain_fatigue = base_fatigue * failure_multiplier
        costs.chain_fatigue *= (Decimal("1") - field_strength / Decimal("10"))

        # 计算污染
        costs.pollution = base_pollution * failure_multiplier
        costs.pollution *= Decimal("1") + chain_master.current_rarity / Decimal("10")

        # 高级法则链可能产生因果债
        if chain_master.current_level >= 4:
            costs.causal_debt = Decimal("5") * (chain_master.current_level - 3)

        # 特定行动可能产生寿债
        if action_type in ["TIME_MANIPULATION", "LIFE_EXCHANGE"]:
            costs.life_debt = Decimal("10") * failure_multiplier

        # 正当性风险
        if chain_master.current_rarity >= 4:
            costs.legitimacy_risk = Decimal("3") * chain_master.current_rarity

        return costs

    async def _update_chain_master_after_use(
        self,
        character_id: str,
        chain_id: str,
        success: bool,
        costs: CostRecord
    ):
        """使用后更新法则链掌握者状态"""
        query = """
        UPDATE law_chain_masters
        SET chain_fatigue = LEAST(100, chain_fatigue + $1),
            pollution_level = LEAST(100, pollution_level + $2),
            total_uses = total_uses + 1,
            successful_uses = successful_uses + $3,
            failed_uses = failed_uses + $4,
            mastery_progress = LEAST(100, mastery_progress + $5),
            updated_at = CURRENT_TIMESTAMP
        WHERE character_id = $6 AND chain_id = $7
        """

        # 成功增加熟练度，失败增加少量熟练度
        mastery_gain = Decimal("2") if success else Decimal("0.5")

        await self._connection.execute(
            query,
            float(costs.chain_fatigue),
            float(costs.pollution),
            1 if success else 0,
            0 if success else 1,
            float(mastery_gain),
            character_id,
            chain_id
        )

    # =========================================================================
    # 法则链组合
    # =========================================================================

    async def create_combination(
        self,
        combination_data: LawChainCombination
    ) -> str:
        """创建法则链组合"""
        query = """
        INSERT INTO law_chain_combinations (
            novel_id, combination_name, combination_type, description,
            required_chains, effects, activation_conditions,
            combination_cost, stability_rating, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING id
        """

        result = await self._connection.fetchval(
            query,
            combination_data.novel_id,
            combination_data.combination_name,
            combination_data.combination_type.value,
            combination_data.description,
            json.dumps([r.model_dump() for r in combination_data.required_chains]),
            json.dumps(combination_data.effects.model_dump()),
            json.dumps(combination_data.activation_conditions),
            json.dumps(combination_data.combination_cost.model_dump()),
            combination_data.stability_rating,
            json.dumps(combination_data.metadata)
        )

        return result

    async def use_combination(
        self,
        character_id: str,
        combination_id: str,
        zone_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> LawChainUsageLog:
        """使用法则链组合"""
        # 获取组合信息
        combination = await self._get_combination(combination_id)
        if not combination:
            raise ValueError(f"组合 {combination_id} 不存在")

        # 检查角色是否满足组合要求
        if not await self._check_combination_requirements(character_id, combination):
            raise ValueError("不满足组合要求")

        # 获取角色的组合熟练度
        char_combo = await self._get_character_combination(character_id, combination_id)

        # 计算场强
        field_strength = Decimal("0")
        if zone_id:
            field_calc = await self.calculate_field_strength(zone_id)
            field_strength = field_calc.calculated_strength

        # 计算成功率（组合的成功率计算更复杂）
        success_rate = await self._calculate_combination_success_rate(
            combination,
            char_combo,
            field_strength
        )

        # 判定成功
        success = random.random() * 100 < float(success_rate)

        # 计算组合代价
        costs = await self._calculate_combination_costs(
            combination,
            success,
            field_strength
        )

        # 更新所有涉及的法则链状态
        for req_chain in combination.required_chains:
            await self._update_chain_master_after_use(
                character_id,
                req_chain.chain_id,
                success,
                CostRecord(chain_fatigue=costs.chain_fatigue / len(combination.required_chains))
            )

        # 更新组合熟练度
        await self._update_combination_proficiency(
            character_id,
            combination_id,
            success
        )

        # 创建使用日志
        usage_log = LawChainUsageLog(
            character_id=character_id,
            combination_id=combination_id,
            action_type="COMBINATION_USE",
            action_description=f"使用组合：{combination.combination_name}",
            input_parameters=parameters or {},
            field_strength=field_strength,
            zone_id=zone_id,
            success=success,
            output_results={
                "success_rate": float(success_rate),
                "combination_type": combination.combination_type.value
            },
            costs_incurred=costs,
            started_at=datetime.now()
        )

        # 保存日志
        await self._save_usage_log(usage_log)

        return usage_log

    async def _check_combination_requirements(
        self,
        character_id: str,
        combination: LawChainCombination
    ) -> bool:
        """检查角色是否满足组合要求"""
        for req in combination.required_chains:
            chain_master = await self.get_character_chain(character_id, req.chain_id)
            if not chain_master:
                return False

            if chain_master.current_level < req.min_level:
                return False

            if chain_master.current_rarity < req.min_rarity:
                return False

            if chain_master.is_exhausted:
                return False

        return True

    async def _calculate_combination_success_rate(
        self,
        combination: LawChainCombination,
        char_combo: Optional[CharacterChainCombination],
        field_strength: Decimal
    ) -> Decimal:
        """计算组合成功率"""
        # 基础成功率取决于稳定性
        base_rate = Decimal(str(combination.stability_rating))

        # 熟练度加成
        proficiency_bonus = Decimal("0")
        if char_combo:
            proficiency_bonus = Decimal(str(char_combo.proficiency_level)) / Decimal("2")

        # 场强加成
        field_bonus = field_strength * Decimal("10")

        # 组合类型修正
        type_modifiers = {
            CombinationType.SYNERGY: Decimal("1.2"),
            CombinationType.TACTICAL: Decimal("1.0"),
            CombinationType.COUNTER: Decimal("0.8")
        }
        type_mod = type_modifiers.get(combination.combination_type, Decimal("1.0"))

        # 计算最终成功率
        final_rate = (base_rate + proficiency_bonus + field_bonus) * type_mod

        return max(Decimal("0"), min(Decimal("100"), final_rate))

    # =========================================================================
    # 场强系统
    # =========================================================================

    async def create_field_zone(
        self,
        zone_data: FieldStrengthZone
    ) -> str:
        """创建场强区域"""
        query = """
        INSERT INTO field_strength_zones (
            novel_id, zone_name, zone_type, location_data,
            base_field_strength, current_field_strength,
            time_modifiers, resonance_factors, affected_chains,
            special_events, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING id
        """

        result = await self._connection.fetchval(
            query,
            zone_data.novel_id,
            zone_data.zone_name,
            zone_data.zone_type,
            json.dumps(zone_data.location_data.model_dump()),
            float(zone_data.base_field_strength),
            float(zone_data.current_field_strength),
            json.dumps(zone_data.time_modifiers.model_dump()),
            json.dumps(zone_data.resonance_factors.model_dump()),
            json.dumps(zone_data.affected_chains),
            json.dumps(zone_data.special_events),
            json.dumps(zone_data.metadata)
        )

        return result

    async def calculate_field_strength(
        self,
        zone_id: str,
        people_count: int = 0
    ) -> FieldStrengthCalculation:
        """计算当前场强"""
        # 获取区域信息
        zone = await self._get_field_zone(zone_id)
        if not zone:
            raise ValueError(f"场强区域 {zone_id} 不存在")

        current_time = datetime.now()

        # 获取时段修正
        hour = current_time.hour
        time_period = self._get_time_period(hour)
        time_factor = getattr(zone.time_modifiers, time_period, 0)

        # 计算人群共振
        resonance_factor = Decimal("1.0")
        if people_count >= zone.resonance_factors.min_people:
            resonance_factor = Decimal(str(zone.resonance_factors.resonance_multiplier))

        # 计算最终场强
        location_factor = zone.base_field_strength
        calculated_strength = (location_factor + Decimal(str(time_factor))) * resonance_factor
        calculated_strength = max(Decimal("0"), min(Decimal("5"), calculated_strength))

        # 创建计算记录
        calculation = FieldStrengthCalculation(
            zone_id=zone_id,
            location_factor=location_factor,
            time_factor=Decimal(str(time_factor)),
            people_count=people_count,
            resonance_factor=resonance_factor,
            calculated_strength=calculated_strength,
            active_chains=zone.affected_chains
        )

        # 保存计算记录
        await self._save_field_calculation(calculation)

        return calculation

    def _get_time_period(self, hour: int) -> str:
        """根据小时获取时段"""
        if 5 <= hour < 7:
            return "dawn"
        elif 7 <= hour < 11:
            return "morning"
        elif 11 <= hour < 13:
            return "noon"
        elif 13 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 19:
            return "dusk"
        elif 19 <= hour < 23:
            return "night"
        else:
            return "midnight"

    # =========================================================================
    # 代价和债务管理
    # =========================================================================

    async def _record_costs(
        self,
        character_id: str,
        chain_id: str,
        costs: CostRecord
    ):
        """记录法则链使用代价"""
        # 记录各种代价
        cost_types = [
            (CostType.CHAIN_FATIGUE, "F", costs.chain_fatigue),
            (CostType.POLLUTION, "P", costs.pollution),
            (CostType.CAUSAL_DEBT, "C", costs.causal_debt),
            (CostType.LIFE_DEBT, "L", costs.life_debt),
            (CostType.LEGITIMACY_RISK, "N", costs.legitimacy_risk)
        ]

        for cost_type, code, value in cost_types:
            if value > 0:
                query = """
                INSERT INTO law_chain_costs (
                    character_id, chain_id, cost_type, cost_code,
                    cost_value, accumulated_value, source_action,
                    source_timestamp
                ) VALUES ($1, $2, $3, $4, $5, $5, $6, $7)
                """

                await self._connection.execute(
                    query,
                    character_id,
                    chain_id,
                    cost_type.value,
                    code,
                    float(value),
                    "LAW_CHAIN_USE",
                    datetime.now()
                )

        # 如果产生因果债，创建债务记录
        if costs.causal_debt > 0:
            await self._create_causal_debt(
                character_id,
                chain_id,
                costs.causal_debt
            )

    async def _create_causal_debt(
        self,
        character_id: str,
        chain_id: str,
        amount: Decimal
    ):
        """创建因果债务"""
        query = """
        INSERT INTO causal_debts (
            character_id, debt_type, original_amount, current_amount,
            interest_rate, creditor_type, status, source_chains
        ) VALUES ($1, $2, $3, $3, $4, $5, $6, $7)
        """

        await self._connection.execute(
            query,
            character_id,
            "LAW_CHAIN_CAUSAL",
            float(amount),
            2.0,  # 2%利率
            "天道",
            "active",
            json.dumps([chain_id])
        )

    async def get_character_debts(
        self,
        character_id: str,
        status: Optional[str] = None
    ) -> List[CausalDebt]:
        """获取角色的债务"""
        query = """
        SELECT * FROM causal_debts
        WHERE character_id = $1
        """
        params = [character_id]

        if status:
            query += f" AND status = ${len(params) + 1}"
            params.append(status)

        query += " ORDER BY current_amount DESC"

        rows = await self._connection.fetch(query, *params)
        return [CausalDebt(**dict(row)) for row in rows]

    async def pay_debt(
        self,
        debt_id: str,
        payment_amount: Decimal
    ) -> bool:
        """偿还债务"""
        query = """
        UPDATE causal_debts
        SET current_amount = GREATEST(0, current_amount - $1),
            status = CASE
                WHEN current_amount - $1 <= 0 THEN 'paid'
                WHEN current_amount - $1 < original_amount THEN 'partial'
                ELSE status
            END,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = $2
        """

        await self._connection.execute(query, float(payment_amount), debt_id)
        return True

    # =========================================================================
    # 恢复和维护
    # =========================================================================

    async def recover_chain_fatigue(
        self,
        character_id: str,
        hours: float = 1.0
    ):
        """恢复链疲劳"""
        recovery_amount = self.config.fatigue_recovery_rate * hours

        query = """
        UPDATE law_chain_masters
        SET chain_fatigue = GREATEST(0, chain_fatigue - $1),
            last_recovery_time = CURRENT_TIMESTAMP
        WHERE character_id = $2
        """

        await self._connection.execute(query, recovery_amount, character_id)

    async def decay_pollution(
        self,
        character_id: str,
        days: float = 1.0
    ):
        """衰减污染"""
        decay_amount = self.config.pollution_decay_rate * days

        query = """
        UPDATE law_chain_masters
        SET pollution_level = GREATEST(0, pollution_level - $1)
        WHERE character_id = $2
        """

        await self._connection.execute(query, decay_amount, character_id)

    # =========================================================================
    # 分析和统计
    # =========================================================================

    async def get_character_chain_stats(self, character_id: str) -> Dict[str, Any]:
        """获取角色的法则链统计"""
        query = """
        SELECT
            COUNT(*) as total_chains,
            AVG(current_level) as avg_level,
            AVG(current_rarity) as avg_rarity,
            SUM(total_uses) as total_uses,
            SUM(successful_uses) as successful_uses,
            AVG(mastery_progress) as avg_mastery,
            AVG(chain_fatigue) as avg_fatigue,
            AVG(pollution_level) as avg_pollution
        FROM law_chain_masters
        WHERE character_id = $1
        """

        row = await self._connection.fetchrow(query, character_id)

        return {
            "total_chains": row["total_chains"],
            "average_level": float(row["avg_level"] or 0),
            "average_rarity": float(row["avg_rarity"] or 0),
            "total_uses": row["total_uses"] or 0,
            "success_rate": (
                float(row["successful_uses"] / row["total_uses"] * 100)
                if row["total_uses"] else 0
            ),
            "average_mastery": float(row["avg_mastery"] or 0),
            "average_fatigue": float(row["avg_fatigue"] or 0),
            "average_pollution": float(row["avg_pollution"] or 0)
        }

    async def get_combination_recommendations(
        self,
        character_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """获取组合推荐"""
        # 获取角色掌握的法则链
        chains = await self.list_character_chains(character_id)
        chain_ids = {c.chain_id for c in chains}

        # 查找可用的组合
        query = """
        SELECT lcc.*,
               COUNT(DISTINCT ccc.id) as usage_count,
               AVG(ccc.proficiency_level) as avg_proficiency
        FROM law_chain_combinations lcc
        LEFT JOIN character_chain_combinations ccc
            ON lcc.id = ccc.combination_id AND ccc.character_id = $1
        WHERE lcc.stability_rating >= $2
        GROUP BY lcc.id
        ORDER BY lcc.stability_rating DESC, usage_count DESC
        LIMIT $3
        """

        rows = await self._connection.fetch(
            query,
            character_id,
            self.config.combination_stability_threshold,
            limit
        )

        recommendations = []
        for row in rows:
            # 检查是否满足要求
            required_chains = json.loads(row["required_chains"])
            required_chain_ids = {rc["chain_id"] for rc in required_chains}

            if required_chain_ids.issubset(chain_ids):
                recommendations.append({
                    "combination_id": row["id"],
                    "name": row["combination_name"],
                    "type": row["combination_type"],
                    "stability": row["stability_rating"],
                    "usage_count": row["usage_count"] or 0,
                    "proficiency": float(row["avg_proficiency"] or 0),
                    "missing_chains": []
                })
            else:
                missing = required_chain_ids - chain_ids
                if len(missing) <= 2:  # 只推荐缺少不超过2条链的组合
                    recommendations.append({
                        "combination_id": row["id"],
                        "name": row["combination_name"],
                        "type": row["combination_type"],
                        "stability": row["stability_rating"],
                        "usage_count": row["usage_count"] or 0,
                        "proficiency": float(row["avg_proficiency"] or 0),
                        "missing_chains": list(missing)
                    })

        return recommendations[:limit]

    # =========================================================================
    # 私有辅助方法
    # =========================================================================

    async def _get_level_info(self, chain_id: str, level: int) -> Optional[LawChainLevel]:
        """获取等级信息"""
        query = """
        SELECT * FROM law_chain_levels
        WHERE chain_id = $1 AND level_number = $2
        """

        row = await self._connection.fetchrow(query, chain_id, level)
        if row:
            return LawChainLevel(**dict(row))
        return None

    async def _check_level_requirements(
        self,
        character_id: str,
        level_info: LawChainLevel
    ) -> bool:
        """检查等级升级要求"""
        # 这里可以添加更复杂的检查逻辑
        # 比如检查修炼阶段、资源等
        return True

    async def _log_chain_event(
        self,
        character_id: str,
        chain_id: str,
        event_type: str,
        details: Dict[str, Any]
    ):
        """记录法则链事件"""
        # 可以记录到事件表或日志表
        pass

    async def _get_combination(self, combination_id: str) -> Optional[LawChainCombination]:
        """获取组合信息"""
        query = """
        SELECT * FROM law_chain_combinations WHERE id = $1
        """

        row = await self._connection.fetchrow(query, combination_id)
        if row:
            data = dict(row)
            data["required_chains"] = [
                ChainRequirement(**rc) for rc in json.loads(data["required_chains"])
            ]
            return LawChainCombination(**data)
        return None

    async def _get_character_combination(
        self,
        character_id: str,
        combination_id: str
    ) -> Optional[CharacterChainCombination]:
        """获取角色的组合信息"""
        query = """
        SELECT * FROM character_chain_combinations
        WHERE character_id = $1 AND combination_id = $2
        """

        row = await self._connection.fetchrow(query, character_id, combination_id)
        if row:
            return CharacterChainCombination(**dict(row))
        return None

    async def _update_combination_proficiency(
        self,
        character_id: str,
        combination_id: str,
        success: bool
    ):
        """更新组合熟练度"""
        proficiency_gain = 3 if success else 1

        query = """
        INSERT INTO character_chain_combinations (
            character_id, combination_id, proficiency_level,
            total_uses, successful_uses, last_used_at
        ) VALUES ($1, $2, $3, 1, $4, $5)
        ON CONFLICT (character_id, combination_id) DO UPDATE
        SET proficiency_level = LEAST(100,
                character_chain_combinations.proficiency_level + $3),
            total_uses = character_chain_combinations.total_uses + 1,
            successful_uses = character_chain_combinations.successful_uses + $4,
            last_used_at = $5
        """

        await self._connection.execute(
            query,
            character_id,
            combination_id,
            proficiency_gain,
            1 if success else 0,
            datetime.now()
        )

    async def _calculate_combination_costs(
        self,
        combination: LawChainCombination,
        success: bool,
        field_strength: Decimal
    ) -> CostRecord:
        """计算组合使用代价"""
        costs = CostRecord()

        # 组合的基础代价
        costs.chain_fatigue = combination.combination_cost.chain_fatigue
        costs.pollution = combination.combination_cost.pollution_risk

        # 失败惩罚
        if not success:
            costs.chain_fatigue *= Decimal("1.5")
            costs.pollution *= Decimal("2")

        # 场强减免
        reduction = field_strength / Decimal("10")
        costs.chain_fatigue *= (Decimal("1") - reduction)

        return costs

    async def _get_field_zone(self, zone_id: str) -> Optional[FieldStrengthZone]:
        """获取场强区域"""
        query = """
        SELECT * FROM field_strength_zones WHERE id = $1
        """

        row = await self._connection.fetchrow(query, zone_id)
        if row:
            return FieldStrengthZone(**dict(row))
        return None

    async def _save_usage_log(self, log: LawChainUsageLog):
        """保存使用日志"""
        query = """
        INSERT INTO law_chain_usage_logs (
            character_id, chain_id, combination_id, action_type,
            action_description, input_parameters, field_strength,
            zone_id, success, output_results, costs_incurred,
            side_effects, started_at, completed_at, duration_ms
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
        """

        await self._connection.execute(
            query,
            log.character_id,
            log.chain_id,
            log.combination_id,
            log.action_type,
            log.action_description,
            json.dumps(log.input_parameters),
            float(log.field_strength) if log.field_strength else None,
            log.zone_id,
            log.success,
            json.dumps(log.output_results),
            json.dumps(log.costs_incurred.model_dump()),
            json.dumps(log.side_effects),
            log.started_at,
            log.completed_at,
            log.duration_ms
        )

    async def _save_field_calculation(self, calc: FieldStrengthCalculation):
        """保存场强计算"""
        query = """
        INSERT INTO field_strength_calculations (
            zone_id, calculation_time, location_factor, time_factor,
            people_count, resonance_factor, calculated_strength,
            active_chains, special_modifiers
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """

        await self._connection.execute(
            query,
            calc.zone_id,
            calc.calculation_time,
            float(calc.location_factor),
            float(calc.time_factor),
            calc.people_count,
            float(calc.resonance_factor),
            float(calc.calculated_strength),
            json.dumps(calc.active_chains),
            json.dumps(calc.special_modifiers)
        )