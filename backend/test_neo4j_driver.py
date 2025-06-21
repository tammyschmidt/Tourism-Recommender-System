#!/usr/bin/env python3
"""
Test script for Neo4j driver to verify connection and execute Cypher queries.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from utils.neo4j_driver import Neo4jDriver, get_neo4j_driver, close_neo4j_driver

def test_connection():
    """Test basic connection to Neo4j."""
    print("Testing Neo4j connection...")
    try:
        driver = get_neo4j_driver()
        print("SUCCESS: Successfully connected to Neo4j!")
        return driver
    except Exception as e:
        print(f"ERROR: Failed to connect to Neo4j: {e}")
        return None

def test_basic_query(driver):
    """Test a basic Cypher query."""
    print("\nTesting basic query...")
    try:
        result = driver.run_query("MATCH (n) RETURN count(n) as node_count")
        print(f"SUCCESS: Basic query successful. Node count: {result[0]['node_count']}")
        return True
    except Exception as e:
        print(f"ERROR: Basic query failed: {e}")
        return False

def test_schema_execution(driver):
    """Test schema creation."""
    print("\nTesting schema execution...")
    try:
        driver.execute_schema()
        print("SUCCESS: Schema executed successfully!")
        return True
    except Exception as e:
        print(f"ERROR: Schema execution failed: {e}")
        return False

def test_data_loading(driver):
    """Test data loading."""
    print("\nTesting data loading...")
    try:
        driver.load_data()
        print("SUCCESS: Data loaded successfully!")
        return True
    except Exception as e:
        print(f"ERROR: Data loading failed: {e}")
        return False

def test_distance_calculation(driver):
    """Test distance calculation."""
    print("\nTesting distance calculation...")
    try:
        # Provide sample parameters for distance calculation
        parameters = {
            "latitude": 39.9555052,
            "longitude": -75.1555641
        }
        driver.calculate_distances(parameters=parameters)
        print("SUCCESS: Distance calculation successful!")
        return True
    except Exception as e:
        print(f"ERROR: Distance calculation failed: {e}")
        return False

def test_rating_score_calculation(driver):
    """Test rating score calculation."""
    print("\nTesting rating score calculation...")
    try:
        driver.calculate_rating_scores()
        print("SUCCESS: Rating score calculation successful!")
        return True
    except Exception as e:
        print(f"ERROR: Rating score calculation failed: {e}")
        return False

def test_custom_query(driver):
    """Test a custom query to get some data."""
    print("\nTesting custom query...")
    try:
        # Test query to get some restaurant data
        query = """
        MATCH (r:Restaurant)
        RETURN r.name as name, r.cuisine as cuisine
        LIMIT 5
        """
        result = driver.run_query(query)
        print(f"SUCCESS: Custom query successful. Found {len(result)} restaurants:")
        for restaurant in result:
            print(f"  - {restaurant['name']} ({restaurant['cuisine']})")
        return True
    except Exception as e:
        print(f"ERROR: Custom query failed: {e}")
        return False

def test_strategy_queries(driver):
    """Test strategy queries from the strategies directory."""
    print("\nTesting strategy queries...")
    
    strategies_dir = backend_dir / "service" / "neo4j_setup" / "strategies"
    if not strategies_dir.exists():
        print("WARNING: Strategies directory not found, skipping strategy tests.")
        return True
    
    strategy_files = list(strategies_dir.glob("*.cypher"))
    if not strategy_files:
        print("WARNING: No strategy files found, skipping strategy tests.")
        return True
    
    # Sample parameters for strategy queries
    sample_parameters = {
        "restaurant_id": "1",  # Sample restaurant ID
        "top_n": 5,
        "latitude": 39.9555052,
        "longitude": -75.1555641,
        "categories": ["Italian"],
        "inputCategories": ["Italian"],
        "maxDistance": 100,
        "alpha": 1,
        "beta": 1,
        "gamma": 1,
        "delta": 1
    }
    
    success_count = 0
    for strategy_file in strategy_files:
        print(f"  Testing {strategy_file.name}...")
        try:
            # Determine which parameters to use based on the file name
            if "category_jaccard" in strategy_file.name or "category_shortest_path" in strategy_file.name or "setting_based" in strategy_file.name:
                params = {"restaurant_id": "1", "top_n": 5}
            elif "location_knn" in strategy_file.name:
                params = {"latitude": 39.9555052, "longitude": -75.1555641, "categories": ["Italian"], "top_n": 5}
            elif "multi_objective_scoring" in strategy_file.name:
                params = {"inputCategories": ["Italian"], "latitude": 39.9555052, "longitude": -75.1555641, 
                         "maxDistance": 100, "alpha": 1, "beta": 1, "gamma": 1, "delta": 1, "top_n": 5}
            elif "weighted_jaccard" in strategy_file.name:
                params = {"inputCategories": ["Italian"], "top_n": 5}
            else:
                params = {}
            
            result = driver.load_cypher_file(str(strategy_file), params)
            print(f"    SUCCESS: {strategy_file.name} executed successfully")
            success_count += 1
        except Exception as e:
            print(f"    ERROR: {strategy_file.name} failed: {e}")
    
    print(f"SUCCESS: {success_count}/{len(strategy_files)} strategy queries executed successfully!")
    return success_count == len(strategy_files)

def main():
    """Main test function."""
    print("STARTING: Neo4j Driver Tests")
    print("=" * 50)
    
    # Test connection
    driver = test_connection()
    if not driver:
        print("\nERROR: Cannot proceed without Neo4j connection.")
        return False
    
    # Run all tests
    tests = [
        ("Basic Query", lambda: test_basic_query(driver)),
        ("Schema Execution", lambda: test_schema_execution(driver)),
        ("Data Loading", lambda: test_data_loading(driver)),
        ("Distance Calculation", lambda: test_distance_calculation(driver)),
        ("Rating Score Calculation", lambda: test_rating_score_calculation(driver)),
        ("Custom Query", lambda: test_custom_query(driver)),
        ("Strategy Queries", lambda: test_strategy_queries(driver)),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR: {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    # Cleanup
    close_neo4j_driver()
    
    if passed == len(results):
        print("\nSUCCESS: All tests passed! Neo4j driver is working correctly.")
        return True
    else:
        print(f"\nWARNING: {len(results) - passed} tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 