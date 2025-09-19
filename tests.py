import unittest
from pysimdb import JsonDatabase, TableSchema, SchemaError
import os
import shutil

class TestPySimDB(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data"
        os.makedirs(self.test_dir, exist_ok=True)
        self.db = JsonDatabase(self.test_dir)
        
        # Create test schemas
        self.user_schema = TableSchema({
            "id": int,
            "name": str,
            "age": int,
            "email": str
        }, primary_key="id")
        
        self.post_schema = TableSchema({
            "id": int,
            "user_id": int,
            "title": str,
            "content": str
        }, primary_key="id")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_table(self):
        self.db.create_table("users", self.user_schema)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "users.json")))
        self.assertIn("users", self.db.schemas)

    def test_insert_and_select(self):
        self.db.create_table("users", self.user_schema)
        test_user = {
            "id": 1,
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        self.db.insert("users", test_user)
        users = self.db.select("users")
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], test_user)

    def test_schema_validation(self):
        self.db.create_table("users", self.user_schema)
        invalid_user = {
            "id": "1",  # Should be int, not str
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        with self.assertRaises(SchemaError):
            self.db.insert("users", invalid_user)

    def test_primary_key_constraint(self):
        self.db.create_table("users", self.user_schema)
        user1 = {"id": 1, "name": "John", "age": 30, "email": "john@example.com"}
        user2 = {"id": 1, "name": "Jane", "age": 25, "email": "jane@example.com"}
        
        self.db.insert("users", user1)
        with self.assertRaises(ValueError):
            self.db.insert("users", user2)

    def test_query_builder(self):
        self.db.create_table("users", self.user_schema)
        users = [
            {"id": 1, "name": "John", "age": 30, "email": "john@example.com"},
            {"id": 2, "name": "Jane", "age": 25, "email": "jane@example.com"},
            {"id": 3, "name": "Bob", "age": 35, "email": "bob@example.com"}
        ]
        for user in users:
            self.db.insert("users", user)

        # Test where clause
        results = self.db.query("users").where("age", ">", 25).all()
        self.assertEqual(len(results), 2)

        # Test order by
        results = self.db.query("users").order_by("age").all()
        self.assertEqual(results[0]["age"], 25)
        self.assertEqual(results[-1]["age"], 35)

        # Test limit and offset
        results = self.db.query("users").order_by("id").limit(2).all()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], 1)

    def test_join_operations(self):
        self.db.create_table("users", self.user_schema)
        self.db.create_table("posts", self.post_schema)

        user = {"id": 1, "name": "John", "age": 30, "email": "john@example.com"}
        self.db.insert("users", user)

        posts = [
            {"id": 1, "user_id": 1, "title": "Post 1", "content": "Content 1"},
            {"id": 2, "user_id": 1, "title": "Post 2", "content": "Content 2"}
        ]
        for post in posts:
            self.db.insert("posts", post)

        results = (
            self.db.query("users")
            .join("posts", "id", "user_id")
            .where("name", "=", "John")
            .all()
        )
        self.assertEqual(len(results), 2)
        self.assertIn("title", results[0])
        self.assertIn("content", results[0])

    def test_update(self):
        self.db.create_table("users", self.user_schema)
        user = {"id": 1, "name": "John", "age": 30, "email": "john@example.com"}
        self.db.insert("users", user)
        
        self.db.update("users", {"id": 1}, {"age": 31})
        updated_user = self.db.select("users")[0]
        self.assertEqual(updated_user["age"], 31)

    def test_if_exists_options(self):
        self.db.create_table("users", self.user_schema)
        user = {"id": 1, "name": "John", "age": 30, "email": "john@example.com"}
        
        # Test if_exists="ignore"
        self.db.insert("users", user)
        self.db.insert("users", user, if_exists="ignore")
        self.assertEqual(len(self.db.select("users")), 1)
        
        # Test if_exists="replace"
        updated_user = dict(user)
        updated_user["age"] = 31
        self.db.insert("users", updated_user, if_exists="replace")
        self.assertEqual(len(self.db.select("users")), 1)
        self.assertEqual(self.db.select("users")[0]["age"], 31)

    def test_drop_table(self):
        self.db.create_table("users", self.user_schema)
        self.db.drop_table("users")
        self.assertNotIn("users", self.db.schemas)
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, "users.json")))

if __name__ == "__main__":
    unittest.main()
