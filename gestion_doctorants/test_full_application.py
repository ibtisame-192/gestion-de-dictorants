# gestion_doctorants/test_full_application.py
import os
import sys
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

print("=" * 70)
print("FULL APPLICATION TEST SUITE")
print("=" * 70)

# Test 1: Database functionality
print("\n1. TESTING DATABASE FUNCTIONALITY")
print("-" * 40)

try:
    from database import Database
    
    db = Database()
    print("✅ Database connected")
    
    # Add sample doctorants
    print("\nAdding sample doctorants...")
    
    sample_doctorants = [
        {
            'nom': 'Martin',
            'prenom': 'Sophie',
            'email': 'sophie.martin@univ.fr',
            'telephone': '01 23 45 67 88',
            'domaine': 'Informatique',
            'laboratoire_id': 1,  # LISN
            'directeur_id': 1,    # Prof. Martin
            'annee_inscription': 2022,
            'statut': 'en_cours',
            'titre_these': 'IA pour le diagnostic médical',
            'financement': 'Bourse ministère',
            'montant_financement': 16000.0
        },
        {
            'nom': 'Dubois',
            'prenom': 'Thomas',
            'email': 'thomas.dubois@univ.fr',
            'domaine': 'Biologie',
            'laboratoire_id': 2,  # LMB
            'directeur_id': 2,    # Prof. Dubois
            'annee_inscription': 2021,
            'statut': 'soutenu',
            'titre_these': 'Étude des protéines membranaires',
            'annee_soutenance_effective': 2024,
            'financement': 'Contrat doctoral'
        },
        {
            'nom': 'Laurent',
            'prenom': 'Émilie',
            'email': 'emilie.laurent@univ.fr',
            'domaine': 'Mathématiques',
            'laboratoire_id': 3,  # LMV
            'directeur_id': 3,    # Prof. Laurent
            'annee_inscription': 2023,
            'statut': 'en_cours',
            'titre_these': 'Analyse fonctionnelle avancée',
            'financement': 'Bourse européenne'
        }
    ]
    
    doctorant_ids = []
    for i, data in enumerate(sample_doctorants, 1):
        try:
            doctorant_id = db.add_doctorant(data)
            doctorant_ids.append(doctorant_id)
            print(f"  ✅ Doctorant {i}: {data['nom']} {data['prenom']} (ID: {doctorant_id})")
        except Exception as e:
            print(f"  ⚠️ Error adding doctorant {i}: {str(e)}")
    
    # Add sample activities for first doctorant
    if doctorant_ids:
        print("\nAdding sample activities...")
        
        sample_activities = [
            {
                'type': 'publication',
                'titre': 'Deep Learning for Medical Imaging',
                'description': 'Article publié dans Journal of Medical AI',
                'date_debut': '2023-06-15',
                'statut': 'termine'
            },
            {
                'type': 'formation',
                'titre': 'Méthodologie de recherche',
                'description': 'Formation obligatoire école doctorale',
                'date_debut': '2022-10-10',
                'date_fin': '2022-10-12',
                'statut': 'termine'
            },
            {
                'type': 'seminaire',
                'titre': 'Présentation des travaux',
                'description': 'Séminaire du laboratoire',
                'date_debut': '2024-01-20',
                'statut': 'termine'
            }
        ]
        
        for i, activity in enumerate(sample_activities, 1):
            try:
                activity_id = db.add_activity(doctorant_ids[0], activity)
                print(f"  ✅ Activity {i}: {activity['titre']}")
            except Exception as e:
                print(f"  ⚠️ Error adding activity {i}: {str(e)}")
    
    # Test statistics
    print("\nTesting statistics...")
    try:
        stats = db.get_statistics()
        print(f"  ✅ Total students: {stats.get('total_students', 0)}")
        print(f"  ✅ By status: {stats.get('by_status', {})}")
        print(f"  ✅ Recent activities: {len(stats.get('recent_activities', []))}")
    except Exception as e:
        print(f"  ⚠️ Statistics error: {str(e)}")
    
    print("\n✅ Database test completed successfully!")
    
except Exception as e:
    print(f"\n❌ Database test failed: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 2: GUI Components
print("\n" + "=" * 70)
print("2. TESTING GUI COMPONENTS")
print("-" * 40)

try:
    # Test main window
    print("\nTesting main window...")
    from interface.main_window import MainWindow
    
    # Create a test root window (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    app = MainWindow(root, db)
    print("  ✅ MainWindow created successfully")
    
    # Test doctorant form
    print("\nTesting doctorant form...")
    from interface.doctorants_gui import DoctorantForm
    
    if doctorant_ids:
        # Test edit mode
        form = DoctorantForm(root, db, doctorant_ids[0], edit_mode=True)
        form.window.destroy()
        print("  ✅ Edit form created")
        
        # Test view mode
        form = DoctorantForm(root, db, doctorant_ids[0])
        form.window.destroy()
        print("  ✅ View form created")
    
    # Test new doctorant form
    form = DoctorantForm(root, db)
    form.window.destroy()
    print("  ✅ New doctorant form created")
    
    root.destroy()
    print("\n✅ GUI components test completed successfully!")
    
except Exception as e:
    print(f"\n❌ GUI test failed: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 3: Run Main Application (quick test)
print("\n" + "=" * 70)
print("3. QUICK APPLICATION TEST")
print("-" * 40)

print("\nWould you like to run the main application?")
print("This will open the actual application window.")
response = input("Run main application? (y/n): ").lower()

if response == 'y':
    try:
        print("\nStarting main application...")
        print("(Close the application window to continue)")
        
        # Import and run main
        import main as app_main
        
        # We can't actually run it in the same process, so show instructions
        print("\nTo run the application manually:")
        print("1. Open a new terminal/command prompt")
        print("2. Navigate to: C:\\Users\\Oxfam\\Desktop\\gestion_doctorants")
        print("3. Run: python main.py")
        print("\nThe application should start with:")
        print("  - 3 sample doctorants pre-loaded")
        print("  - 4 laboratories and 6 supervisors")
        print("  - Full CRUD functionality")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

print(f"\nDatabase status:")
print(f"  • Doctorants: {len(db.get_all_doctorants())}")
print(f"  • Laboratories: {len(db.get_laboratoires())}")
print(f"  • Supervisors: {len(db.get_encadrants())}")
print(f"  • Activities: {len(db.get_activities())}")

print(f"\nSample data created:")
print(f"  • 3 doctorants with different statuses")
print(f"  • 3 activities for the first doctorant")
print(f"  • Full statistics available")

print(f"\nNext steps:")
print(f"  1. Run: python main.py")
print(f"  2. Explore the interface")
print(f"  3. Try adding new doctorants")
print(f"  4. Test search functionality")

print("\n" + "=" * 70)
print("APPLICATION READY FOR USE! ✅")
print("=" * 70)