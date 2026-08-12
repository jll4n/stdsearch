import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pymupdf
import os
import threading
import time
from PIL import Image, ImageTk

# ------------------ FONCTIONS ------------------

def lister_pdf(dossier):
    if recursive_var.get():
        return list(Path(dossier).rglob("*.pdf"))
    else:
        return list(Path(dossier).glob("*.pdf"))

def ouvrir_pdf_tree(event):
    item = result_tree.selection()
    if not item:
        return
    pdf_path = result_tree.item(item[0], "values")[1]
    if os.path.isfile(pdf_path):
        os.startfile(pdf_path)
    else:
        messagebox.showerror("Erreur", "Le fichier PDF n'existe plus.")

def notifier_fin():
    # Popup
    messagebox.showinfo("Terminé", "La recherche est terminée.")

    # Clignotement du bouton
    def blink():
        original = btn_search.cget("text")
        btn_search.config(text="✔ Terminé ✔")
        root.after(800, lambda: btn_search.config(text=original))

    blink()

def rechercher():
    search = entry_search.get().strip()
    folder = folder_var.get()
    mode = search_mode_var.get()

    if not folder or not os.path.isdir(folder):
        messagebox.showerror("Erreur", "Veuillez sélectionner un dossier valide.")
        return

    if not search:
        messagebox.showwarning("Attention", "Veuillez entrer un texte à rechercher.")
        return

    # Nettoyage des résultats
    for item in result_tree.get_children():
        result_tree.delete(item)

    pdfs = lister_pdf(folder)

    progress_bar["maximum"] = len(pdfs)
    progress_bar["value"] = 0
    root.update_idletasks()

    # Multi-mots
    terms = search.split()

    def match_all(text):
        return all(t.lower() in text.lower() for t in terms)

    def match_any(text):
        return any(t.lower() in text.lower() for t in terms)

    for pdf in pdfs:
        try:
            doc = pymupdf.open(pdf)
            found = False

            if mode == "Page de garde":
                if len(doc) > 0:
                    text = doc[0].get_text()
                    if logic_var.get() == "ET":
                        found = match_all(text)
                    else:
                        found = match_any(text)
            else:
                for page in doc:
                    text = page.get_text()
                    if logic_var.get() == "ET":
                        found = match_all(text)
                    else:
                        found = match_any(text)
                    if found:
                        break

            if found:
                result_tree.insert("", tk.END, values=(pdf.name, str(pdf)))

            doc.close()

        except Exception as e:
            result_tree.insert("", tk.END, values=("Erreur", f"{pdf} : {e}"))

        progress_bar["value"] += 1
        root.update_idletasks()

        # Micro pause pour éviter le freeze
        time.sleep(0.001)

    notifier_fin()

    if len(result_tree.get_children()) == 0:
        result_tree.insert("", tk.END, values=("Aucun résultat", ""))


def lancer_recherche_thread():
    thread = threading.Thread(target=rechercher, daemon=True)
    thread.start()

def choisir_dossier():
    dossier = filedialog.askdirectory()
    if dossier:
        folder_var.set(dossier)

# ------------------ THEMES ------------------

def apply_dark_mode():
    bg_dark = "#1e1e1e"
    fg_light = "#e0e0e0"
    accent = "#3a7bd5"

    root.configure(bg=bg_dark)

    style.theme_use("clam")
    style.configure("TFrame", background=bg_dark)
    style.configure("TLabel", background=bg_dark, foreground=fg_light)
    style.configure("TEntry", fieldbackground="#2b2b2b", foreground=fg_light)
    style.configure("TButton", background="#2b2b2b", foreground=fg_light)
    style.map("TButton",
              background=[("active", accent)],
              foreground=[("active", "white")])

    style.configure("Horizontal.TProgressbar",
                    troughcolor="#2b2b2b",
                    background=accent)

    # Treeview
    style.configure("Treeview",
                    background="#2b2b2b",
                    foreground=fg_light,
                    fieldbackground="#2b2b2b")
    style.map("Treeview",
              background=[("selected", accent)],
              foreground=[("selected", "white")])

def apply_light_mode():
    root.configure(bg="#f0f0f0")

    style.theme_use("clam")
    style.configure("TFrame", background="#f0f0f0")
    style.configure("TLabel", background="#f0f0f0", foreground="black")
    style.configure("TEntry", fieldbackground="white", foreground="black")
    style.configure("TButton", background="#e0e0e0", foreground="black")
    style.map("TButton",
              background=[("active", "#d0d0d0")],
              foreground=[("active", "black")])

    style.configure("Horizontal.TProgressbar",
                    troughcolor="#e0e0e0",
                    background="#3a7bd5")

    style.configure("Treeview",
                    background="white",
                    foreground="black",
                    fieldbackground="white")
    style.map("Treeview",
              background=[("selected", "#3a7bd5")],
              foreground=[("selected", "white")])

