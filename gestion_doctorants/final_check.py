# final_check.py
from database import Database

db = Database()
print("=" * 60)
print("FINAL SYSTEM CHECK")
print("=" * 60)

doctorants = db.get_all_doctorants()
print(f"✅ Doctorants in system: {len(doctorants)}")

labs = db.get_laboratoires()
print(f"✅ Laboratories: {len(labs)}")

supervisors = db.get_encadrants()
print(f"✅ Supervisors: {len(supervisors)}")

activities = db.get_activities()
print(f"✅ Activities: {len(activities)}")

print("\nSample Doctorants:")
for i, doc in enumerate(doctorants[:3], 1):
    print(f"  {i}. {doc['nom']} {doc['prenom']} - {doc['domaine']} ({doc['statut']})")

print("\n" + "=" * 60)
print("SYSTEM READY FOR USE! 🎉")
print("=" * 60)