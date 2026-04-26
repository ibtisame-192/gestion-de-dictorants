# gestion_doctorants/database.py 
import sqlite3
import os
import json
import time
import threading
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import contextlib

class Database:
    def __init__(self, db_path="data/database.db"):
        """Initialize database connection with locking"""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self._lock = threading.Lock()  # Thread lock for database access
        
        # Clean up any existing lock files
        self.cleanup_lock_files()
        
        # Initialize database
        self.init_database()
    
    def cleanup_lock_files(self):
        """Clean up SQLite lock files"""
        lock_files = [
            self.db_path + '-wal',
            self.db_path + '-shm',
            self.db_path + '-journal',
        ]
        
        for lock_file in lock_files:
            if os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                    print(f"Removed lock file: {lock_file}")
                except:
                    pass
    
    def get_connection(self):
        """Create and return a database connection with timeout"""
        # Use thread lock to prevent concurrent connections
        with self._lock:
            try:
                # Increase timeout to 30 seconds and enable WAL mode
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                conn.row_factory = sqlite3.Row
                
                # Set pragmas for better concurrency
                conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA foreign_keys=ON")
                conn.execute("PRAGMA busy_timeout=10000")  # 10 second busy timeout
                
                return conn
            except sqlite3.Error as e:
                if "locked" in str(e):
                    # Wait and retry once
                    time.sleep(0.5)
                    conn = sqlite3.connect(self.db_path, timeout=30.0)
                    conn.row_factory = sqlite3.Row
                    return conn
                raise e
    
    @contextlib.contextmanager
    def transaction(self):
        """Context manager for safe transactions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN IMMEDIATE")  # Get immediate lock
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with all tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create tables
            self.create_tables(cursor)
            
            # Insert default data
            self.insert_default_data(cursor)
            
            conn.commit()
            print(f"Database initialized successfully at: {self.db_path}")
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de l'initialisation de la base: {str(e)}")
        finally:
            conn.close()
    
    def create_tables(self, cursor):
        """Create all required tables"""
        
        # Laboratoires table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS laboratoires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            faculte TEXT,
            responsable TEXT,
            email TEXT,
            telephone TEXT,
            adresse TEXT
        )
        ''')
        
        # Encadrants table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS encadrants (
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
        ''')
        
        # Doctorants table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctorants (
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
        ''')
        
        # Activites table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS activites (
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
        ''')
        
        # Publications table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS publications (
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
        ''')
        
        # Formations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS formations (
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
        ''')
        
        # Suivi table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS suivi (
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
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_doctorant_labo ON doctorants(laboratoire_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_doctorant_directeur ON doctorants(directeur_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_doctorant_statut ON doctorants(statut)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_activites_doctorant ON activites(doctorant_id)')
        
        print("✅ Tables created successfully")
    
    def insert_default_data(self, cursor):
        """Insert default laboratory and supervisor data"""
        
        # Insert default laboratories
        cursor.execute("SELECT COUNT(*) as count FROM laboratoires")
        if cursor.fetchone()['count'] == 0:
            default_labs = [
                ('LISN', 'Informatique', 'Prof. Martin', 'lisn@univ.fr', '01 23 45 67 00', 'Bâtiment 508, Rue Noetzlin'),
                ('LMB', 'Biologie', 'Prof. Dubois', 'lmb@univ.fr', '01 23 45 67 01', 'Bâtiment 400'),
                ('LMV', 'Mathématiques', 'Prof. Laurent', 'lmv@univ.fr', '01 23 45 67 02', 'Bâtiment 425'),
                ('LCH', 'Chimie', 'Prof. Garnier', 'lch@univ.fr', '01 23 45 67 03', 'Bâtiment 410')
            ]
            cursor.executemany('''
                INSERT INTO laboratoires (nom, faculte, responsable, email, telephone, adresse)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', default_labs)
            print("Default laboratories inserted")
        
        # Insert default supervisors
        cursor.execute("SELECT COUNT(*) as count FROM encadrants")
        if cursor.fetchone()['count'] == 0:
            default_supervisors = [
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
            ''', default_supervisors)
            print("Default supervisors inserted")
    
    # ===== DOCTORANTS CRUD =====
    
    def add_doctorant(self, data: Dict[str, Any]) -> int:
        """Add a new PhD student and return the ID - FIXED VERSION"""
        print(f"Adding doctorant: {data.get('nom')} {data.get('prenom')}")
        
        # Use transaction context manager for safety
        with self.transaction() as cursor:
            try:
                # Generate matricule if not provided
                if 'matricule' not in data or not data['matricule']:
                    year = data.get('annee_inscription', datetime.now().year)
                    cursor.execute("""
                        SELECT COUNT(*) FROM doctorants 
                        WHERE annee_inscription = ?
                    """, (year,))
                    count = cursor.fetchone()[0] + 1
                    data['matricule'] = f"DOC{year}{str(count).zfill(3)}"
                    print(f"Generated matricule: {data['matricule']}")
                
                query = '''
                INSERT INTO doctorants (
                    matricule, nom, prenom, email, telephone, date_naissance, nationalite,
                    domaine, laboratoire_id, directeur_id, co_directeur_id, annee_inscription,
                    annee_soutenance_prevue, annee_soutenance_effective, statut, titre_these,
                    resume, mots_cles, financement, montant_financement, adresse, ville, code_postal
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                
                # Handle None values
                values = (
                    data.get('matricule'),
                    data.get('nom', '').strip() or '',
                    data.get('prenom', '').strip() or '',
                    data.get('email', '').strip() or '',
                    data.get('telephone', '').strip() or '',
                    data.get('date_naissance'),
                    data.get('nationalite', '').strip() or '',
                    data.get('domaine', '').strip() or '',
                    data.get('laboratoire_id'),
                    data.get('directeur_id'),
                    data.get('co_directeur_id'),
                    data.get('annee_inscription', datetime.now().year),
                    data.get('annee_soutenance_prevue'),
                    data.get('annee_soutenance_effective'),
                    data.get('statut', 'en_cours'),
                    data.get('titre_these', '').strip() or '',
                    data.get('resume', '').strip() or '',
                    data.get('mots_cles', '').strip() or '',
                    data.get('financement', '').strip() or '',
                    data.get('montant_financement', 0.0) or 0.0,
                    data.get('adresse', '').strip() or '',
                    data.get('ville', '').strip() or '',
                    data.get('code_postal', '').strip() or ''
                )
                
                cursor.execute(query, values)
                doctorant_id = cursor.lastrowid
                
                # Add default activity
                cursor.execute('''
                    INSERT INTO activites (
                        doctorant_id, type, categorie, titre, description, 
                        date_debut, statut
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    doctorant_id,
                    'these',
                    'inscription',
                    'Inscription en thèse',
                    f"Inscription du doctorant {data.get('nom', '')} {data.get('prenom', '')}",
                    datetime.now().strftime('%Y-%m-%d'),
                    'termine'
                ))
                
                print(f"Doctorant added successfully with ID: {doctorant_id}")
                return doctorant_id
                
            except sqlite3.Error as e:
                print(f"SQL Error: {e}")
                raise Exception(f"Erreur lors de l'ajout du doctorant: {str(e)}")
            except Exception as e:
                print(f"General Error: {e}")
                raise Exception(f"Erreur générale: {str(e)}")
    
    def update_doctorant(self, doctorant_id: int, data: Dict[str, Any]) -> bool:
        """Update a PhD student with lock protection"""
        with self.transaction() as cursor:
            try:
                # Build dynamic query
                fields = []
                values = []
                
                for key, value in data.items():
                    if key != 'id' and value is not None:
                        fields.append(f"{key} = ?")
                        values.append(value)
                
                # Add modification date
                fields.append("date_modification = ?")
                values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                # Add WHERE condition
                values.append(doctorant_id)
                
                query = f"UPDATE doctorants SET {', '.join(fields)} WHERE id = ?"
                cursor.execute(query, values)
                
                # Add activity
                cursor.execute('''
                    INSERT INTO activites (
                        doctorant_id, type, titre, description, date_debut, statut
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    doctorant_id,
                    'reunion',
                    'Mise à jour des informations',
                    'Mise à jour des informations personnelles',
                    datetime.now().strftime('%Y-%m-%d'),
                    'termine'
                ))
                
                return cursor.rowcount > 0
                
            except sqlite3.Error as e:
                raise Exception(f"Erreur SQLite : {str(e)}")
    
    def delete_doctorant(self, doctorant_id: int) -> bool:
        """Delete a PhD student and all related data"""
        with self.transaction() as cursor:
            try:
                # Delete related records
                tables = ['suivi', 'formations', 'publications', 'activites']
                for table in tables:
                    cursor.execute(f"DELETE FROM {table} WHERE doctorant_id = ?", (doctorant_id,))
                
                # Delete the doctorant
                cursor.execute("DELETE FROM doctorants WHERE id = ?", (doctorant_id,))
                
                return cursor.rowcount > 0
                
            except sqlite3.Error as e:
                raise Exception(f"Erreur lors de la suppression du doctorant: {str(e)}")
    
    def get_doctorant(self, doctorant_id: int) -> Optional[Dict[str, Any]]:
        """Get a single PhD student with full details"""
        conn = self.get_connection()
        
        try:
            query = '''
            SELECT d.*, 
                   l.nom as labo_nom, l.faculte as labo_faculte, l.responsable as labo_responsable,
                   dir.nom as directeur_nom, dir.prenom as directeur_prenom, dir.grade as directeur_grade,
                   dir.email as directeur_email, dir.telephone as directeur_telephone,
                   co.nom as co_directeur_nom, co.prenom as co_directeur_prenom, 
                   co.grade as co_directeur_grade
            FROM doctorants d
            LEFT JOIN laboratoires l ON d.laboratoire_id = l.id
            LEFT JOIN encadrants dir ON d.directeur_id = dir.id
            LEFT JOIN encadrants co ON d.co_directeur_id = co.id
            WHERE d.id = ?
            '''
            
            cursor = conn.cursor()
            cursor.execute(query, (doctorant_id,))
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            return None
            
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la récupération du doctorant: {str(e)}")
        finally:
            conn.close()
    
    def get_all_doctorants(self) -> List[Dict[str, Any]]:
        """Get all PhD students"""
        conn = self.get_connection()
        
        try:
            query = '''
            SELECT d.*, 
                   l.nom as labo_nom, 
                   dir.nom as directeur_nom, dir.prenom as directeur_prenom,
                   dir.grade as directeur_grade
            FROM doctorants d
            LEFT JOIN laboratoires l ON d.laboratoire_id = l.id
            LEFT JOIN encadrants dir ON d.directeur_id = dir.id
            ORDER BY d.nom, d.prenom
            '''
            
            cursor = conn.cursor()
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la récupération des doctorants: {str(e)}")
        finally:
            conn.close()
    
    # ... (KEEP ALL OTHER METHODS AS THEY ARE, but update connection usage)
    # For other methods like search_doctorants, get_activities, etc.
    
    # ===== ACTIVITIES CRUD =====
    
    def add_activity(self, doctorant_id: int, activity_data: Dict[str, Any]) -> int:
        """Add a new activity"""
        with self.transaction() as cursor:
            try:
                query = '''
                INSERT INTO activites (
                    doctorant_id, type, categorie, titre, description, 
                    date_debut, date_fin, lieu, statut, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                
                values = (
                    doctorant_id,
                    activity_data.get('type', 'autre'),
                    activity_data.get('categorie', ''),
                    activity_data.get('titre', '').strip(),
                    activity_data.get('description', '').strip(),
                    activity_data.get('date_debut'),
                    activity_data.get('date_fin'),
                    activity_data.get('lieu', '').strip(),
                    activity_data.get('statut', 'planifie'),
                    activity_data.get('details', '').strip()
                )
                
                cursor.execute(query, values)
                return cursor.lastrowid
                
            except sqlite3.Error as e:
                raise Exception(f"Erreur lors de l'ajout de l'activité: {str(e)}")
    
    # ===== TEST METHOD =====
    
    def test_database_operations(self):
        """Test basic database operations"""
        print("\n" + "="*50)
        print("DATABASE CONNECTION TEST")
        print("="*50)
        
        # 1. Test connection
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Connection successful")
            print(f"Tables found: {[t[0] for t in tables]}")
            conn.close()
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            return False
        
        # 2. Test inserting a doctorant
        print("\nTesting doctorant insertion...")
        try:
            test_data = {
                'nom': 'Test',
                'prenom': 'Student',
                'email': 'test.student@univ.fr',
                'domaine': 'Informatique',
                'laboratoire_id': 1,
                'directeur_id': 1,
                'annee_inscription': 2024,
                'statut': 'en_cours'
            }
            
            print(f"📝 Test data: {test_data}")
            doctorant_id = self.add_doctorant(test_data)
            print(f"Test doctorant added with ID: {doctorant_id}")
            
            # 3. Verify insertion
            doctorant = self.get_doctorant(doctorant_id)
            if doctorant:
                print(f"Doctorant retrieved: {doctorant['nom']} {doctorant['prenom']}")
                print(f"Matricule: {doctorant.get('matricule', 'N/A')}")
                
                # 4. Clean up test data
                success = self.delete_doctorant(doctorant_id)
                if success:
                    print(f"Test doctorant deleted")
                else:
                    print(f"Could not delete test doctorant")
            else:
                print(f"Failed to retrieve test doctorant")
                return False
                
            print("\n" + "="*50)
            print("ALL TESTS PASSED!")
            print("="*50)
            return True
            
        except Exception as e:
            print(f"Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            
            print("\n" + "="*50)
            print("TESTS FAILED")
            print("="*50)
            return False
    
    # ===== DIAGNOSTIC METHOD =====
    
    def diagnose_connection(self):
        """Diagnose database connection issues"""
        print("\nDATABASE DIAGNOSIS")
        print("-" * 40)
        
        # Check if file exists
        if not os.path.exists(self.db_path):
            print(f"Database file not found: {self.db_path}")
            print("Creating new database...")
            self.init_database()
            return
        
        # Check file permissions
        try:
            import stat
            st = os.stat(self.db_path)
            size_kb = st.st_size / 1024
            print(f"Database file: {self.db_path}")
            print(f"Size: {size_kb:.2f} KB")
            print(f"Permissions: {oct(st.st_mode)[-3:]}")
            print(f"Writable: {os.access(self.db_path, os.W_OK)}")
        except Exception as e:
            print(f"Cannot access file: {e}")
        
        # Try to connect
        print("\nTesting connection...")
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Test simple query
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"Basic query test: {result['test']}")
            
            # Count doctorants
            cursor.execute("SELECT COUNT(*) as count FROM doctorants")
            count = cursor.fetchone()['count']
            print(f"Total doctorants: {count}")
            
            # Count laboratories
            cursor.execute("SELECT COUNT(*) as count FROM laboratoires")
            count = cursor.fetchone()['count']
            print(f"Total laboratories: {count}")
            
            conn.close()
            print("Connection test successful")
            
        except sqlite3.Error as e:
            print(f"Connection error: {e}")
            
            # Try to repair
            if "locked" in str(e):
                print("Attempting to repair locked database...")
                self.cleanup_lock_files()
                time.sleep(1)
                
                # Try again
                try:
                    conn = sqlite3.connect(self.db_path, timeout=5.0)
                    conn.execute("PRAGMA wal_checkpoint(FULL)")
                    conn.close()
                    print("Database repaired")
                except:
                    print("Could not repair database")
    
    # ... (KEEP ALL OTHER METHODS THE SAME, just ensure they use proper connection handling)
    
    def search_doctorants(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search PhD students with filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            SELECT d.*, 
                   l.nom as labo_nom, 
                   dir.nom as directeur_nom, dir.prenom as directeur_prenom,
                   dir.grade as directeur_grade
            FROM doctorants d
            LEFT JOIN laboratoires l ON d.laboratoire_id = l.id
            LEFT JOIN encadrants dir ON d.directeur_id = dir.id
            WHERE 1=1
            '''
            params = []
            
            if filters:
                # Search by name
                if filters.get('nom'):
                    query += " AND (d.nom LIKE ? OR d.prenom LIKE ? OR d.matricule LIKE ?)"
                    search_term = f"%{filters['nom']}%"
                    params.extend([search_term, search_term, search_term])
                
                # Search by exact matricule
                if filters.get('matricule'):
                    query += " AND d.matricule = ?"
                    params.append(filters['matricule'])
                
                # Filter by domaine
                if filters.get('domaine'):
                    query += " AND d.domaine = ?"
                    params.append(filters['domaine'])
                
                # Filter by laboratoire
                if filters.get('laboratoire_id'):
                    query += " AND d.laboratoire_id = ?"
                    params.append(filters['laboratoire_id'])
                
                # Filter by directeur
                if filters.get('directeur_id'):
                    query += " AND d.directeur_id = ?"
                    params.append(filters['directeur_id'])
                
                # Filter by year
                if filters.get('annee_inscription'):
                    query += " AND d.annee_inscription = ?"
                    params.append(filters['annee_inscription'])
                
                # Filter by status
                if filters.get('statut'):
                    query += " AND d.statut = ?"
                    params.append(filters['statut'])
                
                # Filter by financement
                if filters.get('financement'):
                    query += " AND d.financement = ?"
                    params.append(filters['financement'])
                
                # Date range filters
                if filters.get('date_debut'):
                    query += " AND d.date_creation >= ?"
                    params.append(filters['date_debut'])
                
                if filters.get('date_fin'):
                    query += " AND d.date_creation <= ?"
                    params.append(filters['date_fin'])
            
            query += " ORDER BY d.nom, d.prenom"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la recherche des doctorants: {str(e)}")
        finally:
            conn.close()
    
    # ===== ACTIVITIES CRUD =====
    
    def add_activity(self, doctorant_id: int, activity_data: Dict[str, Any]) -> int:
        """Add a new activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            INSERT INTO activites (
                doctorant_id, type, categorie, titre, description, 
                date_debut, date_fin, lieu, statut, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            values = (
                doctorant_id,
                activity_data.get('type', 'autre'),
                activity_data.get('categorie', ''),
                activity_data.get('titre', '').strip(),
                activity_data.get('description', '').strip(),
                activity_data.get('date_debut'),
                activity_data.get('date_fin'),
                activity_data.get('lieu', '').strip(),
                activity_data.get('statut', 'planifie'),
                activity_data.get('details', '').strip()
            )
            
            cursor.execute(query, values)
            activity_id = cursor.lastrowid
            conn.commit()
            return activity_id
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de l'ajout de l'activité: {str(e)}")
        finally:
            conn.close()
    
    def update_activity(self, activity_id: int, activity_data: Dict[str, Any]) -> bool:
        """Update an activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            UPDATE activites SET
                type = ?, categorie = ?, titre = ?, description = ?,
                date_debut = ?, date_fin = ?, lieu = ?, statut = ?, details = ?
            WHERE id = ?
            '''
            
            values = (
                activity_data.get('type'),
                activity_data.get('categorie'),
                activity_data.get('titre'),
                activity_data.get('description'),
                activity_data.get('date_debut'),
                activity_data.get('date_fin'),
                activity_data.get('lieu'),
                activity_data.get('statut'),
                activity_data.get('details'),
                activity_id
            )
            
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de la mise à jour de l'activité: {str(e)}")
        finally:
            conn.close()
    
    def delete_activity(self, activity_id: int) -> bool:
        """Delete an activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM activites WHERE id = ?", (activity_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de la suppression de l'activité: {str(e)}")
        finally:
            conn.close()
    
    def get_activities(self, doctorant_id: int = None, 
                      filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get activities, optionally filtered by doctorant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            SELECT a.*, d.nom as doctorant_nom, d.prenom as doctorant_prenom
            FROM activites a
            JOIN doctorants d ON a.doctorant_id = d.id
            WHERE 1=1
            '''
            params = []
            
            if doctorant_id:
                query += " AND a.doctorant_id = ?"
                params.append(doctorant_id)
            
            if filters:
                if filters.get('type'):
                    query += " AND a.type = ?"
                    params.append(filters['type'])
                
                if filters.get('statut'):
                    query += " AND a.statut = ?"
                    params.append(filters['statut'])
                
                if filters.get('date_debut'):
                    query += " AND a.date_debut >= ?"
                    params.append(filters['date_debut'])
                
                if filters.get('date_fin'):
                    query += " AND a.date_fin <= ?"
                    params.append(filters['date_fin'])
            
            query += " ORDER BY a.date_debut DESC, a.date_creation DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la récupération des activités: {str(e)}")
        finally:
            conn.close()
    
    # ===== PUBLICATIONS CRUD =====
    
    def add_publication(self, doctorant_id: int, publication_data: Dict[str, Any]) -> int:
        """Add a new publication"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            INSERT INTO publications (
                doctorant_id, type, titre, auteurs, revue, date_publication,
                volume, pages, doi, url, statut, impact_factor, citations, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            values = (
                doctorant_id,
                publication_data.get('type', 'article'),
                publication_data.get('titre', '').strip(),
                publication_data.get('auteurs', '').strip(),
                publication_data.get('revue', '').strip(),
                publication_data.get('date_publication'),
                publication_data.get('volume', ''),
                publication_data.get('pages', ''),
                publication_data.get('doi', ''),
                publication_data.get('url', ''),
                publication_data.get('statut', 'soumis'),
                publication_data.get('impact_factor', 0.0),
                publication_data.get('citations', 0),
                publication_data.get('details', '').strip()
            )
            
            cursor.execute(query, values)
            publication_id = cursor.lastrowid
            
            # Also add as activity
            self.add_activity(doctorant_id, {
                'type': 'publication',
                'titre': publication_data.get('titre', ''),
                'description': f"Publication: {publication_data.get('titre', '')}",
                'date_debut': publication_data.get('date_publication'),
                'statut': publication_data.get('statut', 'soumis')
            })
            
            conn.commit()
            return publication_id
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de l'ajout de la publication: {str(e)}")
        finally:
            conn.close()
    
    def get_publications(self, doctorant_id: int = None) -> List[Dict[str, Any]]:
        """Get publications, optionally filtered by doctorant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            SELECT p.*, d.nom as doctorant_nom, d.prenom as doctorant_prenom
            FROM publications p
            JOIN doctorants d ON p.doctorant_id = d.id
            '''
            params = []
            
            if doctorant_id:
                query += " WHERE p.doctorant_id = ?"
                params.append(doctorant_id)
            
            query += " ORDER BY p.date_publication DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la récupération des publications: {str(e)}")
        finally:
            conn.close()
    
    def update_publication(self, publication_id: int, publication_data: Dict[str, Any]) -> bool:
        """Update a publication"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            UPDATE publications SET
                type = ?, titre = ?, auteurs = ?, revue = ?, date_publication = ?,
                volume = ?, pages = ?, doi = ?, url = ?, statut = ?,
                impact_factor = ?, citations = ?, details = ?
            WHERE id = ?
            '''
            
            values = (
                publication_data.get('type'),
                publication_data.get('titre'),
                publication_data.get('auteurs'),
                publication_data.get('revue'),
                publication_data.get('date_publication'),
                publication_data.get('volume'),
                publication_data.get('pages'),
                publication_data.get('doi'),
                publication_data.get('url'),
                publication_data.get('statut'),
                publication_data.get('impact_factor'),
                publication_data.get('citations'),
                publication_data.get('details'),
                publication_id
            )
            
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de la mise à jour de la publication: {str(e)}")
        finally:
            conn.close()
    
    def delete_publication(self, publication_id: int) -> bool:
        """Delete a publication"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM publications WHERE id = ?", (publication_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de la suppression de la publication: {str(e)}")
        finally:
            conn.close()
    
    # ===== FORMATIONS CRUD =====
    
    def add_formation(self, doctorant_id: int, formation_data: Dict[str, Any]) -> int:
        """Add a new formation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            INSERT INTO formations (
                doctorant_id, type, intitule, organisateur, date_debut, date_fin,
                duree_heures, lieu, certificat, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            values = (
                doctorant_id,
                formation_data.get('type', 'formation'),
                formation_data.get('intitule', '').strip(),
                formation_data.get('organisateur', '').strip(),
                formation_data.get('date_debut'),
                formation_data.get('date_fin'),
                formation_data.get('duree_heures', 0),
                formation_data.get('lieu', '').strip(),
                formation_data.get('certificat', '').strip(),
                formation_data.get('details', '').strip()
            )
            
            cursor.execute(query, values)
            formation_id = cursor.lastrowid
            
            # Also add as activity
            self.add_activity(doctorant_id, {
                'type': 'formation',
                'titre': formation_data.get('intitule', ''),
                'description': f"Formation: {formation_data.get('intitule', '')}",
                'date_debut': formation_data.get('date_debut'),
                'date_fin': formation_data.get('date_fin'),
                'statut': 'termine'
            })
            
            conn.commit()
            return formation_id
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de l'ajout de la formation: {str(e)}")
        finally:
            conn.close()
    
    def get_formations(self, doctorant_id: int = None) -> List[Dict[str, Any]]:
        """Get formations, optionally filtered by doctorant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            SELECT f.*, d.nom as doctorant_nom, d.prenom as doctorant_prenom
            FROM formations f
            JOIN doctorants d ON f.doctorant_id = d.id
            '''
            params = []
            
            if doctorant_id:
                query += " WHERE f.doctorant_id = ?"
                params.append(doctorant_id)
            
            query += " ORDER BY f.date_debut DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la récupération des formations: {str(e)}")
        finally:
            conn.close()
    
    # ===== SUIVI CRUD =====
    
    def add_suivi(self, doctorant_id: int, suivi_data: Dict[str, Any]) -> int:
        """Add a new follow-up meeting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            INSERT INTO suivi (
                doctorant_id, date_rencontre, type_rencontre, participants,
                points_abordes, decisions, prochaines_etapes, date_prochaine_rencontre, rapport
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            values = (
                doctorant_id,
                suivi_data.get('date_rencontre'),
                suivi_data.get('type_rencontre', 'comite'),
                suivi_data.get('participants', '').strip(),
                suivi_data.get('points_abordes', '').strip(),
                suivi_data.get('decisions', '').strip(),
                suivi_data.get('prochaines_etapes', '').strip(),
                suivi_data.get('date_prochaine_rencontre'),
                suivi_data.get('rapport', '').strip()
            )
            
            cursor.execute(query, values)
            suivi_id = cursor.lastrowid
            
            # Also add as activity
            self.add_activity(doctorant_id, {
                'type': 'reunion',
                'titre': f"Réunion de suivi: {suivi_data.get('type_rencontre', '')}",
                'description': suivi_data.get('points_abordes', ''),
                'date_debut': suivi_data.get('date_rencontre'),
                'statut': 'termine',
                'details': suivi_data.get('decisions', '')
            })
            
            conn.commit()
            return suivi_id
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de l'ajout du suivi: {str(e)}")
        finally:
            conn.close()
    
    def get_suivi(self, doctorant_id: int = None) -> List[Dict[str, Any]]:
        """Get follow-up meetings, optionally filtered by doctorant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            SELECT s.*, d.nom as doctorant_nom, d.prenom as doctorant_prenom
            FROM suivi s
            JOIN doctorants d ON s.doctorant_id = d.id
            '''
            params = []
            
            if doctorant_id:
                query += " WHERE s.doctorant_id = ?"
                params.append(doctorant_id)
            
            query += " ORDER BY s.date_rencontre DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la récupération du suivi: {str(e)}")
        finally:
            conn.close()
    
    # ===== REFERENCE DATA METHODS =====
    
    def get_laboratoires(self) -> List[Dict[str, Any]]:
        """Get all laboratories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM laboratoires ORDER BY nom")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la récupération des laboratoires: {str(e)}")
        finally:
            conn.close()
    
    def get_encadrants(self) -> List[Dict[str, Any]]:
        """Get all supervisors"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT e.*, l.nom as labo_nom 
                FROM encadrants e
                LEFT JOIN laboratoires l ON e.laboratoire_id = l.id
                ORDER BY e.nom, e.prenom
            """)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la récupération des encadrants: {str(e)}")
        finally:
            conn.close()
    
    def add_laboratoire(self, lab_data: Dict[str, Any]) -> int:
        """Add a new laboratory"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            INSERT INTO laboratoires (nom, faculte, responsable, email, telephone, adresse)
            VALUES (?, ?, ?, ?, ?, ?)
            '''
            
            values = (
                lab_data.get('nom', '').strip(),
                lab_data.get('faculte', '').strip(),
                lab_data.get('responsable', '').strip(),
                lab_data.get('email', '').strip(),
                lab_data.get('telephone', '').strip(),
                lab_data.get('adresse', '').strip()
            )
            
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de l'ajout du laboratoire: {str(e)}")
        finally:
            conn.close()
    
    def add_encadrant(self, encadrant_data: Dict[str, Any]) -> int:
        """Add a new supervisor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
            INSERT INTO encadrants (
                nom, prenom, grade, laboratoire_id, email, telephone, specialite, date_embauche
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            values = (
                encadrant_data.get('nom', '').strip(),
                encadrant_data.get('prenom', '').strip(),
                encadrant_data.get('grade', '').strip(),
                encadrant_data.get('laboratoire_id'),
                encadrant_data.get('email', '').strip(),
                encadrant_data.get('telephone', '').strip(),
                encadrant_data.get('specialite', '').strip(),
                encadrant_data.get('date_embauche')
            )
            
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de l'ajout de l'encadrant: {str(e)}")
        finally:
            conn.close()
    
    # ===== STATISTICS METHODS =====
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        try:
            # Total students
            cursor.execute("SELECT COUNT(*) as total FROM doctorants")
            stats['total_students'] = cursor.fetchone()['total']
            
            # Students by status
            cursor.execute('''
                SELECT statut, COUNT(*) as count 
                FROM doctorants 
                GROUP BY statut
            ''')
            stats['by_status'] = {row['statut']: row['count'] for row in cursor.fetchall()}
            
            # Students by year
            cursor.execute('''
                SELECT annee_inscription, COUNT(*) as count 
                FROM doctorants 
                GROUP BY annee_inscription
                ORDER BY annee_inscription DESC
            ''')
            stats['by_year'] = {row['annee_inscription']: row['count'] for row in cursor.fetchall()}
            
            # Students by laboratory
            cursor.execute('''
                SELECT l.nom, COUNT(d.id) as count
                FROM doctorants d
                LEFT JOIN laboratoires l ON d.laboratoire_id = l.id
                GROUP BY d.laboratoire_id
                ORDER BY count DESC
            ''')
            stats['by_laboratory'] = {row['nom'] or 'Non assigné': row['count'] for row in cursor.fetchall()}
            
            # Students by supervisor
            cursor.execute('''
                SELECT e.nom, e.prenom, COUNT(d.id) as count
                FROM doctorants d
                LEFT JOIN encadrants e ON d.directeur_id = e.id
                GROUP BY d.directeur_id
                ORDER BY count DESC
            ''')
            stats['by_supervisor'] = {
                f"{row['nom']} {row['prenom']}": row['count'] 
                for row in cursor.fetchall()
            }
            
            # Total publications
            cursor.execute("SELECT COUNT(*) as total FROM publications")
            stats['total_publications'] = cursor.fetchone()['total']
            
            # Publications by status
            cursor.execute('''
                SELECT statut, COUNT(*) as count 
                FROM publications 
                GROUP BY statut
            ''')
            stats['publications_by_status'] = {row['statut']: row['count'] for row in cursor.fetchall()}
            
            # Recent activities
            cursor.execute('''
                SELECT a.*, d.nom, d.prenom 
                FROM activites a
                JOIN doctorants d ON a.doctorant_id = d.id
                ORDER BY a.date_creation DESC
                LIMIT 10
            ''')
            stats['recent_activities'] = [dict(row) for row in cursor.fetchall()]
            
            # Upcoming deadlines (soutenance prévue dans les 6 mois)
            cursor.execute('''
                SELECT d.*, l.nom as labo_nom
                FROM doctorants d
                LEFT JOIN laboratoires l ON d.laboratoire_id = l.id
                WHERE d.annee_soutenance_prevue IS NOT NULL
                AND d.statut = 'en_cours'
                ORDER BY d.annee_soutenance_prevue
                LIMIT 10
            ''')
            stats['upcoming_deadlines'] = [dict(row) for row in cursor.fetchall()]
            
            # Count of laboratories
            cursor.execute("SELECT COUNT(*) as total FROM laboratoires")
            stats['total_laboratories'] = cursor.fetchone()['total']
            
            # Count of supervisors
            cursor.execute("SELECT COUNT(*) as total FROM encadrants")
            stats['total_supervisors'] = cursor.fetchone()['total']
            
            return stats
            
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors du calcul des statistiques: {str(e)}")
        finally:
            conn.close()
    
    def get_doctorant_statistics(self, doctorant_id: int) -> Dict[str, Any]:
        """Get statistics for a specific doctorant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        try:
            # Publication count
            cursor.execute("SELECT COUNT(*) as count FROM publications WHERE doctorant_id = ?", (doctorant_id,))
            stats['publication_count'] = cursor.fetchone()['count']
            
            # Formation count
            cursor.execute("SELECT COUNT(*) as count FROM formations WHERE doctorant_id = ?", (doctorant_id,))
            stats['formation_count'] = cursor.fetchone()['count']
            
            # Suivi count
            cursor.execute("SELECT COUNT(*) as count FROM suivi WHERE doctorant_id = ?", (doctorant_id,))
            stats['suivi_count'] = cursor.fetchone()['count']
            
            # Activity count by type
            cursor.execute('''
                SELECT type, COUNT(*) as count 
                FROM activites 
                WHERE doctorant_id = ?
                GROUP BY type
            ''', (doctorant_id,))
            stats['activities_by_type'] = {row['type']: row['count'] for row in cursor.fetchall()}
            
            # Last activity
            cursor.execute('''
                SELECT MAX(date_debut) as last_activity 
                FROM activites 
                WHERE doctorant_id = ?
            ''', (doctorant_id,))
            stats['last_activity'] = cursor.fetchone()['last_activity']
            
            # Thesis duration
            cursor.execute('''
                SELECT annee_inscription, annee_soutenance_prevue 
                FROM doctorants 
                WHERE id = ?
            ''', (doctorant_id,))
            row = cursor.fetchone()
            if row:
                stats['thesis_duration'] = {
                    'start_year': row['annee_inscription'],
                    'planned_end': row['annee_soutenance_prevue']
                }
            
            return stats
            
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors du calcul des statistiques du doctorant: {str(e)}")
        finally:
            conn.close()
    
    # ===== UTILITY METHODS =====
    
    def backup_database(self) -> tuple:
        """Create a backup of the database"""
        backup_dir = "data/backups/"
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{backup_dir}backup_{timestamp}.db"
        
        try:
            source = sqlite3.connect(self.db_path)
            dest = sqlite3.connect(backup_file)
            
            # Backup the database
            source.backup(dest)
            
            source.close()
            dest.close()
            
            # Also create a JSON export
            self.export_to_json(f"{backup_dir}backup_{timestamp}.json")
            
            return True, backup_file
        except Exception as e:
            return False, str(e)
    def test_database_operations(self):
        """Test basic database operations"""
        print("\n=== DATABASE TEST ===")
        
        # 1. Test connection
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"✅ Connection successful")
            print(f"✅ Tables found: {[t[0] for t in tables]}")
            conn.close()
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
        
        # 2. Test inserting a doctorant
        print("\nTesting doctorant insertion...")
        try:
            test_data = {
                'nom': 'Test',
                'prenom': 'Student',
                'email': 'test.student@univ.fr',
                'domaine': 'Informatique',
                'laboratoire_id': 1,
                'directeur_id': 1,
                'annee_inscription': 2024,
                'statut': 'en_cours'
            }
            
            doctorant_id = self.add_doctorant(test_data)
            print(f"✅ Test doctorant added with ID: {doctorant_id}")
            
            # 3. Verify insertion
            doctorant = self.get_doctorant(doctorant_id)
            if doctorant:
                print(f"✅ Doctorant retrieved: {doctorant['nom']} {doctorant['prenom']}")
                
                # 4. Clean up test data
                self.delete_doctorant(doctorant_id)
                print(f"✅ Test doctorant deleted")
            else:
                print(f"❌ Failed to retrieve test doctorant")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    def export_to_json(self, filename: str):
        """Export all data to JSON file"""
        data = {
            'doctorants': self.get_all_doctorants(),
            'laboratoires': self.get_laboratoires(),
            'encadrants': self.get_encadrants(),
            'activites': self.get_activities(),
            'publications': self.get_publications(),
            'formations': self.get_formations(),
            'suivi': self.get_suivi(),
            'export_date': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def import_from_json(self, filename: str) -> bool:
        """Import data from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("BEGIN TRANSACTION")
                
                # Clear existing data (in reverse order of foreign keys)
                cursor.execute("DELETE FROM suivi")
                cursor.execute("DELETE FROM formations")
                cursor.execute("DELETE FROM publications")
                cursor.execute("DELETE FROM activites")
                cursor.execute("DELETE FROM doctorants")
                cursor.execute("DELETE FROM encadrants")
                cursor.execute("DELETE FROM laboratoires")
                
                # Import laboratories
                for lab in data.get('laboratoires', []):
                    cursor.execute('''
                        INSERT INTO laboratoires (id, nom, faculte, responsable, email, telephone, adresse)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        lab.get('id'),
                        lab.get('nom'),
                        lab.get('faculte'),
                        lab.get('responsable'),
                        lab.get('email'),
                        lab.get('telephone'),
                        lab.get('adresse')
                    ))
                
                # Import supervisors
                for enc in data.get('encadrants', []):
                    cursor.execute('''
                        INSERT INTO encadrants (id, nom, prenom, grade, laboratoire_id, email, telephone, specialite, date_embauche, statut)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        enc.get('id'),
                        enc.get('nom'),
                        enc.get('prenom'),
                        enc.get('grade'),
                        enc.get('laboratoire_id'),
                        enc.get('email'),
                        enc.get('telephone'),
                        enc.get('specialite'),
                        enc.get('date_embauche'),
                        enc.get('statut', 'actif')
                    ))
                
                # Import doctorants
                for doc in data.get('doctorants', []):
                    cursor.execute('''
                        INSERT INTO doctorants (
                            id, matricule, nom, prenom, email, telephone, date_naissance, nationalite,
                            domaine, laboratoire_id, directeur_id, co_directeur_id, annee_inscription,
                            annee_soutenance_prevue, annee_soutenance_effective, statut, titre_these,
                            resume, mots_cles, financement, montant_financement, adresse, ville, code_postal,
                            date_creation, date_modification
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        doc.get('id'),
                        doc.get('matricule'),
                        doc.get('nom'),
                        doc.get('prenom'),
                        doc.get('email'),
                        doc.get('telephone'),
                        doc.get('date_naissance'),
                        doc.get('nationalite'),
                        doc.get('domaine'),
                        doc.get('laboratoire_id'),
                        doc.get('directeur_id'),
                        doc.get('co_directeur_id'),
                        doc.get('annee_inscription'),
                        doc.get('annee_soutenance_prevue'),
                        doc.get('annee_soutenance_effective'),
                        doc.get('statut'),
                        doc.get('titre_these'),
                        doc.get('resume'),
                        doc.get('mots_cles'),
                        doc.get('financement'),
                        doc.get('montant_financement'),
                        doc.get('adresse'),
                        doc.get('ville'),
                        doc.get('code_postal'),
                        doc.get('date_creation'),
                        doc.get('date_modification')
                    ))
                
                # Import activities
                for act in data.get('activites', []):
                    cursor.execute('''
                        INSERT INTO activites (
                            id, doctorant_id, type, categorie, titre, description, date_debut, date_fin,
                            lieu, statut, details, fichier_joint, date_creation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        act.get('id'),
                        act.get('doctorant_id'),
                        act.get('type'),
                        act.get('categorie'),
                        act.get('titre'),
                        act.get('description'),
                        act.get('date_debut'),
                        act.get('date_fin'),
                        act.get('lieu'),
                        act.get('statut'),
                        act.get('details'),
                        act.get('fichier_joint'),
                        act.get('date_creation')
                    ))
                
                conn.commit()
                return True
                
            except sqlite3.Error:
                conn.rollback()
                raise
            finally:
                conn.close()
                
        except Exception as e:
            raise Exception(f"Erreur lors de l'import: {str(e)}")
    
    # ===== SEARCH AND FILTER HELPERS =====
    
    def get_domaines(self) -> List[str]:
        """Get list of unique domains"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT DISTINCT domaine FROM doctorants WHERE domaine IS NOT NULL AND domaine != '' ORDER BY domaine")
            return [row['domaine'] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_financement_types(self) -> List[str]:
        """Get list of unique financement types"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT DISTINCT financement FROM doctorants WHERE financement IS NOT NULL AND financement != '' ORDER BY financement")
            return [row['financement'] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_inscription_years(self) -> List[int]:
        """Get list of unique inscription years"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT DISTINCT annee_inscription FROM doctorants WHERE annee_inscription IS NOT NULL ORDER BY annee_inscription DESC")
            return [row['annee_inscription'] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_activity_types(self) -> List[str]:
        """Get list of unique activity types"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT DISTINCT type FROM activites ORDER BY type")
            return [row['type'] for row in cursor.fetchall()]
        finally:
            conn.close()
