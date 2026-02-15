# gestion_doctorants/list_files.py
import os

print("Files in gestion_doctorants directory:")
print("=" * 60)

files_and_dirs = os.listdir()
for item in sorted(files_and_dirs):
    if os.path.isfile(item):
        print(f"📄 {item}")
    else:
        print(f"📁 {item}/")

print("\n" + "=" * 60)
print(f"Total: {len(files_and_dirs)} items")