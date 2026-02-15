# test_doctorant_form.py
import tkinter as tk
from interface.doctorants_gui import DoctorantForm
from database import Database

def test_form():
    """Test the doctorant form"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    db = Database()
    
    # Test creating a new doctorant
    form = DoctorantForm(root, db)
    form.show()
    
    # Test editing an existing doctorant (uncomment and set a valid ID)
    # form2 = DoctorantForm(root, db, doctorant_id=1, edit_mode=True)
    # form2.show()

if __name__ == "__main__":
    test_form()