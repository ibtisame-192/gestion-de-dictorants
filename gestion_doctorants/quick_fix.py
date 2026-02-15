# gestion_doctorants/quick_fix.py
import os

# Read the file
with open("interface/main_window.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the annoying message box with a silent update
new_content = content.replace(
    '''    def refresh_dashboard(self):
        """Refresh dashboard data"""
        self.update_dashboard()
        messagebox.showinfo("Actualisation", "Tableau de bord actualisé")''',
    
    '''    def refresh_dashboard(self):
        """Refresh dashboard data - silent update"""
        self.update_dashboard()
        # Dashboard updated silently without annoying popup'''
)

# Write back the fixed content
with open("interface/main_window.py", 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Fixed! The annoying 'Tableau de bord actualisé' popup has been removed.")
print("   The dashboard will now refresh silently.")
print("\nRun 'python main.py' to test the fix.")