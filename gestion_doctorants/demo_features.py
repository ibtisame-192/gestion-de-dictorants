# gestion_doctorants/demo_features.py
import sys
from database import Database

def demo_features():
    """Demonstrate all application features"""
    print("=" * 70)
    print("GESTION DOCTORANTS - FEATURE DEMONSTRATION")
    print("=" * 70)
    
    db = Database()
    
    print("\n📊 CURRENT DATABASE STATISTICS:")
    print("-" * 40)
    
    stats = db.get_statistics()
    
    print(f"Total Doctorants: {stats.get('total_students', 0)}")
    print(f"By Status: {stats.get('by_status', {})}")
    print(f"Total Laboratories: {stats.get('total_laboratories', 0)}")
    print(f"Total Supervisors: {stats.get('total_supervisors', 0)}")
    
    print("\n🏛️ LABORATORIES:")
    print("-" * 40)
    labs = db.get_laboratoires()
    for lab in labs:
        print(f"  • {lab['nom']} ({lab['faculte']})")
        print(f"    Responsable: {lab.get('responsable', 'N/A')}")
    
    print("\n👨‍🏫 SUPERVISORS:")
    print("-" * 40)
    supervisors = db.get_encadrants()
    for sup in supervisors[:5]:  # Show first 5
        print(f"  • {sup['grade']} {sup['nom']} {sup['prenom']}")
        print(f"    Spécialité: {sup.get('specialite', 'N/A')}")
        if sup.get('labo_nom'):
            print(f"    Laboratoire: {sup['labo_nom']}")
    
    print("\n👨‍🎓 DOCTORANTS:")
    print("-" * 40)
    doctorants = db.get_all_doctorants()
    if doctorants:
        for doc in doctorants:
            status_text = {
                'en_cours': '📚 En cours',
                'soutenu': '🎓 Soutenu',
                'abandon': '❌ Abandon'
            }.get(doc['statut'], doc['statut'])
            
            print(f"  • {doc['nom']} {doc['prenom']}")
            print(f"    {status_text} | {doc.get('domaine', 'N/A')}")
            print(f"    Laboratoire: {doc.get('labo_nom', 'N/A')}")
            print(f"    Directeur: {doc.get('directeur_nom', 'N/A')} {doc.get('directeur_prenom', 'N/A')}")
            if doc.get('titre_these'):
                print(f"    Thèse: {doc['titre_these'][:60]}...")
            print()
    else:
        print("  No doctorants found. Add some using the application!")
    
    print("\n🔍 SEARCH EXAMPLES:")
    print("-" * 40)
    
    # Search by domain
    print("Search for 'Informatique' domain:")
    results = db.search_doctorants({'domaine': 'Informatique'})
    print(f"  Found: {len(results)} doctorant(s)")
    
    # Search by status
    print("\nSearch for 'en_cours' status:")
    results = db.search_doctorants({'statut': 'en_cours'})
    print(f"  Found: {len(results)} doctorant(s)")
    
    print("\n🎯 AVAILABLE FEATURES:")
    print("-" * 40)
    features = [
        "✅ Complete CRUD for doctorants",
        "✅ Activity tracking (publications, formations, seminars)",
        "✅ Advanced search with filters",
        "✅ Statistics dashboard",
        "✅ Laboratory and supervisor management",
        "✅ Follow-up meeting tracking",
        "✅ Database backup and export",
        "✅ User-friendly GUI interface"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n🚀 GETTING STARTED:")
    print("-" * 40)
    print("To start the application:")
    print("  1. Run: python main.py")
    print("  2. Use the 'Tableau de bord' for overview")
    print("  3. Use 'Doctorants' tab to manage students")
    print("  4. Use 'Recherche avancée' for filtered searches")
    print("  5. Use 'Activités' to track student progress")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE! 🎉")
    print("=" * 70)

if __name__ == "__main__":
    demo_features()