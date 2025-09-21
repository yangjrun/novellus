
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证脚本
验证冲突要素数据的完整性和一致性
"""

import json
import uuid
from typing import Dict, List, Any

def validate_entities(entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """验证实体数据"""
    issues = []
    stats = {"total": len(entities), "by_type": {}}

    for entity in entities:
        # 检查必填字段
        required_fields = ["id", "name", "entity_type", "description"]
        for field in required_fields:
            if not entity.get(field):
                issues.append(f"实体 {entity.get('id', 'unknown')} 缺少必填字段: {field}")

        # 统计类型分布
        entity_type = entity.get("entity_type", "unknown")
        stats["by_type"][entity_type] = stats["by_type"].get(entity_type, 0) + 1

        # 验证ID格式
        try:
            uuid.UUID(entity.get("id", ""))
        except ValueError:
            issues.append(f"实体 {entity.get('id')} ID格式不正确")

    return {"stats": stats, "issues": issues}

def validate_relations(relations: List[Dict[str, Any]], entity_ids: set) -> Dict[str, Any]:
    """验证关系数据"""
    issues = []
    stats = {"total": len(relations), "by_type": {}}

    for relation in relations:
        # 检查实体引用
        source_id = relation.get("source_entity_id")
        target_id = relation.get("target_entity_id")

        if source_id not in entity_ids:
            issues.append(f"关系 {relation.get('id')} 引用不存在的源实体: {source_id}")
        if target_id not in entity_ids:
            issues.append(f"关系 {relation.get('id')} 引用不存在的目标实体: {target_id}")

        # 统计关系类型
        relation_type = relation.get("relation_type", "unknown")
        stats["by_type"][relation_type] = stats["by_type"].get(relation_type, 0) + 1

        # 验证强度范围
        strength = relation.get("strength", 0)
        if not (0 <= strength <= 1):
            issues.append(f"关系 {relation.get('id')} 强度值超出范围[0,1]: {strength}")

    return {"stats": stats, "issues": issues}

def main():
    """主验证函数"""
    print("开始数据验证...")

    # 这里应该加载实际的数据文件
    # 示例代码省略具体加载逻辑

    print("数据验证完成")

if __name__ == "__main__":
    main()
