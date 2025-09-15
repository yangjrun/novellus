#!/usr/bin/env python3
"""
A basic MCP server using the Python SDK with FastMCP.
"""

import signal
import sys
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

from mcp.server.fastmcp import FastMCP
from config import config
from database import db, sync_db, mongodb, sync_mongodb, init_database, close_database, get_database_info, DatabaseError

# Create the MCP server instance
mcp = FastMCP(config.server_name)


# Example resource: Read local files
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """Read and return the contents of a local file."""
    try:
        file_path = Path(path)
        if file_path.exists() and file_path.is_file():
            return file_path.read_text(encoding="utf-8")
        else:
            return f"File not found: {path}"
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"


# Example tool: Calculator
@mcp.tool()
def calculate(expression: str) -> str:
    """Safely evaluate basic mathematical expressions."""
    try:
        # Simple whitelist of allowed characters for safety
        allowed_chars = set("0123456789+-*/.()")
        if not all(c in allowed_chars or c.isspace() for c in expression):
            return "Error: Invalid characters in expression"

        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


# Example tool: List directory contents
@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List the contents of a directory."""
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return f"Directory not found: {path}"

        if not dir_path.is_dir():
            return f"Path is not a directory: {path}"

        items = []
        for item in dir_path.iterdir():
            item_type = "DIR" if item.is_dir() else "FILE"
            items.append(f"{item_type}: {item.name}")

        return "\n".join(sorted(items))
    except Exception as e:
        return f"Error listing directory {path}: {str(e)}"


# Example tool: Create file
@mcp.tool()
def create_file(path: str, content: str) -> str:
    """Create a new file with the specified content."""
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"File created successfully: {path}"
    except Exception as e:
        return f"Error creating file {path}: {str(e)}"


# Example prompt: Generate greeting
@mcp.prompt()
def generate_greeting(name: str, style: str = "friendly") -> str:
    """Generate a greeting message for a person."""
    styles = {
        "friendly": f"Please write a warm, friendly greeting for {name}.",
        "formal": f"Please write a formal, professional greeting for {name}.",
        "casual": f"Please write a casual, relaxed greeting for {name}.",
    }

    return styles.get(style, styles["friendly"])


# Example prompt: Code review
@mcp.prompt()
def code_review_prompt(language: str, code: str) -> str:
    """Generate a prompt for code review."""
    return f"""Please review the following {language} code and provide feedback:

Code:
```{language}
{code}
```

