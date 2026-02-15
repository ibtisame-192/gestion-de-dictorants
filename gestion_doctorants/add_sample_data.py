# gestion_doctorants/add_sample_data_fixed.py
import time
from database import Database
from datetime import datetime
import random
import sqlite3

def add_sample_data():
    """Add comprehensive sample data for testing"""
    print("=" * 70)
    print("ADDING SAMPLE DATA TO DATABASE")
    print("=" * 70)
    
    # Close any existing connections first
    time.sleep(1)
    
    try:
        db = Database()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return
    
    # First, let's check if database is empty
    try:
        doctorants = db.get_all_doctorants()
        print(f"Existing doctorants in database: {len(doctorants)}")
        
        if len(doctorants) > 0:
            response = input(f"\nDatabase already has {len(doctorants)} doctorants. Clear and add new sample data? (y/n): ").lower()
            if response != 'y':
                print("Operation cancelled.")
                return
            else:
                # Clear existing doctorants
                for doc in doctorants:
                    try:
                        db.delete_doctorant(doc['id'])
                    except:
                        pass
                print("✅ Cleared existing data")
                time.sleep(1)
    except:
        pass
    
    # Sample doctorants data (simplified - remove activity creation from add_doctorant)
    sample_doctorants = [
        {
            'nom': 'Martin',
            'prenom': 'Sophie',
            'email': 'sophie.martin@univ.fr',
            'telephone': '01 23 45 67 88',
            'date_naissance': '1995-03-15',
            'nationalite': 'Française',
            'domaine': 'Informatique',
            'laboratoire_id': 1,
            'directeur_id': 1,
            'co_directeur_id': 5,
            'annee_inscription': 2022,
            'annee_soutenance_prevue': 2025,
            'statut': 'en_cours',
            'titre_these': 'Intelligence Artificielle pour le Diagnostic Médical Précoce',
            'resume': 'Recherche sur les applications de l\'IA en imagerie médicale',
            'mots_cles': 'IA, deep learning, imagerie médicale, diagnostic',
            'financement': 'Bourse ministère',
            'montant_financement': 16800.0,
            'adresse': '123 Rue de la Science',
            'ville': 'Paris',
            'code_postal': '75013'
        },
        {
            'nom': 'Dubois',
            'prenom': 'Thomas',
            'email': 'thomas.dubois@univ.fr',
            'telephone': '01 23 45 67 89',
            'date_naissance': '1993-07-22',
            'nationalite': 'Française',
            'domaine': 'Biologie',
            'laboratoire_id': 2,
            'directeur_id': 2,
            'annee_inscription': 2021,
            'annee_soutenance_prevue': 2024,
            'annee_soutenance_effective': 2024,
            'statut': 'soutenu',
            'titre_these': 'Étude des Protéines Membranaires dans les Cellules Cancéreuses',
            'resume': 'Analyse des mécanismes protéiques dans l\'évolution tumorale',
            'mots_cles': 'protéines membranaires, cancer, biologie cellulaire',
            'financement': 'Contrat doctoral',
            'montant_financement': 18500.0,
            'adresse': '456 Avenue des Sciences',
            'ville': 'Lyon',
            'code_postal': '69007'
        },
        {
            'nom': 'Laurent',
            'prenom': 'Émilie',
            'email': 'emilie.laurent@univ.fr',
            'telephone': '01 23 45 67 90',
            'date_naissance': '1996-11-30',
            'nationalite': 'Canadienne',
            'domaine': 'Mathématiques',
            'laboratoire_id': 3,
            'directeur_id': 3,
            'annee_inscription': 2023,
            'annee_soutenance_prevue': 2026,
            'statut': 'en_cours',
            'titre_these': 'Analyse Fonctionnelle et ses Applications aux Équations Différentielles',
            'resume': 'Recherche en analyse fonctionnelle avec applications pratiques',
            'mots_cles': 'analyse fonctionnelle, équations différentielles, mathématiques appliquées',
            'financement': 'Bourse européenne',
            'montant_financement': 20000.0,
            'adresse': '789 Boulevard des Mathématiciens',
            'ville': 'Nice',
            'code_postal': '06000'
        },
        {
            'nom': 'Garnier',
            'prenom': 'Pierre',
            'email': 'pierre.garnier@univ.fr',
            'telephone': '01 23 45 67 91',
            'date_naissance': '1994-05-18',
            'nationalite': 'Française',
            'domaine': 'Chimie',
            'laboratoire_id': 4,
            'directeur_id': 4,
            'annee_inscription': 2020,
            'annee_soutenance_prevue': 2023,
            'annee_soutenance_effective': 2023,
            'statut': 'soutenu',
            'titre_these': 'Synthèse de Nouveaux Composés Organiques pour la Pharmacologie',
            'resume': 'Développement de composés chimiques innovants pour applications médicales',
            'mots_cles': 'chimie organique, synthèse, pharmacologie, composés bioactifs',
            'financement': 'Projet européen',
            'montant_financement': 21000.0,
            'adresse': '321 Rue des Chimistes',
            'ville': 'Strasbourg',
            'code_postal': '67000'
        },
        {
            'nom': 'Rousseau',
            'prenom': 'Anne',
            'email': 'anne.rousseau@univ.fr',
            'telephone': '01 23 45 67 92',
            'date_naissance': '1997-02-14',
            'nationalite': 'Belge',
            'domaine': 'Biologie',
            'laboratoire_id': 2,
            'directeur_id': 6,
            'annee_inscription': 2024,
            'annee_soutenance_prevue': 2027,
            'statut': 'en_cours',
            'titre_these': 'Génétique des Populations et Évolution des Espèces',
            'resume': 'Étude de la diversité génétique et des mécanismes évolutifs',
            'mots_cles': 'génétique, évolution, biodiversité, populations',
            'financement': 'Bourse ministère',
            'montant_financement': 16800.0,
            'adresse': '654 Allée de la Biologie',
            'ville': 'Montpellier',
            'code_postal': '34000'
        }
    ]
    
    print("\nAdding doctorants...")
    doctorant_ids = []
    
    for data in sample_doctorants:
        try:
            # Create a new connection for each doctorant to avoid locking
            temp_db = Database()
            
            # Add doctorant WITHOUT automatic activity creation
            conn = temp_db.get_connection()
            cursor = conn.cursor()
            
            # Generate matricule
            year = data.get('annee_inscription', datetime.now().year)
            cursor.execute("SELECT COUNT(*) FROM doctorants WHERE annee_inscription = ?", (year,))
            count = cursor.fetchone()[0] + 1
            matricule = f"DOC{year}{str(count).zfill(3)}"
            
            query = '''
            INSERT INTO doctorants (
                matricule, nom, prenom, email, telephone, date_naissance, nationalite,
                domaine, laboratoire_id, directeur_id, co_directeur_id, annee_inscription,
                annee_soutenance_prevue, annee_soutenance_effective, statut, titre_these,
                resume, mots_cles, financement, montant_financement, adresse, ville, code_postal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            values = (
                matricule,
                data.get('nom', '').strip(),
                data.get('prenom', '').strip(),
                data.get('email', '').strip(),
                data.get('telephone', '').strip(),
                data.get('date_naissance'),
                data.get('nationalite', '').strip(),
                data.get('domaine', '').strip(),
                data.get('laboratoire_id'),
                data.get('directeur_id'),
                data.get('co_directeur_id'),
                data.get('annee_inscription'),
                data.get('annee_soutenance_prevue'),
                data.get('annee_soutenance_effective'),
                data.get('statut', 'en_cours'),
                data.get('titre_these', '').strip(),
                data.get('resume', '').strip(),
                data.get('mots_cles', '').strip(),
                data.get('financement', '').strip(),
                data.get('montant_financement', 0.0),
                data.get('adresse', '').strip(),
                data.get('ville', '').strip(),
                data.get('code_postal', '').strip()
            )
            
            cursor.execute(query, values)
            doctorant_id = cursor.lastrowid
            doctorant_ids.append(doctorant_id)
            
            conn.commit()
            conn.close()
            
            print(f"  ✅ {data['nom']} {data['prenom']} - {data['domaine']} (ID: {doctorant_id})")
            
            # Add activity manually after a delay
            time.sleep(0.5)
            try:
                db.add_activity(doctorant_id, {
                    'type': 'these',
                    'titre': 'Inscription en thèse',
                    'description': f"Inscription du doctorant {data['nom']} {data['prenom']}",
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'statut': 'termine'
                })
            except:
                pass  # Skip if activity fails
            
        except Exception as e:
            print(f"  ❌ Error adding {data['nom']}: {str(e)}")
    
    if not doctorant_ids:
        print("\n❌ No doctorants were added. Database might be locked.")
        print("Please close any other application that might be using the database.")
        return
    
    # Add activities for each doctorant
    print("\nAdding activities...")
    activity_types = ['publication', 'formation', 'seminaire', 'conference', 'reunion']
    
    for doctorant_id in doctorant_ids:
        try:
            doctorant = db.get_doctorant(doctorant_id)
            if not doctorant:
                continue
                
            # Add 2-3 activities per doctorant
            num_activities = random.randint(2, 3)
            for j in range(num_activities):
                activity_type = random.choice(activity_types)
                year = doctorant['annee_inscription'] + random.randint(0, 2)
                
                activity_data = {
                    'type': activity_type,
                    'titre': f"{activity_type.capitalize()} {j+1} - {doctorant['nom']}",
                    'description': f"Description de {activity_type} {j+1}",
                    'date_debut': f"{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                    'statut': random.choice(['planifie', 'en_cours', 'termine'])
                }
                
                if activity_type == 'formation':
                    activity_data['date_fin'] = f"{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                    activity_data['duree_heures'] = random.randint(8, 40)
                    activity_data['lieu'] = random.choice(['Paris', 'Lyon', 'Marseille', 'Toulouse'])
                
                try:
                    db.add_activity(doctorant_id, activity_data)
                except:
                    pass
                    
        except Exception as e:
            print(f"  ⚠️ Error processing doctorant {doctorant_id}: {str(e)}")
    
    print(f"  ✅ Added activities for {len(doctorant_ids)} doctorants")
    
    # Add publications if we have doctorants
    if doctorant_ids:
        print("\nAdding publications...")
        publication_data = [
            {
                'type': 'article',
                'titre': 'Deep Learning Approaches for Medical Image Analysis',
                'auteurs': 'Martin, S., Dubois, T., Laurent, J.',
                'revue': 'Journal of Medical AI',
                'date_publication': '2023-06-15',
                'statut': 'publie',
                'impact_factor': 8.5,
                'citations': 24
            },
            {
                'type': 'conference',
                'titre': 'Advances in Protein Membrane Research',
                'auteurs': 'Dubois, T., Garnier, P.',
                'revue': 'International Conference on Biology',
                'date_publication': '2022-09-10',
                'statut': 'publie',
                'citations': 12
            }
        ]
        
        for pub in publication_data:
            try:
                db.add_publication(doctorant_ids[0], pub)
                print(f"  ✅ {pub['titre'][:50]}...")
            except Exception as e:
                print(f"  ⚠️ Error adding publication: {str(e)}")
    
    # Add formations if we have doctorants
    if len(doctorant_ids) > 1:
        print("\nAdding formations...")
        formation_data = [
            {
                'intitule': 'Méthodologie de Recherche Scientifique',
                'organisateur': 'École Doctorale',
                'date_debut': '2022-10-10',
                'date_fin': '2022-10-12',
                'duree_heures': 18,
                'lieu': 'Paris',
                'certificat': 'CERT-MRS-2022'
            },
            {
                'intitule': 'Rédaction Scientifique en Anglais',
                'organisateur': 'Centre de Langues',
                'date_debut': '2023-03-15',
                'date_fin': '2023-03-17',
                'duree_heures': 12,
                'lieu': 'Lyon',
                'certificat': 'CERT-RSA-2023'
            }
        ]
        
        for formation in formation_data:
            try:
                db.add_formation(doctorant_ids[1], formation)
                print(f"  ✅ {formation['intitule'][:50]}...")
            except Exception as e:
                print(f"  ⚠️ Error adding formation: {str(e)}")
    
    # Show final statistics
    print("\n" + "=" * 70)
    print("SAMPLE DATA SUMMARY")
    print("=" * 70)
    
    time.sleep(1)  # Give database time to update
    
    try:
        stats = db.get_statistics()
        
        print(f"\n📊 Database Statistics:")
        print(f"  • Doctorants: {stats.get('total_students', 0)}")
        print(f"  • By Status: {stats.get('by_status', {})}")
        print(f"  • Laboratories: {stats.get('total_laboratories', 0)}")
        print(f"  • Supervisors: {stats.get('total_supervisors', 0)}")
        print(f"  • Publications: {stats.get('total_publications', 0)}")
        
        print(f"\n👨‍🎓 Added Doctorants:")
        doctorants = db.get_all_doctorants()
        for doc in doctorants:
            status_icon = '📚' if doc['statut'] == 'en_cours' else '🎓'
            print(f"  {status_icon} {doc['nom']} {doc['prenom']} - {doc['domaine']} ({doc['statut']})")
        
    except Exception as e:
        print(f"Error getting statistics: {str(e)}")
        # Manual count
        doctorants = db.get_all_doctorants()
        print(f"\n👨‍🎓 Doctorants in database: {len(doctorants)}")
        for doc in doctorants:
            print(f"  • {doc['nom']} {doc['prenom']}")
    
    print(f"\n🚀 Next Steps:")
    print(f"  1. Run: python main.py")
    print(f"  2. Explore the interface with real data")
    print(f"  3. Test all CRUD operations")
    print(f"  4. Try the search functionality")
    
    print("\n" + "=" * 70)
    print("SAMPLE DATA ADDED SUCCESSFULLY! 🎉")
    print("=" * 70)

if __name__ == "__main__":
    add_sample_data()