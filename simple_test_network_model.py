"""
Simple test script for the comprehensive conflict network model
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'analysis'))

import json
import traceback
from pathlib import Path
import time

# Import analysis modules
from comprehensive_conflict_network_model import ComprehensiveConflictNetworkModel

def simple_test():
    """Simple test of the comprehensive network model"""
    print("=" * 60)
    print("COMPREHENSIVE NETWORK MODEL TEST")
    print("=" * 60)

    start_time = time.time()

    try:
        # 1. Initialize model
        print("\n1. Initializing model...")
        model = ComprehensiveConflictNetworkModel()
        print("   SUCCESS: Model initialized")

        # 2. Load data
        print("\n2. Loading data...")
        data_path = "D:/work/novellus/enhanced_conflict_output/enhanced_conflict_elements_data.json"

        if not Path(data_path).exists():
            print(f"   ERROR: Data file not found: {data_path}")
            return False

        model.load_data(data_path)
        print(f"   SUCCESS: Data loaded - {len(model.entities_df)} entities, {len(model.relations_df)} relations")

        # 3. Build network
        print("\n3. Building network...")
        main_network = model.build_main_network()
        print(f"   SUCCESS: Network built - {main_network.number_of_nodes()} nodes, {main_network.number_of_edges()} edges")

        # 4. Topology analysis
        print("\n4. Topology analysis...")
        topology_metrics = model.analyze_network_topology()
        print(f"   SUCCESS: Topology analysis completed")
        print(f"      - Density: {topology_metrics.density:.4f}")
        print(f"      - Clustering: {topology_metrics.global_clustering:.4f}")
        print(f"      - Components: {topology_metrics.num_components}")

        # 5. Intensity modeling
        print("\n5. Intensity modeling...")
        intensity_model = model.build_conflict_intensity_model()
        print(f"   SUCCESS: Intensity model built")
        print(f"      - Average intensity: {intensity_model.intensity_distribution['mean']:.3f}")

        # 6. Community detection
        print("\n6. Community detection...")
        community_structure = model.discover_communities()
        print(f"   SUCCESS: Community detection completed")
        print(f"      - Communities: {community_structure.num_communities}")
        print(f"      - Modularity: {community_structure.louvain_modularity:.3f}")

        # 7. Centrality analysis
        print("\n7. Centrality analysis...")
        centrality_analysis = model.analyze_centrality()
        print(f"   SUCCESS: Centrality analysis completed")

        # 8. Propagation modeling
        print("\n8. Propagation modeling...")
        propagation_model = model.model_conflict_propagation()
        print(f"   SUCCESS: Propagation model built")
        print(f"      - Transmission rate: {propagation_model.transmission_rate:.3f}")

        # 9. Robustness analysis
        print("\n9. Robustness analysis...")
        robustness_analysis = model.analyze_network_robustness()
        print(f"   SUCCESS: Robustness analysis completed")
        print(f"      - Risk score: {robustness_analysis.systemic_risk_score:.3f}")

        # 10. Comprehensive analysis
        print("\n10. Running comprehensive analysis...")
        results = model.run_comprehensive_analysis()
        print(f"   SUCCESS: Comprehensive analysis completed")

        # Performance
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\n11. Performance: {total_time:.2f} seconds")

        # Summary
        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Network: {main_network.number_of_nodes()} nodes, {main_network.number_of_edges()} edges")
        print(f"Density: {topology_metrics.density:.4f}")
        print(f"Communities: {community_structure.num_communities}")
        print(f"Risk Score: {robustness_analysis.systemic_risk_score:.3f}")
        print(f"Execution Time: {total_time:.2f} seconds")

        # Risk assessment
        risk_score = robustness_analysis.systemic_risk_score
        if risk_score > 0.7:
            risk_level = "HIGH RISK"
        elif risk_score > 0.4:
            risk_level = "MEDIUM RISK"
        else:
            risk_level = "LOW RISK"
        print(f"Risk Level: {risk_level}")

        print("\nAll core functions are working properly!")
        return True

    except Exception as e:
        print(f"\nERROR during test: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting simple network model test...\n")

    success = simple_test()

    if success:
        print("\nTEST PASSED! System is ready for use.")
        exit(0)
    else:
        print("\nTEST FAILED! Please check the errors.")
        exit(1)