Please analyze:
1. Code quality and readability
2. Potential bugs or issues
3. Performance considerations
4. Best practices adherence
5. Suggestions for improvement
"""


# Database Connection Tools
@mcp.tool()
def database_info() -> str:
    """Get comprehensive database connection information for both PostgreSQL and MongoDB."""
    try:
        info = get_database_info()
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error getting database info: {str(e)}"


# PostgreSQL Tools
@mcp.tool()
def postgres_connection_info() -> str:
    """Get PostgreSQL database connection information and test connectivity."""
    try:
        info = get_database_info()
        postgres_info = info.get("databases", {}).get("postgresql", {})
        return json.dumps(postgres_info, indent=2)
    except Exception as e:
        return f"Error getting PostgreSQL info: {str(e)}"


@mcp.tool()
def postgres_query(sql: str) -> str:
    """Execute a SELECT query against the PostgreSQL database."""
    try:
        if not sql.strip().upper().startswith('SELECT'):
            return "Error: Only SELECT queries are allowed for security reasons"

        results = sync_db.execute_query(sql)
        return json.dumps(results, indent=2, default=str)
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error executing query: {str(e)}"


@mcp.tool()
def postgres_table_info(table_name: str = "") -> str:
    """Get information about PostgreSQL tables. If table_name is provided, get detailed info for that table."""
    try:
        if table_name:
            # Get detailed table information
            query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                ordinal_position
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
            """
            results = sync_db.execute_query(query, (table_name,))
            if not results:
                return f"Table '{table_name}' not found or no access"
        else:
            # Get list of all tables
            query = """
            SELECT
                table_name,
                table_type,
                table_schema
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
            results = sync_db.execute_query(query)

        return json.dumps(results, indent=2)
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error getting table info: {str(e)}"


@mcp.tool()
def postgres_demo_queries() -> str:
    """Get a list of demo PostgreSQL queries that can be used for testing."""
    demo_queries = {
        "basic_queries": [
            "SELECT version()",
            "SELECT current_database()",
            "SELECT current_user",
            "SELECT now()",
            "SELECT 1 + 1 as result"
        ],
        "system_info": [
            "SELECT * FROM information_schema.tables WHERE table_schema = 'public' LIMIT 10",
            "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public'",
            "SELECT datname FROM pg_database",
            "SELECT count(*) as table_count FROM information_schema.tables WHERE table_schema = 'public'"
        ],
        "sample_data_queries": [
            "SELECT 'Hello PostgreSQL' as message, 42 as number, now() as timestamp",
            "SELECT generate_series(1, 5) as numbers",
            "SELECT chr(65 + generate_series(0, 25)) as alphabet",
            "SELECT * FROM demo_users ORDER BY created_at DESC LIMIT 5"
        ]
    }

    return json.dumps(demo_queries, indent=2)


@mcp.tool()
def postgres_create_demo_table() -> str:
    """Create a PostgreSQL demo table with sample data for testing purposes."""
    try:
        # Create demo table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS demo_users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            age INTEGER CHECK (age > 0 AND age < 150),
            department VARCHAR(50),
            salary DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Create index
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_demo_users_email ON demo_users(email);
        CREATE INDEX IF NOT EXISTS idx_demo_users_department ON demo_users(department);
        """

        # Insert sample data
        insert_data_sql = """
        INSERT INTO demo_users (name, email, age, department, salary) VALUES
        ('Alice Johnson', 'alice@example.com', 28, 'Engineering', 85000.00),
        ('Bob Smith', 'bob@example.com', 35, 'Marketing', 72000.00),
        ('Charlie Brown', 'charlie@example.com', 42, 'Sales', 68000.00),
        ('Diana Prince', 'diana@example.com', 31, 'Engineering', 92000.00),
        ('Eve Wilson', 'eve@example.com', 29, 'HR', 65000.00)
        ON CONFLICT (email) DO NOTHING
        """

        # Execute using sync connection
        with sync_db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_sql)
                cursor.execute(create_index_sql)
                cursor.execute(insert_data_sql)
                conn.commit()

        return "PostgreSQL demo table 'demo_users' created successfully with enhanced structure and sample data"
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error creating demo table: {str(e)}"


# MongoDB Tools
@mcp.tool()
def mongo_connection_info() -> str:
    """Get MongoDB connection information and test connectivity."""
    try:
        info = get_database_info()
        mongodb_info = info.get("databases", {}).get("mongodb", {})
        return json.dumps(mongodb_info, indent=2)
    except Exception as e:
        return f"Error getting MongoDB info: {str(e)}"


@mcp.tool()
def mongo_find(collection: str, filter_query: str = "{}", limit: int = 10) -> str:
    """Find documents in a MongoDB collection with optional filter and limit."""
    try:
        import json as json_lib
        filter_dict = json_lib.loads(filter_query)
        results = sync_mongodb.find_many(collection, filter_dict, limit=limit)
        return json.dumps({
            "collection": collection,
            "filter": filter_dict,
            "count": len(results),
            "limit": limit,
            "documents": results
        }, indent=2, default=str)
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error executing find: {str(e)}"


