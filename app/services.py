"""Services métier de l'ERP.

Les services encapsulent les règles métier afin que l'interface graphique reste
claire et que les opérations critiques soient testables indépendamment.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.config import DEFAULT_LOW_STOCK_THRESHOLD
from app.database import DatabaseManager


class ERPService:
    """Façade métier utilisée par toutes les vues de l'application."""

    def __init__(self, database: DatabaseManager) -> None:
        self.database = database
        self.ensure_default_settings()
        self.seed_demo_data_if_empty()

    def ensure_default_settings(self) -> None:
        """Insère les paramètres par défaut de l'entreprise."""
        defaults = {
            "company_name": "ERP Premium SAS",
            "company_address": "12 Avenue SaaS, 75000 Paris",
            "company_phone": "+33 1 23 45 67 89",
            "company_email": "contact@erp-premium.local",
            "vat_rate": "20",
            "theme": "dark",
            "auto_backup": "enabled",
        }
        for key, value in defaults.items():
            self.database.execute(
                "INSERT OR IGNORE INTO settings (cle, valeur) VALUES (?, ?)",
                (key, value),
            )

    def seed_demo_data_if_empty(self) -> None:
        """Ajoute quelques données de démonstration au premier lancement."""
        count = self.database.fetch_one("SELECT COUNT(*) AS total FROM produits")
        if count and count["total"]:
            return
        products = [
            ("MacBook Pro 14", "Informatique", 8, 1600, 2290, "Apple", 3),
            ("Chaise ergonomique", "Bureau", 4, 120, 289, "OfficePro", 5),
            ("Licence CRM", "Logiciel", 25, 20, 79, "CloudSoft", 10),
        ]
        self.database.executemany(
            """
            INSERT INTO produits (nom, categorie, quantite, prix_achat, prix_vente, fournisseur, seuil_stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            products,
        )
        clients = [
            ("Martin", "Alice", "+33 6 11 22 33 44", "alice@example.com", "Lyon", "Client premium"),
            ("Bernard", "Hugo", "+33 6 55 66 77 88", "hugo@example.com", "Paris", "Paiement rapide"),
        ]
        self.database.executemany(
            "INSERT INTO clients (nom, prenom, telephone, email, adresse, notes) VALUES (?, ?, ?, ?, ?, ?)",
            clients,
        )
        self.database.executemany(
            "INSERT INTO revenus (libelle, categorie, montant, date_revenu) VALUES (?, ?, ?, ?)",
            [
                ("Vente licences", "Logiciel", 2370, "2026-04-12"),
                ("Vente matériel", "Informatique", 4580, "2026-05-08"),
                ("Services", "Conseil", 1800, "2026-06-01"),
            ],
        )
        self.database.executemany(
            "INSERT INTO depenses (libelle, categorie, montant, date_depense) VALUES (?, ?, ?, ?)",
            [
                ("Marketing", "Publicité", 650, "2026-04-20"),
                ("Fournitures", "Bureau", 320, "2026-05-18"),
                ("Hébergement", "Infrastructure", 180, "2026-06-02"),
            ],
        )

    def dashboard_metrics(self) -> dict[str, Any]:
        """Calcule les indicateurs clés affichés sur le dashboard."""
        revenue = self.database.fetch_one("SELECT COALESCE(SUM(montant), 0) AS total FROM revenus")
        clients = self.database.fetch_one("SELECT COUNT(*) AS total FROM clients")
        products = self.database.fetch_one("SELECT COUNT(*) AS total FROM produits")
        low_stock = self.database.fetch_one(
            "SELECT COUNT(*) AS total FROM produits WHERE quantite <= seuil_stock"
        )
        expenses = self.database.fetch_one("SELECT COALESCE(SUM(montant), 0) AS total FROM depenses")
        return {
            "revenue": float(revenue["total"] if revenue else 0),
            "clients": int(clients["total"] if clients else 0),
            "products": int(products["total"] if products else 0),
            "low_stock": int(low_stock["total"] if low_stock else 0),
            "profit": float((revenue["total"] if revenue else 0) - (expenses["total"] if expenses else 0)),
        }

    def list_products(self, search: str = "") -> list[dict[str, Any]]:
        """Liste les produits avec recherche par nom, catégorie ou fournisseur."""
        pattern = f"%{search}%"
        rows = self.database.fetch_all(
            """
            SELECT * FROM produits
            WHERE nom LIKE ? OR categorie LIKE ? OR fournisseur LIKE ?
            ORDER BY date_creation DESC
            """,
            (pattern, pattern, pattern),
        )
        return [dict(row) for row in rows]

    def add_product(self, values: dict[str, Any]) -> int:
        """Ajoute un produit et journalise l'entrée de stock initiale."""
        product_id = self.database.execute(
            """
            INSERT INTO produits (nom, categorie, quantite, prix_achat, prix_vente, fournisseur, seuil_stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                values["nom"],
                values.get("categorie", "Général"),
                int(values.get("quantite", 0)),
                float(values.get("prix_achat", 0)),
                float(values.get("prix_vente", 0)),
                values.get("fournisseur", ""),
                int(values.get("seuil_stock", DEFAULT_LOW_STOCK_THRESHOLD)),
            ),
        )
        self.database.execute(
            "INSERT INTO stock_mouvements (produit_id, type_mouvement, quantite, commentaire) VALUES (?, ?, ?, ?)",
            (product_id, "Entrée", int(values.get("quantite", 0)), "Création produit"),
        )
        return product_id

    def update_product(self, product_id: int, values: dict[str, Any]) -> None:
        """Met à jour les informations principales d'un produit."""
        self.database.execute(
            """
            UPDATE produits
            SET nom = ?, categorie = ?, quantite = ?, prix_achat = ?, prix_vente = ?, fournisseur = ?, seuil_stock = ?
            WHERE id = ?
            """,
            (
                values["nom"],
                values.get("categorie", "Général"),
                int(values.get("quantite", 0)),
                float(values.get("prix_achat", 0)),
                float(values.get("prix_vente", 0)),
                values.get("fournisseur", ""),
                int(values.get("seuil_stock", DEFAULT_LOW_STOCK_THRESHOLD)),
                product_id,
            ),
        )

    def delete_product(self, product_id: int) -> None:
        """Supprime un produit du catalogue."""
        self.database.execute("DELETE FROM produits WHERE id = ?", (product_id,))

    def list_clients(self, search: str = "") -> list[dict[str, Any]]:
        """Liste les clients avec recherche instantanée."""
        pattern = f"%{search}%"
        rows = self.database.fetch_all(
            """
            SELECT * FROM clients
            WHERE nom LIKE ? OR prenom LIKE ? OR telephone LIKE ? OR email LIKE ?
            ORDER BY date_ajout DESC
            """,
            (pattern, pattern, pattern, pattern),
        )
        return [dict(row) for row in rows]

    def add_client(self, values: dict[str, str]) -> int:
        """Crée une fiche client complète."""
        return self.database.execute(
            """
            INSERT INTO clients (nom, prenom, telephone, email, adresse, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                values["nom"],
                values.get("prenom", ""),
                values.get("telephone", ""),
                values.get("email", ""),
                values.get("adresse", ""),
                values.get("notes", ""),
            ),
        )


    def update_client(self, client_id: int, values: dict[str, str]) -> None:
        """Met à jour une fiche client existante."""
        self.database.execute(
            """
            UPDATE clients
            SET nom = ?, prenom = ?, telephone = ?, email = ?, adresse = ?, notes = ?
            WHERE id = ?
            """,
            (
                values["nom"],
                values.get("prenom", ""),
                values.get("telephone", ""),
                values.get("email", ""),
                values.get("adresse", ""),
                values.get("notes", ""),
                client_id,
            ),
        )

    def delete_client(self, client_id: int) -> None:
        """Supprime une fiche client."""
        self.database.execute("DELETE FROM clients WHERE id = ?", (client_id,))

    def accounting_summary(self) -> dict[str, float]:
        """Retourne revenus, dépenses et bénéfice global."""
        revenue = self.database.fetch_one("SELECT COALESCE(SUM(montant), 0) AS total FROM revenus")
        expenses = self.database.fetch_one("SELECT COALESCE(SUM(montant), 0) AS total FROM depenses")
        revenue_total = float(revenue["total"] if revenue else 0)
        expense_total = float(expenses["total"] if expenses else 0)
        return {"revenus": revenue_total, "depenses": expense_total, "benefice": revenue_total - expense_total}

    def add_revenue(self, libelle: str, categorie: str, montant: float) -> int:
        """Ajoute une entrée de revenu."""
        return self.database.execute(
            "INSERT INTO revenus (libelle, categorie, montant) VALUES (?, ?, ?)",
            (libelle, categorie, montant),
        )

    def add_expense(self, libelle: str, categorie: str, montant: float) -> int:
        """Ajoute une dépense."""
        return self.database.execute(
            "INSERT INTO depenses (libelle, categorie, montant) VALUES (?, ?, ?)",
            (libelle, categorie, montant),
        )

    def monthly_finance(self) -> list[dict[str, Any]]:
        """Agrège les revenus et dépenses par mois pour les graphiques."""
        rows = self.database.fetch_all(
            """
            SELECT mois, SUM(revenus) AS revenus, SUM(depenses) AS depenses
            FROM (
                SELECT strftime('%Y-%m', date_revenu) AS mois, montant AS revenus, 0 AS depenses FROM revenus
                UNION ALL
                SELECT strftime('%Y-%m', date_depense) AS mois, 0 AS revenus, montant AS depenses FROM depenses
            )
            GROUP BY mois
            ORDER BY mois
            """
        )
        return [dict(row) for row in rows]

    def top_products(self) -> list[dict[str, Any]]:
        """Retourne les produits les plus vendus à partir des lignes de vente."""
        rows = self.database.fetch_all(
            """
            SELECT nom_produit, COALESCE(SUM(quantite), 0) AS total
            FROM vente_items
            GROUP BY nom_produit
            ORDER BY total DESC
            LIMIT 8
            """
        )
        return [dict(row) for row in rows]

    def list_invoices(self) -> list[dict[str, Any]]:
        """Liste les factures avec le nom du client associé."""
        rows = self.database.fetch_all(
            """
            SELECT f.*, COALESCE(c.prenom || ' ' || c.nom, 'Client supprimé') AS client
            FROM factures f
            LEFT JOIN clients c ON c.id = f.client_id
            ORDER BY f.date_facture DESC
            """
        )
        return [dict(row) for row in rows]

    def create_invoice_record(self, client_id: int | None, total: float, tva: float) -> int:
        """Crée l'enregistrement d'une facture et génère son numéro lisible."""
        number = f"FAC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        return self.database.execute(
            "INSERT INTO factures (numero, client_id, total, tva, statut) VALUES (?, ?, ?, ?, ?)",
            (number, client_id, total, tva, "Émise"),
        )

    def update_invoice_pdf_path(self, invoice_id: int, path: str) -> None:
        """Associe un chemin PDF à une facture."""
        self.database.execute("UPDATE factures SET chemin_pdf = ? WHERE id = ?", (path, invoice_id))

    def list_agenda(self) -> list[dict[str, Any]]:
        """Liste les rendez-vous, tâches et événements."""
        rows = self.database.fetch_all("SELECT * FROM agenda ORDER BY date_evenement ASC")
        return [dict(row) for row in rows]

    def add_event(self, values: dict[str, Any]) -> int:
        """Ajoute un élément d'agenda."""
        return self.database.execute(
            """
            INSERT INTO agenda (titre, description, date_evenement, type_evenement, notification, statut)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                values["titre"],
                values.get("description", ""),
                values["date_evenement"],
                values.get("type_evenement", "Tâche"),
                int(values.get("notification", 0)),
                values.get("statut", "À faire"),
            ),
        )

    def settings(self) -> dict[str, str]:
        """Retourne tous les paramètres applicatifs."""
        rows = self.database.fetch_all("SELECT cle, valeur FROM settings")
        return {row["cle"]: row["valeur"] for row in rows}

    def save_setting(self, key: str, value: str) -> None:
        """Crée ou met à jour un paramètre."""
        self.database.execute(
            "INSERT INTO settings (cle, valeur) VALUES (?, ?) ON CONFLICT(cle) DO UPDATE SET valeur = excluded.valeur",
            (key, value),
        )
