#!/usr/bin/env python3
"""
跨域冲突分析系统数据导入工具
用于将分析结果导入到"裂世九域·法则链纪元"数据库中
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import asyncpg
from dataclasses import dataclass

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ImportConfig:
    """导入配置"""
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "novellus"
    db_user: str = "postgres"
    db_password: str = "postgres"

    # 项目信息
    project_id: str = "29c170c5-4a3e-4829-a242-74c1acb96453"
    novel_id: str = "e1fd1aa4-bde2-4c76-8cee-334e54fa47d1"

    # 数据源路径
    conflict_analysis_file: str = "cross_domain_conflict_analysis_report.json"
    conflict_elements_file: str = "conflict_extraction_output/conflict_elements_structured_data.json"
    enhanced_conflict_file: str = "enhanced_conflict_output/conflict_elements_enhanced_data.json"

    # 导入选项
    clear_existing_data: bool = False
    validate_data_integrity: bool = True
    create_backup: bool = True

class ConflictDataImporter:
    """冲突数据导入器"""

    def __init__(self, config: ImportConfig):
        self.config = config
        self.conn: Optional[asyncpg.Connection] = None
        self.stats = {
            'matrices_imported': 0,
            'entities_imported': 0,
            'relations_imported': 0,
            'hooks_imported': 0,
            'scenarios_imported': 0,
            'network_analyses_imported': 0,
            'ai_content_imported': 0,
            'errors': []
        }

    async def connect(self):
        """连接数据库"""
        try:
            self.conn = await asyncpg.connect(
                host=self.config.db_host,
                port=self.config.db_port,
                database=self.config.db_name,
                user=self.config.db_user,
                password=self.config.db_password
            )
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    async def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            await self.conn.close()
            logger.info("数据库连接已关闭")

    async def validate_project_exists(self) -> bool:
        """验证项目和小说是否存在"""
        try:
            # 检查项目
            project_result = await self.conn.fetchrow(
                "SELECT id, name FROM projects WHERE id = $1",
                uuid.UUID(self.config.project_id)
            )
            if not project_result:
                logger.error(f"项目 {self.config.project_id} 不存在")
                return False

            # 检查小说
            novel_result = await self.conn.fetchrow(
                "SELECT id, name FROM novels WHERE id = $1",
                uuid.UUID(self.config.novel_id)
            )
            if not novel_result:
                logger.error(f"小说 {self.config.novel_id} 不存在")
                return False

            logger.info(f"项目: {project_result['name']}, 小说: {novel_result['name']}")
            return True

        except Exception as e:
            logger.error(f"验证项目小说失败: {e}")
            return False

    async def clear_existing_conflict_data(self):
        """清除现有冲突数据"""
        if not self.config.clear_existing_data:
            return

        try:
            # 按依赖关系顺序删除
            tables_to_clear = [
                'conflict_predictions',
                'network_analysis_results',
                'ai_generated_content',
                'conflict_analysis_results',
                'conflict_story_hooks',
                'conflict_scenarios',
                'conflict_escalation_paths',
                'conflict_relations',
                'conflict_entities',
                'cross_domain_conflict_matrix'
            ]

            for table in tables_to_clear:
                result = await self.conn.execute(
                    f"DELETE FROM {table} WHERE novel_id = $1",
                    uuid.UUID(self.config.novel_id)
                )
                deleted_count = int(result.split()[-1])
                if deleted_count > 0:
                    logger.info(f"清除 {table}: {deleted_count} 条记录")

        except Exception as e:
            logger.error(f"清除现有数据失败: {e}")
            raise

    async def load_conflict_analysis_data(self) -> Dict[str, Any]:
        """加载冲突分析数据"""
        data_files = [
            (self.config.conflict_analysis_file, "conflict_analysis"),
            (self.config.conflict_elements_file, "conflict_elements"),
            (self.config.enhanced_conflict_file, "enhanced_elements")
        ]

        loaded_data = {}

        for file_path, data_key in data_files:
            try:
                full_path = Path(file_path)
                if not full_path.exists():
                    logger.warning(f"文件不存在: {file_path}")
                    continue

                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    loaded_data[data_key] = data
                    logger.info(f"成功加载 {data_key}: {file_path}")

            except Exception as e:
                logger.error(f"加载文件失败 {file_path}: {e}")
                self.stats['errors'].append(f"文件加载失败: {file_path} - {e}")

        return loaded_data

    async def import_conflict_matrices(self, analysis_data: Dict[str, Any]) -> Dict[str, uuid.UUID]:
        """导入冲突矩阵数据"""
        if 'conflict_analysis' not in analysis_data:
            logger.warning("未找到冲突矩阵分析数据")
            return {}

        conflict_data = analysis_data['conflict_analysis']
        if '1. 冲突矩阵深度分析' not in conflict_data:
            logger.warning("冲突矩阵数据格式不正确")
            return {}

        matrix_analysis = conflict_data['1. 冲突矩阵深度分析']
        domains = ['人域', '天域', '灵域', '荒域']  # 前四域
        intensity_matrix = matrix_analysis.get('强度矩阵', [])

        matrix_ids = {}

        try:
            for i, domain_a in enumerate(domains):
                for j, domain_b in enumerate(domains):
                    if i >= j:  # 只处理上三角矩阵，避免重复
                        continue

                    if i < len(intensity_matrix) and j < len(intensity_matrix[i]):
                        intensity = intensity_matrix[i][j]

                        if intensity > 0:  # 只导入有冲突的域对
                            matrix_id = uuid.uuid4()

                            # 创建冲突矩阵记录
                            await self.conn.execute("""
                                INSERT INTO cross_domain_conflict_matrix (
                                    id, novel_id, matrix_name, domain_a, domain_b, intensity,
                                    conflict_type, risk_level, status, priority,
                                    core_resources, trigger_laws, typical_scenarios, key_roles
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                            """,
                                matrix_id,
                                uuid.UUID(self.config.novel_id),
                                f"{domain_a}↔{domain_b}跨域冲突",
                                domain_a,
                                domain_b,
                                float(intensity),
                                "综合冲突",
                                min(int(intensity * 2.5), 10),  # 风险等级
                                "active",
                                min(int(intensity * 2), 10),  # 优先级
                                [],  # core_resources - 暂时为空，后续填充
                                [],  # trigger_laws
                                [],  # typical_scenarios
                                []   # key_roles
                            )

                            matrix_ids[f"{domain_a}↔{domain_b}"] = matrix_id
                            self.stats['matrices_imported'] += 1
                            logger.info(f"导入冲突矩阵: {domain_a}↔{domain_b}, 强度: {intensity}")

        except Exception as e:
            logger.error(f"导入冲突矩阵失败: {e}")
            self.stats['errors'].append(f"冲突矩阵导入失败: {e}")

        return matrix_ids

    async def import_conflict_entities(self, analysis_data: Dict[str, Any], matrix_ids: Dict[str, uuid.UUID]) -> Dict[str, uuid.UUID]:
        """导入冲突实体数据"""
        entity_ids = {}

        # 处理结构化实体数据
        for data_key in ['conflict_elements', 'enhanced_elements']:
            if data_key not in analysis_data:
                continue

            entities_data = analysis_data[data_key].get('entities', [])

            try:
                for entity in entities_data:
                    entity_id = uuid.uuid4()

                    # 确定关联的冲突矩阵
                    conflict_matrix_id = None
                    domains = entity.get('domains', [])
                    if len(domains) >= 2:
                        domain_pair = f"{domains[0]}↔{domains[1]}"
                        conflict_matrix_id = matrix_ids.get(domain_pair)

                    # 映射实体类型
                    entity_type_mapping = {
                        '推断实体': '核心资源',
                        '明确实体': '核心资源',
                        '关键角色': '关键角色',
                        '制度法条': '法条制度',
                        '技术工艺': '技术工艺',
                        '地理位置': '地理位置',
                        '文化符号': '文化符号'
                    }

                    mapped_type = entity_type_mapping.get(
                        entity.get('entity_type', ''),
                        '核心资源'
                    )

                    await self.conn.execute("""
                        INSERT INTO conflict_entities (
                            id, novel_id, conflict_matrix_id, name, entity_type, entity_subtype,
                            primary_domain, involved_domains, description, characteristics,
                            strategic_value, economic_value, symbolic_value, scarcity_level,
                            conflict_roles, dispute_intensity, confidence_score, validation_status,
                            aliases, tags, source_locations
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
                    """,
                        entity_id,
                        uuid.UUID(self.config.novel_id),
                        conflict_matrix_id,
                        entity.get('name', ''),
                        mapped_type,
                        entity.get('category', ''),
                        domains[0] if domains else None,
                        domains,
                        entity.get('description', ''),
                        json.dumps(entity.get('characteristics', {})),
                        5.0,  # 默认战略价值
                        5.0,  # 默认经济价值
                        5.0,  # 默认象征价值
                        5.0,  # 默认稀缺性
                        [],   # conflict_roles
                        5,    # 默认争议强度
                        entity.get('confidence_score', 0.8),
                        'validated' if entity.get('confidence_score', 0) > 0.7 else 'pending',
                        entity.get('aliases', []),
                        [],   # tags
                        json.dumps({'extraction_method': entity.get('extraction_method', '')})
                    )

                    entity_ids[entity.get('name', '')] = entity_id
                    self.stats['entities_imported'] += 1

            except Exception as e:
                logger.error(f"导入实体数据失败 ({data_key}): {e}")
                self.stats['errors'].append(f"实体导入失败: {e}")

        logger.info(f"成功导入 {self.stats['entities_imported']} 个冲突实体")
        return entity_ids

    async def import_conflict_relations(self, analysis_data: Dict[str, Any], entity_ids: Dict[str, uuid.UUID]):
        """导入冲突关系数据"""

        for data_key in ['conflict_elements', 'enhanced_elements']:
            if data_key not in analysis_data:
                continue

            relations_data = analysis_data[data_key].get('relationships', [])

            try:
                for relation in relations_data:
                    source_name = relation.get('source', '')
                    target_name = relation.get('target', '')

                    source_id = entity_ids.get(source_name)
                    target_id = entity_ids.get(target_name)

                    if not source_id or not target_id:
                        continue  # 跳过无法找到实体的关系

                    relation_id = uuid.uuid4()

                    # 映射关系类型
                    relation_type_mapping = {
                        'conflicts_with': '冲突',
                        'depends_on': '依赖',
                        'controls': '控制',
                        'influences': '影响',
                        'competes_with': '竞争',
                        'cooperates_with': '合作',
                        'threatens': '威胁',
                        'supports': '支持'
                    }

                    mapped_type = relation_type_mapping.get(
                        relation.get('relationship_type', ''),
                        '影响'
                    )

                    await self.conn.execute("""
                        INSERT INTO conflict_relations (
                            id, novel_id, source_entity_id, target_entity_id,
                            relation_type, relation_subtype, strength, directionality,
                            description, context, is_cross_domain, impact_level,
                            confidence_score, detection_method
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    """,
                        relation_id,
                        uuid.UUID(self.config.novel_id),
                        source_id,
                        target_id,
                        mapped_type,
                        relation.get('category', ''),
                        relation.get('strength', 0.5),
                        'bidirectional',
                        relation.get('description', ''),
                        relation.get('context', ''),
                        True,  # 默认为跨域关系
                        5,     # 默认影响等级
                        relation.get('confidence', 0.7),
                        'automated_analysis'
                    )

                    self.stats['relations_imported'] += 1

            except Exception as e:
                logger.error(f"导入关系数据失败 ({data_key}): {e}")
                self.stats['errors'].append(f"关系导入失败: {e}")

        logger.info(f"成功导入 {self.stats['relations_imported']} 个冲突关系")

    async def import_story_hooks(self, analysis_data: Dict[str, Any], matrix_ids: Dict[str, uuid.UUID]):
        """导入剧情钩子数据"""
        if 'conflict_analysis' not in analysis_data:
            return

        hooks_section = analysis_data['conflict_analysis'].get('4. 智能剧情钩子推荐', {})

        # 处理现有剧情钩子
        existing_hooks = hooks_section.get('现有剧情钩子评估', {})
        ai_generated_hooks = hooks_section.get('AI生成新钩子', {})

        try:
            # 导入现有剧情钩子
            for hook_key, hook_data in existing_hooks.items():
                if isinstance(hook_data, dict) and 'title' in hook_data:
                    hook_id = uuid.uuid4()

                    # 确定相关域和冲突矩阵
                    domains = hook_data.get('domains_involved', [])
                    conflict_matrix_id = None
                    if len(domains) >= 2:
                        domain_pair = f"{domains[0]}↔{domains[1]}"
                        conflict_matrix_id = matrix_ids.get(domain_pair)

                    await self.conn.execute("""
                        INSERT INTO conflict_story_hooks (
                            id, novel_id, conflict_matrix_id, title, description,
                            hook_type, hook_subtype, domains_involved, main_characters,
                            moral_themes, inciting_incident, originality, complexity,
                            emotional_impact, plot_integration, overall_score, priority_level,
                            is_ai_generated, tags
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
                    """,
                        hook_id,
                        uuid.UUID(self.config.novel_id),
                        conflict_matrix_id,
                        hook_data.get('title', ''),
                        hook_data.get('description', ''),
                        hook_data.get('hook_type', '综合冲突'),
                        hook_data.get('subtype', ''),
                        domains,
                        hook_data.get('characters', []),
                        hook_data.get('themes', []),
                        hook_data.get('inciting_incident', ''),
                        hook_data.get('originality', 5),
                        hook_data.get('complexity', 5),
                        hook_data.get('emotional_impact', 5),
                        hook_data.get('plot_integration', 5),
                        hook_data.get('overall_score', 5.0),
                        hook_data.get('priority', 5),
                        False,  # 不是AI生成
                        hook_data.get('tags', [])
                    )

                    self.stats['hooks_imported'] += 1

            # 导入AI生成的剧情钩子
            for hook_key, hook_data in ai_generated_hooks.items():
                if isinstance(hook_data, dict) and 'title' in hook_data:
                    hook_id = uuid.uuid4()

                    domains = hook_data.get('domains_involved', [])
                    conflict_matrix_id = None
                    if len(domains) >= 2:
                        domain_pair = f"{domains[0]}↔{domains[1]}"
                        conflict_matrix_id = matrix_ids.get(domain_pair)

                    await self.conn.execute("""
                        INSERT INTO conflict_story_hooks (
                            id, novel_id, conflict_matrix_id, title, description,
                            hook_type, hook_subtype, domains_involved, main_characters,
                            moral_themes, inciting_incident, originality, complexity,
                            emotional_impact, plot_integration, overall_score, priority_level,
                            is_ai_generated, generation_method, generation_model,
                            human_validation_status, tags
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
                    """,
                        hook_id,
                        uuid.UUID(self.config.novel_id),
                        conflict_matrix_id,
                        hook_data.get('title', ''),
                        hook_data.get('description', ''),
                        hook_data.get('hook_type', '综合冲突'),
                        hook_data.get('subtype', ''),
                        domains,
                        hook_data.get('characters', []),
                        hook_data.get('themes', []),
                        hook_data.get('inciting_incident', ''),
                        hook_data.get('originality', 5),
                        hook_data.get('complexity', 5),
                        hook_data.get('emotional_impact', 5),
                        hook_data.get('plot_integration', 5),
                        hook_data.get('overall_score', 5.0),
                        hook_data.get('priority', 5),
                        True,   # AI生成
                        'conflict_analysis_system',
                        'claude-sonnet',
                        'pending',
                        hook_data.get('tags', [])
                    )

                    self.stats['hooks_imported'] += 1

        except Exception as e:
            logger.error(f"导入剧情钩子失败: {e}")
            self.stats['errors'].append(f"剧情钩子导入失败: {e}")

        logger.info(f"成功导入 {self.stats['hooks_imported']} 个剧情钩子")

    async def import_network_analysis(self, analysis_data: Dict[str, Any], matrix_ids: Dict[str, uuid.UUID]):
        """导入网络分析结果"""
        if 'conflict_analysis' not in analysis_data:
            return

        network_section = analysis_data['conflict_analysis'].get('2. 网络拓扑分析', {})

        try:
            for analysis_key, analysis_data_item in network_section.items():
                if not isinstance(analysis_data_item, dict):
                    continue

                analysis_id = uuid.uuid4()

                # 确定分析类型
                analysis_type_mapping = {
                    '基础网络指标': '网络密度分析',
                    '度分布分析': '度分布分析',
                    '中心性分析': '中心性分析',
                    '社团检测': '社团检测',
                    '路径分析': '路径分析'
                }

                analysis_type = analysis_type_mapping.get(analysis_key, '网络密度分析')

                await self.conn.execute("""
                    INSERT INTO network_analysis_results (
                        id, novel_id, analysis_type, network_type,
                        node_count, edge_count, network_density,
                        average_clustering_coefficient, average_path_length,
                        diameter, results, analysis_confidence
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                    analysis_id,
                    uuid.UUID(self.config.novel_id),
                    analysis_type,
                    '冲突关系网络',
                    analysis_data_item.get('节点数', 100),
                    analysis_data_item.get('边数', 2296),
                    analysis_data_item.get('网络密度', 0.46),
                    analysis_data_item.get('平均聚类系数', 0.72),
                    analysis_data_item.get('平均路径长度', 2.1),
                    analysis_data_item.get('网络直径', 4),
                    json.dumps(analysis_data_item),
                    0.85
                )

                self.stats['network_analyses_imported'] += 1

        except Exception as e:
            logger.error(f"导入网络分析失败: {e}")
            self.stats['errors'].append(f"网络分析导入失败: {e}")

        logger.info(f"成功导入 {self.stats['network_analyses_imported']} 个网络分析结果")

    async def run_import(self) -> Dict[str, Any]:
        """执行完整的数据导入流程"""
        start_time = datetime.now()

        try:
            # 1. 连接数据库
            await self.connect()

            # 2. 验证项目存在
            if not await self.validate_project_exists():
                raise Exception("项目验证失败")

            # 3. 清除现有数据（如果配置允许）
            await self.clear_existing_conflict_data()

            # 4. 加载分析数据
            logger.info("开始加载分析数据...")
            analysis_data = await self.load_conflict_analysis_data()

            if not analysis_data:
                raise Exception("没有加载到任何分析数据")

            # 5. 导入冲突矩阵
            logger.info("开始导入冲突矩阵...")
            matrix_ids = await self.import_conflict_matrices(analysis_data)

            # 6. 导入冲突实体
            logger.info("开始导入冲突实体...")
            entity_ids = await self.import_conflict_entities(analysis_data, matrix_ids)

            # 7. 导入冲突关系
            logger.info("开始导入冲突关系...")
            await self.import_conflict_relations(analysis_data, entity_ids)

            # 8. 导入剧情钩子
            logger.info("开始导入剧情钩子...")
            await self.import_story_hooks(analysis_data, matrix_ids)

            # 9. 导入网络分析结果
            logger.info("开始导入网络分析结果...")
            await self.import_network_analysis(analysis_data, matrix_ids)

            # 10. 计算导入统计
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            result = {
                'success': True,
                'duration_seconds': duration,
                'statistics': self.stats,
                'summary': {
                    'total_imported': (
                        self.stats['matrices_imported'] +
                        self.stats['entities_imported'] +
                        self.stats['relations_imported'] +
                        self.stats['hooks_imported'] +
                        self.stats['network_analyses_imported']
                    ),
                    'errors_count': len(self.stats['errors'])
                }
            }

            logger.info(f"数据导入完成，耗时 {duration:.2f} 秒")
            logger.info(f"导入统计: {result['summary']}")

            return result

        except Exception as e:
            logger.error(f"数据导入失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'statistics': self.stats
            }

        finally:
            await self.disconnect()

async def main():
    """主函数"""
    config = ImportConfig()
    importer = ConflictDataImporter(config)

    result = await importer.run_import()

    if result['success']:
        print("\n✅ 数据导入成功完成!")
        print(f"📊 导入统计:")
        print(f"   - 冲突矩阵: {result['statistics']['matrices_imported']}")
        print(f"   - 冲突实体: {result['statistics']['entities_imported']}")
        print(f"   - 冲突关系: {result['statistics']['relations_imported']}")
        print(f"   - 剧情钩子: {result['statistics']['hooks_imported']}")
        print(f"   - 网络分析: {result['statistics']['network_analyses_imported']}")
        print(f"⏱️  总耗时: {result['duration_seconds']:.2f} 秒")

        if result['statistics']['errors']:
            print(f"\n⚠️  导入过程中出现 {len(result['statistics']['errors'])} 个错误:")
            for error in result['statistics']['errors']:
                print(f"   - {error}")
    else:
        print(f"\n❌ 数据导入失败: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())