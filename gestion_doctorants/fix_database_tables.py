# gestion_doctorants/fix_database_tables.py
import sqlite3
import os
import sys

def check_and_fix_database():
    """Check database structure and fix missing columns"""
    print("=" * 70)
    print("DATABASE STRUCTURE FIX")
    print("=" * 70)
    
    db_path = "data/database.db"
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        print("Creating new database...")
        from database import Database
        db = Database()
        print("✅ New database created with correct structure")
        return True
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Checking database: {db_path}")
    
    # Check doctorants table structure
    print("\n1. Checking 'doctorants' table...")
    cursor.execute("PRAGMA table_info(doctorants)")
    columns = {row[1]: row for row in cursor.fetchall()}
    
    # List current columns
    print("   Current columns:")
    for col_name in sorted(columns.keys()):
        col_info = columns[col_name]
        print(f"     • {col_name} ({col_info[2]})")
    
    # Columns that should exist
    required_columns = ['adresse', 'ville', 'code_postal']
    missing_columns = []
    
    for col in required_columns:
        if col not in columns:
            missing_columns.append(col)
    
    if missing_columns:
        print(f"\n   ❌ Missing columns: {missing_columns}")
        
        response = input(f"\nAdd missing columns to database? (y/n): ").lower()
        if response == 'y':
            print("\n   Adding missing columns...")
            
            try:
                for col in missing_columns:
                    if col == 'adresse':
                        cursor.execute("ALTER TABLE doctorants ADD COLUMN adresse TEXT")
                        print(f"     ✅ Added column: adresse")
                    elif col == 'ville':
                        cursor.execute("ALTER TABLE doctorants ADD COLUMN ville TEXT")
                        print(f"     ✅ Added column: ville")
                    elif col == 'code_postal':
                        cursor.execute("ALTER TABLE doctorants ADD COLUMN code_postal TEXT")
                        print(f"     ✅ Added column: code_postal")
                
                conn.commit()
                print("\n   ✅ Database structure updated successfully!")
                
            except Exception as e:
                print(f"\n   ❌ Error updating database: {str(e)}")
                conn.rollback()
                return False
        else:
            print("\n   Database not modified.")
            return False
    else:
        print("\n   ✅ All required columns exist!")
    
    # Check other tables
    print("\n2. Checking other tables...")
    
    tables_to_check = ['laboratoires', 'encadrants', 'activites', 'publications', 'formations', 'suivi']
    
    for table in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {table}: {count} records")
        except:
            print(f"   ⚠️ {table}: Error or table doesn't exist")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("DATABASE CHECK COMPLETE")
    print("=" * 70)
    
    return True

def recreate_database():
    """Create a fresh database with correct structure"""
    print("\n" + "=" * 70)
    print("CREATING FRESH DATABASE")
    print("=" * 70)
    
    db_path = "data/database.db"
    backup_path = "data/database_backup.db"
    
    # Backup existing database if it exists
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Existing database backed up to: {backup_path}")
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ Removed old database")
    
    # Create new database
    try:
        from database import Database
        db = Database()
        
        print("✅ New database created with correct structure")
        
        # Verify structure
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(doctorants)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print("\nNew 'doctorants' table columns:")
        for col in sorted(columns):
            print(f"  • {col}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating new database: {str(e)}")
        
        # Restore backup if creation failed
        if os.path.exists(backup_path) and not os.path.exists(db_path):
            shutil.copy2(backup_path, db_path)
            print(f"✅ Restored database from backup")
        
        return False

def test_database_fix():
    """Test if database is working after fix"""
    print("\n" + "=" * 70)
    print("TESTING DATABASE")
    print("=" * 70)
    
    try:
        from database import Database
        
        db = Database()
        print("✅ Database connection successful")
        
        # Try to add a doctorant
        test_data = {
            'nom': 'Test',
            'prenom': 'Fix',
            'email': 'test.fix@univ.fr',
            'domaine': 'Test',
            'laboratoire_id': 1,
            'directeur_id': 1,
            'annee_inscription': 2024,
            'statut': 'en_cours',
            'titre_these': 'Test de la base de données',
            'adresse': '123 Test Street',
            'ville': 'Test City',
            'code_postal': '12345'
        }
        
        doctorant_id = db.add_doctorant(test_data)
        print(f"✅ Doctorant added successfully (ID: {doctorant_id})")
        
        # Retrieve doctorant
        doctorant = db.get_doctorant(doctorant_id)
        print(f"✅ Doctorant retrieved: {doctorant['nom']} {doctorant['prenom']}")
        print(f"   Address: {doctorant.get('adresse', 'N/A')}")
        print(f"   City: {doctorant.get('ville', 'N/A')}")
        print(f"   Postal code: {doctorant.get('code_postal', 'N/A')}")
        
        # Clean up test data
        db.delete_doctorant(doctorant_id)
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Database Fix Utility")
    print("\nChoose an option:")
    print("1. Check and fix existing database")
    print("2. Create fresh database (recommended)")
    print("3. Test database functionality")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        success = check_and_fix_database()
    elif choice == '2':
        success = recreate_database()
    elif choice == '3':
        success = test_database_fix()
    else:
        print("Invalid choice")
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✅ OPERATION SUCCESSFUL!")
        print("\nNext steps:")
        print("1. Run: python add_sample_data.py")
        print("2. Run: python main.py")
    else:
        print("❌ OPERATION FAILED!")
    print("=" * 70)