@mcp.tool()
def mongo_insert(collection: str, document: str) -> str:
    """Insert a document into a MongoDB collection."""
    try:
        import json as json_lib
        doc_dict = json_lib.loads(document)

        # Add timestamp if not present
        from datetime import datetime
        if 'created_at' not in doc_dict:
            doc_dict['created_at'] = datetime.utcnow().isoformat()

        # Use sync connection for simple operation
        collection_obj = sync_mongodb.get_collection(collection)
        result = collection_obj.insert_one(doc_dict)

        return json.dumps({
            "success": True,
            "collection": collection,
            "inserted_id": str(result.inserted_id),
            "document": doc_dict
        }, indent=2, default=str)
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error inserting document: {str(e)}"


@mcp.tool()
def mongo_collections() -> str:
    """List all collections in the MongoDB database with document counts."""
    try:
        collections = sync_mongodb.database.list_collection_names()
        collection_info = []

        for collection_name in collections:
            try:
                collection = sync_mongodb.get_collection(collection_name)
                count = collection.count_documents({})
                collection_info.append({
                    "name": collection_name,
                    "document_count": count
                })
            except Exception as e:
                collection_info.append({
                    "name": collection_name,
                    "document_count": "error",
                    "error": str(e)
                })

        return json.dumps({
            "total_collections": len(collections),
            "collections": collection_info
        }, indent=2)
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error listing collections: {str(e)}"


@mcp.tool()
def mongo_create_demo_collection() -> str:
    """Create a demo collection with sample data for testing purposes."""
    try:
        collection_name = "demo_users"

        # Sample documents
        demo_docs = [
            {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "age": 28,
                "department": "Engineering",
                "skills": ["Python", "JavaScript", "MongoDB"],
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "name": "Bob Smith",
                "email": "bob@example.com",
                "age": 35,
                "department": "Marketing",
                "skills": ["Analytics", "Content", "Social Media"],
                "created_at": "2024-01-16T09:15:00Z"
            },
            {
                "name": "Charlie Brown",
                "email": "charlie@example.com",
                "age": 42,
                "department": "Sales",
                "skills": ["Negotiation", "CRM", "Networking"],
                "created_at": "2024-01-17T14:45:00Z"
            }
        ]

        # Insert documents
        collection = sync_mongodb.get_collection(collection_name)

        # Clear existing data first
        collection.delete_many({})

        # Insert new data
        result = collection.insert_many(demo_docs)

        return f"Demo collection '{collection_name}' created successfully with {len(result.inserted_ids)} documents"
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error creating demo collection: {str(e)}"


@mcp.tool()
def mongo_demo_queries() -> str:
    """Get a list of demo MongoDB queries that can be used for testing."""
    demo_queries = {
        "basic_queries": [
            {"description": "Find all documents", "collection": "demo_users", "filter": "{}"},
            {"description": "Find by name", "collection": "demo_users", "filter": '{"name": "Alice Johnson"}'},
            {"description": "Find by age range", "collection": "demo_users", "filter": '{"age": {"$gte": 30}}'},
            {"description": "Find by department", "collection": "demo_users", "filter": '{"department": "Engineering"}'}
        ],
        "advanced_queries": [
            {"description": "Find by skills array", "collection": "demo_users", "filter": '{"skills": "Python"}'},
            {"description": "Multiple conditions", "collection": "demo_users", "filter": '{"age": {"$lt": 40}, "department": "Marketing"}'},
            {"description": "Regex search", "collection": "demo_users", "filter": '{"email": {"$regex": "@example.com$"}}'}
        ],
        "sample_documents": [
            {"name": "Test User", "email": "test@example.com", "age": 25, "department": "QA"},
            {"title": "Sample Post", "content": "This is a test post", "tags": ["test", "demo"]}
        ]
    }

    return json.dumps(demo_queries, indent=2)


