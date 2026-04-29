import os
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
from datetime import datetime

from config import BASE_LEGAL_DIR, UPLOADS_DIR
from src.auth import AuthManager
from src.processor import DocumentProcessor
from src.vector_store import VectorIndexManager
from src.engine import ComplianceEngine
from src.router import RouterService

# UI Constants
COLOR_BG = "#1A1A1A"
COLOR_PRIMARY = "#2D5CFE"
COLOR_SECONDARY = "#333333"
COLOR_TEXT = "#FFFFFF"
COLOR_ACCENT = "#00D1FF"

class SACRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SACR - Sistema de Análise de Conformidade Regulatória")
        self.geometry("1100x700")
        ctk.set_appearance_mode("Dark")
        
        # Managers
        self.auth = AuthManager()
        self.processor = DocumentProcessor()
        self.vector_mgr = VectorIndexManager()
        self.router = RouterService()
        self.engine = ComplianceEngine() # Needs API KEY in ENV

        self.current_user = None

        # Main container
        self.container = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.container.pack(fill="both", expand=True)

        self.show_login()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_container()
        
        login_frame = ctk.CTkFrame(self.container, width=400, height=500, fg_color=COLOR_SECONDARY, corner_radius=20)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        label_title = ctk.CTkLabel(login_frame, text="SACR LOGIN", font=("Inter", 24, "bold"), text_color=COLOR_ACCENT)
        label_title.pack(pady=(40, 20))

        self.entry_user = ctk.CTkEntry(login_frame, placeholder_text="Usuário", width=250, height=45)
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(login_frame, placeholder_text="Senha", show="*", width=250, height=45)
        self.entry_pass.pack(pady=10)

        btn_login = ctk.CTkButton(login_frame, text="ENTRAR", command=self.handle_login, 
                                  fg_color=COLOR_PRIMARY, hover_color="#1E40AF", width=250, height=45)
        btn_login.pack(pady=30)

    def handle_login(self):
        user = self.entry_user.get()
        pw = self.entry_pass.get()
        
        result = self.auth.login(user, pw)
        if result:
            self.current_user = result
            if result['role'] == 'ADM':
                self.show_adm_dashboard()
            else:
                self.show_sector_dashboard()
        else:
            messagebox.showerror("Erro", "Credenciais inválidas")

    def show_adm_dashboard(self):
        self.clear_container()
        
        # Sidebar
        sidebar = ctk.CTkFrame(self.container, width=200, fg_color=COLOR_SECONDARY, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="ADM PANEL", font=("Inter", 18, "bold"), text_color=COLOR_ACCENT).pack(pady=20)
        
        ctk.CTkButton(sidebar, text="Base Legal", fg_color="transparent", anchor="w", 
                      command=self.show_legal_base_view).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(sidebar, text="Nova Auditoria", fg_color="transparent", anchor="w",
                      command=self.show_new_audit_view).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(sidebar, text="Revisão IA", fg_color="transparent", anchor="w",
                      command=self.show_review_panel).pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(sidebar, text="Sair", fg_color="#B91C1C", hover_color="#991B1B", command=self.show_login).pack(side="bottom", fill="x", padx=10, pady=20)

        # Content Area
        self.content_area = ctk.CTkFrame(self.container, fg_color=COLOR_BG)
        self.content_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        self.show_legal_base_view()

    def show_legal_base_view(self):
        for w in self.content_area.winfo_children(): w.destroy()
        
        ctk.CTkLabel(self.content_area, text="Gestão de Base Legal (RDC/ISO)", font=("Inter", 20, "bold")).pack(anchor="w", pady=(0, 20))
        
        btn_upload = ctk.CTkButton(self.content_area, text="+ Upload Nova Lei", command=self.upload_law)
        btn_upload.pack(anchor="w", pady=10)
        
        # List files in base_legal
        self.files_list = ctk.CTkTextbox(self.content_area, height=300)
        self.files_list.pack(fill="x", pady=10)
        self.refresh_law_list()

    def refresh_law_list(self):
        files = os.listdir(BASE_LEGAL_DIR)
        self.files_list.delete("1.0", "end")
        for f in files:
            self.files_list.insert("end", f"{f}\n")

    def upload_law(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            filename = os.path.basename(path)
            dest = os.path.join(BASE_LEGAL_DIR, filename)
            with open(path, "rb") as f_src, open(dest, "wb") as f_dest:
                f_dest.write(f_src.read())
            
            self.refresh_law_list()
            # Trigger ChromaDB Sync
            self.vector_mgr.sync_legal_base()
            messagebox.showinfo("Sucesso", "Lei enviada e indexada com sucesso.")

    def show_new_audit_view(self):
        for w in self.content_area.winfo_children(): w.destroy()
        
        ctk.CTkLabel(self.content_area, text="Nova Auditoria de Documento", font=("Inter", 20, "bold")).pack(anchor="w", pady=(0, 20))
        
        self.btn_select_doc = ctk.CTkButton(self.content_area, text="Selecionar Documento Técnico", command=self.run_audit)
        self.btn_select_doc.pack(pady=50)
        
        self.audit_status_label = ctk.CTkLabel(self.content_area, text="")
        self.audit_status_label.pack()

    def run_audit(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self.audit_status_label.configure(text="Processando documento (IA)...", text_color=COLOR_ACCENT)
            self.update()
            
            # 1. Process PDF
            text, quality = self.processor.process_pdf(path)
            
            # 2. Run IA Engine
            result_json = self.engine.audit_document(text, os.path.basename(path))
            
            # 3. Register in DB as 'Pendente de Revisão'
            import sqlite3
            from config import DB_PATH
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("INSERT INTO documents (filename, original_path, status, uploader_id) VALUES (?, ?, ?, ?)",
                        (os.path.basename(path), path, 'Pendente de Revisão', self.current_user['id']))
            doc_id = cur.lastrowid
            conn.commit()
            conn.close()
            
            self.router.register_initial_analysis(doc_id, result_json)
            
            self.audit_status_label.configure(text="Auditoria concluída! Aguardando revisão do ADM.", text_color="green")
            messagebox.showinfo("Sucesso", "Análise enviada para o painel de revisão.")

    def show_review_panel(self):
        for w in self.content_area.winfo_children(): w.destroy()
        ctk.CTkLabel(self.content_area, text="Painel de Revisão Humana", font=("Inter", 20, "bold")).pack(anchor="w", pady=(0, 20))
        
        pending = self.router.get_pending_reviews()
        
        scroll = ctk.CTkScrollableFrame(self.content_area, height=500)
        scroll.pack(fill="both", expand=True)
        
        for p in pending:
            analysis_id, filename, sector, raw_json_str = p
            item = ctk.CTkFrame(scroll, fg_color=COLOR_SECONDARY, corner_radius=10)
            item.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(item, text=f"Documento: {filename}", font=("Inter", 14, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(item, text=f"Setor IA: {sector}", text_color=COLOR_ACCENT).pack(side="left", padx=20)
            
            btn_rev = ctk.CTkButton(item, text="Revisar", width=100, command=lambda aid=analysis_id, rjs=raw_json_str: self.open_review_modal(aid, rjs))
            btn_rev.pack(side="right", padx=10, pady=5)

    def open_review_modal(self, analysis_id, raw_json_str):
        modal = ctk.CTkToplevel(self)
        modal.title("Revisão de Auditoria")
        modal.geometry("900x600")
        modal.attributes("-topmost", True)
        
        data = json.loads(raw_json_str)
        
        # Split view
        left = ctk.CTkFrame(modal)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        right = ctk.CTkFrame(modal)
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(left, text="Análise da IA", font=("Inter", 16, "bold")).pack()
        ai_text = ctk.CTkTextbox(left)
        ai_text.pack(fill="both", expand=True)
        ai_text.insert("1.0", json.dumps(data, indent=2, ensure_ascii=False))
        
        ctk.CTkLabel(right, text="Evidências Encontradas", font=("Inter", 16, "bold")).pack()
        ev_text = ctk.CTkTextbox(right)
        ev_text.pack(fill="both", expand=True)
        
        ev_content = ""
        for ev in data.get("evidencias", []):
            ev_content += f"NORMA: {ev['item_norma']}\nTRECHO: {ev['trecho_lei']}\nCONCLUSÃO: {ev['conclusao']}\n\n"
        ev_text.insert("1.0", ev_content)
        
        btn_approve = ctk.CTkButton(modal, text="APROVAR E ROTEAR", fg_color="green", 
                                    command=lambda: self.finalize(analysis_id, data, modal))
        btn_approve.pack(side="bottom", pady=20)

    def finalize(self, aid, data, modal):
        self.router.finalize_analysis(aid, data, self.current_user['id'])
        modal.destroy()
        self.show_review_panel()
        messagebox.showinfo("Sucesso", "Documento finalizado e enviado ao setor.")

    def show_sector_dashboard(self):
        self.clear_container()
        
        header = ctk.CTkFrame(self.container, height=60, fg_color=COLOR_SECONDARY)
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text=f"SACR - SETOR: {self.current_user['role']}", font=("Inter", 18, "bold")).pack(side="left", padx=20)
        ctk.CTkButton(header, text="Sair", fg_color="#B91C1C", width=80, command=self.show_login).pack(side="right", padx=20)
        
        content = ctk.CTkFrame(self.container, fg_color=COLOR_BG)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content, text="Documentos Finalizados", font=("Inter", 20, "bold")).pack(anchor="w")
        
        docs = self.router.get_sector_documents(self.current_user['role'])
        
        scroll = ctk.CTkScrollableFrame(content)
        scroll.pack(fill="both", expand=True, pady=10)
        
        for d in docs:
            fname, status, final_json_str = d
            f_data = json.loads(final_json_str)
            
            card = ctk.CTkFrame(scroll, fg_color=COLOR_SECONDARY)
            card.pack(fill="x", pady=5)
            
            ctk.CTkLabel(card, text=f"File: {fname}", font=("Inter", 14, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(card, text=f"Status: {f_data['status']}", text_color="green" if f_data['status'] == 'Conforme' else "red").pack(side="left", padx=20)
            
            btn_view = ctk.CTkButton(card, text="Ver Detalhes", width=100, command=lambda dj=final_json_str: self.view_details(dj))
            btn_view.pack(side="right", padx=10, pady=5)

    def view_details(self, json_str):
        modal = ctk.CTkToplevel(self)
        modal.title("Relatório de Auditoria")
        modal.geometry("600x500")
        modal.attributes("-topmost", True)
        
        txt = ctk.CTkTextbox(modal)
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("1.0", json.dumps(json.loads(json_str), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    app = SACRApp()
    app.mainloop()
