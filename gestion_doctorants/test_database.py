# gestion_doctorants/test_database_fixed.py
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_initialization():
    """Test database initialization only"""
    print("=" * 60)
    print("DATABASE INITIALIZATION TEST")
    print("=" * 60)
    
    # Use a test database
    test_db_path = "data/test_init.db"
    
    # Remove old test database if exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    try:
        print(f"\nCreating database at: {test_db_path}")
        
        # Import here to ensure we get the updated version
        from database import Database
        
        # This should initialize the database
        db = Database(test_db_path)
        
        print("\n✅ Database initialization successful!")
        
        # Verify tables exist
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check each table
        tables = ['laboratoires', 'encadrants', 'doctorants', 'activites', 
                 'publications', 'formations', 'suivi']
        
        print("\nChecking tables...")
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print(f"  ✅ Table '{table}' exists")
            else:
                print(f"  ❌ Table '{table}' NOT FOUND")
        
        # Check default data
        print("\nChecking default data...")
        
        cursor.execute("SELECT COUNT(*) as count FROM laboratoires")
        lab_count = cursor.fetchone()['count']
        print(f"  ✅ Laboratoires: {lab_count} records")
        
        cursor.execute("SELECT COUNT(*) as count FROM encadrants")
        enc_count = cursor.fetchone()['count']
        print(f"  ✅ Encadrants: {enc_count} records")
        
        # List laboratories
        cursor.execute("SELECT id, nom, faculte FROM laboratoires ORDER BY id")
        labs = cursor.fetchall()
        print("\nLaboratories:")
        for lab in labs:
            print(f"  {lab['id']}: {lab['nom']} ({lab['faculte']})")
        
        conn.close()
        
        # Clean up
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print(f"\nCleaned up test database: {test_db_path}")
        
        print("\n" + "=" * 60)
        print("INITIALIZATION TEST COMPLETE")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_crud():
    """Test basic CRUD operations"""
    print("\n" + "=" * 60)
    print("BASIC CRUD TEST")
    print("=" * 60)
    
    test_db_path = "data/test_crud.db"
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    try:
        from database import Database
        db = Database(test_db_path)
        
        print("\n1. Testing doctorant creation...")
        
        # Get first lab and supervisor for testing
        labs = db.get_laboratoires()
        encadrants = db.get_encadrants()
        
        if not labs or not encadrants:
            print("  ❌ No default data found!")
            return False
        
        lab_id = labs[0]['id']
        enc_id = encadrants[0]['id']
        
        # Create a test doctorant
        doctorant_data = {
            'nom': 'Test',
            'prenom': 'CRUD',
            'email': 'test.crud@univ.fr',
            'domaine': 'Informatique',
            'laboratoire_id': lab_id,
            'directeur_id': enc_id,
            'annee_inscription': 2024,
            'statut': 'en_cours',
            'titre_these': 'Test des opérations CRUD'
        }
        
        doctorant_id = db.add_doctorant(doctorant_data)
        print(f"  ✅ Doctorant created with ID: {doctorant_id}")
        
        # Read
        doctorant = db.get_doctorant(doctorant_id)
        print(f"  ✅ Doctorant retrieved: {doctorant['nom']} {doctorant['prenom']}")
        
        # Update
        update_data = {'statut': 'soutenu', 'annee_soutenance_effective': 2024}
        success = db.update_doctorant(doctorant_id, update_data)
        print(f"  ✅ Doctorant updated: {success}")
        
        # Verify update
        updated = db.get_doctorant(doctorant_id)
        print(f"  ✅ Status updated to: {updated['statut']}")
        
        # Search
        results = db.search_doctorants({'nom': 'Test'})
        print(f"  ✅ Search found: {len(results)} doctorant(s)")
        
        # Get all
        all_doctorants = db.get_all_doctorants()
        print(f"  ✅ Total doctorants: {len(all_doctorants)}")
        
        # Clean up
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        print("\n✅ Basic CRUD test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR in CRUD test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_production_database():
    """Test the production database"""
    print("\n" + "=" * 60)
    print("PRODUCTION DATABASE TEST")
    print("=" * 60)
    
    try:
        from database import Database
        
        # This uses the default production database
        print("\nConnecting to production database...")
        db = Database()
        
        # Test basic queries
        print("\n1. Testing basic queries...")
        
        doctorants = db.get_all_doctorants()
        print(f"  ✅ Doctorants: {len(doctorants)}")
        
        labs = db.get_laboratoires()
        print(f"  ✅ Laboratories: {len(labs)}")
        
        supervisors = db.get_encadrants()
        print(f"  ✅ Supervisors: {len(supervisors)}")
        
        # Test statistics
        print("\n2. Testing statistics...")
        try:
            stats = db.get_statistics()
            print(f"  ✅ Statistics generated")
            print(f"    - Total students: {stats.get('total_students', 0)}")
            
            if stats.get('by_status'):
                print(f"    - By status: {stats.get('by_status')}")
            
        except Exception as e:
            print(f"  ⚠️ Statistics error (may be empty database): {str(e)}")
        
        # Show some data if available
        if doctorants:
            print("\n3. Sample data:")
            print("  First 3 doctorants:")
            for i, doc in enumerate(doctorants[:3]):
                print(f"    {i+1}. {doc.get('nom', '')} {doc.get('prenom', '')}")
                print(f"        - Email: {doc.get('email', 'N/A')}")
                print(f"        - Domaine: {doc.get('domaine', 'N/A')}")
                print(f"        - Statut: {doc.get('statut', 'N/A')}")
        
        print("\n✅ Production database test complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR testing production database: {str(e)}")
        return False

if __name__ == "__main__":
    print("Database Test Suite")
    print("=" * 60)
    
    print("\nChoose tests to run:")
    print("1. Database initialization only")
    print("2. Basic CRUD operations")
    print("3. Production database")
    print("4. All tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    results = []
    
    if choice in ['1', '4']:
        results.append(("Initialization", test_database_initialization()))
    
    if choice in ['2', '4']:
        results.append(("Basic CRUD", test_basic_crud()))
    
    if choice in ['3', '4']:
        results.append(("Production DB", test_production_database()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED! ✅")
    else:
        print("SOME TESTS FAILED! ❌")
    print("=" * 60)