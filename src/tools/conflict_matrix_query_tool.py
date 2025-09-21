"""
跨域冲突矩阵查询和分析工具
提供数据查询、统计分析和可视化功能
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime


class ConflictMatrixQueryTool:
    """冲突矩阵查询工具"""

    def __init__(self, report_file: str):
        """初始化查询工具"""
        self.report_data = self._load_report(report_file)
        self.domains = ["人域", "天域", "灵域", "荒域"]

    def _load_report(self, file_path: str) -> Dict[str, Any]:
        """加载分析报告"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"无法加载报告文件: {e}")

    def get_conflict_matrix_summary(self) -> Dict[str, Any]:
        """获取冲突矩阵概要"""
        matrix_analysis = self.report_data.get('1. 冲突矩阵深度分析', {})
        basic_stats = matrix_analysis.get('基础统计', {})

        return {
            "总体概况": {
                "分析时间": self.report_data.get('报告元数据', {}).get('生成时间', ''),
                "分析范围": self.report_data.get('报告元数据', {}).get('分析范围', ''),
                "总冲突对数": basic_stats.get('总冲突对数', 0),
                "平均冲突强度": round(basic_stats.get('平均冲突强度', 0), 2),
                "最高冲突强度": basic_stats.get('最高冲突强度', 0)
            },
            "强度分布": basic_stats.get('冲突强度分布', {}),
            "高风险冲突对": basic_stats.get('高风险冲突对', []),
            "网络特征": matrix_analysis.get('网络特征', {}),
            "冲突模式": matrix_analysis.get('冲突模式', [])
        }

    def get_domain_analysis(self, domain: str = None) -> Dict[str, Any]:
        """获取域分析结果"""
        domain_analysis = self.report_data.get('1. 冲突矩阵深度分析', {}).get('域分析', {})

        if domain:
            if domain not in domain_analysis:
                return {"error": f"域 '{domain}' 不存在"}
            return {domain: domain_analysis[domain]}

        # 返回所有域的分析
        result = {}
        for d in self.domains:
            if d in domain_analysis:
                result[d] = domain_analysis[d]

        return result

    def get_conflict_pair_details(self, domain_a: str, domain_b: str) -> Dict[str, Any]:
        """获取特定冲突对的详细信息"""
        db_data = self.report_data.get('5. 数据库模型', {})
        matrices = db_data.get('conflict_matrices', [])

        # 查找匹配的冲突对
        for matrix in matrices:
            if ((matrix['domain_a'] == domain_a and matrix['domain_b'] == domain_b) or
                (matrix['domain_a'] == domain_b and matrix['domain_b'] == domain_a)):

                return {
                    "冲突对": f"{matrix['domain_a']} ↔ {matrix['domain_b']}",
                    "冲突强度": matrix['intensity'],
                    "核心资源": matrix['core_resources'],
                    "触发法条": matrix['trigger_laws'],
                    "典型场景": matrix['typical_scenarios'],
                    "关键角色": matrix['key_roles']
                }

        return {"error": f"未找到 {domain_a} 与 {domain_b} 的冲突数据"}

    def get_escalation_analysis(self, domain_a: str = None, domain_b: str = None) -> Dict[str, Any]:
        """获取冲突升级分析"""
        escalation_data = self.report_data.get('3. 冲突升级路径分析', {})

        if domain_a and domain_b:
            # 查找特定冲突对的升级路径
            conflict_key = f"{domain_a}↔{domain_b}"
            reverse_key = f"{domain_b}↔{domain_a}"

            path_models = escalation_data.get('路径模型', {})
            path_data = path_models.get(conflict_key) or path_models.get(reverse_key)

            if path_data:
                return {
                    "冲突对": conflict_key if conflict_key in path_models else reverse_key,
                    "路径详情": path_data
                }
            else:
                return {"error": f"未找到 {domain_a} 与 {domain_b} 的升级路径"}

        # 返回所有升级分析
        return {
            "路径模型": escalation_data.get('路径模型', {}),
            "关键转折点": escalation_data.get('关键转折点', []),
            "升级概率分析": escalation_data.get('升级概率分析', {})
        }

    def get_story_hooks(self, domain: str = None, hook_type: str = None) -> List[Dict[str, Any]]:
        """获取故事钩子数据"""
        db_data = self.report_data.get('5. 数据库模型', {})
        hooks = db_data.get('story_hooks', [])

        filtered_hooks = []
        for hook in hooks:
            # 域过滤
            if domain and domain not in hook.get('domains_involved', []):
                continue

            # 类型过滤
            if hook_type and hook.get('hook_type', '') != hook_type:
                continue

            filtered_hooks.append({
                "标题": hook['title'],
                "描述": hook['description'],
                "类型": hook['hook_type'],
                "涉及域": hook['domains_involved'],
                "复杂度": hook['complexity'],
                "戏剧价值": hook['drama_value']
            })

        return filtered_hooks

    def get_entity_analysis(self, entity_type: str = None, domain: str = None) -> Dict[str, Any]:
        """获取实体分析"""
        entity_data = self.report_data.get('2. 实体关系网络分析', {})
        db_data = self.report_data.get('5. 数据库模型', {})
        entities = db_data.get('conflict_entities', [])

        # 过滤实体
        filtered_entities = []
        for entity in entities:
            if entity_type and entity.get('entity_type', '') != entity_type:
                continue

            if domain and domain not in entity.get('domains', []):
                continue

            filtered_entities.append({
                "名称": entity['name'],
                "类型": entity['entity_type'],
                "域": entity['domains'],
                "重要性": entity['importance'],
                "描述": entity['description']
            })

        # 统计信息
        stats = entity_data.get('实体统计', {})
        type_distribution = entity_data.get('实体类型分布', {})

        return {
            "实体列表": filtered_entities,
            "统计信息": {
                "筛选结果数量": len(filtered_entities),
                "总体统计": stats,
                "类型分布": type_distribution
            }
        }

    def get_conflict_intensity_ranking(self) -> List[Dict[str, Any]]:
        """获取冲突强度排名"""
        db_data = self.report_data.get('5. 数据库模型', {})
        matrices = db_data.get('conflict_matrices', [])

        # 按强度排序
        sorted_conflicts = sorted(matrices, key=lambda x: x['intensity'], reverse=True)

        ranking = []
        for i, conflict in enumerate(sorted_conflicts, 1):
            ranking.append({
                "排名": i,
                "冲突对": f"{conflict['domain_a']} ↔ {conflict['domain_b']}",
                "强度": conflict['intensity'],
                "风险等级": self._classify_risk_level(conflict['intensity']),
                "核心争议": conflict['core_resources'][:2]  # 显示前2个核心资源
            })

        return ranking

    def _classify_risk_level(self, intensity: int) -> str:
        """分类风险等级"""
        if intensity >= 4:
            return "极高风险"
        elif intensity >= 3:
            return "高风险"
        elif intensity >= 2:
            return "中等风险"
        else:
            return "低风险"

    def get_story_potential_ranking(self) -> List[Dict[str, Any]]:
        """获取故事潜力排名"""
        story_analysis = self.report_data.get('4. 故事情节潜力评估', {})
        hooks_analysis = story_analysis.get('剧情钩子分析', {})

        potential_ranking = []
        for conflict_key, analysis in hooks_analysis.items():
            potential_ranking.append({
                "冲突域": conflict_key,
                "钩子数量": analysis.get('钩子数量', 0),
                "平均复杂度": round(analysis.get('平均复杂度', 0), 2),
                "平均戏剧价值": round(analysis.get('平均戏剧价值', 0), 2),
                "故事潜力": round((analysis.get('平均复杂度', 0) + analysis.get('平均戏剧价值', 0)) / 2, 2)
            })

        # 按故事潜力排序
        potential_ranking.sort(key=lambda x: x['故事潜力'], reverse=True)

        return potential_ranking

    def search_content(self, keyword: str) -> Dict[str, List[Dict[str, Any]]]:
        """搜索内容"""
        results = {
            "冲突场景": [],
            "故事钩子": [],
            "实体": [],
            "法条": []
        }

        db_data = self.report_data.get('5. 数据库模型', {})

        # 搜索冲突矩阵中的场景
        matrices = db_data.get('conflict_matrices', [])
        for matrix in matrices:
            for scenario in matrix.get('typical_scenarios', []):
                if keyword.lower() in scenario.lower():
                    results["冲突场景"].append({
                        "冲突域": f"{matrix['domain_a']} ↔ {matrix['domain_b']}",
                        "场景": scenario,
                        "相关角色": matrix.get('key_roles', [])
                    })

        # 搜索故事钩子
        hooks = db_data.get('story_hooks', [])
        for hook in hooks:
            if (keyword.lower() in hook['title'].lower() or
                keyword.lower() in hook['description'].lower()):
                results["故事钩子"].append({
                    "标题": hook['title'],
                    "描述": hook['description'],
                    "类型": hook['hook_type']
                })

        # 搜索实体
        entities = db_data.get('conflict_entities', [])
        for entity in entities:
            if keyword.lower() in entity['name'].lower():
                results["实体"].append({
                    "名称": entity['name'],
                    "类型": entity['entity_type'],
                    "域": entity['domains']
                })

        # 搜索法条
        for matrix in matrices:
            for law in matrix.get('trigger_laws', []):
                if keyword.lower() in law.lower():
                    results["法条"].append({
                        "法条": law,
                        "适用域": f"{matrix['domain_a']} ↔ {matrix['domain_b']}"
                    })

        return results

    def generate_conflict_report(self, domain_a: str, domain_b: str) -> Dict[str, Any]:
        """生成特定冲突对的详细报告"""
        # 基础信息
        conflict_details = self.get_conflict_pair_details(domain_a, domain_b)
        if "error" in conflict_details:
            return conflict_details

        # 升级路径
        escalation_info = self.get_escalation_analysis(domain_a, domain_b)

        # 相关故事钩子
        all_hooks = self.get_story_hooks()
        related_hooks = [
            hook for hook in all_hooks
            if domain_a in hook['涉及域'] and domain_b in hook['涉及域']
        ]

        # 相关实体
        entity_analysis = self.get_entity_analysis()
        related_entities = [
            entity for entity in entity_analysis['实体列表']
            if domain_a in entity['域'] or domain_b in entity['域']
        ]

        return {
            "冲突基础信息": conflict_details,
            "升级路径分析": escalation_info,
            "相关故事钩子": related_hooks,
            "涉及实体": related_entities[:10],  # 限制数量
            "分析建议": self._generate_conflict_recommendations(domain_a, domain_b, conflict_details)
        }

    def _generate_conflict_recommendations(self, domain_a: str, domain_b: str,
                                         conflict_details: Dict[str, Any]) -> List[str]:
        """生成冲突分析建议"""
        recommendations = []

        intensity = conflict_details.get('冲突强度', 0)

        if intensity >= 4:
            recommendations.append("高强度冲突，建议重点关注冲突升级的预防机制")
            recommendations.append("可以设计涉及高层政治博弈的复杂情节")

        if intensity >= 3:
            recommendations.append("具有较强的故事张力，适合作为主要情节线")

        # 基于资源类型的建议
        resources = conflict_details.get('核心资源', [])
        if any('税' in r or '征' in r for r in resources):
            recommendations.append("涉及税收征收，可以探讨权力与民生的主题")

        if any('器械' in r or '技术' in r for r in resources):
            recommendations.append("涉及技术争议，可以加入科技发展与传统的冲突")

        if any('走私' in r or '贸易' in r for r in resources):
            recommendations.append("涉及贸易争端，适合设计冒险和悬疑情节")

        return recommendations

    def export_summary_report(self, output_file: str = None) -> str:
        """导出概要报告"""
        if not output_file:
            output_file = f"conflict_matrix_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("裂世九域跨域冲突矩阵分析概要报告\n")
            f.write("=" * 50 + "\n\n")

            # 总体概况
            summary = self.get_conflict_matrix_summary()
            f.write("1. 总体概况\n")
            f.write("-" * 20 + "\n")
            for key, value in summary['总体概况'].items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

            # 冲突强度排名
            f.write("2. 冲突强度排名\n")
            f.write("-" * 20 + "\n")
            ranking = self.get_conflict_intensity_ranking()
            for rank in ranking:
                f.write(f"{rank['排名']}. {rank['冲突对']} - 强度: {rank['强度']} ({rank['风险等级']})\n")
            f.write("\n")

            # 故事潜力排名
            f.write("3. 故事潜力排名\n")
            f.write("-" * 20 + "\n")
            story_ranking = self.get_story_potential_ranking()
            for item in story_ranking:
                f.write(f"{item['冲突域']} - 潜力: {item['故事潜力']}/10\n")
            f.write("\n")

            # 域分析
            f.write("4. 各域特征分析\n")
            f.write("-" * 20 + "\n")
            domain_analysis = self.get_domain_analysis()
            for domain, analysis in domain_analysis.items():
                f.write(f"{domain}: {analysis['冲突倾向']}, ")
                f.write(f"参与冲突 {analysis['参与冲突数']} 个, ")
                f.write(f"平均强度 {analysis['平均冲突强度']:.2f}\n")

        return output_file


