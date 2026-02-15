# gestion_doctorants/main.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from interface.main_window import MainWindow

def main():
    """Main entry point of the application"""
    try:
        # Create database instance
        db = Database()
        
        # Create main window
        root = tk.Tk()
        
        # Configure style
        style = ttk.Style(root)
        
        # Try to use a modern theme if available
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Configure colors and fonts
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Error.TLabel', foreground='red')
        
        # Create main application window
        app = MainWindow(root, db)
        
        # Center window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Erreur d'initialisation", 
                           f"Une erreur est survenue lors du démarrage:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()