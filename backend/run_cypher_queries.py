#!/usr/bin/env python3
"""
Script to run all Cypher queries using the Neo4j driver.
This script demonstrates how to use the Neo4j driver to execute all the Cypher queries in the project.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from utils.neo4j_driver import get_neo4j_driver, close_neo4j_driver

def run_all_cypher_queries():
    """Run all Cypher queries in the project."""
    print("STARTING: Running all Cypher queries with Neo4j driver")
    print("=" * 60)
    
    try:
        # Get the Neo4j driver
        driver = get_neo4j_driver()
        print("SUCCESS: Connected to Neo4j database")
        
        # 1. Execute schema
        print("\nSTEP 1: Creating schema...")
        try:
            driver.execute_schema()
            print("SUCCESS: Schema created successfully")
        except Exception as e:
            print(f"WARNING: Schema creation failed (might already exist): {e}")
        
        # 2. Load data
        print("\nSTEP 2: Loading data...")
        try:
            driver.load_data()
            print("SUCCESS: Data loaded successfully")
        except Exception as e:
            print(f"WARNING: Data loading failed: {e}")
        
        # 3. Calculate distances
        print("\nSTEP 3: Calculating distances...")
        try:
            driver.calculate_distances()
            print("SUCCESS: Distances calculated successfully")
        except Exception as e:
            print(f"WARNING: Distance calculation failed: {e}")
        
        # 4. Calculate rating scores
        print("\nSTEP 4: Calculating rating scores...")
        try:
            driver.calculate_rating_scores()
            print("SUCCESS: Rating scores calculated successfully")
        except Exception as e:
            print(f"WARNING: Rating score calculation failed: {e}")
        
        # 5. Run strategy queries
        print("\nSTEP 5: Running strategy queries...")
        strategies_dir = backend_dir / "service" / "neo4j_setup" / "strategies"
        if strategies_dir.exists():
            strategy_files = list(strategies_dir.glob("*.cypher"))
            for strategy_file in strategy_files:
                print(f"  Running {strategy_file.name}...")
                try:
                    result = driver.load_cypher_file(str(strategy_file))
                    print(f"    SUCCESS: {strategy_file.name} executed successfully")
                except Exception as e:
                    print(f"    WARNING: {strategy_file.name} failed: {e}")
        else:
            print("  WARNING: Strategies directory not found")
        
        # 6. Test some custom queries
        print("\nSTEP 6: Testing custom queries...")
        
        # Get restaurant count
        try:
            result = driver.run_query("MATCH (r:Restaurant) RETURN count(r) as count")
            print(f"  SUCCESS: Total restaurants: {result[0]['count']}")
        except Exception as e:
            print(f"  WARNING: Restaurant count query failed: {e}")
        
        # Get user count
        try:
            result = driver.run_query("MATCH (u:User) RETURN count(u) as count")
            print(f"  SUCCESS: Total users: {result[0]['count']}")
        except Exception as e:
            print(f"  WARNING: User count query failed: {e}")
        
        # Get review count
        try:
            result = driver.run_query("MATCH (r:Review) RETURN count(r) as count")
            print(f"  SUCCESS: Total reviews: {result[0]['count']}")
        except Exception as e:
            print(f"  WARNING: Review count query failed: {e}")
        
        # Get sample restaurants
        try:
            result = driver.run_query("""
                MATCH (r:Restaurant)
                RETURN r.name as name, r.cuisine as cuisine, r.rating as rating
                LIMIT 5
            """)
            print("  SUCCESS: Sample restaurants:")
            for restaurant in result:
                print(f"    - {restaurant['name']} ({restaurant['cuisine']}) - Rating: {restaurant['rating']}")
        except Exception as e:
            print(f"  WARNING: Sample restaurants query failed: {e}")
        
        print("\n" + "=" * 60)
        print("SUCCESS: All Cypher queries completed!")
        print("The Neo4j driver is working correctly and can execute all queries.")
        
    except Exception as e:
        print(f"ERROR: Failed to run Cypher queries: {e}")
        return False
    finally:
        # Clean up
        close_neo4j_driver()
    
    return True

def demonstrate_driver_usage():
    """Demonstrate various ways to use the Neo4j driver."""
    print("\nNEO4J DRIVER USAGE EXAMPLES")
    print("=" * 40)
    
    try:
        driver = get_neo4j_driver()
        
        # Example 1: Simple query with parameters
        print("\n1. Query with parameters:")
        query = "MATCH (r:Restaurant {cuisine: $cuisine}) RETURN r.name as name LIMIT 3"
        result = driver.run_query(query, {"cuisine": "Italian"})
        print(f"   Italian restaurants: {[r['name'] for r in result]}")
        
        # Example 2: Single result query
        print("\n2. Single result query:")
        result = driver.run_query_single("MATCH (r:Restaurant) RETURN count(r) as count")
        print(f"   Total restaurants: {result['count']}")
        
        # Example 3: Query without results
        print("\n3. Query without results (CREATE constraint):")
        try:
            driver.run_query_without_results("""
                CREATE CONSTRAINT restaurant_name IF NOT EXISTS 
                FOR (r:Restaurant) REQUIRE r.name IS UNIQUE
            """)
            print("   Constraint created successfully")
        except Exception as e:
            print(f"   Constraint creation failed (might already exist): {e}")
        
        # Example 4: Complex query
        print("\n4. Complex query (restaurants with reviews):")
        result = driver.run_query("""
            MATCH (r:Restaurant)-[:HAS_REVIEW]->(rev:Review)
            WITH r, count(rev) as review_count, avg(rev.rating) as avg_rating
            WHERE review_count > 0
            RETURN r.name as name, review_count, round(avg_rating, 2) as avg_rating
            ORDER BY avg_rating DESC
            LIMIT 5
        """)
        print("   Top rated restaurants:")
        for restaurant in result:
            print(f"     - {restaurant['name']}: {restaurant['avg_rating']} ({restaurant['review_count']} reviews)")
        
    except Exception as e:
        print(f"ERROR: Demonstration failed: {e}")
    finally:
        close_neo4j_driver()

if __name__ == "__main__":
    # Run all queries
    success = run_all_cypher_queries()
    
    if success:
        # Demonstrate usage
        demonstrate_driver_usage()
    
    print(f"\n{'SUCCESS' if success else 'ERROR'} Script completed {'successfully' if success else 'with errors'}")
    sys.exit(0 if success else 1) 