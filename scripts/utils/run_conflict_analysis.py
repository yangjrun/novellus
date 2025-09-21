#!/usr/bin/env python3
"""
跨域冲突网络分析系统运行脚本
快速运行完整的分析流程
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.analysis.main_conflict_analyzer import ConflictAnalysisSystem

def main():
    """主函数"""
    print("="*60)
    print("跨域冲突网络分析系统")
    print("="*60)

    # 创建分析系统
    system = ConflictAnalysisSystem()

    # 数据文件路径
    data_path = project_root / "enhanced_conflict_output" / "enhanced_conflict_elements_data.json"

    if not data_path.exists():
        print(f"错误: 数据文件不存在 {data_path}")
        print("请确保已运行数据提取和结构化流程")
        return 1

    print(f"数据文件: {data_path}")
    print("开始分析...")

    # 运行完整分析
    results = system.run_complete_analysis(
        data_source=str(data_path),
        report_title="裂世九域·法则链纪元 - 跨域冲突网络分析报告"
    )

    if results["success"]:
        print("\n分析成功完成！")
        print(f"报告ID: {results['report_id']}")

        # 显示分析摘要
        system.print_analysis_summary()

        # 输出文件位置
        output_dir = Path("/d/work/novellus/output")
        print(f"\n输出文件:")
        report_id = results['report_id']
        print(f"  HTML报告: {output_dir / f'{report_id}.html'}")
        print(f"  JSON数据: {output_dir / f'{report_id}.json'}")
        print(f"  可视化: {output_dir / 'visualizations'}")

        return 0
    else:
        print(f"\n分析失败: {results['error_message']}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)