# gestion_doctorants/check_current_location.py
import os

print("Current working directory:", os.getcwd())
print("\nFiles and folders in current directory:")
print("-" * 40)

for item in os.listdir():
    if os.path.isfile(item):
        print(f"📄 {item}")
    else:
        print(f"📁 {item}/")

print("\n" + "=" * 40)
print("Checking for database.py...")

# Look for database.py in current directory and parent
possible_paths = [
    "database.py",
    "gestion_doctorants/database.py",
    "../database.py"
]

for path in possible_paths:
    if os.path.exists(path):
        print(f"✅ Found: {path}")
        break
else:
    print("❌ database.py not found in common locations")