# gestion_doctorants/debug_application.py
import tkinter as tk
from tkinter import messagebox
import sys
import traceback

def debug_main():
    """Debug the main application"""
    print("=" * 70)
    print("DEBUGGING APPLICATION STARTUP")
    print("=" * 70)
    
    try:
        # Test database
        print("\n1. Testing database...")
        from database import Database
        db = Database()
        print("   ✅ Database OK")
        
        # Check for doctorants
        doctorants = db.get_all_doctorants()
        print(f"   Doctorants in database: {len(doctorants)}")
        
        if len(doctorants) == 0:
            print("   ⚠️ No doctorants found. Adding sample data...")
            # Add a sample doctorant
            sample_data = {
                'nom': 'Demo',
                'prenom': 'Doctorant',
                'email': 'demo.doctorant@univ.fr',
                'domaine': 'Informatique',
                'laboratoire_id': 1,
                'directeur_id': 1,
                'annee_inscription': 2024,
                'statut': 'en_cours',
                'titre_these': 'Démonstration du système'
            }
            doctorant_id = db.add_doctorant(sample_data)
            print(f"   ✅ Added demo doctorant (ID: {doctorant_id})")
        
        # Test main window
        print("\n2. Testing main window creation...")
        from interface.main_window import MainWindow
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Keep it hidden for now
        
        print("   Creating MainWindow...")
        app = MainWindow(root, db)
        print("   ✅ MainWindow created successfully")
        
        # Test if window is visible
        print(f"   Window geometry: {root.winfo_geometry()}")
        print(f"   Window title: {root.title()}")
        
        # Ask if we should show the window
        response = input("\nShow application window? (y/n): ").lower()
        if response == 'y':
            print("\nShowing application window...")
            print("(Close the window to continue)")
            root.deiconify()  # Show the window
            root.mainloop()
        else:
            root.destroy()
            print("\nWindow not shown (destroyed)")
        
        print("\n✅ Application debugging complete!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        
        # Try to get more specific error
        error_type = type(e).__name__
        if error_type == 'ModuleNotFoundError':
            print(f"\nMissing module: {str(e)}")
            print("Make sure all required files are in the interface/ directory.")
        elif error_type == 'AttributeError':
            print(f"\nAttribute error in: {str(e)}")
            print("Check that all methods are defined in the classes.")
        
        return False
    
    return True

if __name__ == "__main__":
    success = debug_main()
    
    print("\n" + "=" * 70)
    if success:
        print("DEBUGGING SUCCESSFUL! 🎉")
        print("\nNext: Run 'python main.py' to start the application.")
    else:
        print("DEBUGGING FAILED! ❌")
        print("\nPlease check the error messages above.")
    print("=" * 70)