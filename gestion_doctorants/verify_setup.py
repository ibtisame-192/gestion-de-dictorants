# gestion_doctorants/verify_setup.py
import os
import sys

print("=" * 60)
print("GESTION DOCTORANTS - SETUP VERIFICATION")
print("=" * 60)

# Check current directory
current_dir = os.getcwd()
print(f"\n1. Current directory: {current_dir}")

# List files
print("\n2. Files in directory:")
files = os.listdir()
for file in sorted(files):
    if os.path.isfile(file):
        print(f"   📄 {file}")
    else:
        print(f"   📁 {file}/")

# Check for required files
required_files = ['database.py', 'main.py']
print("\n3. Checking required files:")
for file in required_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} - MISSING!")

# Check for data directory
print("\n4. Checking directory structure:")
if os.path.exists("data"):
    print("   ✅ data/ directory exists")
else:
    print("   ⚠️ data/ directory doesn't exist (will be created)")

if os.path.exists("interface"):
    print("   ✅ interface/ directory exists")
else:
    print("   ⚠️ interface/ directory doesn't exist")

# Try to import database
print("\n5. Testing database import:")
try:
    from database import Database
    print("   ✅ Database class imported successfully")
    
    # Test database creation
    print("   Testing database initialization...")
    db = Database("data/test_verify.db")
    print("   ✅ Database initialized successfully")
    
    # Remove test database
    if os.path.exists("data/test_verify.db"):
        os.remove("data/test_verify.db")
    
except Exception as e:
    print(f"   ❌ Error importing database: {str(e)}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)