def interactive_query():
    """交互式查询界面"""
    print("跨域冲突矩阵查询工具")
    print("=" * 30)

    # 初始化工具
    try:
        tool = ConflictMatrixQueryTool("D:/work/novellus/cross_domain_conflict_analysis_report.json")
        print("[OK] 数据加载成功")
    except Exception as e:
        print(f"[ERROR] 数据加载失败: {e}")
        return

    domains = ["人域", "天域", "灵域", "荒域"]

    while True:
        print("\n查询选项:")
        print("1. 冲突矩阵概要")
        print("2. 域分析")
        print("3. 冲突对详情")
        print("4. 升级路径分析")
        print("5. 故事钩子查询")
        print("6. 实体查询")
        print("7. 冲突强度排名")
        print("8. 内容搜索")
        print("9. 生成冲突报告")
        print("10. 导出概要报告")
        print("0. 退出")

        choice = input("\n请选择操作 (0-10): ").strip()

        try:
            if choice == "0":
                print("退出查询工具")
                break

            elif choice == "1":
                summary = tool.get_conflict_matrix_summary()
                print("\n冲突矩阵概要:")
                print(json.dumps(summary, ensure_ascii=False, indent=2))

            elif choice == "2":
                print(f"\n可选域: {', '.join(domains)}")
                domain = input("输入域名 (留空查看所有): ").strip()
                result = tool.get_domain_analysis(domain if domain else None)
                print(json.dumps(result, ensure_ascii=False, indent=2))

            elif choice == "3":
                print(f"\n可选域: {', '.join(domains)}")
                domain_a = input("输入第一个域: ").strip()
                domain_b = input("输入第二个域: ").strip()
                if domain_a and domain_b:
                    result = tool.get_conflict_pair_details(domain_a, domain_b)
                    print(json.dumps(result, ensure_ascii=False, indent=2))

            elif choice == "4":
                print(f"\n可选域: {', '.join(domains)}")
                domain_a = input("输入第一个域 (留空查看所有): ").strip()
                domain_b = input("输入第二个域 (留空查看所有): ").strip()
                result = tool.get_escalation_analysis(
                    domain_a if domain_a else None,
                    domain_b if domain_b else None
                )
                print(json.dumps(result, ensure_ascii=False, indent=2))

            elif choice == "5":
                domain = input("输入域名过滤 (留空查看所有): ").strip()
                hook_type = input("输入钩子类型过滤 (留空查看所有): ").strip()
                hooks = tool.get_story_hooks(
                    domain if domain else None,
                    hook_type if hook_type else None
                )
                print(f"\n找到 {len(hooks)} 个故事钩子:")
                for hook in hooks[:5]:  # 显示前5个
                    print(json.dumps(hook, ensure_ascii=False, indent=2))

            elif choice == "6":
                entity_type = input("输入实体类型过滤 (留空查看所有): ").strip()
                domain = input("输入域名过滤 (留空查看所有): ").strip()
                result = tool.get_entity_analysis(
                    entity_type if entity_type else None,
                    domain if domain else None
                )
                print(json.dumps(result, ensure_ascii=False, indent=2))

            elif choice == "7":
                ranking = tool.get_conflict_intensity_ranking()
                print("\n冲突强度排名:")
                for rank in ranking:
                    print(f"{rank['排名']}. {rank['冲突对']} - 强度: {rank['强度']} ({rank['风险等级']})")

            elif choice == "8":
                keyword = input("输入搜索关键词: ").strip()
                if keyword:
                    results = tool.search_content(keyword)
                    print(f"\n搜索结果 (关键词: {keyword}):")
                    for category, items in results.items():
                        if items:
                            print(f"\n{category} ({len(items)} 个结果):")
                            for item in items[:3]:  # 显示前3个结果
                                print(f"  - {item}")

            elif choice == "9":
                print(f"\n可选域: {', '.join(domains)}")
                domain_a = input("输入第一个域: ").strip()
                domain_b = input("输入第二个域: ").strip()
                if domain_a and domain_b:
                    report = tool.generate_conflict_report(domain_a, domain_b)
                    print(json.dumps(report, ensure_ascii=False, indent=2))

            elif choice == "10":
                output_file = tool.export_summary_report()
                print(f"[OK] 概要报告已导出到: {output_file}")

            else:
                print("无效选择，请重新输入")

        except Exception as e:
            print(f"[ERROR] 操作失败: {e}")


if __name__ == "__main__":
    interactive_query()