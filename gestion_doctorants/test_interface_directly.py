# gestion_doctorants/test_interface_directly.py
import tkinter as tk
from database import Database

print("Testing Interface Directly")
print("=" * 60)

root = tk.Tk()
root.title("Direct Test")
root.geometry("800x600")

# Create database
db = Database()

# Try to create a simple version of the interface
try:
    from interface.doctorants_gui import DoctorantForm
    
    # Test with first doctorant
    doctorants = db.get_all_doctorants()
    if doctorants:
        print(f"Found {len(doctorants)} doctorants")
        print("Opening doctorant form...")
        
        form = DoctorantForm(root, db, doctorants[0]['id'])
        print("✅ Doctorant form opened successfully")
        
        # Don't show it yet, just test creation
        form.window.destroy()
        print("Form destroyed (test only)")
    else:
        print("No doctorants found")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

# Create a simple button to exit
button = tk.Button(root, text="Test Successful! Click to exit", command=root.destroy)
button.pack(pady=50)

# Center window
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{width}x{height}+{x}+{y}')

print("\n✅ Test completed. Window should appear.")
print("Click the button to exit.")

root.mainloop()