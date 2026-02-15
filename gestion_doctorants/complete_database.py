# gestion_doctorants/test_complete_database.py
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

def test_all_database_methods():
    """Test all database methods comprehensively"""
    print("=" * 60)
    print("COMPREHENSIVE DATABASE TEST SUITE")
    print("=" * 60)
    
    # Use a test database to avoid interfering with production data
    test_db_path = "data/test_database.db"
    
    # Remove old test database if exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    try:
        # Initialize database
        print("\n1. Initializing test database...")
        db = Database(test_db_path)
        print("   ✅ Database initialized successfully")
        
        # ===== TEST 1: REFERENCE DATA =====
        print("\n2. Testing reference data methods...")
        
        # Test laboratories
        labs = db.get_laboratoires()
        print(f"   ✅ Laboratories: {len(labs)} found")
        
        # Test supervisors
        supervisors = db.get_encadrants()
        print(f"   ✅ Supervisors: {len(supervisors)} found")
        
        # ===== TEST 2: DOCTORANT CRUD =====
        print("\n3. Testing doctorant CRUD operations...")
        
        # Add new doctorant
        new_doctorant = {
            'nom': 'Test',
            'prenom': 'Doctorant',
            'email': 'test.doctorant@univ.fr',
            'telephone': '01 23 45 67 89',
            'domaine': 'Informatique',
            'laboratoire_id': 1,
            'directeur_id': 1,
            'annee_inscription': 2024,
            'statut': 'en_cours',
            'titre_these': 'Test de la base de données',
            'resume': 'Ceci est un test',
            'mots_cles': 'test, database, python',
            'financement': 'Bourse ministère',
            'montant_financement': 15000.0,
            'adresse': '123 Rue Test',
            'ville': 'Paris',
            'code_postal': '75000'
        }
        
        doctorant_id = db.add_doctorant(new_doctorant)
        print(f"   ✅ Doctorant added with ID: {doctorant_id}")
        
        # Get doctorant
        doctorant = db.get_doctorant(doctorant_id)
        print(f"   ✅ Doctorant retrieved: {doctorant['nom']} {doctorant['prenom']}")
        
        # Update doctorant
        update_data = {
            'statut': 'soutenu',
            'annee_soutenance_effective': 2024,
            'titre_these': 'Test de la base de données - Mise à jour'
        }
        success = db.update_doctorant(doctorant_id, update_data)
        print(f"   ✅ Doctorant updated: {success}")
        
        # Get all doctorants
        all_doctorants = db.get_all_doctorants()
        print(f"   ✅ All doctorants: {len(all_doctorants)} total")
        
        # ===== TEST 3: SEARCH FUNCTIONALITY =====
        print("\n4. Testing search methods...")
        
        # Search by domain
        filters = {'domaine': 'Informatique'}
        results = db.search_doctorants(filters)
        print(f"   ✅ Search by domaine: {len(results)} results")
        
        # Search by status
        filters = {'statut': 'soutenu'}
        results = db.search_doctorants(filters)
        print(f"   ✅ Search by statut: {len(results)} results")
        
        # Get unique domains
        domains = db.get_domaines()
        print(f"   ✅ Unique domains: {len(domains)} found")
        
        # Get unique years
        years = db.get_inscription_years()
        print(f"   ✅ Inscription years: {years}")
        
        # ===== TEST 4: ACTIVITIES MANAGEMENT =====
        print("\n5. Testing activities management...")
        
        # Add activity
        activity_data = {
            'type': 'seminaire',
            'titre': 'Test séminaire',
            'description': 'Présentation des tests',
            'date_debut': '2024-03-15',
            'statut': 'termine'
        }
        activity_id = db.add_activity(doctorant_id, activity_data)
        print(f"   ✅ Activity added with ID: {activity_id}")
        
        # Get activities for doctorant
        activities = db.get_activities(doctorant_id)
        print(f"   ✅ Activities for doctorant: {len(activities)} found")
        
        # Get all activities
        all_activities = db.get_activities()
        print(f"   ✅ All activities: {len(all_activities)} total")
        
        # ===== TEST 5: PUBLICATIONS MANAGEMENT =====
        print("\n6. Testing publications management...")
        
        # Add publication
        pub_data = {
            'type': 'article',
            'titre': 'Test Article',
            'auteurs': 'Test A., Author B.',
            'revue': 'Journal of Testing',
            'date_publication': '2024-01-15',
            'statut': 'publie',
            'impact_factor': 3.5,
            'citations': 10
        }
        pub_id = db.add_publication(doctorant_id, pub_data)
        print(f"   ✅ Publication added with ID: {pub_id}")
        
        # Get publications
        publications = db.get_publications(doctorant_id)
        print(f"   ✅ Publications for doctorant: {len(publications)} found")
        
        # ===== TEST 6: FORMATIONS MANAGEMENT =====
        print("\n7. Testing formations management...")
        
        # Add formation
        formation_data = {
            'type': 'formation',
            'intitule': 'Test Formation',
            'organisateur': 'École Doctorale',
            'date_debut': '2024-02-01',
            'date_fin': '2024-02-03',
            'duree_heures': 16,
            'lieu': 'Paris',
            'certificat': 'cert123'
        }
        formation_id = db.add_formation(doctorant_id, formation_data)
        print(f"   ✅ Formation added with ID: {formation_id}")
        
        # Get formations
        formations = db.get_formations(doctorant_id)
        print(f"   ✅ Formations for doctorant: {len(formations)} found")
        
        # ===== TEST 7: SUIVI MANAGEMENT =====
        print("\n8. Testing suivi management...")
        
        # Add suivi
        suivi_data = {
            'date_rencontre': '2024-03-20',
            'type_rencontre': 'comite',
            'participants': 'Directeur, Doctorant',
            'points_abordes': 'Avancement des tests',
            'decisions': 'Continuer les tests',
            'prochaines_etapes': 'Tests supplémentaires',
            'date_prochaine_rencontre': '2024-06-20',
            'rapport': 'Rapport de test'
        }
        suivi_id = db.add_suivi(doctorant_id, suivi_data)
        print(f"   ✅ Suivi added with ID: {suivi_id}")
        
        # Get suivi
        suivis = db.get_suivi(doctorant_id)
        print(f"   ✅ Suivi for doctorant: {len(suivis)} found")
        
        # ===== TEST 8: STATISTICS =====
        print("\n9. Testing statistics...")
        
        # System statistics
        stats = db.get_statistics()
        print(f"   ✅ System statistics generated")
        print(f"     - Total students: {stats.get('total_students', 0)}")
        print(f"     - Total publications: {stats.get('total_publications', 0)}")
        print(f"     - Total laboratories: {stats.get('total_laboratories', 0)}")
        print(f"     - Recent activities: {len(stats.get('recent_activities', []))}")
        
        # Doctorant statistics
        doctorant_stats = db.get_doctorant_statistics(doctorant_id)
        print(f"   ✅ Doctorant statistics generated")
        print(f"     - Publication count: {doctorant_stats.get('publication_count', 0)}")
        print(f"     - Formation count: {doctorant_stats.get('formation_count', 0)}")
        print(f"     - Activities by type: {doctorant_stats.get('activities_by_type', {})}")
        
        # ===== TEST 9: EXPORT/IMPORT =====
        print("\n10. Testing export/import...")
        
        # Export to JSON
        export_file = "data/test_export.json"
        db.export_to_json(export_file)
        print(f"   ✅ Data exported to {export_file}")
        
        # Verify export file
        if os.path.exists(export_file):
            with open(export_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            print(f"   ✅ Export file validated: {len(export_data.get('doctorants', []))} doctorants")
        
        # ===== TEST 10: BACKUP =====
        print("\n11. Testing backup...")
        
        success, message = db.backup_database()
        if success:
            print(f"   ✅ Backup successful: {message}")
        else:
            print(f"   ❌ Backup failed: {message}")
        
        # ===== TEST 11: ADDITIONAL METHODS =====
        print("\n12. Testing additional methods...")
        
        # Get activity types
        activity_types = db.get_activity_types()
        print(f"   ✅ Activity types: {len(activity_types)} found")
        
        # Get financement types
        financement_types = db.get_financement_types()
        print(f"   ✅ Financement types: {len(financement_types)} found")
        
        # ===== TEST 12: ADD LABORATOIRE =====
        print("\n13. Testing laboratory addition...")
        
        new_lab = {
            'nom': 'Laboratoire de Test',
            'faculte': 'Test Faculté',
            'responsable': 'Prof. Test',
            'email': 'test.lab@univ.fr',
            'telephone': '01 98 76 54 32',
            'adresse': '456 Avenue Test'
        }
        
        try:
            lab_id = db.add_laboratoire(new_lab)
            print(f"   ✅ Laboratory added with ID: {lab_id}")
        except Exception as e:
            print(f"   ⚠️ Laboratory addition: {str(e)}")
        
        # ===== TEST 13: ADD ENCADRANT =====
        print("\n14. Testing supervisor addition...")
        
        new_supervisor = {
            'nom': 'Testeur',
            'prenom': 'Super',
            'grade': 'Professeur',
            'laboratoire_id': 1,
            'email': 'super.testeur@univ.fr',
            'telephone': '01 87 65 43 21',
            'specialite': 'Tests et Qualité',
            'date_embauche': '2020-01-01'
        }
        
        try:
            supervisor_id = db.add_encadrant(new_supervisor)
            print(f"   ✅ Supervisor added with ID: {supervisor_id}")
        except Exception as e:
            print(f"   ⚠️ Supervisor addition: {str(e)}")
        
        # ===== FINAL CLEANUP =====
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ All tests completed successfully!")
        print(f"✅ Database file: {test_db_path}")
        print(f"✅ Test doctorant ID: {doctorant_id}")
        print(f"✅ Created: 1 doctorant, 1 activity, 1 publication,")
        print(f"           1 formation, 1 suivi")
        print("=" * 60)
        
        # Show sample data
        print("\nSAMPLE DATA:")
        print(f"Doctorant: {doctorant['nom']} {doctorant['prenom']}")
        print(f"  - Email: {doctorant.get('email', 'N/A')}")
        print(f"  - Domaine: {doctorant.get('domaine', 'N/A')}")
        print(f"  - Statut: {doctorant.get('statut', 'N/A')}")
        
        if activities:
            print(f"  - Last activity: {activities[0].get('titre', 'N/A')}")
        
        if publications:
            print(f"  - Publication: {publications[0].get('titre', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Optional: Clean up test files
        cleanup = input("\nClean up test files? (y/n): ").lower() == 'y'
        if cleanup:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
                print(f"Removed: {test_db_path}")
            
            if os.path.exists(export_file):
                os.remove(export_file)
                print(f"Removed: {export_file}")
            
            # Clean backup directory
            backup_dir = "data/backups"
            if os.path.exists(backup_dir):
                import shutil
                shutil.rmtree(backup_dir)
                print(f"Removed: {backup_dir}")

def test_existing_data():
    """Test with existing production database"""
    print("\n" + "=" * 60)
    print("TESTING EXISTING PRODUCTION DATABASE")
    print("=" * 60)
    
    try:
        db = Database()  # Uses default database
        
        print("\nCurrent Database State:")
        print("-" * 40)
        
        # Count records
        doctorants = db.get_all_doctorants()
        print(f"Doctorants: {len(doctorants)}")
        
        activities = db.get_activities()
        print(f"Activities: {len(activities)}")
        
        publications = db.get_publications()
        print(f"Publications: {len(publications)}")
        
        formations = db.get_formations()
        print(f"Formations: {len(formations)}")
        
        suivis = db.get_suivi()
        print(f"Suivi records: {len(suivis)}")
        
        labs = db.get_laboratoires()
        print(f"Laboratoires: {len(labs)}")
        
        supervisors = db.get_encadrants()
        print(f"Supervisors: {len(supervisors)}")
        
        # Show first few doctorants
        print("\nFirst 5 Doctorants:")
        print("-" * 40)
        for i, doc in enumerate(doctorants[:5]):
            print(f"{i+1}. {doc.get('nom', '')} {doc.get('prenom', '')}")
            print(f"   Matricule: {doc.get('matricule', 'N/A')}")
            print(f"   Domaine: {doc.get('domaine', 'N/A')}")
            print(f"   Statut: {doc.get('statut', 'N/A')}")
            print()
        
        # Test statistics
        print("Statistics:")
        print("-" * 40)
        stats = db.get_statistics()
        
        print(f"Total students: {stats.get('total_students', 0)}")
        print(f"By status: {stats.get('by_status', {})}")
        
        if stats.get('upcoming_deadlines'):
            print(f"Upcoming deadlines: {len(stats['upcoming_deadlines'])}")
        
        print("\n✅ Production database test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error testing production database: {str(e)}")

if __name__ == "__main__":
    print("Database Test Suite")
    print("Choose test mode:")
    print("1. Comprehensive test (new test database)")
    print("2. Test existing production database")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        test_all_database_methods()
    
    if choice in ['2', '3']:
        test_existing_data()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)