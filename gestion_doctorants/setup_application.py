# gestion_doctorants/setup_application.py
import os
import shutil
import sqlite3
from datetime import datetime

def setup_application():
    """Setup the application with clean database and sample data"""
    print("=" * 70)
    print("GESTION DOCTORANTS - APPLICATION SETUP")
    print("=" * 70)
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/backups", exist_ok=True)
    
    db_path = "data/database.db"
    backup_dir = "data/backups"
    
    # Backup existing database if it exists
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{backup_dir}/database_backup_{timestamp}.db"
        shutil.copy2(db_path, backup_path)
        print(f"✅ Existing database backed up to: {backup_path}")
    
    # Remove old database
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ Removed old database")
    
    # Create fresh database with correct structure
    print("\nCreating fresh database...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables with correct structure
    tables_sql = [
        # Laboratoires table
        '''
        CREATE TABLE laboratoires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            faculte TEXT,
            responsable TEXT,
            email TEXT,
            telephone TEXT,
            adresse TEXT
        )
        ''',
        
        # Encadrants table
        '''
        CREATE TABLE encadrants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            grade TEXT,
            laboratoire_id INTEGER,
            email TEXT UNIQUE,
            telephone TEXT,
            specialite TEXT,
            date_embauche DATE,
            statut TEXT DEFAULT 'actif',
            FOREIGN KEY (laboratoire_id) REFERENCES laboratoires(id)
        )
        ''',
        
        # Doctorants table (with all required columns)
        '''
        CREATE TABLE doctorants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricule TEXT UNIQUE,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE,
            telephone TEXT,
            date_naissance DATE,
            nationalite TEXT,
            domaine TEXT,
            laboratoire_id INTEGER,
            directeur_id INTEGER,
            co_directeur_id INTEGER,
            annee_inscription INTEGER,
            annee_soutenance_prevue INTEGER,
            annee_soutenance_effective INTEGER,
            statut TEXT DEFAULT 'en_cours',
            titre_these TEXT,
            resume TEXT,
            mots_cles TEXT,
            financement TEXT,
            montant_financement REAL,
            adresse TEXT,
            ville TEXT,
            code_postal TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (laboratoire_id) REFERENCES laboratoires(id),
            FOREIGN KEY (directeur_id) REFERENCES encadrants(id),
            FOREIGN KEY (co_directeur_id) REFERENCES encadrants(id)
        )
        ''',
        
        # Activites table
        '''
        CREATE TABLE activites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctorant_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            categorie TEXT,
            titre TEXT NOT NULL,
            description TEXT,
            date_debut DATE,
            date_fin DATE,
            lieu TEXT,
            statut TEXT DEFAULT 'planifie',
            details TEXT,
            fichier_joint TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctorant_id) REFERENCES doctorants(id)
        )
        ''',
        
        # Publications table
        '''
        CREATE TABLE publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctorant_id INTEGER NOT NULL,
            type TEXT,
            titre TEXT NOT NULL,
            auteurs TEXT,
            revue TEXT,
            date_publication DATE,
            volume TEXT,
            pages TEXT,
            doi TEXT,
            url TEXT,
            statut TEXT DEFAULT 'soumis',
            impact_factor REAL,
            citations INTEGER DEFAULT 0,
            details TEXT,
            FOREIGN KEY (doctorant_id) REFERENCES doctorants(id)
        )
        ''',
        
        # Formations table
        '''
        CREATE TABLE formations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctorant_id INTEGER NOT NULL,
            type TEXT,
            intitule TEXT NOT NULL,
            organisateur TEXT,
            date_debut DATE,
            date_fin DATE,
            duree_heures INTEGER,
            lieu TEXT,
            certificat TEXT,
            details TEXT,
            FOREIGN KEY (doctorant_id) REFERENCES doctorants(id)
        )
        ''',
        
        # Suivi table
        '''
        CREATE TABLE suivi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctorant_id INTEGER NOT NULL,
            date_rencontre DATE NOT NULL,
            type_rencontre TEXT,
            participants TEXT,
            points_abordes TEXT,
            decisions TEXT,
            prochaines_etapes TEXT,
            date_prochaine_rencontre DATE,
            rapport TEXT,
            FOREIGN KEY (doctorant_id) REFERENCES doctorants(id)
        )
        '''
    ]
    
    for sql in tables_sql:
        cursor.execute(sql)
    
    print("✅ All tables created")
    
    # Add default laboratories
    print("\nAdding default laboratories...")
    labs = [
        ('LISN', 'Informatique', 'Prof. Martin', 'lisn@univ.fr', '01 23 45 67 00', 'Bâtiment 508'),
        ('LMB', 'Biologie', 'Prof. Dubois', 'lmb@univ.fr', '01 23 45 67 01', 'Bâtiment 400'),
        ('LMV', 'Mathématiques', 'Prof. Laurent', 'lmv@univ.fr', '01 23 45 67 02', 'Bâtiment 425'),
        ('LCH', 'Chimie', 'Prof. Garnier', 'lch@univ.fr', '01 23 45 67 03', 'Bâtiment 410')
    ]
    
    cursor.executemany('''
        INSERT INTO laboratoires (nom, faculte, responsable, email, telephone, adresse)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', labs)
    print(f"✅ Added {len(labs)} laboratories")
    
    # Add default supervisors
    print("\nAdding default supervisors...")
    supervisors = [
        ('Martin', 'Pierre', 'Professeur', 1, 'p.martin@univ.fr', '01 23 45 67 89', 'IA, Machine Learning'),
        ('Dubois', 'Marie', 'Professeur', 2, 'm.dubois@univ.fr', '01 23 45 67 90', 'Biologie Moléculaire'),
        ('Laurent', 'Jean', 'Professeur', 3, 'j.laurent@univ.fr', '01 23 45 67 91', 'Analyse Fonctionnelle'),
        ('Garnier', 'Sophie', 'Maître de Conférences', 4, 's.garnier@univ.fr', '01 23 45 67 92', 'Chimie Organique'),
        ('Moreau', 'Thomas', 'Professeur', 1, 't.moreau@univ.fr', '01 23 45 67 93', 'Systèmes Distribués'),
        ('Rousseau', 'Anne', 'Maître de Conférences', 2, 'a.rousseau@univ.fr', '01 23 45 67 94', 'Génétique')
    ]
    
    cursor.executemany('''
        INSERT INTO encadrants (nom, prenom, grade, laboratoire_id, email, telephone, specialite)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', supervisors)
    print(f"✅ Added {len(supervisors)} supervisors")
    
    # Add sample doctorants
    print("\nAdding sample doctorants...")
    doctorants = [
        ('DOC2022001', 'Martin', 'Sophie', 'sophie.martin@univ.fr', '01 23 45 67 88',
         '1995-03-15', 'Française', 'Informatique', 1, 1, None, 2022, 2025, None,
         'en_cours', 'Intelligence Artificielle pour le Diagnostic Médical', 
         'Recherche sur les applications de l\'IA en imagerie médicale', 
         'IA, deep learning, imagerie médicale', 'Bourse ministère', 16800.0,
         '123 Rue de la Science', 'Paris', '75013'),
        
        ('DOC2021001', 'Dubois', 'Thomas', 'thomas.dubois@univ.fr', '01 23 45 67 89',
         '1993-07-22', 'Française', 'Biologie', 2, 2, None, 2021, 2024, 2024,
         'soutenu', 'Étude des Protéines Membranaires dans les Cellules Cancéreuses',
         'Analyse des mécanismes protéiques dans l\'évolution tumorale',
         'protéines membranaires, cancer, biologie cellulaire', 'Contrat doctoral', 18500.0,
         '456 Avenue des Sciences', 'Lyon', '69007'),
        
        ('DOC2023001', 'Laurent', 'Émilie', 'emilie.laurent@univ.fr', '01 23 45 67 90',
         '1996-11-30', 'Canadienne', 'Mathématiques', 3, 3, None, 2023, 2026, None,
         'en_cours', 'Analyse Fonctionnelle et ses Applications',
         'Recherche en analyse fonctionnelle avec applications pratiques',
         'analyse fonctionnelle, équations différentielles', 'Bourse européenne', 20000.0,
         '789 Boulevard des Mathématiciens', 'Nice', '06000'),
        
        ('DOC2020001', 'Garnier', 'Pierre', 'pierre.garnier@univ.fr', '01 23 45 67 91',
         '1994-05-18', 'Française', 'Chimie', 4, 4, None, 2020, 2023, 2023,
         'soutenu', 'Synthèse de Nouveaux Composés Organiques',
         'Développement de composés chimiques innovants',
         'chimie organique, synthèse, pharmacologie', 'Projet européen', 21000.0,
         '321 Rue des Chimistes', 'Strasbourg', '67000'),
        
        ('DOC2024001', 'Rousseau', 'Anne', 'anne.rousseau@univ.fr', '01 23 45 67 92',
         '1997-02-14', 'Belge', 'Biologie', 2, 6, None, 2024, 2027, None,
         'en_cours', 'Génétique des Populations et Évolution',
         'Étude de la diversité génétique et des mécanismes évolutifs',
         'génétique, évolution, biodiversité', 'Bourse ministère', 16800.0,
         '654 Allée de la Biologie', 'Montpellier', '34000')
    ]
    
    cursor.executemany('''
        INSERT INTO doctorants (
            matricule, nom, prenom, email, telephone, date_naissance, nationalite,
            domaine, laboratoire_id, directeur_id, co_directeur_id, annee_inscription,
            annee_soutenance_prevue, annee_soutenance_effective, statut, titre_these,
            resume, mots_cles, financement, montant_financement, adresse, ville, code_postal
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', doctorants)
    print(f"✅ Added {len(doctorants)} doctorants")
    
    # Add sample activities
    print("\nAdding sample activities...")
    
    # Get doctorant IDs
    cursor.execute("SELECT id FROM doctorants ORDER BY id")
    doctorant_ids = [row[0] for row in cursor.fetchall()]
    
    activities = []
    for doc_id in doctorant_ids:
        # Add inscription activity
        cursor.execute("SELECT annee_inscription FROM doctorants WHERE id = ?", (doc_id,))
        year = cursor.fetchone()[0]
        
        activities.append((
            doc_id, 'these', 'inscription', 'Inscription en thèse',
            f'Inscription du doctorant pour l\'année {year}',
            f'{year}-09-01', f'{year}-09-01', 'Université', 'termine', 'Inscription initiale'
        ))
        
        # Add a seminar activity
        activities.append((
            doc_id, 'seminaire', 'presentation', 'Présentation des travaux',
            'Présentation des avancées de la thèse',
            f'{year + 1}-03-15', None, 'Laboratoire', 'termine', 'Présentation annuelle'
        ))
    
    cursor.executemany('''
        INSERT INTO activites (doctorant_id, type, categorie, titre, description, 
                              date_debut, date_fin, lieu, statut, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', activities)
    print(f"✅ Added {len(activities)} activities")
    
    # Add a sample publication
    print("\nAdding sample publications...")
    publications = [
        (doctorant_ids[0], 'article', 'Deep Learning for Medical Imaging',
         'Martin, S., Dubois, T.', 'Journal of Medical AI', '2023-06-15',
         '12', '123-135', '10.1000/xyz123', 'http://example.com', 'publie', 8.5, 24,
         'Article sur les applications du deep learning en imagerie médicale')
    ]
    
    cursor.executemany('''
        INSERT INTO publications (
            doctorant_id, type, titre, auteurs, revue, date_publication,
            volume, pages, doi, url, statut, impact_factor, citations, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', publications)
    print("✅ Added sample publication")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("SETUP COMPLETE! 🎉")
    print("=" * 70)
    
    # Show summary
    print("\n📊 DATABASE SUMMARY:")
    print(f"  • Laboratories: 4")
    print(f"  • Supervisors: 6")
    print(f"  • Doctorants: 5")
    print(f"  • Activities: {len(activities)}")
    print(f"  • Publications: 1")
    
    print("\n👨‍🎓 SAMPLE DOCTORANTS:")
    print("  1. Sophie Martin - Informatique (en cours)")
    print("  2. Thomas Dubois - Biologie (soutenu)")
    print("  3. Émilie Laurent - Mathématiques (en cours)")
    print("  4. Pierre Garnier - Chimie (soutenu)")
    print("  5. Anne Rousseau - Biologie (en cours)")
    
    print("\n🚀 NEXT STEPS:")
    print("  1. Run: python main.py")
    print("  2. Explore all features")
    print("  3. Test CRUD operations")
    print("  4. Try search functionality")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    setup_application()