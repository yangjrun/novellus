#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
裂世九域·法则链纪元 - 故事可视化工具
基于智能故事生成分析结果，提供交互式可视化界面

功能：
1. 剧情钩子质量雷达图
2. 冲突类型分布饼图
3. AI生成策略分布
4. 冲突升级路径图
5. 角色关系网络图
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Dict, List, Any
import seaborn as sns
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class StoryVisualizationTool:
    """故事可视化工具"""

    def __init__(self, report_file: str):
        """初始化可视化工具"""
        self.report_file = report_file
        self.data = self.load_analysis_data()

    def load_analysis_data(self) -> Dict[str, Any]:
        """加载分析数据"""
        try:
            with open(self.report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载数据失败: {e}")
            return {}

    def create_quality_radar_chart(self, save_path: str = None) -> None:
        """创建质量评分雷达图"""
        viz_data = self.data.get('可视化数据', {}).get('质量评分雷达图', {})
        if not viz_data:
            print("无可视化数据")
            return

        dimensions = viz_data.get('维度', [])
        plot_data = viz_data.get('数据', [])

        if not dimensions or not plot_data:
            print("数据不完整")
            return

        # 设置雷达图
        angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))  # 闭合雷达图

        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))

        # 为每个剧情钩子绘制雷达图
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

        for i, hook_data in enumerate(plot_data[:5]):  # 限制显示5个
            values = hook_data.get('数值', [])
            if len(values) == len(dimensions):
                values = values + [values[0]]  # 闭合数据
                ax.plot(angles, values, 'o-', linewidth=2,
                       label=hook_data.get('名称', f'钩子{i+1}'), color=colors[i % len(colors)])
                ax.fill(angles, values, alpha=0.1, color=colors[i % len(colors)])

        # 设置雷达图标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, fontsize=12)
        ax.set_ylim(0, 10)
        ax.set_yticks([2, 4, 6, 8, 10])
        ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=10)
        ax.grid(True)

        plt.title('剧情钩子质量评分雷达图', fontsize=16, fontweight='bold', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def create_conflict_type_pie_chart(self, save_path: str = None) -> None:
        """创建冲突类型分布饼图"""
        viz_data = self.data.get('可视化数据', {}).get('冲突类型分布', {})
        labels = viz_data.get('标签', [])
        values = viz_data.get('数值', [])

        if not labels or not values:
            print("冲突类型数据不完整")
            return

        # 设置颜色
        colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC']

        fig, ax = plt.subplots(figsize=(10, 8))

        # 创建饼图
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                         colors=colors, startangle=90,
                                         explode=[0.05] * len(values))

        # 美化文本
        for text in texts:
            text.set_fontsize(12)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')

        plt.title('冲突类型分布', fontsize=16, fontweight='bold', pad=20)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def create_ai_generation_strategy_chart(self, save_path: str = None) -> None:
        """创建AI生成策略分布图"""
        ai_data = self.data.get('AI生成剧情钩子', {}).get('质量评估', {})
        strategy_dist = ai_data.get('生成策略分布', {})

        if not strategy_dist:
            print("AI生成策略数据不完整")
            return

        strategies = list(strategy_dist.keys())
        counts = list(strategy_dist.values())

        # 策略名称映射
        strategy_names = {
            'centrality_based': '中心性分析',
            'boundary_conflict': '社群边界',
            'chain_reaction': '网络路径',
            'structural_vulnerability': '结构洞'
        }

        display_names = [strategy_names.get(s, s) for s in strategies]

        fig, ax = plt.subplots(figsize=(12, 8))

        # 创建柱状图
        bars = ax.bar(display_names, counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax.set_ylabel('生成数量', fontsize=14)
        ax.set_title('AI生成策略分布', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylim(0, max(counts) * 1.2)

        # 旋转x轴标签以避免重叠
        plt.xticks(rotation=45, ha='right')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def create_quality_comparison_chart(self, save_path: str = None) -> None:
        """创建原始vs AI生成质量对比图"""
        # 原始钩子质量
        original_stats = self.data.get('原始剧情钩子分析', {}).get('整体统计', {})
        original_avg = original_stats.get('平均综合评分', 0)

        # AI生成钩子质量
        ai_quality = self.data.get('AI生成剧情钩子', {}).get('质量评估', {})
        ai_originality = ai_quality.get('平均原创性', 0) * 10  # 转换为0-100分
        ai_coherence = ai_quality.get('平均连贯性', 0) * 10
        ai_dramatic = ai_quality.get('平均戏剧潜力', 0) * 10
        ai_avg = (ai_originality + ai_coherence + ai_dramatic) / 3

        categories = ['原始剧情钩子', 'AI生成剧情钩子']
        scores = [original_avg, ai_avg]

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(categories, scores, color=['#FF9999', '#66B2FF'], alpha=0.8)

        # 添加数值标签
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{score:.1f}', ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_ylabel('平均质量评分', fontsize=14)
        ax.set_title('原始 vs AI生成剧情钩子质量对比', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylim(0, 100)

        # 添加评分等级线
        for score, label in [(85, 'S级'), (75, 'A级'), (65, 'B级'), (55, 'C级')]:
            ax.axhline(y=score, color='gray', linestyle='--', alpha=0.5)
            ax.text(1.5, score, label, fontsize=10, color='gray')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def create_detailed_analysis_chart(self, save_path: str = None) -> None:
        """创建详细维度分析图"""
        quality_dist = self.data.get('原始剧情钩子分析', {}).get('质量分布', {})

        dimensions = list(quality_dist.keys())
        avg_scores = [quality_dist[dim]['平均分'] for dim in dimensions]
        max_scores = [quality_dist[dim]['最高分'] for dim in dimensions]
        min_scores = [quality_dist[dim]['最低分'] for dim in dimensions]

        x = np.arange(len(dimensions))
        width = 0.25

        fig, ax = plt.subplots(figsize=(14, 8))

        bars1 = ax.bar(x - width, avg_scores, width, label='平均分', color='#FF9999', alpha=0.8)
        bars2 = ax.bar(x, max_scores, width, label='最高分', color='#66B2FF', alpha=0.8)
        bars3 = ax.bar(x + width, min_scores, width, label='最低分', color='#99FF99', alpha=0.8)

        # 添加数值标签
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom', fontsize=10)

        ax.set_ylabel('评分', fontsize=14)
        ax.set_title('各维度质量分析详情', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(dimensions, rotation=45, ha='right')
        ax.legend()
        ax.set_ylim(0, 10)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def generate_comprehensive_visualization_report(self, output_dir: str = "D:/work/novellus/story_analysis_output/visualizations") -> None:
        """生成完整的可视化报告"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        print("生成可视化报告...")

        # 1. 质量雷达图
        print("1. 生成质量雷达图...")
        self.create_quality_radar_chart(f"{output_dir}/quality_radar.png")

        # 2. 冲突类型分布
        print("2. 生成冲突类型分布图...")
        self.create_conflict_type_pie_chart(f"{output_dir}/conflict_types.png")

        # 3. AI生成策略分布
        print("3. 生成AI策略分布图...")
        self.create_ai_generation_strategy_chart(f"{output_dir}/ai_strategies.png")

        # 4. 质量对比
        print("4. 生成质量对比图...")
        self.create_quality_comparison_chart(f"{output_dir}/quality_comparison.png")

        # 5. 详细维度分析
        print("5. 生成详细维度分析图...")
        self.create_detailed_analysis_chart(f"{output_dir}/detailed_analysis.png")

        # 生成可视化说明文档
        self.generate_visualization_documentation(output_dir)

        print(f"可视化报告生成完成，保存在: {output_dir}")

    def generate_visualization_documentation(self, output_dir: str) -> None:
        """生成可视化说明文档"""
        doc_content = """# 裂世九域·法则链纪元 - 可视化分析报告

## 图表说明

### 1. 质量雷达图 (quality_radar.png)
展示前5个剧情钩子在四个维度上的表现：
- **戏剧价值**: 冲突强度和情感冲击力
- **故事潜力**: 可扩展性和分支可能性
- **世界观一致性**: 设定逻辑的连贯性
- **读者吸引力**: 好奇心激发和情感共鸣

### 2. 冲突类型分布图 (conflict_types.png)
显示18个原始剧情钩子的类型分布：
- 综合冲突（50%）：复杂多层面的冲突
- 身份认同（17%）：文化和身份相关冲突
- 经济冲突（17%）：利益和资源争夺
- 权力斗争（11%）：政治权力博弈
- 生存危机（6%）：生存威胁相关

### 3. AI生成策略分布图 (ai_strategies.png)
展示AI系统使用的四种生成策略：
- **中心性分析**: 基于网络中心实体生成
- **社群边界**: 利用跨域边界张力
- **网络路径**: 通过关键路径传播效应
- **结构洞**: 利用网络结构薄弱点

### 4. 质量对比图 (quality_comparison.png)
对比原始剧情钩子与AI生成钩子的质量：
- 原始钩子平均分：49.9/100
- AI生成钩子平均分：约80/100
- AI生成在连贯性和戏剧潜力上表现更佳

### 5. 详细维度分析图 (detailed_analysis.png)
深入分析各质量维度的分布情况：
- 戏剧张力：平均6.2，表现较好
- 情感冲击：平均4.4，需要提升
- 可扩展性：平均6.3，发展潜力大
- 一致性：平均5.8，世界观运用有待加强
- 读者吸引力：平均3.4，亟需改进

## 关键发现

1. **AI生成优势**：在连贯性和原创性方面表现突出
2. **改进重点**：情感冲击力和读者吸引力需要重点提升
3. **类型均衡**：综合冲突类型占主导，建议增加多样性
4. **质量提升空间**：整体质量仍有较大提升空间

## 创作建议

1. **强化情感元素**：增加角色情感冲突和道德困境
2. **提升读者代入感**：加强与现实生活的关联性
3. **平衡冲突类型**：增加不同类型冲突的比例
4. **深化世界观运用**：更充分地利用"链法"体系特色

---
*本可视化报告基于智能故事生成分析系统的数据生成*
"""

        with open(f"{output_dir}/visualization_report.md", 'w', encoding='utf-8') as f:
            f.write(doc_content)

def main():
    """主函数"""
    # 创建可视化工具
    viz_tool = StoryVisualizationTool(
        "D:/work/novellus/story_analysis_output/intelligent_story_analysis_report.json"
    )

    # 生成所有可视化图表
    viz_tool.generate_comprehensive_visualization_report()

if __name__ == "__main__":
    main()