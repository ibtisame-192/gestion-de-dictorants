# gestion_doctorants/models/doctorant.py
from datetime import datetime

class Doctorant:
    """PhD student model class"""
    
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('soutenu', 'Soutenu'),
        ('abandon', 'Abandon'),
        ('interrompu', 'Interrompu')
    ]
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.matricule = kwargs.get('matricule', '')
        self.nom = kwargs.get('nom', '')
        self.prenom = kwargs.get('prenom', '')
        self.email = kwargs.get('email', '')
        self.telephone = kwargs.get('telephone', '')
        self.date_naissance = kwargs.get('date_naissance')
        self.nationalite = kwargs.get('nationalite', '')
        self.domaine = kwargs.get('domaine', '')
        self.laboratoire_id = kwargs.get('laboratoire_id')
        self.directeur_id = kwargs.get('directeur_id')
        self.co_directeur_id = kwargs.get('co_directeur_id')
        self.annee_inscription = kwargs.get('annee_inscription')
        self.annee_soutenance_prevue = kwargs.get('annee_soutenance_prevue')
        self.annee_soutenance_effective = kwargs.get('annee_soutenance_effective')
        self.statut = kwargs.get('statut', 'en_cours')
        self.titre_these = kwargs.get('titre_these', '')
        self.resume = kwargs.get('resume', '')
        self.mots_cles = kwargs.get('mots_cles', '')
        self.financement = kwargs.get('financement', '')
        self.montant_financement = kwargs.get('montant_financement', 0.0)
        
        # Joined fields
        self.labo_nom = kwargs.get('labo_nom', '')
        self.labo_faculte = kwargs.get('labo_faculte', '')
        self.directeur_nom = kwargs.get('directeur_nom', '')
        self.directeur_prenom = kwargs.get('directeur_prenom', '')
        self.directeur_grade = kwargs.get('directeur_grade', '')
        self.co_directeur_nom = kwargs.get('co_directeur_nom', '')
        self.co_directeur_prenom = kwargs.get('co_directeur_prenom', '')
    
    @property
    def nom_complet(self):
        return f"{self.nom} {self.prenom}"
    
    @property
    def directeur_complet(self):
        if self.directeur_nom and self.directeur_prenom:
            return f"{self.directeur_grade} {self.directeur_nom} {self.directeur_prenom}"
        return ""
    
    @property
    def age(self):
        if self.date_naissance:
            try:
                birth_date = datetime.strptime(self.date_naissance, '%Y-%m-%d')
                today = datetime.now()
                return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            except:
                return None
        return None
    
    @property
    def duree_these(self):
        if self.annee_inscription:
            current_year = datetime.now().year
            return current_year - self.annee_inscription
        return None
    
    def to_dict(self):
        """Convert object to dictionary for database operations"""
        return {
            'matricule': self.matricule,
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'telephone': self.telephone,
            'date_naissance': self.date_naissance,
            'nationalite': self.nationalite,
            'domaine': self.domaine,
            'laboratoire_id': self.laboratoire_id,
            'directeur_id': self.directeur_id,
            'co_directeur_id': self.co_directeur_id,
            'annee_inscription': self.annee_inscription,
            'annee_soutenance_prevue': self.annee_soutenance_prevue,
            'annee_soutenance_effective': self.annee_soutenance_effective,
            'statut': self.statut,
            'titre_these': self.titre_these,
            'resume': self.resume,
            'mots_cles': self.mots_cles,
            'financement': self.financement,
            'montant_financement': self.montant_financement
        }
    
    def __str__(self):
        return f"{self.matricule} - {self.nom_complet}"