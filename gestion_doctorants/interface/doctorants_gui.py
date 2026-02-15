# gestion_doctorants/interface/doctorants_gui.py
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.toast import ToastNotification

class DoctorantForm:
    def __init__(self, parent, db, doctorant_id=None, edit_mode=False):
        """
        Initialize the modern doctorant form
        """
        self.parent = parent
        self.db = db
        self.doctorant_id = doctorant_id
        self.edit_mode = edit_mode
        self.current_tab = 0
        
        # Create window using ttkbootstrap Toplevel
        self.window = ttk.Toplevel(parent)
        self.window.title("Fiche Doctorant" if doctorant_id else "Nouveau Doctorant")
        self.window.geometry("1100x800")
        
        # Determine if parent is a root or toplevel to set transient
        try:
            self.window.transient(parent)
        except:
            pass
            
        self.window.grab_set()
        
        # Configure grid layout
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        
        # Variables
        self.photo_path = None
        
        # Initialize data
        self.load_doctorant_data()
        self.load_reference_data()
        
        # Create UI
        self.create_header()
        self.create_notebook()
        self.create_footer()
        
        # Center window
        self.center_window()
        
        # Bind events
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def load_doctorant_data(self):
        if self.doctorant_id:
            self.doctorant_data = self.db.get_doctorant(self.doctorant_id)
            if not self.doctorant_data:
                Messagebox.show_error("Doctorant non trouvé", "Erreur")
                self.window.destroy()
                return
        else:
            self.doctorant_data = {}
    
    def load_reference_data(self):
        # Mocking empty lists if DB fails or returns nothing for safety
        self.laboratoires = self.db.get_laboratoires() or []
        self.encadrants = self.db.get_encadrants() or []
        
        self.lab_dict = {lab['id']: f"{lab['nom']} ({lab['faculte']})" for lab in self.laboratoires}
        self.sup_dict = {sup['id']: f"{sup['grade']} {sup['nom']} {sup['prenom']}" for sup in self.encadrants}
    
    def create_header(self):
        """Create a modern header"""
        header_frame = ttk.Frame(self.window, padding=20, bootstyle="primary")
        header_frame.grid(row=0, column=0, sticky="ew")
        
        # Title
        if self.doctorant_id:
            nom_complet = f"{self.doctorant_data.get('nom', '')} {self.doctorant_data.get('prenom', '')}"
            title_text = f"Fiche Doctorant : {nom_complet}"
            icon = "👤"
        else:
            title_text = "Création Nouveau Doctorant"
            icon = "✨"
        
        # Title Label with inverse color for contrast against primary background
        title_label = ttk.Label(
            header_frame,
            text=f"{icon}  {title_text}",
            font=("Helvetica", 16, "bold"),
            bootstyle="inverse-primary"
        )
        title_label.pack(side="left")
        
        # Close button (modern outline style)
        close_btn = ttk.Button(
            header_frame,
            text="Fermer",
            bootstyle="light-outline",
            command=self.on_close
        )
        close_btn.pack(side="right")
    
    def create_notebook(self):
        """Create modern flat notebook"""
        self.notebook = ttk.Notebook(self.window, bootstyle="primary")
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        self.info_tab = ttk.Frame(self.notebook, padding=10)
        self.these_tab = ttk.Frame(self.notebook, padding=10)
        self.activites_tab = ttk.Frame(self.notebook, padding=10)
        self.documents_tab = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.info_tab, text="  Informations  ")
        self.notebook.add(self.these_tab, text="  Thèse & Encadrement  ")
        self.notebook.add(self.activites_tab, text="  Activités  ")
        self.notebook.add(self.documents_tab, text="  Documents  ")
        
        self.create_info_tab()
        self.create_these_tab()
        self.create_activites_tab()
        self.create_documents_tab()
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_info_tab(self):
        # Using a ScrolledFrame logic via simple canvas/frame for vertical scrolling
        container = ttk.Frame(self.info_tab)
        container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Photo Section ---
        photo_frame = ttk.Labelframe(scrollable_frame, text="Photo de profil", padding=15, bootstyle="info")
        photo_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=10, sticky="n")
        
        self.photo_label = ttk.Label(photo_frame, text="👤", font=("Arial", 64), anchor="center")
        self.photo_label.pack(pady=10, fill="x")
        
        ttk.Button(photo_frame, text="Importer", bootstyle="info-outline", command=self.choose_photo).pack(pady=5, fill="x")
        ttk.Button(photo_frame, text="Supprimer", bootstyle="danger-outline", command=self.remove_photo).pack(pady=5, fill="x")

        # --- Personal Info Section ---
        info_frame = ttk.Labelframe(scrollable_frame, text="État Civil", padding=15, bootstyle="primary")
        info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Helper to create rows cleaner
        def add_entry(parent, label_text, var, r, c=1, width=30):
            ttk.Label(parent, text=label_text).grid(row=r, column=0, sticky="w", pady=10)
            entry = ttk.Entry(parent, textvariable=var, width=width)
            entry.grid(row=r, column=c, sticky="ew", pady=10, padx=(10, 0))
            return entry

        row = 0
        self.matricule_var = tk.StringVar(value=self.doctorant_data.get('matricule', ''))
        add_entry(info_frame, "Matricule", self.matricule_var, row)
        row += 1
        
        self.nom_var = tk.StringVar(value=self.doctorant_data.get('nom', ''))
        add_entry(info_frame, "Nom *", self.nom_var, row)
        row += 1
        
        self.prenom_var = tk.StringVar(value=self.doctorant_data.get('prenom', ''))
        add_entry(info_frame, "Prénom *", self.prenom_var, row)
        row += 1

        self.email_var = tk.StringVar(value=self.doctorant_data.get('email', ''))
        add_entry(info_frame, "Email", self.email_var, row)
        row += 1
        
        self.telephone_var = tk.StringVar(value=self.doctorant_data.get('telephone', ''))
        add_entry(info_frame, "Téléphone", self.telephone_var, row)
        row += 1

        # Modern Date Picker
        ttk.Label(info_frame, text="Date de naissance").grid(row=row, column=0, sticky="w", pady=10)
        self.date_naissance_entry = ttk.DateEntry(info_frame, bootstyle="primary")
        # Try setting date if exists
        try:
            if self.doctorant_data.get('date_naissance'):
                self.date_naissance_entry.entry.insert(0, self.doctorant_data.get('date_naissance'))
        except: pass
        self.date_naissance_entry.grid(row=row, column=1, sticky="w", pady=10, padx=(10, 0))
        row += 1

        self.nationalite_var = tk.StringVar(value=self.doctorant_data.get('nationalite', ''))
        add_entry(info_frame, "Nationalité", self.nationalite_var, row)

        # --- Contact & Status Grid ---
        contact_frame = ttk.Labelframe(scrollable_frame, text="Coordonnées", padding=15, bootstyle="secondary")
        contact_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        contact_frame.grid_columnconfigure(1, weight=1)

        row_c = 0
        ttk.Label(contact_frame, text="Adresse").grid(row=row_c, column=0, sticky="nw", pady=10)
        self.adresse_var = tk.StringVar(value=self.doctorant_data.get('adresse', ''))
        # Using ScrolledText for multiline
        self.adresse_text_widget = ScrolledText(contact_frame, height=3, width=30, bootstyle="round")
        self.adresse_text_widget.text.insert("1.0", self.adresse_var.get())
        self.adresse_text_widget.grid(row=row_c, column=1, sticky="ew", pady=10, padx=(10,0))
        row_c +=1

        self.ville_var = tk.StringVar(value=self.doctorant_data.get('ville', ''))
        add_entry(contact_frame, "Ville", self.ville_var, row_c)
        row_c += 1
        
        self.cp_var = tk.StringVar(value=self.doctorant_data.get('code_postal', ''))
        add_entry(contact_frame, "Code Postal", self.cp_var, row_c)

        # --- Status ---
        status_frame = ttk.Labelframe(scrollable_frame, text="Statut Actuel", padding=15, bootstyle="warning")
        status_frame.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        self.statut_var = tk.StringVar(value=self.doctorant_data.get('statut', 'en_cours'))
        statuses = [("En cours", "en_cours"), ("Soutenu", "soutenu"), ("Abandon", "abandon"), ("Interrompu", "interrompu")]
        
        for i, (text, value) in enumerate(statuses):
            ttk.Radiobutton(status_frame, text=text, variable=self.statut_var, value=value, bootstyle="warning").pack(side="left", padx=15)

    def create_these_tab(self):
        # Main scroll container setup (abbreviated, same as info tab)
        container = ttk.Frame(self.these_tab)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Thesis Info ---
        these_frame = ttk.Labelframe(scrollable_frame, text="Détails de la Thèse", padding=15, bootstyle="info")
        these_frame.pack(fill="x", padx=10, pady=10)
        these_frame.grid_columnconfigure(1, weight=1)

        # Title (ScrolledText)
        ttk.Label(these_frame, text="Titre de la thèse *").grid(row=0, column=0, sticky="nw", pady=10)
        self.titre_these_text_widget = ScrolledText(these_frame, height=3, width=50, bootstyle="round")
        self.titre_these_text_widget.text.insert("1.0", self.doctorant_data.get('titre_these', ''))
        self.titre_these_text_widget.grid(row=0, column=1, sticky="ew", pady=10, padx=(10,0))

        # Domaine (Combobox)
        ttk.Label(these_frame, text="Domaine").grid(row=1, column=0, sticky="w", pady=10)
        self.domaine_var = tk.StringVar(value=self.doctorant_data.get('domaine', ''))
        domaines = ["Informatique", "Mathématiques", "Physique", "Chimie", "Biologie", "Sciences Sociales", "Lettres", "Droit", "Autre"]
        ttk.Combobox(these_frame, textvariable=self.domaine_var, values=domaines, state="readonly", bootstyle="info").grid(row=1, column=1, sticky="w", pady=10, padx=(10,0))

        # Abstract (ScrolledText)
        ttk.Label(these_frame, text="Résumé").grid(row=3, column=0, sticky="nw", pady=10)
        self.resume_text_widget = ScrolledText(these_frame, height=5, width=50)
        self.resume_text_widget.text.insert("1.0", self.doctorant_data.get('resume', ''))
        self.resume_text_widget.grid(row=3, column=1, sticky="ew", pady=10, padx=(10,0))
        
        # Mots clés
        ttk.Label(these_frame, text="Mots-clés").grid(row=2, column=0, sticky="w", pady=10)
        self.mots_cles_text_widget = ttk.Entry(these_frame, width=50)
        self.mots_cles_text_widget.insert(0, self.doctorant_data.get('mots_cles', ''))
        self.mots_cles_text_widget.grid(row=2, column=1, sticky="ew", pady=10, padx=(10,0))

        # --- Dates ---
        dates_frame = ttk.Labelframe(scrollable_frame, text="Calendrier", padding=15, bootstyle="success")
        dates_frame.pack(fill="x", padx=10, pady=10)
        
        current_year = datetime.now().year
        years = list(range(current_year - 10, current_year + 5))
        
        def add_year_combo(parent, label, var_name, r, c):
            ttk.Label(parent, text=label).grid(row=r, column=c, sticky="w", padx=5, pady=5)
            val = self.doctorant_data.get(var_name, '')
            if not val and var_name == 'annee_inscription': val = current_year
            var = tk.StringVar(value=val)
            setattr(self, f"{var_name}_var", var)
            ttk.Combobox(parent, textvariable=var, values=years, state="readonly", width=10).grid(row=r, column=c+1, padx=5, pady=5)

        add_year_combo(dates_frame, "Inscription *", 'annee_inscription', 0, 0)
        add_year_combo(dates_frame, "Soutenance Prévue", 'annee_soutenance_prevue', 0, 2)
        add_year_combo(dates_frame, "Soutenance Effective", 'annee_soutenance_effective', 0, 4)

        # --- Supervision ---
        sup_frame = ttk.Labelframe(scrollable_frame, text="Encadrement", padding=15, bootstyle="primary")
        sup_frame.pack(fill="x", padx=10, pady=10)
        
        # Lab
        ttk.Label(sup_frame, text="Laboratoire *").grid(row=0, column=0, sticky="w", pady=10)
        self.laboratoire_var = tk.StringVar()
        if self.doctorant_id and self.doctorant_data.get('laboratoire_id'):
            self.laboratoire_var.set(self.lab_dict.get(self.doctorant_data['laboratoire_id'], ''))
        ttk.Combobox(sup_frame, textvariable=self.laboratoire_var, values=list(self.lab_dict.values()), state="readonly", width=40).grid(row=0, column=1, sticky="w", pady=10, padx=(10,0))

        # Director
        ttk.Label(sup_frame, text="Directeur *").grid(row=1, column=0, sticky="w", pady=10)
        self.directeur_var = tk.StringVar()
        if self.doctorant_id and self.doctorant_data.get('directeur_id'):
             self.directeur_var.set(self.sup_dict.get(self.doctorant_data['directeur_id'], ''))
        ttk.Combobox(sup_frame, textvariable=self.directeur_var, values=list(self.sup_dict.values()), state="readonly", width=40).grid(row=1, column=1, sticky="w", pady=10, padx=(10,0))
        
        # Co-Director
        ttk.Label(sup_frame, text="Co-Directeur").grid(row=2, column=0, sticky="w", pady=10)
        self.co_directeur_var = tk.StringVar()
        if self.doctorant_id and self.doctorant_data.get('co_directeur_id'):
             self.co_directeur_var.set(self.sup_dict.get(self.doctorant_data['co_directeur_id'], ''))
        ttk.Combobox(sup_frame, textvariable=self.co_directeur_var, values=list(self.sup_dict.values()), state="readonly", width=40).grid(row=2, column=1, sticky="w", pady=10, padx=(10,0))

    def create_activites_tab(self):
        # Using a sub-notebook with a different style to differentiate
        self.activites_notebook = ttk.Notebook(self.activites_tab, bootstyle="secondary")
        self.activites_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.publications_tab = ttk.Frame(self.activites_notebook, padding=10)
        self.formations_tab = ttk.Frame(self.activites_notebook, padding=10)
        self.timeline_tab = ttk.Frame(self.activites_notebook, padding=10)
        
        self.activites_notebook.add(self.publications_tab, text=" Publications ")
        self.activites_notebook.add(self.formations_tab, text=" Formations ")
        self.activites_notebook.add(self.timeline_tab, text=" Timeline ")
        
        self.create_publications_tab()
        self.create_timeline_tab()

    def create_publications_tab(self):
        # Modern Toolbar
        toolbar = ttk.Frame(self.publications_tab)
        toolbar.pack(fill="x", pady=(0, 10))
        
        ttk.Button(toolbar, text="Ajouter", bootstyle="success", command=self.add_publication).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Modifier", bootstyle="info", command=self.edit_publication).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Supprimer", bootstyle="danger", command=self.delete_publication).pack(side="left", padx=2)
        
        # Modern Treeview
        columns = ('Titre', 'Revue', 'Date', 'Statut')
        self.publications_tree = ttk.Treeview(self.publications_tab, columns=columns, show='headings', bootstyle="info")
        
        for col in columns:
            self.publications_tree.heading(col, text=col)
            self.publications_tree.column(col, width=100)
            
        self.publications_tree.pack(fill="both", expand=True)

    def create_timeline_tab(self):
        # Simplified Timeline with modern aesthetics
        container = ttk.Frame(self.timeline_tab)
        container.pack(fill="both", expand=True)
        
        ttk.Label(container, text="Parcours Doctoral", font=("Helvetica", 12, "bold"), bootstyle="secondary").pack(pady=10)
        
        self.timeline_canvas = tk.Canvas(container, bg="#ffffff", height=300, highlightthickness=0)
        self.timeline_canvas.pack(fill="x", padx=20)
        
        # Timeline update trigger
        if self.doctorant_id:
            self.window.after(100, self.update_timeline)

    def create_documents_tab(self):
        main_frame = ttk.Frame(self.documents_tab)
        main_frame.pack(fill="both", expand=True)
        
        # Drag and drop zone visual simulation
        drop_zone = ttk.Label(main_frame, text="📂 Zone de documents\n(Glisser-déposer ou cliquer pour ajouter)", 
                              bootstyle="secondary-inverse", anchor="center", font=("Helvetica", 11))
        drop_zone.pack(fill="x", pady=20, ipady=20)
        
        # List
        columns = ('Nom', 'Type', 'Date')
        self.documents_tree = ttk.Treeview(main_frame, columns=columns, show='headings', bootstyle="primary")
        for col in columns:
            self.documents_tree.heading(col, text=col)
        self.documents_tree.pack(fill="both", expand=True)

    def create_footer(self):
        footer_frame = ttk.Frame(self.window, padding=15, bootstyle="light")
        footer_frame.grid(row=2, column=0, sticky="ew")
        
        ttk.Separator(footer_frame).pack(fill="x", pady=(0, 10))
        
        # Action Buttons
        save_text = "Enregistrer les modifications" if self.edit_mode else "Créer le doctorant"
        
        # Save is Primary/Success
        ttk.Button(footer_frame, text=save_text, command=self.save_doctorant, bootstyle="success", width=25).pack(side="right", padx=5)
        
        # Cancel is secondary/link
        ttk.Button(footer_frame, text="Annuler", command=self.on_close, bootstyle="secondary-outline").pack(side="right", padx=5)

    def update_timeline(self):
        if not self.doctorant_id: return
        self.timeline_canvas.delete("all")
        w = self.timeline_canvas.winfo_width()
        h = self.timeline_canvas.winfo_height()
        cy = h / 2
        
        # Modern line
        self.timeline_canvas.create_line(50, cy, w-50, cy, width=4, fill="#BDC3C7", capstyle="round")
        
        # Draw dummy points
        points = [("Inscription", 0.1), ("Formation 1", 0.3), ("Article", 0.6), ("Soutenance", 0.9)]
        for text, pct in points:
            x = 50 + (w-100) * pct
            # Circle
            self.timeline_canvas.create_oval(x-8, cy-8, x+8, cy+8, fill="#3498DB", outline="white", width=2)
            # Text
            self.timeline_canvas.create_text(x, cy+25, text=text, font=("Segoe UI", 9), fill="#2C3E50")

    def get_form_data(self):
        # Extract data logic - largely unchanged but adapted for widgets
        data = {
            'matricule': self.matricule_var.get(),
            'nom': self.nom_var.get(),
            'prenom': self.prenom_var.get(),
            'email': self.email_var.get(),
            'telephone': self.telephone_var.get(),
            'date_naissance': self.date_naissance_entry.entry.get(), # DateEntry specific
            'nationalite': self.nationalite_var.get(),
            'domaine': self.domaine_var.get(),
            'annee_inscription': self.annee_inscription_var.get(),
            'statut': self.statut_var.get(),
            'titre_these': self.titre_these_text_widget.text.get("1.0", "end-1c").strip(), # ScrolledText
            'resume': self.resume_text_widget.text.get("1.0", "end-1c").strip(),
            'mots_cles': self.mots_cles_text_widget.get(),
            'adresse': self.adresse_text_widget.text.get("1.0", "end-1c").strip(),
            'ville': self.ville_var.get(),
            'code_postal': self.cp_var.get(),
        }
        
        # Resolve foreign keys
        lab_text = self.laboratoire_var.get()
        for lid, name in self.lab_dict.items():
            if name == lab_text: data['laboratoire_id'] = lid; break
            
        dir_text = self.directeur_var.get()
        for did, name in self.sup_dict.items():
            if name == dir_text: data['directeur_id'] = did; break

        co_dir_text = self.co_directeur_var.get()
        for cid, name in self.sup_dict.items():
            if name == co_dir_text: data['co_directeur_id'] = cid; break
            
        return data
    def save_doctorant(self):
            data = self.get_form_data()
            
            # 1. Validation de base
            if not data.get('nom') or not data.get('prenom'):
                Messagebox.show_error("Le nom et le prénom sont requis.", "Validation")
                return

            # 2. Changer le curseur en mode "chargement" pour éviter le double clic
            self.window.config(cursor="watch")
            self.window.update_idletasks()

            try:
                if self.doctorant_id:
                    # MISE À JOUR
                    success = self.db.update_doctorant(self.doctorant_id, data)
                    if success:
                        ToastNotification(
                            title="Succès", 
                            message="Les modifications ont été enregistrées.", 
                            duration=3000, 
                            bootstyle="success"
                        ).show_toast()
                        # On ferme la fenêtre après un court délai
                        self.window.after(800, self.window.destroy)
                else:
                    # CRÉATION
                    new_id = self.db.add_doctorant(data)
                    if new_id:
                        ToastNotification(
                            title="Succès", 
                            message="Nouveau doctorant ajouté avec succès.", 
                            duration=3000, 
                            bootstyle="success"
                        ).show_toast()
                        self.window.after(800, self.window.destroy)

            except Exception as e:
                # En cas d'erreur "locked", on affiche un message clair
                error_msg = str(e)
                if "locked" in error_msg.lower():
                    Messagebox.show_error(
                        "La base de données est occupée par une autre opération.\n"
                        "Veuillez fermer les autres fenêtres ou DB Browser et réessayer.", 
                        "Base de données verrouillée"
                    )
                else:
                    Messagebox.show_error(f"Erreur technique: {error_msg}", "Erreur")
            
            finally:
                # 3. Remettre le curseur normal
                if self.window.winfo_exists():
                    self.window.config(cursor="")
        # Stubs for missing methods to prevent crashing
    def center_window(self):
        self.window.update_idletasks()
        w, h = self.window.winfo_width(), self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f'{w}x{h}+{x}+{y}')

    def on_close(self):
        self.window.destroy()
    def choose_photo(self): pass
    def remove_photo(self): pass
    def on_tab_changed(self, event): pass
    def add_publication(self): pass
    def edit_publication(self): pass
    def delete_publication(self): pass
    def show(self):
        """
        Affiche la fenêtre et bloque l'exécution du parent tant qu'elle est ouverte.
        Nécessaire si votre contrôleur appelle form.show()
        """
        # S'assure que la fenêtre est bien au premier plan
        self.window.lift()
        self.window.focus_force()
        
        # Attend que la fenêtre soit détruite avant de redonner la main au code parent
        self.window.wait_window()