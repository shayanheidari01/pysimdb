from pysimdb import JsonDatabase, TableSchema, QueryBuilder

# --- راه‌اندازی دیتابیس ---
db = JsonDatabase("data")

# --- تعریف schema جدول users ---
user_schema = TableSchema({"id": int, "name": str, "age": int}, primary_key="id")
db.drop_table("users")
db.create_table("users", user_schema)

# --- تعریف schema جدول posts ---
post_schema = TableSchema({"id": int, "user_id": int, "title": str}, primary_key="id")
db.drop_table("posts")
db.create_table("posts", post_schema)

# --- درج رکوردهای اولیه ---
users = [
    {"id": 1, "name": "Ali", "age": 25},
    {"id": 2, "name": "Sara", "age": 30},
    {"id": 3, "name": "Reza", "age": 28},
    {"id": 4, "name": "Nima", "age": 35},
]

posts = [
    {"id": 1, "user_id": 1, "title": "Hello World"},
    {"id": 2, "user_id": 2, "title": "Python Rocks"},
    {"id": 3, "user_id": 3, "title": "JSON Magic"},
    {"id": 4, "user_id": 4, "title": "Mini SQLite"},
]

for u in users:
    db.insert("users", u)

existing = db.select("users")
if len(existing) < 10:
    for i in range(10, 100):
        db.insert("users", {"id": i, "name": f"user {i}", "age": 22})

for p in posts:
    db.insert("posts", p)

# --- تست Select ساده ---
print("\n--- All Users ---")
for u in db.select("users"):
    print(u)

# --- تست Update ---
db.update("users", {"id": 2}, {"age": 31})
print("\n--- After Update (Sara age -> 31) ---")
for u in db.select("users"):
    print(u)

# --- تست Delete ---
db.delete("users", {"id": 1})
print("\n--- After Delete (id=1 removed) ---")
for u in db.select("users"):
    print(u)

# --- تست Query Builder با join و filter ---
print("\n--- Query Builder Join & Filter ---")
q = QueryBuilder(db, "users")
results = (
    q.join("posts", base_field="id", other_field="user_id")
     .where("age", ">", 28)
     .order_by("age", desc=True)
     .select("name", "title")
     .all()
)
for r in results:
    print(r)

# --- تست Limit و Offset ---
print("\n--- Limit & Offset ---")
q2 = QueryBuilder(db, "users")
results2 = (
    q2.order_by("age")
       .limit(2)
       .offset(1)
       .select("id", "name")
       .all()
)
for r in results2:
    print(r)

# --- تست Transaction و Rollback ---
print("\n--- Transaction & Rollback ---")
def tx_ops():
    db.insert("users", {"id": 5, "name": "Hassan", "age": 22})
    db.insert("posts", {"id": 5, "user_id": 5, "title": "Rollback Test"})
    raise Exception("Simulated Error for Rollback")

try:
    db.transaction(tx_ops)
except Exception as e:
    print("Transaction rolled back:", e)

print("\n--- Users after Transaction ---")
for u in db.select("users"):
    print(u)

print("\n--- Posts after Transaction ---")
for p in db.select("posts"):
    print(p)

# --- تست Schema Validation Error ---
print("\n--- Schema Validation Error ---")
try:
    db.insert("users", {"id": 6, "name": "Lara"})  # missing 'age'
except Exception as e:
    print("Error:", e)
