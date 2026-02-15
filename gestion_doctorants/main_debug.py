# gestion_doctorants/main_debug.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import traceback

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main_debug():
    """Debug version of main application"""
    print("=" * 60)
    print("DEBUG MODE - Gestion des Doctorants")
    print("=" * 60)
    
    try:
        from database import Database
        
        # Create database instance
        print("1. Initializing database...")
        db = Database()
        print("   ✅ Database ready")
        
        # Create main window
        print("2. Creating main window...")
        root = tk.Tk()
        
        # Set window properties
        root.title("Système de Gestion des Doctorants - DEBUG")
        root.geometry("1200x700")
        
        # Make window always on top for debugging
        root.attributes('-topmost', True)
        
        # Add a visible label
        label = ttk.Label(root, text="Application is running!", font=("Arial", 16))
        label.pack(pady=50)
        
        # Add a button to load the real interface
        def load_real_interface():
            label.destroy()
            button.destroy()
            print("3. Loading real interface...")
            try:
                from interface.main_window import MainWindow
                app = MainWindow(root, db)
                print("   ✅ Interface loaded successfully")
                root.attributes('-topmost', False)  # Remove always on top
            except Exception as e:
                print(f"   ❌ Error loading interface: {str(e)}")
                error_label = ttk.Label(root, text=f"Error: {str(e)}", foreground="red")
                error_label.pack(pady=20)
                traceback.print_exc()
        
        button = ttk.Button(root, text="Load Full Interface", command=load_real_interface)
        button.pack(pady=20)
        
        # Add status label
        status = ttk.Label(root, text="Click button above to load the full application")
        status.pack(pady=10)
        
        # Center window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        print("4. Starting main loop...")
        print("   Window should appear now")
        print("   Close window to exit")
        
        root.mainloop()
        
        print("\n✅ Application closed successfully")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        traceback.print_exc()
        messagebox.showerror("Error", f"Application failed to start:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main_debug()