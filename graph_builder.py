import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load credentials from your .env file
load_dotenv()

class OSINTGraphDatabase:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not password:
            raise ValueError("Neo4j Password not found. Please check your .env file.")
            
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print("✅ Successfully connected to Neo4j Graph Database.")

    def close(self):
        self.driver.close()

    def insert_triplet(self, subject_label, subject_value, relation, object_label, object_value):
        """
        Inserts an AI-extracted triplet into the Neo4j Database.
        Uses MERGE to ensure no duplicate nodes or relationships are created.
        """
        with self.driver.session() as session:
            # Note: Cypher labels and relationship types cannot be parameterized natively, 
            # so we inject them cleanly using f-strings, while parameterizing the values.
            
            # Clean up relation string (e.g., remove spaces or weird characters)
            clean_relation = relation.upper().replace(" ", "_").replace("-", "_")
            
            cypher_query = f"""
                MERGE (s:{subject_label} {{value: $s_val}})
                MERGE (o:{object_label} {{value: $o_val}})
                MERGE (s)-[r:{clean_relation}]->(o)
                RETURN s, r, o
            """
            
            session.run(
                cypher_query, 
                s_val=subject_value, 
                o_val=object_value
            )
