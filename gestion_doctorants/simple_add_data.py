# gestion_doctorants/simple_add_data.py
import sqlite3
import os
from datetime import datetime

def simple_add_data():
    """Simple script to add sample data directly"""
    print("Simple Data Addition")
    print("=" * 60)
    
    db_path = "data/database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    # Close any other connections first
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current state
        cursor.execute("SELECT COUNT(*) FROM doctorants")
        count = cursor.fetchone()[0]
        print(f"Current doctorants in database: {count}")
        
        if count > 0:
            response = input("Clear existing data? (y/n): ").lower()
            if response == 'y':
                # Clear in correct order
                cursor.execute("DELETE FROM suivi")
                cursor.execute("DELETE FROM formations")
                cursor.execute("DELETE FROM publications")
                cursor.execute("DELETE FROM activites")
                cursor.execute("DELETE FROM doctorants")
                conn.commit()
                print("✅ Cleared existing data")
                count = 0
        
        if count == 0:
            print("\nAdding sample doctorants...")
            
            # Simple doctorant data
            doctorants = [
                ('DOC2024001', 'Martin', 'Sophie', 'sophie.martin@univ.fr', '01 23 45 67 88',
                 '1995-03-15', 'Française', 'Informatique', 1, 1, None, 2022, 2025, None,
                 'en_cours', 'IA pour le Diagnostic Médical', 'Recherche IA', 'IA, santé',
                 'Bourse ministère', 16800.0, '123 Rue Test', 'Paris', '75013'),
                
                ('DOC2021001', 'Dubois', 'Thomas', 'thomas.dubois@univ.fr', '01 23 45 67 89',
                 '1993-07-22', 'Française', 'Biologie', 2, 2, None, 2021, 2024, 2024,
                 'soutenu', 'Protéines Membranaires', 'Recherche biologie', 'protéines, cancer',
                 'Contrat doctoral', 18500.0, '456 Avenue Test', 'Lyon', '69007'),
                
                ('DOC2023001', 'Laurent', 'Émilie', 'emilie.laurent@univ.fr', '01 23 45 67 90',
                 '1996-11-30', 'Canadienne', 'Mathématiques', 3, 3, None, 2023, 2026, None,
                 'en_cours', 'Analyse Fonctionnelle', 'Recherche maths', 'analyse, équations',
                 'Bourse européenne', 20000.0, '789 Blvd Test', 'Nice', '06000')
            ]
            
            cursor.executemany('''
                INSERT INTO doctorants (
                    matricule, nom, prenom, email, telephone, date_naissance, nationalite,
                    domaine, laboratoire_id, directeur_id, co_directeur_id, annee_inscription,
                    annee_soutenance_prevue, annee_soutenance_effective, statut, titre_these,
                    resume, mots_cles, financement, montant_financement, adresse, ville, code_postal
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', doctorants)
            
            conn.commit()
            print(f"✅ Added {len(doctorants)} doctorants")
            
            # Get their IDs
            cursor.execute("SELECT id, nom, prenom FROM doctorants ORDER BY id")
            added = cursor.fetchall()
            
            print("\nAdded doctorants:")
            for doc_id, nom, prenom in added:
                print(f"  • {nom} {prenom} (ID: {doc_id})")
                
                # Add a simple activity
                cursor.execute('''
                    INSERT INTO activites (doctorant_id, type, titre, description, date_debut, statut)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (doc_id, 'these', 'Inscription', f"Inscription de {nom} {prenom}", 
                      f"{2020 + doc_id}-09-01", 'termine'))
            
            conn.commit()
            print("✅ Added basic activities")
        
        # Final count
        cursor.execute("SELECT COUNT(*) FROM doctorants")
        final_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM activites")
        activity_count = cursor.fetchone()[0]
        
        print(f"\n📊 Final counts:")
        print(f"  • Doctorants: {final_count}")
        print(f"  • Activities: {activity_count}")
        print(f"  • Laboratories: 4")
        print(f"  • Supervisors: 6")
        
        conn.close()
        
        print("\n✅ Data added successfully!")
        print("\nNext: Run 'python main.py' to start the application.")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
        return False

if __name__ == "__main__":
    simple_add_data()