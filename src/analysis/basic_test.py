# -*- coding: utf-8 -*-

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cultural_framework_analyzer import CulturalFrameworkAnalyzer, DomainType

def test_import():
    """Test if we can import the analyzer"""
    try:
        analyzer = CulturalFrameworkAnalyzer()
        print("SUCCESS: Imported CulturalFrameworkAnalyzer")
        print("   - Entity patterns loaded: {}".format(len(analyzer.entity_patterns)))
        print("   - Chain concepts loaded: {}".format(len(analyzer.chain_concepts)))
        return True
    except Exception as e:
        print("ERROR: Import failed: {}".format(e))
        return False

async def test_simple_analysis():
    """Test basic analysis with minimal text"""
    try:
        analyzer = CulturalFrameworkAnalyzer()

        # Simple test text in Chinese
        test_text = u"""
人域
A. 神话与宗教
天命信仰主导，法则链体系。

B. 权力与法律
天命王朝统治，环印身份象征。

情节钩子：
- 测试钩子1
- 测试钩子2
"""

        result = await analyzer.analyze_full_text(test_text)

        print("SUCCESS: Basic analysis completed")
        print("   - Total domains: {}".format(result['analysis_metadata']['total_domains']))
        print("   - Total entities: {}".format(result['analysis_metadata']['total_entities']))

        return True
    except Exception as e:
        print("ERROR: Analysis failed: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Testing Cultural Framework Analyzer")
    print("=" * 40)

    # Test import
    if not test_import():
        return

    # Test analysis
    result = asyncio.run(test_simple_analysis())

    if result:
        print("\nAll tests passed!")
    else:
        print("\nTests failed!")

if __name__ == "__main__":
    main()