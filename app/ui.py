"""Interface graphique moderne de l'ERP avec CustomTkinter."""

from __future__ import annotations

import csv
from datetime import datetime
from typing import Any, Callable
from tkinter import messagebox

import customtkinter as ctk

from app.backup import BackupManager
from app.charts import ChartFactory
from app.config import BODY_FONT, COLORS, EXPORT_DIR, SMALL_FONT, SUBTITLE_FONT, TITLE_FONT
from app.database import DatabaseManager
from app.pdf_generator import InvoicePDFGenerator
from app.services import ERPService


class PremiumERPApp(ctk.CTk):
    """Fenêtre principale maximisée avec navigation latérale et vues métier."""

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.database = DatabaseManager()
        self.service = ERPService(self.database)
        self.backup_manager = BackupManager()
        self.pdf_generator = InvoicePDFGenerator()
        self.current_view = "Dashboard"
        self._sale_cart: list[dict[str, Any]] = []

        self.title("ERP Premium - Suite professionnelle")
        self.configure(fg_color=COLORS["background"])
        self.after(50, self._maximize_window)
        self._build_layout()
        self.show_dashboard()
        self.after(3000, self._auto_backup)

    def _maximize_window(self) -> None:
        """Maximise la fenêtre au démarrage selon la plateforme."""
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}+0+0")

    def _build_layout(self) -> None:
        """Construit la barre latérale et la zone centrale responsive."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=252, fg_color=COLORS["panel"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(11, weight=1)

        logo = ctk.CTkLabel(self.sidebar, text="✦ ERP Premium", font=("Inter", 24, "bold"), text_color=COLORS["text"])
        logo.grid(row=0, column=0, padx=24, pady=(28, 6), sticky="w")
        ctk.CTkLabel(self.sidebar, text="Suite polyvalente locale", font=SMALL_FONT, text_color=COLORS["muted"]).grid(
            row=1, column=0, padx=24, pady=(0, 14), sticky="w"
        )

        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        menu_items: list[tuple[str, str, Callable[[], None]]] = [
            ("🏠", "Dashboard", self.show_dashboard),
            ("📦", "Stock", self.show_stock),
            ("🛒", "Ventes", self.show_sales),
            ("👥", "Clients", self.show_clients),
            ("💰", "Comptabilité", self.show_accounting),
            ("🧾", "Factures", self.show_invoices),
            ("📊", "Statistiques", self.show_statistics),
            ("📅", "Agenda", self.show_agenda),
            ("⚙️", "Paramètres", self.show_settings),
        ]
        for index, (icon, label, command) in enumerate(menu_items, start=2):
            button = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}  {label}",
                command=command,
                height=44,
                corner_radius=14,
                anchor="w",
                font=BODY_FONT,
                fg_color="transparent",
                hover_color=COLORS["panel_light"],
                text_color=COLORS["text"],
            )
            button.grid(row=index, column=0, padx=16, pady=5, sticky="ew")
            self.nav_buttons[label] = button

        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="Sauvegarde auto activée",
            font=SMALL_FONT,
            text_color=COLORS["muted"],
            wraplength=210,
            justify="left",
        )
        self.status_label.grid(row=12, column=0, padx=20, pady=20, sticky="sw")

        self.content = ctk.CTkScrollableFrame(self, fg_color=COLORS["background"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)

    def _set_active(self, view: str) -> None:
        """Met visuellement en évidence l'entrée de menu active."""
        self.current_view = view
        for name, button in self.nav_buttons.items():
            button.configure(fg_color=COLORS["primary"] if name == view else "transparent")

    def _clear_content(self) -> None:
        """Supprime les widgets de la vue précédente."""
        for child in self.content.winfo_children():
            child.destroy()

    def _page_title(self, title: str, subtitle: str) -> None:
        """Affiche l'en-tête commun de chaque page."""
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, padx=30, pady=(28, 16), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=title, font=TITLE_FONT, text_color=COLORS["text"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text=subtitle, font=SUBTITLE_FONT, text_color=COLORS["muted"]).grid(row=1, column=0, sticky="w", pady=(4, 0))
        ctk.CTkButton(header, text="↻ Actualiser", width=120, command=self._reload_current_view).grid(row=0, column=1, rowspan=2, padx=8, sticky="e")

    def _card(self, parent: Any, row: int, column: int, title: str, value: str, color: str) -> ctk.CTkFrame:
        """Crée une carte KPI réutilisable."""
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=22, border_width=1, border_color=COLORS["border"])
        card.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(card, text=title, font=SMALL_FONT, text_color=COLORS["muted"]).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(card, text=value, font=("Inter", 25, "bold"), text_color=color).pack(anchor="w", padx=18, pady=(0, 18))
        return card

    def show_dashboard(self) -> None:
        """Vue Dashboard : KPIs, derniers éléments et graphique de revenus."""
        self._set_active("Dashboard")
        self._clear_content()
        self._page_title("Dashboard", "Vue d'ensemble temps réel de votre activité")
        metrics = self.service.dashboard_metrics()
        stock = self.service.stock_overview()

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.grid(row=1, column=0, padx=20, sticky="ew")
        for column in range(5):
            cards.grid_columnconfigure(column, weight=1)
        self._card(cards, 0, 0, "Chiffre d'affaires", f"{metrics['revenue']:,.0f} €", COLORS["accent"])
        self._card(cards, 0, 1, "Bénéfice", f"{metrics['profit']:,.0f} €", COLORS["success"])
        self._card(cards, 0, 2, "Clients", str(metrics["clients"]), COLORS["success"])
        self._card(cards, 0, 3, "Produits", str(metrics["products"]), COLORS["primary"])
        self._card(cards, 0, 4, "Valeur stock", f"{stock['sale_value']:,.0f} €", COLORS["warning"])

        quick = self._section_frame(2, "Actions rapides")
        ctk.CTkButton(quick, text="Nouvelle vente", command=self.show_sales).grid(row=0, column=0, padx=8, pady=12, sticky="ew")
        ctk.CTkButton(quick, text="Ajouter produit", command=lambda: self._open_product_dialog()).grid(row=0, column=1, padx=8, pady=12, sticky="ew")
        ctk.CTkButton(quick, text="Nouveau client", command=lambda: self._open_client_dialog()).grid(row=0, column=2, padx=8, pady=12, sticky="ew")
        ctk.CTkButton(quick, text="Sauvegarde", fg_color=COLORS["success"], command=self._manual_backup).grid(row=0, column=3, padx=8, pady=12, sticky="ew")
        quick.grid_columnconfigure((0, 1, 2, 3), weight=1)

        chart_card = self._section_frame(3, "Revenus, dépenses et bénéfices")
        canvas = ChartFactory.finance_chart(chart_card, self.service.monthly_finance())
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)
        canvas.draw()

        lists = ctk.CTkFrame(self.content, fg_color="transparent")
        lists.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        lists.grid_columnconfigure((0, 1, 2), weight=1)
        self._simple_list(lists, 0, "Dernières ventes", [f"#{row['id']} — {row['montant_total']:,.2f} €" for row in self.service.list_sales()[:5]])
        self._simple_list(lists, 1, "Dernières factures", [f"{row['numero']} — {row['total']:,.2f} €" for row in self.service.list_invoices()[:5]])
        low_products = [p for p in self.service.list_products() if p["quantite"] <= p["seuil_stock"]]
        self._simple_list(lists, 2, "Alertes stock", [f"{p['nom']} — {p['quantite']} unité(s)" for p in low_products[:5]])

    def show_stock(self) -> None:
        """Vue de gestion du stock avec ajout, suppression, export et mouvements."""
        self._set_active("Stock")
        self._clear_content()
        self._page_title("Stock", "Catalogue produits, fournisseurs, valeur et alertes")
        overview = self.service.stock_overview()
        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.grid(row=1, column=0, padx=20, sticky="ew")
        cards.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self._card(cards, 0, 0, "Références", str(overview["products"]), COLORS["primary"])
        self._card(cards, 0, 1, "Unités", str(overview["units"]), COLORS["accent"])
        self._card(cards, 0, 2, "Valeur achat", f"{overview['purchase_value']:,.0f} €", COLORS["success"])
        self._card(cards, 0, 3, "Alertes", str(overview["low_stock"]), COLORS["warning"])
        self._searchable_table(
            row=2,
            title="Produits",
            columns=("id", "nom", "categorie", "quantite", "prix_achat", "prix_vente", "fournisseur", "seuil_stock"),
            loader=self.service.list_products,
            add_callback=lambda: self._open_product_dialog(),
            edit_callback=self._edit_product,
            delete_callback=self.service.delete_product,
        )
        self._stock_movement_panel(3)
        self._table_only(4, "Historique des mouvements", ("id", "produit", "type_mouvement", "quantite", "commentaire", "date_mouvement"), self.service.list_stock_movements())

    def show_sales(self) -> None:
        """Vue ventes : panier simple, décrément stock, revenu et facture optionnelle."""
        self._set_active("Ventes")
        self._clear_content()
        self._page_title("Ventes", "Encaissement, panier produits et automatisation stock")
        panel = self._section_frame(1, "Nouvelle vente")
        clients = self.service.list_clients()
        products = self.service.list_products()
        client_names = [f"{c['id']} — {c['prenom']} {c['nom']}" for c in clients] or ["Aucun client"]
        product_names = [f"{p['id']} — {p['nom']} ({p['quantite']} dispo, {p['prix_vente']} €)" for p in products] or ["Aucun produit"]
        client_select = ctk.CTkOptionMenu(panel, values=client_names)
        product_select = ctk.CTkOptionMenu(panel, values=product_names)
        quantity = ctk.CTkEntry(panel, placeholder_text="Quantité", height=38)
        price = ctk.CTkEntry(panel, placeholder_text="Prix unitaire optionnel", height=38)
        vat_rate = ctk.CTkEntry(panel, placeholder_text=f"TVA % ({self.service.settings().get('vat_rate', '20')})", height=38)
        client_select.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        product_select.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        quantity.grid(row=0, column=2, padx=8, pady=8, sticky="ew")
        price.grid(row=0, column=3, padx=8, pady=8, sticky="ew")
        vat_rate.grid(row=0, column=4, padx=8, pady=8, sticky="ew")
        panel.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        ctk.CTkButton(panel, text="Ajouter au panier", command=lambda: self._add_sale_item(product_select, quantity, price)).grid(row=1, column=1, padx=8, pady=8, sticky="ew")
        ctk.CTkButton(panel, text="Valider vente", fg_color=COLORS["success"], command=lambda: self._create_sale(client_select, vat_rate, False)).grid(row=1, column=2, padx=8, pady=8, sticky="ew")
        ctk.CTkButton(panel, text="Vente + facture PDF", fg_color=COLORS["primary"], command=lambda: self._create_sale(client_select, vat_rate, True)).grid(row=1, column=3, padx=8, pady=8, sticky="ew")
        ctk.CTkButton(panel, text="Vider panier", fg_color=COLORS["warning"], command=self._clear_sale_cart).grid(row=1, column=4, padx=8, pady=8, sticky="ew")
        self._table_only(2, "Panier courant", ("nom_produit", "quantite", "prix_unitaire", "total"), self._sale_cart)
        self._table_only(3, "Historique ventes", ("id", "client", "montant_total", "tva", "lignes", "date_vente"), self.service.list_sales())

    def show_clients(self) -> None:
        """Vue clients avec recherche instantanée et historique préparé."""
        self._set_active("Clients")
        self._clear_content()
        self._page_title("Clients", "Fiches clients, coordonnées, notes et export")
        self._searchable_table(
            row=1,
            title="Clients",
            columns=("id", "prenom", "nom", "telephone", "email", "adresse", "notes"),
            loader=self.service.list_clients,
            add_callback=lambda: self._open_client_dialog(),
            edit_callback=self._edit_client,
            delete_callback=self.service.delete_client,
        )

    def show_accounting(self) -> None:
        """Vue comptabilité avec revenus, dépenses, bénéfices et graphiques."""
        self._set_active("Comptabilité")
        self._clear_content()
        self._page_title("Comptabilité", "Suivi des revenus, dépenses et bénéfices")
        summary = self.service.accounting_summary()
        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.grid(row=1, column=0, padx=20, sticky="ew")
        cards.grid_columnconfigure((0, 1, 2), weight=1)
        self._card(cards, 0, 0, "Revenus", f"{summary['revenus']:,.2f} €", COLORS["success"])
        self._card(cards, 0, 1, "Dépenses", f"{summary['depenses']:,.2f} €", COLORS["warning"])
        self._card(cards, 0, 2, "Bénéfice", f"{summary['benefice']:,.2f} €", COLORS["accent"])

        form = self._section_frame(2, "Ajouter une opération")
        label = ctk.CTkEntry(form, placeholder_text="Libellé", height=38)
        category = ctk.CTkEntry(form, placeholder_text="Catégorie", height=38)
        amount = ctk.CTkEntry(form, placeholder_text="Montant", height=38)
        label.grid(row=0, column=0, padx=8, pady=14, sticky="ew")
        category.grid(row=0, column=1, padx=8, pady=14, sticky="ew")
        amount.grid(row=0, column=2, padx=8, pady=14, sticky="ew")
        form.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(form, text="+ Revenu", command=lambda: self._add_accounting(label, category, amount, True)).grid(row=0, column=3, padx=8)
        ctk.CTkButton(form, text="+ Dépense", fg_color=COLORS["warning"], command=lambda: self._add_accounting(label, category, amount, False)).grid(row=0, column=4, padx=8)

        chart_card = self._section_frame(3, "Évolution mensuelle")
        canvas = ChartFactory.finance_chart(chart_card, self.service.monthly_finance())
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)
        canvas.draw()

    def show_invoices(self) -> None:
        """Vue factures avec export PDF professionnel et statuts."""
        self._set_active("Factures")
        self._clear_content()
        self._page_title("Factures", "Création, export PDF et suivi des statuts")
        actions = self._section_frame(1, "Nouvelle facture")
        clients = self.service.list_clients()
        client_names = [f"{c['id']} — {c['prenom']} {c['nom']}" for c in clients] or ["Aucun client"]
        client_select = ctk.CTkOptionMenu(actions, values=client_names)
        total = ctk.CTkEntry(actions, placeholder_text="Total TTC", height=38)
        vat = ctk.CTkEntry(actions, placeholder_text="TVA", height=38)
        client_select.grid(row=0, column=0, padx=8, pady=14, sticky="ew")
        total.grid(row=0, column=1, padx=8, pady=14, sticky="ew")
        vat.grid(row=0, column=2, padx=8, pady=14, sticky="ew")
        actions.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(actions, text="Générer PDF", command=lambda: self._create_invoice(client_select, total, vat)).grid(row=0, column=3, padx=8)
        self._table_only(2, "Factures", ("id", "numero", "client", "total", "tva", "statut", "chemin_pdf"), self.service.list_invoices())

    def show_statistics(self) -> None:
        """Vue statistiques avec graphiques produits et revenus."""
        self._set_active("Statistiques")
        self._clear_content()
        self._page_title("Statistiques", "Analyses commerciales et opérationnelles")
        finance = self._section_frame(1, "CA par mois")
        canvas = ChartFactory.finance_chart(finance, self.service.monthly_finance())
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)
        canvas.draw()
        products = self._section_frame(2, "Produits les plus vendus")
        rows = self.service.top_products()
        canvas2 = ChartFactory.bar_chart(products, "Top produits", [r["nom_produit"] for r in rows], [float(r["total"]) for r in rows])
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)
        canvas2.draw()

    def show_agenda(self) -> None:
        """Vue agenda : tâches, rendez-vous, notifications et événements."""
        self._set_active("Agenda")
        self._clear_content()
        self._page_title("Agenda", "Calendrier, rendez-vous et tâches")
        form = self._section_frame(1, "Nouvel événement")
        title = ctk.CTkEntry(form, placeholder_text="Titre", height=38)
        date = ctk.CTkEntry(form, placeholder_text="Date YYYY-MM-DD HH:MM", height=38)
        kind = ctk.CTkOptionMenu(form, values=["Tâche", "Rendez-vous", "Événement"])
        status = ctk.CTkOptionMenu(form, values=["À faire", "En cours", "Terminé", "Annulé"])
        title.grid(row=0, column=0, padx=8, pady=14, sticky="ew")
        date.grid(row=0, column=1, padx=8, pady=14, sticky="ew")
        kind.grid(row=0, column=2, padx=8, pady=14, sticky="ew")
        status.grid(row=0, column=3, padx=8, pady=14, sticky="ew")
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ctk.CTkButton(form, text="Ajouter", command=lambda: self._add_event(title, date, kind, status)).grid(row=0, column=4, padx=8)
        self._table_only(2, "Événements", ("id", "titre", "date_evenement", "type_evenement", "statut"), self.service.list_agenda())

    def show_settings(self) -> None:
        """Vue paramètres entreprise, TVA, thème et sauvegarde."""
        self._set_active("Paramètres")
        self._clear_content()
        self._page_title("Paramètres", "Identité entreprise, automatisations et préférences")
        settings = self.service.settings()
        frame = self._section_frame(1, "Entreprise & automatisations")
        entries: dict[str, ctk.CTkEntry] = {}
        fields = [
            ("company_name", "Nom entreprise"),
            ("company_address", "Adresse"),
            ("company_phone", "Téléphone"),
            ("company_email", "Email"),
            ("vat_rate", "TVA par défaut (%)"),
            ("backup_interval_minutes", "Intervalle sauvegarde auto (min)"),
            ("default_invoice_status", "Statut facture par défaut"),
        ]
        for row, (key, placeholder) in enumerate(fields):
            entry = ctk.CTkEntry(frame, placeholder_text=placeholder, height=38)
            entry.insert(0, settings.get(key, ""))
            entry.grid(row=row, column=0, padx=12, pady=8, sticky="ew")
            entries[key] = entry
        theme = ctk.CTkOptionMenu(frame, values=["dark", "light", "system"])
        theme.set(settings.get("theme", "dark"))
        backup = ctk.CTkOptionMenu(frame, values=["enabled", "disabled"])
        backup.set(settings.get("auto_backup", "enabled"))
        theme.grid(row=0, column=1, padx=12, pady=8, sticky="ew")
        backup.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
        frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(frame, text="Enregistrer", command=lambda: self._save_settings(entries, theme, backup)).grid(row=len(fields), column=0, padx=12, pady=12, sticky="e")
        ctk.CTkButton(frame, text="Créer une sauvegarde maintenant", fg_color=COLORS["success"], command=self._manual_backup).grid(row=len(fields), column=1, padx=12, pady=12, sticky="e")

    def _section_frame(self, row: int, title: str) -> ctk.CTkFrame:
        """Crée une section avec titre et retourne son corps de contenu."""
        frame = ctk.CTkFrame(self.content, fg_color=COLORS["card"], corner_radius=22, border_width=1, border_color=COLORS["border"])
        frame.grid(row=row, column=0, padx=30, pady=12, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=title, font=("Inter", 17, "bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 4)
        )
        body = ctk.CTkFrame(frame, fg_color="transparent")
        body.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 8))
        body.grid_columnconfigure(0, weight=1)
        return body

    def _simple_list(self, parent: Any, column: int, title: str, rows: list[str]) -> None:
        """Affiche une petite liste de dashboard."""
        frame = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=20, border_width=1, border_color=COLORS["border"])
        frame.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(frame, text=title, font=("Inter", 16, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 8))
        for row in rows or ["Aucune donnée disponible"]:
            ctk.CTkLabel(frame, text=row, font=BODY_FONT, text_color=COLORS["muted"]).pack(anchor="w", padx=16, pady=4)

    def _searchable_table(
        self,
        row: int,
        title: str,
        columns: tuple[str, ...],
        loader: Callable[[str], list[dict[str, Any]]],
        add_callback: Callable[[], None],
        edit_callback: Callable[[dict[str, Any]], None] | None,
        delete_callback: Callable[[int], None],
    ) -> None:
        """Crée un tableau filtrable avec actions ajouter/supprimer/export."""
        frame = self._section_frame(row, title)
        toolbar = ctk.CTkFrame(frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=8)
        search = ctk.CTkEntry(toolbar, placeholder_text="Recherche instantanée", height=38)
        search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(toolbar, text="Ajouter", command=add_callback).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Exporter CSV", fg_color=COLORS["success"], command=lambda: self._export_rows(title, columns, loader(search.get()))).pack(side="left", padx=4)
        table = ctk.CTkFrame(frame, fg_color="transparent")
        table.pack(fill="both", expand=True, padx=12, pady=12)

        def refresh() -> None:
            for child in table.winfo_children():
                child.destroy()
            rows = loader(search.get())
            self._draw_table(table, columns, rows, delete_callback, edit_callback)

        search.bind("<KeyRelease>", lambda _event: refresh())
        refresh()

    def _table_only(self, row: int, title: str, columns: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
        """Affiche un tableau sans barre de recherche."""
        frame = self._section_frame(row, title)
        toolbar = ctk.CTkFrame(frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=4)
        ctk.CTkButton(toolbar, text="Exporter CSV", fg_color=COLORS["success"], command=lambda: self._export_rows(title, columns, rows)).pack(side="right", padx=4)
        table = ctk.CTkFrame(frame, fg_color="transparent")
        table.pack(fill="both", expand=True, padx=12, pady=12)
        self._draw_table(table, columns, rows, None, None)

    def _draw_table(
        self,
        table: ctk.CTkFrame,
        columns: tuple[str, ...],
        rows: list[dict[str, Any]],
        delete_callback: Callable[[int], None] | None,
        edit_callback: Callable[[dict[str, Any]], None] | None,
    ) -> None:
        """Dessine un tableau moderne en grille CustomTkinter."""
        for col, name in enumerate(columns):
            ctk.CTkLabel(table, text=name.upper(), font=SMALL_FONT, text_color=COLORS["muted"]).grid(row=0, column=col, padx=8, pady=8, sticky="w")
            table.grid_columnconfigure(col, weight=1)
        if delete_callback or edit_callback:
            ctk.CTkLabel(table, text="ACTIONS", font=SMALL_FONT, text_color=COLORS["muted"]).grid(row=0, column=len(columns), padx=8, pady=8)
        for row_index, row in enumerate(rows, start=1):
            color = COLORS["panel_light"] if row_index % 2 == 0 else COLORS["panel"]
            for col, name in enumerate(columns):
                value = str(row.get(name, ""))
                cell = ctk.CTkLabel(table, text=value[:48], font=BODY_FONT, text_color=COLORS["text"], fg_color=color, corner_radius=8)
                cell.grid(row=row_index, column=col, padx=4, pady=3, sticky="ew")
            if delete_callback or edit_callback:
                actions = ctk.CTkFrame(table, fg_color="transparent")
                actions.grid(row=row_index, column=len(columns), padx=4, pady=3)
                if edit_callback:
                    ctk.CTkButton(
                        actions,
                        text="Modifier",
                        width=82,
                        fg_color=COLORS["primary"],
                        command=lambda selected=dict(row): edit_callback(selected),
                    ).pack(side="left", padx=2)
                if delete_callback:
                    ctk.CTkButton(
                        actions,
                        text="Supprimer",
                        width=90,
                        fg_color=COLORS["danger"],
                        command=lambda item_id=int(row["id"]): self._delete_and_refresh(delete_callback, item_id),
                    ).pack(side="left", padx=2)

    def _stock_movement_panel(self, row: int) -> None:
        """Ajoute un panneau de correction entrée/sortie stock."""
        frame = self._section_frame(row, "Mouvement rapide de stock")
        products = self.service.list_products()
        product_names = [f"{p['id']} — {p['nom']} ({p['quantite']} dispo)" for p in products] or ["Aucun produit"]
        product = ctk.CTkOptionMenu(frame, values=product_names)
        movement = ctk.CTkOptionMenu(frame, values=["Entrée", "Sortie"])
        quantity = ctk.CTkEntry(frame, placeholder_text="Quantité", height=38)
        comment = ctk.CTkEntry(frame, placeholder_text="Commentaire", height=38)
        product.grid(row=0, column=0, padx=8, pady=12, sticky="ew")
        movement.grid(row=0, column=1, padx=8, pady=12, sticky="ew")
        quantity.grid(row=0, column=2, padx=8, pady=12, sticky="ew")
        comment.grid(row=0, column=3, padx=8, pady=12, sticky="ew")
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ctk.CTkButton(frame, text="Appliquer", command=lambda: self._adjust_stock(product, movement, quantity, comment)).grid(row=0, column=4, padx=8, pady=12)

    def _export_rows(self, title: str, columns: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
        """Exporte le contenu d'un tableau en CSV dans le dossier exports/."""
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        safe_title = "".join(char.lower() if char.isalnum() else "_" for char in title).strip("_") or "export"
        path = EXPORT_DIR / f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(columns), extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        self.status_label.configure(text=f"Export CSV : {path.name}")

    def _delete_and_refresh(self, callback: Callable[[int], None], item_id: int) -> None:
        """Supprime une ligne puis recharge la vue courante."""
        callback(item_id)
        self._reload_current_view()

    def _open_product_dialog(self, existing: dict[str, Any] | None = None) -> None:
        """Ouvre la fenêtre d'ajout ou modification produit."""
        fields = ["nom", "categorie", "quantite", "prix_achat", "prix_vente", "fournisseur", "seuil_stock"]
        if existing:
            self._entity_dialog(
                "Modifier produit",
                fields,
                lambda values: self.service.update_product(int(existing["id"]), values),
                self.show_stock,
                existing,
            )
        else:
            self._entity_dialog("Ajouter produit", fields, lambda values: self.service.add_product(values), self.show_stock)

    def _edit_product(self, product: dict[str, Any]) -> None:
        """Prépare la modification d'un produit sélectionné."""
        self._open_product_dialog(product)

    def _open_client_dialog(self, existing: dict[str, Any] | None = None) -> None:
        """Ouvre la fenêtre d'ajout ou modification client."""
        fields = ["nom", "prenom", "telephone", "email", "adresse", "notes"]
        if existing:
            self._entity_dialog(
                "Modifier client",
                fields,
                lambda values: self.service.update_client(int(existing["id"]), values),
                self.show_clients,
                existing,
            )
        else:
            self._entity_dialog("Ajouter client", fields, lambda values: self.service.add_client(values), self.show_clients)

    def _edit_client(self, client: dict[str, Any]) -> None:
        """Prépare la modification d'un client sélectionné."""
        self._open_client_dialog(client)

    def _entity_dialog(
        self,
        title: str,
        fields: list[str],
        saver: Callable[[dict[str, str]], Any],
        after_save: Callable[[], None],
        initial_values: dict[str, Any] | None = None,
    ) -> None:
        """Fenêtre générique pour créer ou modifier une entité métier."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("480x560")
        dialog.configure(fg_color=COLORS["background"])
        entries: dict[str, ctk.CTkEntry] = {}
        ctk.CTkLabel(dialog, text=title, font=TITLE_FONT, text_color=COLORS["text"]).pack(anchor="w", padx=24, pady=(24, 12))
        for field in fields:
            entry = ctk.CTkEntry(dialog, placeholder_text=field.replace("_", " ").title(), height=40)
            if initial_values and field in initial_values:
                entry.insert(0, str(initial_values[field]))
            entry.pack(fill="x", padx=24, pady=6)
            entries[field] = entry

        def save() -> None:
            values = {key: entry.get() for key, entry in entries.items()}
            try:
                saver(values)
            except ValueError as exc:
                messagebox.showerror("Validation", str(exc))
                return
            dialog.destroy()
            after_save()

        ctk.CTkButton(dialog, text="Enregistrer", command=save, height=42).pack(padx=24, pady=22, anchor="e")

    def _add_accounting(self, label: ctk.CTkEntry, category: ctk.CTkEntry, amount: ctk.CTkEntry, revenue: bool) -> None:
        """Ajoute un revenu ou une dépense depuis le formulaire comptable."""
        try:
            value = float(amount.get() or 0)
        except ValueError:
            messagebox.showerror("Validation", "Le montant doit être numérique.")
            return
        if revenue:
            self.service.add_revenue(label.get() or "Revenu", category.get() or "Général", value)
        else:
            self.service.add_expense(label.get() or "Dépense", category.get() or "Général", value)
        self.show_accounting()

    def _add_sale_item(self, product_select: ctk.CTkOptionMenu, quantity_entry: ctk.CTkEntry, price_entry: ctk.CTkEntry) -> None:
        """Ajoute une ligne au panier de vente courant."""
        selected = product_select.get()
        if "—" not in selected:
            messagebox.showerror("Validation", "Aucun produit disponible.")
            return
        try:
            product_id = int(selected.split(" — ")[0])
            quantity = int(quantity_entry.get() or 1)
            product = dict(self.database.fetch_one("SELECT * FROM produits WHERE id = ?", (product_id,)) or {})
            unit_price = float(price_entry.get() or product.get("prix_vente", 0))
        except ValueError:
            messagebox.showerror("Validation", "La quantité et le prix doivent être numériques.")
            return
        if quantity <= 0:
            messagebox.showerror("Validation", "La quantité doit être supérieure à zéro.")
            return
        self._sale_cart.append(
            {
                "product_id": product_id,
                "nom_produit": product.get("nom", "Produit"),
                "quantity": quantity,
                "quantite": quantity,
                "price": unit_price,
                "prix_unitaire": unit_price,
                "total": quantity * unit_price,
            }
        )
        self.show_sales()

    def _create_sale(self, client_select: ctk.CTkOptionMenu, vat_entry: ctk.CTkEntry, with_invoice: bool) -> None:
        """Crée une vente depuis le panier courant et génère une facture si demandé."""
        selected = client_select.get()
        client_id = int(selected.split(" — ")[0]) if "—" in selected else None
        try:
            vat_rate = float(vat_entry.get() or self.service.settings().get("vat_rate", 20))
            sale_id = self.service.create_sale(client_id, self._sale_cart, vat_rate)
        except ValueError as exc:
            messagebox.showerror("Validation", str(exc))
            return
        if with_invoice:
            sale = dict(self.database.fetch_one("SELECT * FROM ventes WHERE id = ?", (sale_id,)) or {})
            invoice_id = self.service.create_invoice_record(client_id, float(sale.get("montant_total", 0)), float(sale.get("tva", 0)))
            invoice = dict(self.database.fetch_one("SELECT * FROM factures WHERE id = ?", (invoice_id,)) or {})
            client = dict(self.database.fetch_one("SELECT * FROM clients WHERE id = ?", (client_id,)) or {}) if client_id else None
            pdf_path = self.pdf_generator.generate(invoice, self.service.settings(), client)
            self.service.update_invoice_pdf_path(invoice_id, str(pdf_path))
        self._sale_cart = []
        self.status_label.configure(text=f"Vente #{sale_id} enregistrée")
        self.show_sales()

    def _clear_sale_cart(self) -> None:
        """Vide le panier de vente courant."""
        self._sale_cart = []
        self.show_sales()

    def _adjust_stock(
        self,
        product_select: ctk.CTkOptionMenu,
        movement_select: ctk.CTkOptionMenu,
        quantity_entry: ctk.CTkEntry,
        comment_entry: ctk.CTkEntry,
    ) -> None:
        """Applique un mouvement de stock depuis le panneau rapide."""
        selected = product_select.get()
        if "—" not in selected:
            messagebox.showerror("Validation", "Aucun produit disponible.")
            return
        try:
            self.service.adjust_stock(
                int(selected.split(" — ")[0]),
                movement_select.get(),
                int(quantity_entry.get() or 0),
                comment_entry.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Validation", str(exc))
            return
        self.show_stock()

    def _create_invoice(self, client_select: ctk.CTkOptionMenu, total_entry: ctk.CTkEntry, vat_entry: ctk.CTkEntry) -> None:
        """Crée une facture, génère son PDF et enregistre son chemin."""
        selected = client_select.get()
        client_id = int(selected.split(" — ")[0]) if "—" in selected else None
        try:
            invoice_id = self.service.create_invoice_record(client_id, float(total_entry.get() or 0), float(vat_entry.get() or 0))
        except ValueError:
            messagebox.showerror("Validation", "Le total et la TVA doivent être numériques.")
            return
        invoice = dict(self.database.fetch_one("SELECT * FROM factures WHERE id = ?", (invoice_id,)) or {})
        client = dict(self.database.fetch_one("SELECT * FROM clients WHERE id = ?", (client_id,)) or {}) if client_id else None
        pdf_path = self.pdf_generator.generate(invoice, self.service.settings(), client)
        self.service.update_invoice_pdf_path(invoice_id, str(pdf_path))
        self.show_invoices()

    def _add_event(self, title: ctk.CTkEntry, date: ctk.CTkEntry, kind: ctk.CTkOptionMenu, status: ctk.CTkOptionMenu) -> None:
        """Ajoute rapidement une entrée d'agenda."""
        self.service.add_event(
            {
                "titre": title.get() or "Nouvelle tâche",
                "date_evenement": date.get() or datetime.now().strftime("%Y-%m-%d %H:%M"),
                "type_evenement": kind.get(),
                "statut": status.get(),
            }
        )
        self.show_agenda()

    def _save_settings(
        self,
        entries: dict[str, ctk.CTkEntry],
        theme: ctk.CTkOptionMenu | None = None,
        backup: ctk.CTkOptionMenu | None = None,
    ) -> None:
        """Persiste les paramètres saisis dans la base."""
        for key, entry in entries.items():
            self.service.save_setting(key, entry.get())
        if theme:
            self.service.save_setting("theme", theme.get())
            ctk.set_appearance_mode(theme.get())
        if backup:
            self.service.save_setting("auto_backup", backup.get())
        self.show_settings()

    def _manual_backup(self) -> None:
        """Déclenche une sauvegarde manuelle."""
        path = self.backup_manager.create_backup()
        self.status_label.configure(text=f"Sauvegarde : {path.name if path else 'base absente'}")

    def _auto_backup(self) -> None:
        """Effectue une sauvegarde automatique périodique."""
        settings = self.service.settings()
        if settings.get("auto_backup") == "enabled":
            path = self.backup_manager.create_backup()
            if path:
                self.status_label.configure(text=f"Sauvegarde auto : {path.name}")
        try:
            interval_minutes = max(1, int(settings.get("backup_interval_minutes", "15")))
        except ValueError:
            interval_minutes = 15
        self.after(interval_minutes * 60 * 1000, self._auto_backup)

    def _reload_current_view(self) -> None:
        """Recharge la vue active après une action utilisateur."""
        routes = {
            "Dashboard": self.show_dashboard,
            "Stock": self.show_stock,
            "Ventes": self.show_sales,
            "Clients": self.show_clients,
            "Comptabilité": self.show_accounting,
            "Factures": self.show_invoices,
            "Statistiques": self.show_statistics,
            "Agenda": self.show_agenda,
            "Paramètres": self.show_settings,
        }
        routes[self.current_view]()