@mcp.tool()
def mongo_update(collection: str, filter_query: str, update_query: str) -> str:
    """Update documents in a MongoDB collection."""
    try:
        import json as json_lib
        from datetime import datetime

        filter_dict = json_lib.loads(filter_query)
        update_dict = json_lib.loads(update_query)

        # Add updated_at timestamp
        if '$set' in update_dict:
            update_dict['$set']['updated_at'] = datetime.utcnow().isoformat()
        else:
            update_dict['$set'] = {'updated_at': datetime.utcnow().isoformat()}

        collection_obj = sync_mongodb.get_collection(collection)
        result = collection_obj.update_many(filter_dict, update_dict)

        return json.dumps({
            "success": True,
            "collection": collection,
            "filter": filter_dict,
            "update": update_dict,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }, indent=2, default=str)
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error updating documents: {str(e)}"


@mcp.tool()
def mongo_delete(collection: str, filter_query: str) -> str:
    """Delete documents from a MongoDB collection."""
    try:
        import json as json_lib
        filter_dict = json_lib.loads(filter_query)

        collection_obj = sync_mongodb.get_collection(collection)
        result = collection_obj.delete_many(filter_dict)

        return json.dumps({
            "success": True,
            "collection": collection,
            "filter": filter_dict,
            "deleted_count": result.deleted_count
        }, indent=2, default=str)
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error deleting documents: {str(e)}"


@mcp.tool()
def mongo_aggregate(collection: str, pipeline: str) -> str:
    """Execute an aggregation pipeline on a MongoDB collection."""
    try:
        import json as json_lib
        pipeline_list = json_lib.loads(pipeline)

        collection_obj = sync_mongodb.get_collection(collection)
        results = list(collection_obj.aggregate(pipeline_list))

        return json.dumps({
            "collection": collection,
            "pipeline": pipeline_list,
            "result_count": len(results),
            "results": results
        }, indent=2, default=str)
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error executing aggregation: {str(e)}"


@mcp.tool()
def mongo_collection_stats(collection: str) -> str:
    """Get detailed statistics for a MongoDB collection."""
    try:
        collection_obj = sync_mongodb.get_collection(collection)

        # Get basic stats
        stats = sync_mongodb.database.command("collStats", collection)

        # Get sample documents
        sample_docs = list(collection_obj.find().limit(3))

        # Get indexes
        indexes = list(collection_obj.list_indexes())

        return json.dumps({
            "collection": collection,
            "statistics": {
                "count": stats.get("count", 0),
                "size": stats.get("size", 0),
                "avgObjSize": stats.get("avgObjSize", 0),
                "storageSize": stats.get("storageSize", 0),
                "indexes": stats.get("nindexes", 0)
            },
            "indexes": indexes,
            "sample_documents": sample_docs
        }, indent=2, default=str)
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error getting collection stats: {str(e)}"


@mcp.tool()
def mongo_create_index(collection: str, index_spec: str, options: str = "{}") -> str:
    """Create an index on a MongoDB collection."""
    try:
        import json as json_lib
        index_dict = json_lib.loads(index_spec)
        options_dict = json_lib.loads(options)

        collection_obj = sync_mongodb.get_collection(collection)

        # Convert index specification to pymongo format
        index_keys = [(key, direction) for key, direction in index_dict.items()]

        result = collection_obj.create_index(index_keys, **options_dict)

        return json.dumps({
            "success": True,
            "collection": collection,
            "index_name": result,
            "index_spec": index_dict,
            "options": options_dict
        }, indent=2, default=str)
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error creating index: {str(e)}"


@mcp.tool()
def mongo_drop_collection(collection: str) -> str:
    """Drop a MongoDB collection (use with caution)."""
    try:
        collection_obj = sync_mongodb.get_collection(collection)
        collection_obj.drop()

        return json.dumps({
            "success": True,
            "message": f"Collection '{collection}' dropped successfully"
        }, indent=2)
    except DatabaseError as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error dropping collection: {str(e)}"


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    asyncio.create_task(close_database())
    sys.exit(0)


def main():
    """Main entry point for the MCP server."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize database connection
    try:
        asyncio.run(init_database())
        print("Database connection initialized")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
        print("PostgreSQL tools may not work properly")

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