def change_theme(event=None):
    mode = theme_var.get()
    if mode == "Dark":
        apply_dark_mode()
    else:
        apply_light_mode()

# ------------------ GUI ------------------

root = tk.Tk()
root.title("Recherche documentaire PDF")
root.geometry("900x600")

try:
    logo_img = Image.open("../logo.png")  # chemin vers ton PNG
    logo_img = logo_img.resize((80, 80), Image.LANCZOS)  # taille du logo
    logo_photo = ImageTk.PhotoImage(logo_img)

    # Placement en haut à droite
    logo_label = tk.Label(root, image=logo_photo, bg=root["bg"])
    logo_label.place(relx=1.0, y=10, anchor="ne")
except Exception as e:
    print("Erreur chargement logo :", e)

style = ttk.Style()

# Choix du thème
theme_frame = ttk.Frame(root, padding=10)
theme_frame.pack(fill="x")

ttk.Label(theme_frame, text="Thème :").pack(side=tk.LEFT)
theme_var = tk.StringVar(value="Dark")
theme_menu = ttk.Combobox(theme_frame, textvariable=theme_var,
                          values=["Dark", "Light"], width=10, state="readonly")
theme_menu.pack(side=tk.LEFT, padx=5)
theme_menu.bind("<<ComboboxSelected>>", change_theme)

# Frame dossier
frame_folder = ttk.Frame(root, padding=10)
frame_folder.pack(fill="x")

ttk.Label(frame_folder, text="Dossier de recherche :").pack(side=tk.LEFT)
folder_var = tk.StringVar()
entry_folder = ttk.Entry(frame_folder, textvariable=folder_var, width=50)
entry_folder.pack(side=tk.LEFT, padx=5)

btn_folder = ttk.Button(frame_folder, text="Choisir...", command=choisir_dossier)
btn_folder.pack(side=tk.LEFT)

# Frame recherche
frame_search = ttk.Frame(root, padding=10)
frame_search.pack(fill="x")

ttk.Label(frame_search, text="Texte à rechercher :").pack(side=tk.LEFT)
entry_search = ttk.Entry(frame_search, width=30)
entry_search.pack(side=tk.LEFT, padx=5)

# Mode de recherche
ttk.Label(frame_search, text="Mode :").pack(side=tk.LEFT, padx=10)
search_mode_var = tk.StringVar(value="Page de garde")
search_mode_menu = ttk.Combobox(frame_search, textvariable=search_mode_var,
                                values=["Page de garde", "Toutes les pages"],
                                width=15, state="readonly")
search_mode_menu.pack(side=tk.LEFT)

# Options avancées
frame_options = ttk.Frame(root, padding=10)
frame_options.pack(fill="x")

ttk.Label(frame_options, text="Logique :").pack(side=tk.LEFT)
logic_var = tk.StringVar(value="ET")
logic_menu = ttk.Combobox(frame_options, textvariable=logic_var,
                          values=["ET", "OU"], width=10, state="readonly")
logic_menu.pack(side=tk.LEFT, padx=10)

recursive_var = tk.BooleanVar(value=False)
chk_recursive = ttk.Checkbutton(frame_options, text="Inclure sous-dossiers",
                                variable=recursive_var)
chk_recursive.pack(side=tk.LEFT, padx=10)

btn_search = ttk.Button(root, text="Lancer la recherche", command=lancer_recherche_thread)
btn_search.pack(pady=10)

# Barre de progression
progress_bar = ttk.Progressbar(root, length=600)
progress_bar.pack(pady=10)

# Résultats améliorés
result_frame = ttk.Frame(root)
result_frame.pack(fill="both", expand=True, pady=10)

columns = ("fichier", "chemin")
result_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
result_tree.heading("fichier", text="Nom du fichier")
result_tree.heading("chemin", text="Chemin complet")

result_tree.column("fichier", width=200)
result_tree.column("chemin", width=600)

result_tree.pack(fill="both", expand=True)

result_tree.bind("<Double-Button-1>", ouvrir_pdf_tree)

# Appliquer le thème initial
apply_dark_mode()

root.mainloop()
