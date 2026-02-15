# gestion_doctorants/check_database.py
import os

def check_database_file():
    """Check if database.py has the create_tables method"""
    db_file = "database.py"
    
    if not os.path.exists(db_file):
        print(f"❌ {db_file} not found!")
        return False
    
    with open(db_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Checking {db_file}...")
    print("-" * 60)
    
    # Check for key methods
    methods_to_check = [
        'def create_tables',
        'def insert_default_data',
        'def init_database',
        'class Database:'
    ]
    
    found_methods = []
    for method in methods_to_check:
        if method in content:
            found_methods.append(method)
            print(f"✅ Found: {method}")
        else:
            print(f"❌ Missing: {method}")
    
    print("-" * 60)
    
    # Check table creations
    tables_to_check = [
        'CREATE TABLE IF NOT EXISTS laboratoires',
        'CREATE TABLE IF NOT EXISTS encadrants',
        'CREATE TABLE IF NOT EXISTS doctorants',
        'CREATE TABLE IF NOT EXISTS activites'
    ]
    
    print("\nChecking table creation statements...")
    for table in tables_to_check:
        if table in content:
            print(f"✅ Found: {table}")
        else:
            print(f"❌ Missing: {table}")
    
    return len(found_methods) == len(methods_to_check)

if __name__ == "__main__":
    print("Database File Check")
    print("=" * 60)
    
    success = check_database_file()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Database file appears to be complete!")
    else:
        print("❌ Database file is missing some methods!")
        print("\nPlease replace your database.py with the complete version.")