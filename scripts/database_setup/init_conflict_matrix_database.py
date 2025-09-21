"""
跨域冲突矩阵数据库初始化脚本
将分析结果导入到PostgreSQL数据库中
"""

import json
import asyncio
import asyncpg
from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Any, Optional
import os
from pathlib import Path


class ConflictMatrixDatabaseInitializer:
    """冲突矩阵数据库初始化器"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or "postgresql://localhost:5432/novellus"
        self.report_data = None

    async def load_analysis_report(self, report_file: str) -> None:
        """加载分析报告数据"""
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                self.report_data = json.load(f)
            print(f"✓ 成功加载分析报告: {report_file}")
        except Exception as e:
            print(f"✗ 加载分析报告失败: {e}")
            raise

    async def create_tables(self, conn) -> None:
        """创建数据库表"""

        # 创建扩展的跨域冲突矩阵表
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS cross_domain_conflict_matrix (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            novel_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
            matrix_name VARCHAR(255) NOT NULL,
            domain_a VARCHAR(50) NOT NULL,
            domain_b VARCHAR(50) NOT NULL,
            intensity DECIMAL(3,1) NOT NULL CHECK (intensity >= 0 AND intensity <= 5),
            core_resources TEXT[] NOT NULL,
            trigger_laws TEXT[] NOT NULL,
            typical_scenarios TEXT[] NOT NULL,
            key_roles TEXT[] NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(novel_id, domain_a, domain_b),
            CHECK (domain_a != domain_b)
        );
        """)

        # 创建冲突实体表
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS conflict_entities (
            id UUID PRIMARY KEY,
            novel_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
            name VARCHAR(255) NOT NULL,
            entity_type VARCHAR(100) NOT NULL,
            domains TEXT[] NOT NULL,
            importance VARCHAR(20) DEFAULT '中',
            description TEXT,
            conflict_context VARCHAR(100),
            strategic_value DECIMAL(3,1) DEFAULT 5.0,
            scarcity_level DECIMAL(3,1) DEFAULT 5.0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 创建冲突关系表
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS conflict_relations (
            id UUID PRIMARY KEY,
            novel_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
            source_entity_id UUID REFERENCES conflict_entities(id) ON DELETE CASCADE,
            target_entity_id UUID REFERENCES conflict_entities(id) ON DELETE CASCADE,
            relation_type VARCHAR(50) NOT NULL,
            strength DECIMAL(3,2) DEFAULT 1.0,
            description TEXT,
            context VARCHAR(100),
            is_cross_domain BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 创建冲突升级路径表
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS conflict_escalation_paths (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            conflict_matrix_id UUID REFERENCES cross_domain_conflict_matrix(id) ON DELETE CASCADE,
            level INTEGER NOT NULL CHECK (level >= 1 AND level <= 10),
            level_name VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            triggers TEXT[] NOT NULL,
            probability DECIMAL(3,2) CHECK (probability >= 0 AND probability <= 1),
            risk_level INTEGER CHECK (risk_level >= 1 AND risk_level <= 10),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 创建故事钩子表
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS conflict_story_hooks (
            id UUID PRIMARY KEY,
            novel_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
            conflict_matrix_id UUID REFERENCES cross_domain_conflict_matrix(id) ON DELETE SET NULL,
            title VARCHAR(500) NOT NULL,
            description TEXT NOT NULL,
            hook_type VARCHAR(50) DEFAULT '综合冲突',
            domains_involved TEXT[] NOT NULL,
            complexity INTEGER DEFAULT 5 CHECK (complexity >= 1 AND complexity <= 10),
            drama_value INTEGER DEFAULT 5 CHECK (drama_value >= 1 AND drama_value <= 10),
            character_potential INTEGER DEFAULT 5 CHECK (character_potential >= 1 AND character_potential <= 10),
            story_value DECIMAL(3,1) DEFAULT 5.0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 创建冲突场景表
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS conflict_scenarios (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            novel_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
            conflict_matrix_id UUID REFERENCES cross_domain_conflict_matrix(id) ON DELETE CASCADE,
            title VARCHAR(500) NOT NULL,
            description TEXT NOT NULL,
            scenario_type VARCHAR(50) DEFAULT '跨域冲突',
            domains_involved TEXT[] NOT NULL,
            participants TEXT[] NOT NULL,
            triggers TEXT[] DEFAULT '{}',
            outcomes TEXT[] DEFAULT '{}',
            complexity_level INTEGER DEFAULT 5 CHECK (complexity_level >= 1 AND complexity_level <= 10),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 创建分析结果表
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS conflict_analysis_results (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            novel_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
            analysis_type VARCHAR(100) NOT NULL,
            results JSONB NOT NULL,
            confidence_score DECIMAL(3,2) DEFAULT 0.90,
            analysis_version VARCHAR(20) DEFAULT '1.0',
            generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 创建索引
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_conflict_matrix_domains ON cross_domain_conflict_matrix(domain_a, domain_b);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_conflict_matrix_intensity ON cross_domain_conflict_matrix(intensity DESC);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_conflict_entities_type ON conflict_entities(entity_type);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_conflict_entities_name ON conflict_entities(name);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_conflict_relations_type ON conflict_relations(relation_type);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_escalation_paths_level ON conflict_escalation_paths(level);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_story_hooks_type ON conflict_story_hooks(hook_type);")

        print("✓ 数据库表结构创建完成")

    async def import_conflict_matrices(self, conn) -> Dict[str, str]:
        """导入冲突矩阵数据"""
        if not self.report_data or '5. 数据库模型' not in self.report_data:
            raise ValueError("分析报告数据不完整")

        db_data = self.report_data['5. 数据库模型']
        conflict_matrices = db_data['conflict_matrices']

        matrix_id_map = {}  # 映射原ID到新ID

        for matrix_data in conflict_matrices:
            new_id = str(uuid4())
            matrix_id_map[matrix_data['id']] = new_id

            await conn.execute("""
            INSERT INTO cross_domain_conflict_matrix
            (id, novel_id, matrix_name, domain_a, domain_b, intensity,
             core_resources, trigger_laws, typical_scenarios, key_roles)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
            new_id,
            matrix_data['novel_id'],
            matrix_data['matrix_name'],
            matrix_data['domain_a'],
            matrix_data['domain_b'],
            matrix_data['intensity'],
            matrix_data['core_resources'],
            matrix_data['trigger_laws'],
            matrix_data['typical_scenarios'],
            matrix_data['key_roles']
            )

        print(f"✓ 导入冲突矩阵数据: {len(conflict_matrices)} 条记录")
        return matrix_id_map

    async def import_entities_and_relations(self, conn) -> None:
        """导入实体和关系数据"""
        db_data = self.report_data['5. 数据库模型']

        # 导入实体
        entities = db_data['conflict_entities']
        for entity_data in entities:
            await conn.execute("""
            INSERT INTO conflict_entities
            (id, novel_id, name, entity_type, domains, importance, description, conflict_context)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            entity_data['id'],
            entity_data['novel_id'],
            entity_data['name'],
            entity_data['entity_type'],
            entity_data['domains'],
            entity_data['importance'],
            entity_data['description'],
            entity_data.get('conflict_context', '')
            )

        # 导入关系
        relations = db_data['conflict_relations']
        for relation_data in relations:
            await conn.execute("""
            INSERT INTO conflict_relations
            (id, novel_id, source_entity_id, target_entity_id, relation_type,
             strength, description, is_cross_domain)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            relation_data['id'],
            relation_data['novel_id'],
            relation_data['source_entity_id'],
            relation_data['target_entity_id'],
            relation_data['relation_type'],
            relation_data['strength'],
            relation_data['description'],
            True  # 跨域冲突中的关系默认为跨域
            )

        print(f"✓ 导入实体数据: {len(entities)} 条记录")
        print(f"✓ 导入关系数据: {len(relations)} 条记录")

    async def import_escalation_paths(self, conn, matrix_id_map: Dict[str, str]) -> None:
        """导入升级路径数据"""
        db_data = self.report_data['5. 数据库模型']
        escalation_levels = db_data['escalation_levels']

        for level_data in escalation_levels:
            # 获取新的矩阵ID
            new_matrix_id = matrix_id_map.get(level_data['conflict_matrix_id'])
            if not new_matrix_id:
                continue

            await conn.execute("""
            INSERT INTO conflict_escalation_paths
            (conflict_matrix_id, level, level_name, description, triggers, probability)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            new_matrix_id,
            level_data['level'],
            level_data['description'],  # 使用description作为level_name
            level_data['description'],
            level_data.get('triggers', []),
            level_data['probability']
            )

        print(f"✓ 导入升级路径数据: {len(escalation_levels)} 条记录")

    async def import_story_hooks(self, conn, matrix_id_map: Dict[str, str]) -> None:
        """导入故事钩子数据"""
        db_data = self.report_data['5. 数据库模型']
        story_hooks = db_data['story_hooks']

        for hook_data in story_hooks:
            # 获取新的矩阵ID
            new_matrix_id = matrix_id_map.get(hook_data['conflict_matrix_id'])

            await conn.execute("""
            INSERT INTO conflict_story_hooks
            (id, novel_id, conflict_matrix_id, title, description, hook_type,
             domains_involved, complexity, drama_value)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            hook_data['id'],
            hook_data['novel_id'],
            new_matrix_id,
            hook_data['title'],
            hook_data['description'],
            hook_data['hook_type'],
            hook_data['domains_involved'],
            hook_data['complexity'],
            hook_data['drama_value']
            )

        print(f"✓ 导入故事钩子数据: {len(story_hooks)} 条记录")

    async def import_analysis_results(self, conn) -> None:
        """导入分析结果数据"""
        # 保存整个分析报告作为分析结果
        analysis_sections = [
            ("冲突矩阵分析", self.report_data.get('1. 冲突矩阵深度分析', {})),
            ("实体关系网络分析", self.report_data.get('2. 实体关系网络分析', {})),
            ("冲突升级路径分析", self.report_data.get('3. 冲突升级路径分析', {})),
            ("故事情节潜力评估", self.report_data.get('4. 故事情节潜力评估', {})),
            ("世界观一致性检查", self.report_data.get('6. 世界观一致性检查', {})),
            ("可视化数据", self.report_data.get('8. 可视化数据', {}))
        ]

        for analysis_type, results in analysis_sections:
            if results:
                await conn.execute("""
                INSERT INTO conflict_analysis_results
                (novel_id, analysis_type, results, confidence_score, analysis_version)
                VALUES ($1, $2, $3, $4, $5)
                """,
                '00000000-0000-0000-0000-000000000000',  # 占位符novel_id
                analysis_type,
                json.dumps(results, ensure_ascii=False),
                0.90,
                "简化版 1.0"
                )

        print(f"✓ 导入分析结果数据: {len(analysis_sections)} 条记录")

    async def create_conflict_scenarios(self, conn, matrix_id_map: Dict[str, str]) -> None:
        """创建冲突场景数据"""
        # 基于矩阵数据创建场景
        db_data = self.report_data['5. 数据库模型']
        conflict_matrices = db_data['conflict_matrices']

        for matrix_data in conflict_matrices:
            new_matrix_id = matrix_id_map.get(matrix_data['id'])
            if not new_matrix_id:
                continue

            # 为每个典型场景创建记录
            for i, scenario in enumerate(matrix_data['typical_scenarios']):
                await conn.execute("""
                INSERT INTO conflict_scenarios
                (novel_id, conflict_matrix_id, title, description, domains_involved,
                 participants, complexity_level)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                matrix_data['novel_id'],
                new_matrix_id,
                f"{matrix_data['domain_a']}与{matrix_data['domain_b']}冲突场景{i+1}",
                scenario,
                [matrix_data['domain_a'], matrix_data['domain_b']],
                matrix_data['key_roles'],
                min(5 + matrix_data['intensity'], 10)  # 基于冲突强度设置复杂度
                )

        print(f"✓ 创建冲突场景数据完成")

    async def initialize_database(self, report_file: str) -> None:
        """初始化数据库"""
        print("开始初始化跨域冲突矩阵数据库...")

        # 加载分析报告
        await self.load_analysis_report(report_file)

        try:
            # 连接数据库
            conn = await asyncpg.connect(self.database_url)
            print("✓ 数据库连接成功")

            try:
                # 创建表结构
                await self.create_tables(conn)

                # 清理现有数据（可选）
                await self.clean_existing_data(conn)

                # 导入数据
                matrix_id_map = await self.import_conflict_matrices(conn)
                await self.import_entities_and_relations(conn)
                await self.import_escalation_paths(conn, matrix_id_map)
                await self.import_story_hooks(conn, matrix_id_map)
                await self.create_conflict_scenarios(conn, matrix_id_map)
                await self.import_analysis_results(conn)

                # 验证数据
                await self.verify_data(conn)

                print("\n✓ 跨域冲突矩阵数据库初始化完成！")

            finally:
                await conn.close()

        except Exception as e:
            print(f"✗ 数据库初始化失败: {e}")
            raise

    async def clean_existing_data(self, conn) -> None:
        """清理现有数据"""
        tables = [
            'conflict_analysis_results',
            'conflict_scenarios',
            'conflict_story_hooks',
            'conflict_escalation_paths',
            'conflict_relations',
            'conflict_entities',
            'cross_domain_conflict_matrix'
        ]

        for table in tables:
            await conn.execute(f"DELETE FROM {table}")

        print("✓ 清理现有数据完成")

    async def verify_data(self, conn) -> None:
        """验证导入的数据"""
        verification_queries = [
            ("冲突矩阵", "SELECT COUNT(*) FROM cross_domain_conflict_matrix"),
            ("冲突实体", "SELECT COUNT(*) FROM conflict_entities"),
            ("冲突关系", "SELECT COUNT(*) FROM conflict_relations"),
            ("升级路径", "SELECT COUNT(*) FROM conflict_escalation_paths"),
            ("故事钩子", "SELECT COUNT(*) FROM conflict_story_hooks"),
            ("冲突场景", "SELECT COUNT(*) FROM conflict_scenarios"),
            ("分析结果", "SELECT COUNT(*) FROM conflict_analysis_results")
        ]

        print("\n数据验证结果:")
        for name, query in verification_queries:
            count = await conn.fetchval(query)
            print(f"  {name}: {count} 条记录")

        # 验证矩阵完整性
        domains_result = await conn.fetch("""
        SELECT domain_a, domain_b, intensity
        FROM cross_domain_conflict_matrix
        ORDER BY domain_a, domain_b
        """)

        print(f"\n冲突矩阵详情:")
        for row in domains_result:
            print(f"  {row['domain_a']} ↔ {row['domain_b']}: 强度 {row['intensity']}")


async def main():
    """主函数"""
    # 数据库连接配置
    database_url = "postgresql://postgres:123456@localhost:5432/novellus"

    # 分析报告文件路径
    report_file = "D:/work/novellus/cross_domain_conflict_analysis_report.json"

    # 检查文件是否存在
    if not os.path.exists(report_file):
        print(f"✗ 分析报告文件不存在: {report_file}")
        print("请先运行 simple_conflict_analyzer.py 生成分析报告")
        return

    # 初始化数据库
    initializer = ConflictMatrixDatabaseInitializer(database_url)

    try:
        await initializer.initialize_database(report_file)
        print("\n🎉 跨域冲突矩阵数据库初始化成功完成！")
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())