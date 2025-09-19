"""
Test script to verify the package can be imported and used correctly.
"""
from pysimdb import JsonDatabase, TableSchema, SchemaError

def test_package():
    # Test basic functionality
    db = JsonDatabase("test_data")
    
    # Define schema
    user_schema = TableSchema({
        "id": int,
        "name": str,
        "age": int
    }, primary_key="id")
    
    # Create table
    db.create_table("users", user_schema)
    
    # Insert data
    user = {"id": 1, "name": "Test User", "age": 25}
    db.insert("users", user)
    
    # Query data
    users = db.query("users").where("age", ">", 20).all()
    
    # Verify
    assert len(users) == 1
    assert users[0]["name"] == "Test User"
    
    # Cleanup
    db.drop_table("users")
    
    print("Package test passed successfully!")

if __name__ == "__main__":
    test_package()