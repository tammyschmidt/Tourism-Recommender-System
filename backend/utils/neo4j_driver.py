from neo4j import GraphDatabase
import os
from typing import List, Dict, Any, Optional
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jDriver:
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Initialize Neo4j driver with connection parameters.
        If not provided, will use environment variables or defaults.
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://v2202411241288295404.powersrv.de:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "2kJAHn195lk")
        
        self.driver = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test the connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            logger.info("Successfully connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j driver connection closed")
    
    def _split_cypher_statements(self, query: str) -> List[str]:
        """
        Split a Cypher query into individual statements.
        Handles semicolon-separated statements and comments.
        """
        # Remove comments
        lines = query.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip comment lines
            if line.strip().startswith('//'):
                continue
            # Remove inline comments
            if '//' in line:
                line = line.split('//')[0]
            cleaned_lines.append(line)
        
        query = '\n'.join(cleaned_lines)
        
        # Split by semicolon and filter out empty statements
        statements = [stmt.strip() for stmt in query.split(';') if stmt.strip()]
        return statements
    
    def run_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results as a list of dictionaries.
        
        Args:
            query: Cypher query string
            parameters: Dictionary of parameters for the query
            
        Returns:
            List of dictionaries containing the query results
        """
        if parameters is None:
            parameters = {}
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                records = [dict(record) for record in result]
                logger.info(f"Query executed successfully. Returned {len(records)} records.")
                return records
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            raise
    
    def run_query_single(self, query: str, parameters: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a Cypher query and return a single result.
        
        Args:
            query: Cypher query string
            parameters: Dictionary of parameters for the query
            
        Returns:
            Single dictionary result or None if no results
        """
        results = self.run_query(query, parameters)
        return results[0] if results else None
    
    def run_query_without_results(self, query: str, parameters: Dict[str, Any] = None):
        """
        Execute a Cypher query that doesn't return results (e.g., CREATE, DELETE, SET).
        
        Args:
            query: Cypher query string
            parameters: Dictionary of parameters for the query
        """
        if parameters is None:
            parameters = {}
        
        try:
            with self.driver.session() as session:
                session.run(query, parameters)
                logger.info("Query executed successfully (no results returned).")
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            raise
    
    def run_multiple_statements(self, query: str, parameters: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
        """
        Execute multiple Cypher statements and return results for each.
        
        Args:
            query: Cypher query string containing multiple statements
            parameters: Dictionary of parameters for the queries
            
        Returns:
            List of results for each statement
        """
        statements = self._split_cypher_statements(query)
        all_results = []
        
        for i, statement in enumerate(statements):
            try:
                logger.info(f"Executing statement {i+1}/{len(statements)}")
                if statement.strip().upper().startswith(('CREATE', 'DELETE', 'SET', 'MERGE', 'REMOVE')):
                    # Statement that doesn't return results
                    self.run_query_without_results(statement, parameters)
                    all_results.append([])
                else:
                    # Statement that returns results
                    result = self.run_query(statement, parameters)
                    all_results.append(result)
            except Exception as e:
                logger.error(f"Error executing statement {i+1}: {e}")
                logger.error(f"Statement: {statement}")
                raise
        
        return all_results
    
    def load_cypher_file(self, file_path: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Load and execute a Cypher query from a file.
        Handles both single and multiple statements.
        
        Args:
            file_path: Path to the .cypher file
            parameters: Dictionary of parameters for the query
            
        Returns:
            List of dictionaries containing the query results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                query = file.read().strip()
            
            logger.info(f"Loaded Cypher query from {file_path}")
            
            # Check if the query contains multiple statements
            statements = self._split_cypher_statements(query)
            if len(statements) > 1:
                logger.info(f"Found {len(statements)} statements, executing each separately")
                results = self.run_multiple_statements(query, parameters)
                # Flatten results
                return [item for sublist in results for item in sublist]
            else:
                return self.run_query(query, parameters)
        except FileNotFoundError:
            logger.error(f"Cypher file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading Cypher file {file_path}: {e}")
            raise
    
    def execute_schema(self, schema_file_path: str = None):
        """
        Execute schema creation queries.
        
        Args:
            schema_file_path: Path to schema.cypher file
        """
        if schema_file_path is None:
            # Default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            schema_file_path = os.path.join(current_dir, '..', 'service', 'neo4j_setup', 'schema.cypher')
        
        try:
            self.load_cypher_file(schema_file_path)
            logger.info("Schema executed successfully")
        except Exception as e:
            logger.error(f"Error executing schema: {e}")
            raise
    
    def load_data(self, data_file_path: str = None, parameters: Dict[str, Any] = None):
        """
        Load data using the load_data.cypher file.
        
        Args:
            data_file_path: Path to load_data.cypher file
            parameters: Parameters for the data loading query
        """
        if data_file_path is None:
            # Default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_file_path = os.path.join(current_dir, '..', 'service', 'neo4j_setup', 'load_data.cypher')
        
        try:
            self.load_cypher_file(data_file_path, parameters)
            logger.info("Data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def calculate_distances(self, distance_file_path: str = None, parameters: Dict[str, Any] = None):
        """
        Calculate distances between locations.
        
        Args:
            distance_file_path: Path to calculate_distance.cypher file
            parameters: Parameters for the distance calculation
        """
        if distance_file_path is None:
            # Default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            distance_file_path = os.path.join(current_dir, '..', 'service', 'neo4j_setup', 'calculate_distance.cypher')
        
        try:
            self.load_cypher_file(distance_file_path, parameters)
            logger.info("Distances calculated successfully")
        except Exception as e:
            logger.error(f"Error calculating distances: {e}")
            raise
    
    def calculate_rating_scores(self, rating_file_path: str = None):
        """
        Calculate rating scores.
        
        Args:
            rating_file_path: Path to rating_score.cypher file
        """
        if rating_file_path is None:
            # Default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            rating_file_path = os.path.join(current_dir, '..', 'service', 'neo4j_setup', 'rating_score.cypher')
        
        try:
            self.load_cypher_file(rating_file_path)
            logger.info("Rating scores calculated successfully")
        except Exception as e:
            logger.error(f"Error calculating rating scores: {e}")
            raise

# Global instance for easy access
neo4j_driver = None

def get_neo4j_driver() -> Neo4jDriver:
    """Get or create a global Neo4j driver instance."""
    global neo4j_driver
    if neo4j_driver is None:
        neo4j_driver = Neo4jDriver()
    return neo4j_driver

def close_neo4j_driver():
    """Close the global Neo4j driver instance."""
    global neo4j_driver
    if neo4j_driver:
        neo4j_driver.close()
        neo4j_driver = None 