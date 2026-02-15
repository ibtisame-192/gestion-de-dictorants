# gestion_doctorants/fix_window_size.py
import os
import re

def fix_window_size():
    """Fix the window to use full screen space"""
    file_path = "interface/main_window.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for the __init__ method of MainWindow class
    if 'def __init__' in content and 'class MainWindow' in content:
        print("Found MainWindow class")
        
        # First, let's find where the window geometry is set
        lines = content.split('\n')
        new_lines = []
        changes_made = False
        
        for i, line in enumerate(lines):
            # Remove any hardcoded geometry
            if 'self.root.geometry(' in line and '"' in line:
                print(f"Found geometry setting: {line.strip()}")
                # Replace with full screen or maximize
                new_lines.append('        # Maximize window to use full screen')
                new_lines.append('        self.root.state("zoomed")  # Windows')
                new_lines.append('        # Alternative for other OS: self.root.attributes("-zoomed", True)')
                changes_made = True
            elif 'self.root.geometry(' in line:
                # Just in case it's formatted differently
                print(f"Found geometry setting (different format): {line.strip()}")
                new_lines.append('        # Maximize window')
                new_lines.append('        self.root.state("zoomed")')
                changes_made = True
            else:
                new_lines.append(line)
        
        if changes_made:
            # Create backup
            backup_path = "interface/main_window.py.backup_window"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Backup created: {backup_path}")
            
            # Write new content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print("\n✅ Window size fixed! Application will open maximized.")
            return True
        else:
            print("⚠️ No geometry settings found, adding maximize code...")
            return add_maximize_code(content, file_path)
    
    return False

def add_maximize_code(content, file_path):
    """Add maximize code to the __init__ method"""
    lines = content.split('\n')
    new_lines = []
    
    # Find the __init__ method and add maximize after window creation
    in_init = False
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        if 'def __init__' in line and 'class MainWindow' in content[:i]:
            in_init = True
        
        if in_init and 'self.root =' in line and 'Tk' in line:
            # Add maximize after root creation
            new_lines.append('')
            new_lines.append('        # Maximize window to use full screen')
            new_lines.append('        self.root.state("zoomed")  # Windows maximize')
            new_lines.append('')
    
    # Write new content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Added maximize code to __init__ method")
    return True

def create_better_fix():
    """Create a more comprehensive fix for window sizing"""
    template = '''# Add this to the __init__ method of MainWindow class, after creating self.root:

    # Configure window to use full space
    self.root.title("Système de Gestion des Doctorants - Université")
    
    # Get screen dimensions
    screen_width = self.root.winfo_screenwidth()
    screen_height = self.root.winfo_screenheight()
    
    # Set to 95% of screen size (leaving some margin)
    window_width = int(screen_width * 0.95)
    window_height = int(screen_height * 0.95)
    
    # Calculate position to center
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    
    # Set geometry
    self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    
    # Make window resizable
    self.root.resizable(True, True)
    
    # Alternative: Maximize window (Windows)
    # self.root.state("zoomed")
    
    # Alternative: Fullscreen (F11 to exit)
    # self.root.attributes("-fullscreen", True)
'''
    
    print("\nHere's the code to add to interface/main_window.py:")
    print("=" * 60)
    print(template)
    print("=" * 60)
    
    # Let me directly edit the file for you
    file_path = "interface/main_window.py"
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find where to insert the code (after self.root creation)
        if 'self.root =' in content and 'Tk' in content:
            # Create backup
            backup_path = "interface/main_window.py.backup_fullscreen"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Backup created: {backup_path}")
            
            # Insert the window configuration code
            insert_code = '''        # Configure window to use full space
        self.root.title("Système de Gestion des Doctorants - Université")
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set to 95% of screen size (leaving some margin)
        window_width = int(screen_width * 0.95)
        window_height = int(screen_height * 0.95)
        
        # Calculate position to center
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        # Set geometry
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Make window resizable
        self.root.resizable(True, True)'''
        
            # Find the pattern and insert after it
            pattern = 'self.root = tk.Tk\(\)'
            match = re.search(pattern, content)
            
            if match:
                pos = match.end()
                new_content = content[:pos] + '\n\n' + insert_code + '\n\n' + content[pos:]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("✅ Window configuration added successfully!")
                print("   The application will now open at 95% of screen size, centered.")
                return True
    
    print("⚠️ Could not automatically insert the code.")
    print("   Please add the code manually to the __init__ method.")
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("FIXING WINDOW SIZE - FULL SCREEN")
    print("=" * 60)
    
    print("\nChoose fix method:")
    print("1. Maximize window (Windows 'zoomed' state)")
    print("2. Set to 95% of screen, centered (recommended)")
    print("3. Fullscreen mode (F11-style)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        success = fix_window_size()
    elif choice == '2':
        success = create_better_fix()
    elif choice == '3':
        print("\nFor fullscreen mode, add this to __init__ method:")
        print('self.root.attributes("-fullscreen", True)')
        success = False
    else:
        print("Invalid choice")
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ WINDOW SIZE FIXED!")
        print("\nThe application will now use more screen space.")
    else:
        print("⚠️ Manual editing may be required.")
    
    print("\nRun 'python main.py' to test the new window size.")
    print("=" * 60)