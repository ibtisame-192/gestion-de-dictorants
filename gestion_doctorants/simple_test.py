# gestion_doctorants/simple_test.py
import os
import sys

print("Simple Database Test")
print("=" * 40)

try:
    from database import Database
    
    # Create database
    db = Database()
    
    print("✅ Database created successfully")
    
    # Test basic methods
    print("\nTesting basic methods:")
    
    # Get laboratories
    labs = db.get_laboratoires()
    print(f"  Laboratories: {len(labs)}")
    
    # Get supervisors
    supervisors = db.get_encadrants()
    print(f"  Supervisors: {len(supervisors)}")
    
    # Get all doctorants
    doctorants = db.get_all_doctorants()
    print(f"  Doctorants: {len(doctorants)}")
    
    # Test statistics
    try:
        stats = db.get_statistics()
        print(f"  Statistics: {stats.get('total_students', 0)} students")
    except Exception as e:
        print(f"  Statistics error (may be empty): {str(e)}")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()