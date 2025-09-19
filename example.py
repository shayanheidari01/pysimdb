from pysimdb import JsonDatabase, TableSchema, SchemaError

def test_basic_functionality():
    """Test basic database operations"""
    print("=== Testing Basic Functionality ===")
    
    # Initialize database
    db = JsonDatabase("test_data")
    
    # Define schemas
    user_schema = TableSchema({
        "id": int,
        "name": str,
        "age": int,
        "email": str
    }, primary_key="id")
    
    post_schema = TableSchema({
        "id": int,
        "user_id": int,
        "title": str,
        "content": str
    }, primary_key="id")
    
    # Create tables
    db.create_table("users", user_schema)
    db.create_table("posts", post_schema)
    
    print("✓ Table creation successful")
    
    # Insert sample data
    users = [
        {"id": 1, "name": "John Doe", "age": 30, "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "age": 25, "email": "jane@example.com"},
        {"id": 3, "name": "Bob Brown", "age": 35, "email": "bob@example.com"}
    ]
    
    posts = [
        {"id": 1, "user_id": 1, "title": "First Post", "content": "Hello, World!"},
        {"id": 2, "user_id": 1, "title": "Second Post", "content": "More content..."},
        {"id": 3, "user_id": 2, "title": "Jane's Post", "content": "Hello from Jane!"}
    ]
    
    # Insert with transaction support
    def insert_data():
        for user in users:
            db.insert("users", user, if_exists="ignore")
        for post in posts:
            db.insert("posts", post, if_exists="ignore")
    
    db.transaction(insert_data)
    
    print("✓ Data insertion with transaction successful")
    
    # Select all data
    all_users = db.select("users")
    all_posts = db.select("posts")
    
    print(f"✓ Data selection successful: {len(all_users)} users, {len(all_posts)} posts")
    
    return db

def test_schema_validation(db):
    """Test schema validation"""
    print("\n=== Testing Schema Validation ===")
    
    # Test valid data
    try:
        valid_user = {"id": 4, "name": "Valid User", "age": 28, "email": "valid@example.com"}
        db.insert("users", valid_user)
        print("✓ Valid data insertion successful")
    except Exception as e:
        print(f"✗ Valid data insertion failed: {e}")
    
    # Test invalid data (wrong type)
    try:
        invalid_user = {"id": "5", "name": "Invalid User", "age": 28, "email": "invalid@example.com"}
        db.insert("users", invalid_user)
        print("✗ Invalid data (wrong type) was accepted")
    except SchemaError:
        print("✓ Schema validation caught wrong type correctly")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test missing field
    try:
        incomplete_user = {"id": 6, "name": "Incomplete User", "age": 28}
        db.insert("users", incomplete_user)
        print("✗ Incomplete data was accepted")
    except SchemaError:
        print("✓ Schema validation caught missing field correctly")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

def test_query_builder(db):
    """Test query builder functionality"""
    print("\n=== Testing Query Builder ===")
    
    # Test simple query
    try:
        results = db.query("users").all()
        print(f"✓ Simple query successful: {len(results)} users")
    except Exception as e:
        print(f"✗ Simple query failed: {e}")
    
    # Test where clause
    try:
        results = db.query("users").where("age", ">", 25).all()
        print(f"✓ Where clause query successful: {len(results)} users over 25")
    except Exception as e:
        print(f"✗ Where clause query failed: {e}")
    
    # Test order by
    try:
        results = db.query("users").order_by("age").all()
        print("✓ Order by query successful")
    except Exception as e:
        print(f"✗ Order by query failed: {e}")
    
    # Test limit and offset
    try:
        results = db.query("users").limit(2).offset(1).all()
        print(f"✓ Limit/offset query successful: {len(results)} users")
    except Exception as e:
        print(f"✗ Limit/offset query failed: {e}")
    
    # Test select specific columns
    try:
        results = db.query("users").select("name", "age").all()
        print("✓ Column selection query successful")
    except Exception as e:
        print(f"✗ Column selection query failed: {e}")

def test_joins(db):
    """Test join operations"""
    print("\n=== Testing Join Operations ===")
    
    try:
        results = (
            db.query("posts")
            .join("users", "user_id", "id")
            .select("title", "content", "name")
            .all()
        )
        print(f"✓ Join operation successful: {len(results)} joined records")
    except Exception as e:
        print(f"✗ Join operation failed: {e}")

def test_updates(db):
    """Test update operations"""
    print("\n=== Testing Update Operations ===")
    
    try:
        # Update a user's age
        db.update("users", {"id": 1}, {"age": 31})
        
        # Verify update
        updated_user = db.query("users").where("id", "=", 1).all()[0]
        if updated_user["age"] == 31:
            print("✓ Update operation successful")
        else:
            print("✗ Update operation failed: value not updated")
    except Exception as e:
        print(f"✗ Update operation failed: {e}")

def test_deletes(db):
    """Test delete operations"""
    print("\n=== Testing Delete Operations ===")
    
    try:
        # Delete a user
        db.delete("users", {"id": 3})
        
        # Verify delete
        remaining_users = db.select("users")
        if len(remaining_users) == 3:  # Originally 3 + 1 valid = 4, deleted 1 = 3
            print("✓ Delete operation successful")
        else:
            print(f"✗ Delete operation failed: expected 3 users, got {len(remaining_users)}")
    except Exception as e:
        print(f"✗ Delete operation failed: {e}")

def test_indexes(db):
    """Test index functionality"""
    print("\n=== Testing Index Functionality ===")
    
    try:
        # Create an index
        db.create_index("users", "age")
        print("✓ Index creation successful")
        
        # List indexes
        indexes = db.list_indexes("users")
        if "age" in indexes:
            print("✓ Index listing successful")
        else:
            print("✗ Index listing failed")
            
        # Drop index
        db.drop_index("users", "age")
        indexes = db.list_indexes("users")
        if "age" not in indexes:
            print("✓ Index deletion successful")
        else:
            print("✗ Index deletion failed")
    except Exception as e:
        print(f"✗ Index operations failed: {e}")

def test_transactions(db):
    """Test transaction functionality"""
    print("\n=== Testing Transaction Functionality ===")
    
    try:
        # Test successful transaction
        def successful_tx():
            db.insert("users", {"id": 10, "name": "TX User", "age": 25, "email": "tx@example.com"})
        
        db.transaction(successful_tx)
        print("✓ Successful transaction completed")
        
        # Test rollback transaction
        def failing_tx():
            db.insert("users", {"id": 11, "name": "Rollback User", "age": 26, "email": "rollback@example.com"})
            raise Exception("Simulated error")
        
        try:
            db.transaction(failing_tx)
            print("✗ Transaction should have failed")
        except Exception:
            # Verify rollback
            users = db.select("users")
            found = any(user["id"] == 11 for user in users)
            if not found:
                print("✓ Transaction rollback successful")
            else:
                print("✗ Transaction rollback failed")
    except Exception as e:
        print(f"✗ Transaction operations failed: {e}")

def test_edge_cases(db):
    """Test edge cases"""
    print("\n=== Testing Edge Cases ===")
    
    # Test inserting duplicate with different if_exists options
    try:
        user = {"id": 1, "name": "Duplicate User", "age": 27, "email": "dup@example.com"}
        
        # Test ignore
        db.insert("users", user, if_exists="ignore")
        print("✓ Insert with if_exists='ignore' successful")
        
        # Test replace
        user["age"] = 29
        db.insert("users", user, if_exists="replace")
        updated_user = db.query("users").where("id", "=", 1).all()[0]
        if updated_user["age"] == 29:
            print("✓ Insert with if_exists='replace' successful")
        else:
            print("✗ Insert with if_exists='replace' failed")
    except Exception as e:
        print(f"✗ Edge case testing failed: {e}")

def cleanup(db):
    """Clean up test data"""
    print("\n=== Cleaning Up ===")
    try:
        db.drop_table("users")
        db.drop_table("posts")
        print("✓ Cleanup completed")
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")

def main():
    """Run all tests"""
    print("Starting comprehensive PySimDB library testing...\n")
    
    # Run all tests
    db = test_basic_functionality()
    test_schema_validation(db)
    test_query_builder(db)
    test_joins(db)
    test_updates(db)
    test_deletes(db)
    test_indexes(db)
    test_transactions(db)
    test_edge_cases(db)
    
    # Clean up
    cleanup(db)
    
    print("\n=== Testing Complete ===")
    print("All PySimDB library features have been tested!")

if __name__ == "__main__":
    main()