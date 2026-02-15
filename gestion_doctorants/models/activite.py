# gestion_doctorants/models/activite.py
class Activite:
    """Activity model class"""
    
    TYPE_CHOICES = [
        ('publication', 'Publication'),
        ('formation', 'Formation'),
        ('seminaire', 'Séminaire'),
        ('conference', 'Conférence'),
        ('these', 'Travail de thèse'),
        ('reunion', 'Réunion'),
        ('autre', 'Autre')
    ]
    
    STATUT_CHOICES = [
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé')
    ]
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.doctorant_id = kwargs.get('doctorant_id')
        self.type = kwargs.get('type', 'autre')
        self.categorie = kwargs.get('categorie', '')
        self.titre = kwargs.get('titre', '')
        self.description = kwargs.get('description', '')
        self.date_debut = kwargs.get('date_debut')
        self.date_fin = kwargs.get('date_fin')
        self.lieu = kwargs.get('lieu', '')
        self.statut = kwargs.get('statut', 'planifie')
        self.details = kwargs.get('details', '')
        self.fichier_joint = kwargs.get('fichier_joint', '')
        
        # Joined fields
        self.doctorant_nom = kwargs.get('doctorant_nom', '')
        self.doctorant_prenom = kwargs.get('doctorant_prenom', '')
    
    @property
    def doctorant_complet(self):
        return f"{self.doctorant_nom} {self.doctorant_prenom}"
    
    def to_dict(self):
        return {
            'doctorant_id': self.doctorant_id,
            'type': self.type,
            'categorie': self.categorie,
            'titre': self.titre,
            'description': self.description,
            'date_debut': self.date_debut,
            'date_fin': self.date_fin,
            'lieu': self.lieu,
            'statut': self.statut,
            'details': self.details,
            'fichier_joint': self.fichier_joint
        }