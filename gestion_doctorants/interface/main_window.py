import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image, ImageTk


class MainWindow:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        
        # =========================================================================
        # 1. WINDOW SETUP & STYLE CONFIGURATION
        # =========================================================================
        self.root.title("Système de Gestion des Doctorants")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{int(screen_width)}x{int(screen_height)}+0+0")
        
        # Colors Palette
        self.colors = {
            "bg_main": "#f3f4f6",     # Light Gray
            "bg_sidebar": "#1e293b",  # Dark Slate
            "sidebar_hover": "#334155",
            "card_bg": "#ffffff",
            "primary": "#2563eb",     # Blue
            "success": "#10b981",     # Green
            "warning": "#f59e0b",     # Orange
            "danger": "#ef4444",      # Red
            "purple": "#8b5cf6",      # Purple
            "text_main": "#1f2937",
            "text_light": "#9ca3af"
        }
        
        self.root.configure(bg=self.colors["bg_main"])
        
        # State Variables
        self.current_student_id = None
        self.stats_cards = {}         # For updating stat values
        self.pages = {}               # Page frames
        self._search_after_id = None  # For debouncing
        self.image_refs = []          # Prevent PhotoImage garbage collection
        
        # Initialize UI
        self._setup_styles()
        self._add_rounded_rect_capability()
        self._build_main_layout()
        self._build_pages()
        
        # Start on Dashboard
        self.switch_page("Dashboard")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                        background="white",
                        foreground=self.colors["text_main"],
                        rowheight=35, 
                        fieldbackground="white",
                        font=('Segoe UI', 10))
        style.configure("Treeview.Heading", 
                        font=('Segoe UI', 10, 'bold'),
                        background="#e5e7eb", 
                        foreground=self.colors["text_main"])
        style.map("Treeview", background=[('selected', self.colors["primary"])])

    def _add_rounded_rect_capability(self):
        def _create_rounded_rect(canvas, x1, y1, x2, y2, radius=25, **kwargs):
            points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
                      x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2,
                      x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius,
                      x1, y1+radius, x1, y1]
            return canvas.create_polygon(points, **kwargs, smooth=True)
        tk.Canvas.create_rounded_rect = _create_rounded_rect

    def _build_main_layout(self):
        self.main_container = tk.Frame(self.root, bg=self.colors["bg_main"])
        self.main_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(self.main_container, bg=self.colors["bg_sidebar"], width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="🎓 Gestion PhD", bg=self.colors["bg_sidebar"], 
                 fg="white", font=("Segoe UI", 18, "bold"), pady=30).pack(fill="x")

        self._create_sidebar_btn("  📊  Tableau de Bord", "Dashboard")
        self._create_sidebar_btn("  👥  Doctorants", "Doctorants")
        self._create_sidebar_btn("  📅  Activités", "Activités")
        self._create_sidebar_btn("  ⚙️  Paramètres", "Paramètres")

        tk.Label(self.sidebar, text="v1.0.0", bg=self.colors["bg_sidebar"], 
                 fg="#64748b", font=("Segoe UI", 9)).pack(side="bottom", pady=20)

        # Content Area
        self.content_area = tk.Frame(self.main_container, bg=self.colors["bg_main"])
        self.content_area.pack(side="right", fill="both", expand=True)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    def _create_sidebar_btn(self, text, page_name):
        btn = tk.Button(self.sidebar, text=text, anchor="w", font=("Segoe UI", 11),
                        bg=self.colors["bg_sidebar"], fg="#e2e8f0", bd=0, cursor="hand2",
                        activebackground=self.colors["sidebar_hover"], activeforeground="white",
                        padx=20, pady=12,
                        command=lambda: self.switch_page(page_name))
        btn.pack(fill="x", pady=2)

    def switch_page(self, page_name):
        frame = self.pages.get(page_name)
        if frame:
            frame.tkraise()
            if page_name == "Dashboard":
                self.refresh_dashboard()
            elif page_name == "Doctorants":
                self.load_doctorants_list()

    def _build_pages(self):
        self.pages["Dashboard"] = self._create_dashboard_page()
        self.pages["Doctorants"] = self._create_doctorants_page()
        self.pages["Activités"] = self._create_activities_page()
        self.pages["Paramètres"] = self._create_settings_page()

    # ========================================================================
    # DASHBOARD PAGE (WITH ICON CARDS + NEW ACTIONS)
    # ========================================================================
    def _create_dashboard_page(self):
        frame = tk.Frame(self.content_area, bg=self.colors["bg_main"])
        frame.grid(row=0, column=0, sticky="nsew")
        
        canvas = tk.Canvas(frame, bg=self.colors["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=self.colors["bg_main"])
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        content_width = min(self.root.winfo_screenwidth() - 300, 1200)
        canvas.create_window((0, 0), window=content, anchor="nw", width=content_width)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Header
        tk.Label(content, text="Tableau de Bord", font=("Segoe UI", 24, "bold"), 
                 bg=self.colors["bg_main"], fg=self.colors["text_main"]).pack(anchor="w", padx=40, pady=(30, 20))

        # Statistics Cards (with icons)
        self._create_statistics_cards(content)

        # Bottom Section: RESIZED for better UX
        bottom_row = tk.Frame(content, bg=self.colors["bg_main"])
        bottom_row.pack(fill="both", expand=False, padx=40, pady=20)

        # Recent Activities — taller
        act_frame = tk.Frame(bottom_row, bg="white", padx=20, pady=20)
        act_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        tk.Label(act_frame, text="Activités Récentes", font=("Segoe UI", 14, "bold"), bg="white").pack(anchor="w", pady=(0, 15))
        
        columns = ("Date", "Description")
        self.dashboard_tree = ttk.Treeview(act_frame, columns=columns, show="headings", height=10)
        self.dashboard_tree.heading("Date", text="Date")
        self.dashboard_tree.heading("Description", text="Détail")
        self.dashboard_tree.column("Date", width=100, anchor="center")
        self.dashboard_tree.column("Description", width=300)
        self.dashboard_tree.pack(fill="both", expand=True)

        # Quick Actions — wider, 4 buttons
        act_btns = tk.Frame(bottom_row, bg="white", padx=20, pady=25)
        act_btns.pack(side="right", fill="y", padx=(15, 0))
        tk.Label(act_btns, text="Actions Rapides", font=("Segoe UI", 14, "bold"), bg="white").pack(anchor="w", pady=(0, 20))

        actions = [
            ("➕ Ajouter Doctorant", self.nouveau_doctorant, self.colors["primary"]),
            ("🔍 Rechercher", self.focus_search, self.colors["success"]),
            ("📊 Exporter Données", self.exporter_data, self.colors["warning"]),
            ("🔄 Actualiser", self.refresh_dashboard, self.colors["purple"]),
        ]

        for text, command, color in actions:
            btn = tk.Button(
                act_btns,
                text=text,
                bg=color,
                fg="white",
                font=("Segoe UI", 10, "bold"),
                padx=15,
                pady=10,
                relief="flat",
                cursor="hand2",
                command=command
            )
            btn.pack(fill="x", pady=8)

        return frame

    def _create_statistics_cards(self, parent):
        stats_frame = tk.Frame(parent, bg=self.colors["bg_main"])
        stats_frame.pack(fill='x', padx=40, pady=10)

        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        except:
            base_dir = os.getcwd()

        cards = [
            {"title": "Doctorants total", "key": "total", "icon": "icons/students.png", "color": self.colors["primary"]},
            {"title": "En cours", "key": "en_cours", "icon": "icons/book.png", "color": self.colors["success"]},
            {"title": "Soutenus", "key": "soutenus", "icon": "icons/grad.png", "color": self.colors["purple"]},
            {"title": "Publications", "key": "publications", "icon": "icons/pub.png", "color": self.colors["danger"]},
            {"title": "Laboratoires", "key": "labos", "icon": "icons/lab.png", "color": self.colors["warning"]},
            {"title": "Encadrants", "key": "encadrants", "icon": "icons/prof.png", "color": self.colors["primary"]}
        ]

        self.stats_cards = {}
        self.image_refs = []

        for i, card in enumerate(cards):
            row = i // 3
            col = i % 3

            card_canvas = tk.Canvas(stats_frame, width=260, height=100, highlightthickness=0, bg=self.colors["bg_main"])
            card_canvas.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            card_canvas.create_rounded_rect(5, 5, 255, 95, radius=15, fill="white", outline="#e5e7eb", width=1)

            card_inner = tk.Frame(card_canvas, bg="white")
            card_canvas.create_window(130, 50, window=card_inner, anchor="center")

            # Icon
            full_icon_path = os.path.join(base_dir, card["icon"])
            if os.path.exists(full_icon_path):
                try:
                    pil_img = Image.open(full_icon_path).resize((45, 45), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(pil_img)
                    self.image_refs.append(photo)
                    icon_label = tk.Label(card_inner, image=photo, bg="white")
                except Exception:
                    icon_label = tk.Label(card_inner, text="⚠️", font=("Arial", 20), bg="white")
            else:
                icon_label = tk.Label(card_inner, text="📁", font=("Arial", 25), bg="white")
            icon_label.grid(row=0, column=0, rowspan=2, padx=(10, 15))

            # Text
            title_label = tk.Label(card_inner, text=card["title"], font=("Segoe UI", 10, "bold"),
                                   fg="#64748b", bg="white")
            title_label.grid(row=0, column=1, sticky="sw", pady=(5, 0))

            value_label = tk.Label(card_inner, text="0", font=("Segoe UI", 22, "bold"),
                                   fg=card["color"], bg="white")
            value_label.grid(row=1, column=1, sticky="nw", pady=(0, 5))

            self.stats_cards[card["key"]] = value_label

        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)

    # ========================================================================
    # DOCTORANTS PAGE
    # ========================================================================
    def _create_doctorants_page(self):
        frame = tk.Frame(self.content_area, bg=self.colors["bg_main"])
        frame.grid(row=0, column=0, sticky="nsew")
        
        tk.Label(frame, text="Gestion des Doctorants", font=("Segoe UI", 24, "bold"), 
                 bg=self.colors["bg_main"], fg=self.colors["text_main"]).pack(anchor="w", padx=30, pady=(30, 20))

        toolbar = tk.Frame(frame, bg="white", padx=20, pady=15)
        toolbar.pack(fill="x", padx=30)
        
        tk.Button(toolbar, text="➕ Ajouter", bg=self.colors["primary"], fg="white", relief="flat", 
                  padx=15, pady=5, command=self.nouveau_doctorant).pack(side="left", padx=(0, 10))
        tk.Button(toolbar, text="🗑️ Supprimer", bg=self.colors["danger"], fg="white", relief="flat", 
                  padx=15, pady=5, command=self.delete_doctorant).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(toolbar, textvariable=self.search_var, font=("Segoe UI", 10))
        self.search_entry.pack(side="right", ipady=5, ipadx=5)
        self.search_entry.bind('<KeyRelease>', self._on_search_change)
        tk.Label(toolbar, text="Rechercher (Nom):", bg="white", font=("Segoe UI", 10)).pack(side="right", padx=10)

        cols = ("ID", "Nom", "Prénom", "Matricule", "Spécialité", "Status")
        self.doc_tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        col_widths = [50, 150, 150, 100, 200, 100]
        for col, width in zip(cols, col_widths):
            self.doc_tree.heading(col, text=col)
            self.doc_tree.column(col, width=width)
        self.doc_tree.pack(fill="both", expand=True, padx=30, pady=20)
        self.doc_tree.bind('<<TreeviewSelect>>', self.on_doc_selected)
        
        return frame

    def _on_search_change(self, event=None):
        query = self.search_var.get()
        if self._search_after_id:
            self.root.after_cancel(self._search_after_id)
        self._search_after_id = self.root.after(300, lambda: self.load_doctorants_list(query))

    # ========================================================================
    # PLACEHOLDER PAGES
    # ========================================================================
    def _create_activities_page(self):
        frame = tk.Frame(self.content_area, bg=self.colors["bg_main"])
        frame.grid(row=0, column=0, sticky="nsew")
        tk.Label(frame, text="Historique Complet des Activités", font=("Segoe UI", 24, "bold"), bg=self.colors["bg_main"]).pack(pady=50)
        return frame

    def _create_settings_page(self):
        frame = tk.Frame(self.content_area, bg=self.colors["bg_main"])
        frame.grid(row=0, column=0, sticky="nsew")
        tk.Label(frame, text="Paramètres de l'application", font=("Segoe UI", 24, "bold"), bg=self.colors["bg_main"]).pack(pady=50)
        return frame

    # ========================================================================
    # DATA & LOGIC
    # ========================================================================
    def refresh_dashboard(self):
        try:
            stats = self.db.get_statistics()
            
            # Update stat cards
            self.stats_cards.get('total', tk.Label()).config(text=str(stats.get('total_students', 0)))
            self.stats_cards.get('en_cours', tk.Label()).config(text=str(stats.get('by_status', {}).get('en_cours', 0)))
            self.stats_cards.get('soutenus', tk.Label()).config(text=str(stats.get('by_status', {}).get('soutenu', 0)))
            self.stats_cards.get('publications', tk.Label()).config(text=str(stats.get('total_publications', 0)))
            self.stats_cards.get('labos', tk.Label()).config(text=str(stats.get('total_laboratories', 0)))
            self.stats_cards.get('encadrants', tk.Label()).config(text=str(stats.get('total_supervisors', 0)))
            
            # Update recent activities
            for item in self.dashboard_tree.get_children():
                self.dashboard_tree.delete(item)
            activities = stats.get('recent_activities', [])
            for act in activities[:10]:
                self.dashboard_tree.insert('', 'end', values=(
                    act.get('date', '-'),
                    f"{act.get('type','-')}: {act.get('nom','')} {act.get('prenom','')}"
                ))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le tableau de bord : {str(e)}")
    def load_doctorants_list(self, query=None):
        self.current_student_id = None
        try:
            for item in self.doc_tree.get_children():
                self.doc_tree.delete(item)
            docs = self.db.search_doctorants({'nom': query}) if query else self.db.get_all_doctorants()
            for d in docs:
                self.doc_tree.insert('', 'end', values=(
                    d['id'], d['nom'], d['prenom'], 
                    d.get('matricule', ''), d.get('specialite', ''), 
                    d.get('status', 'En cours')
                ))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger la liste : {str(e)}")

    def on_doc_selected(self, event):
        selection = self.doc_tree.selection()
        if selection:
            item = self.doc_tree.item(selection[0])
            self.current_student_id = item['values'][0]

    def nouveau_doctorant(self):
        try:
            from interface.doctorants_gui import DoctorantForm
            form = DoctorantForm(self.root, self.db)
            form.show()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le formulaire : {str(e)}")

    def delete_doctorant(self):
        if not self.current_student_id:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un doctorant.")
            return
        if messagebox.askyesno("Confirmation", "Supprimer ce doctorant ?"):
            try:
                self.db.delete_doctorant(self.current_student_id)
                self.load_doctorants_list()
                self.refresh_dashboard()
                messagebox.showinfo("Succès", "Doctorant supprimé.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de la suppression : {str(e)}")

    def focus_search(self):
        """Switch to Doctorants page and focus the search bar"""
        self.switch_page("Doctorants")
        self.root.after(100, lambda: self.search_entry.focus_set())

    def exporter_data(self):
        """Export all doctorants to CSV"""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Exporter les données des doctorants"
            )
            if not filepath:
                return

            data = self.db.get_all_doctorants()
            if not data:
                messagebox.showinfo("Export", "Aucune donnée à exporter.")
                return

            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

            messagebox.showinfo("Succès", f"Données exportées vers :\n{os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'export : {str(e)}")

    def on_closing(self):
        if messagebox.askokcancel("Quitter", "Voulez-vous quitter l'application ?"):
            if hasattr(self.db, 'close'):
                try:
                    self.db.close()
                except:
                    pass
            self.root.destroy()