
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本
将冲突要素数据迁移到目标数据库
"""

import json
import psycopg2
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConflictDataMigrator:
    """冲突数据迁移器"""

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None

    def connect(self):
        """连接数据库"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def migrate_entities(self, entities: List[Dict[str, Any]]) -> int:
        """迁移实体数据"""
        if not self.connection:
            raise Exception("数据库未连接")

        cursor = self.connection.cursor()
        success_count = 0

        for entity in entities:
            try:
                cursor.execute("""
                    INSERT INTO cultural_entities (
                        id, novel_id, name, entity_type, domain_type,
                        description, confidence_score, extraction_method,
                        validation_status, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    entity["id"],
                    "novel-placeholder-id",  # 需要替换为实际的novel_id
                    entity["name"],
                    entity["entity_type"],
                    entity["domains"][0] if entity["domains"] else None,
                    entity["description"],
                    entity["confidence_score"],
                    entity["extraction_method"],
                    "pending",
                    entity["created_at"],
                    entity["created_at"]
                ))
                success_count += 1

            except Exception as e:
                logger.error(f"插入实体失败 {entity['id']}: {e}")

        self.connection.commit()
        cursor.close()
        logger.info(f"成功迁移 {success_count} 个实体")
        return success_count

    def migrate_relations(self, relations: List[Dict[str, Any]]) -> int:
        """迁移关系数据"""
        if not self.connection:
            raise Exception("数据库未连接")

        cursor = self.connection.cursor()
        success_count = 0

        for relation in relations:
            try:
                cursor.execute("""
                    INSERT INTO cultural_relations (
                        id, novel_id, source_entity_id, target_entity_id,
                        relation_type, description, strength, context,
                        is_cross_domain, confidence_score, detection_method,
                        bidirectional, temporal_context, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (id) DO UPDATE SET
                        description = EXCLUDED.description,
                        strength = EXCLUDED.strength,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    relation["id"],
                    "novel-placeholder-id",
                    relation["source_entity_id"],
                    relation["target_entity_id"],
                    relation["relation_type"],
                    relation["description"],
                    relation["strength"],
                    relation["context"],
                    relation["is_cross_domain"],
                    relation["confidence_score"],
                    relation["detection_method"],
                    relation["bidirectional"],
                    relation["temporal_context"],
                    relation["created_at"],
                    relation["created_at"]
                ))
                success_count += 1

            except Exception as e:
                logger.error(f"插入关系失败 {relation['id']}: {e}")

        self.connection.commit()
        cursor.close()
        logger.info(f"成功迁移 {success_count} 个关系")
        return success_count

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")

def main():
    """主迁移函数"""
    # 数据库配置
    db_config = {
        "host": "localhost",
        "database": "novellus",
        "user": "your_username",
        "password": "your_password",
        "port": "5432"
    }

    # 创建迁移器
    migrator = ConflictDataMigrator(db_config)

    try:
        migrator.connect()

        # 加载数据文件
        with open("conflict_elements_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # 执行迁移
        migrator.migrate_entities(data["entities"])
        migrator.migrate_relations(data["relations"])

        logger.info("数据迁移完成")

    except Exception as e:
        logger.error(f"迁移失败: {e}")
    finally:
        migrator.close()

if __name__ == "__main__":
    main()
