import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pymupdf
import os

def lister_pdf(dossier):
    return list(Path(dossier).glob("*.pdf"))

def ouvrir_pdf(event):
    selection = result_box.curselection()
    if not selection:
        return

    item = result_box.get(selection[0])
    if item.startswith("Trouvé dans : "):
        pdf_path = item.replace("Trouvé dans : ", "").strip()
        if os.path.isfile(pdf_path):
            os.startfile(pdf_path)
        else:
            messagebox.showerror("Erreur", "Le fichier PDF n'existe plus.")

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

    result_box.delete(0, tk.END)
    pdfs = lister_pdf(folder)

    progress_bar["maximum"] = len(pdfs)
    progress_bar["value"] = 0
    root.update_idletasks()

    for pdf in pdfs:
        try:
            doc = pymupdf.open(pdf)
            found = False

            if mode == "Page de garde":
                if len(doc) > 0:
                    text = doc[0].get_text()
                    if search.lower() in text.lower():
                        found = True
            else:
                for page in doc:
                    text = page.get_text()
                    if search.lower() in text.lower():
                        found = True
                        break

            if found:
                result_box.insert(tk.END, f"Trouvé dans : {pdf}")

            doc.close()

        except Exception as e:
            result_box.insert(tk.END, f"Erreur avec {pdf}: {e}")

        progress_bar["value"] += 1
        root.update_idletasks()

    if result_box.size() == 0:
        result_box.insert(tk.END, "Aucun résultat trouvé.")

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

    result_box.configure(bg="#2b2b2b", fg=fg_light,
                         selectbackground=accent, selectforeground="white")

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

    result_box.configure(bg="white", fg="black",
                         selectbackground="#3a7bd5", selectforeground="white")

def change_theme(event=None):
    mode = theme_var.get()
    if mode == "Dark":
        apply_dark_mode()
    else:
        apply_light_mode()

# ------------------ GUI ------------------

root = tk.Tk()
root.title("Recherche documentaire PDF")
root.geometry("750x550")

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

ttk.Label(frame_search, text="Texte dans la PDG :").pack(side=tk.LEFT)
entry_search = ttk.Entry(frame_search, width=30)
entry_search.pack(side=tk.LEFT, padx=5)

# Mode de recherche
ttk.Label(frame_search, text="Mode :").pack(side=tk.LEFT, padx=10)
search_mode_var = tk.StringVar(value="Page de garde")
search_mode_menu = ttk.Combobox(frame_search, textvariable=search_mode_var,
                                values=["Page de garde", "Toutes les pages"],
                                width=15, state="readonly")
search_mode_menu.pack(side=tk.LEFT)

btn_search = ttk.Button(root, text="Lancer la recherche", command=rechercher)
btn_search.pack(pady=10)

# Barre de progression
progress_bar = ttk.Progressbar(root, length=600)
progress_bar.pack(pady=10)

# Résultats
ttk.Label(root, text="Résultats :").pack()

# Frame pour la listbox + scrollbar
result_frame = ttk.Frame(root)
result_frame.pack(fill="both", expand=True, pady=10)

scrollbar = ttk.Scrollbar(result_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

result_box = tk.Listbox(
    result_frame,
    height=15,
    width=0,  # auto-ajustement
)
result_box.pack(side=tk.LEFT, fill="both", expand=True)

result_box.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=result_box.yview)

result_box.bind("<Double-Button-1>", ouvrir_pdf)

# Appliquer le thème initial
apply_dark_mode()

root.mainloop()
