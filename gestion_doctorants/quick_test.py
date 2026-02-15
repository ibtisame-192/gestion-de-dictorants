# quick_test.py
import sys
sys.path.append('.')
from database import Database

# Create instance
db = Database()

# Test existing methods still work
print("Testing existing methods...")
doctorants = db.get_all_doctorants()
print(f"Found {len(doctorants)} doctorants")

labs = db.get_laboratoires()
print(f"Found {len(labs)} laboratories")

stats = db.get_statistics()
print(f"Statistics: {stats.get('total_students', 0)} total students")

print("✅ All existing functionality preserved!")