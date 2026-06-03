"""Accès SQLite et création automatique du schéma ERP.

La classe :class:`DatabaseManager` centralise toutes les connexions et expose
une API simple pour exécuter des requêtes. Le choix de SQLite permet de fournir
un ERP local, portable et autonome.
"""

import sqlite3
from pathlib import Path
from typing import Any, Iterable

from app.config import DATABASE_PATH


class DatabaseManager:
    """Gestionnaire responsable de la base SQLite locale."""

    def __init__(self, database_path: Path = DATABASE_PATH) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_schema()

    def connect(self) -> sqlite3.Connection:
        """Ouvre une connexion configurée pour retourner des lignes nommées."""
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def execute(self, query: str, params: Iterable[Any] = ()) -> int:
        """Exécute une requête d'écriture et retourne l'identifiant créé."""
        with self.connect() as connection:
            cursor = connection.execute(query, tuple(params))
            connection.commit()
            return int(cursor.lastrowid)

    def executemany(self, query: str, rows: Iterable[Iterable[Any]]) -> None:
        """Exécute plusieurs écritures dans une seule transaction."""
        with self.connect() as connection:
            connection.executemany(query, rows)
            connection.commit()

    def fetch_all(self, query: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        """Retourne toutes les lignes d'une requête de lecture."""
        with self.connect() as connection:
            return list(connection.execute(query, tuple(params)).fetchall())

    def fetch_one(self, query: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
        """Retourne une seule ligne, ou ``None`` si aucun résultat n'existe."""
        with self.connect() as connection:
            return connection.execute(query, tuple(params)).fetchone()

    def initialize_schema(self) -> None:
        """Crée automatiquement toutes les tables nécessaires à l'ERP."""
        schema = """
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            categorie TEXT DEFAULT 'Général',
            quantite INTEGER NOT NULL DEFAULT 0,
            prix_achat REAL NOT NULL DEFAULT 0,
            prix_vente REAL NOT NULL DEFAULT 0,
            fournisseur TEXT DEFAULT '',
            seuil_stock INTEGER NOT NULL DEFAULT 5,
            date_creation TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT DEFAULT '',
            telephone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            adresse TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            date_ajout TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ventes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            montant_total REAL NOT NULL DEFAULT 0,
            tva REAL NOT NULL DEFAULT 0,
            date_vente TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS vente_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vente_id INTEGER NOT NULL,
            produit_id INTEGER,
            nom_produit TEXT NOT NULL,
            quantite INTEGER NOT NULL,
            prix_unitaire REAL NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (vente_id) REFERENCES ventes(id) ON DELETE CASCADE,
            FOREIGN KEY (produit_id) REFERENCES produits(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS factures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL UNIQUE,
            client_id INTEGER,
            vente_id INTEGER,
            chemin_pdf TEXT DEFAULT '',
            statut TEXT NOT NULL DEFAULT 'Brouillon',
            total REAL NOT NULL DEFAULT 0,
            tva REAL NOT NULL DEFAULT 0,
            date_facture TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL,
            FOREIGN KEY (vente_id) REFERENCES ventes(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS revenus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libelle TEXT NOT NULL,
            categorie TEXT DEFAULT 'Vente',
            montant REAL NOT NULL,
            date_revenu TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS depenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libelle TEXT NOT NULL,
            categorie TEXT DEFAULT 'Général',
            montant REAL NOT NULL,
            date_depense TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            description TEXT DEFAULT '',
            date_evenement TEXT NOT NULL,
            type_evenement TEXT DEFAULT 'Tâche',
            notification INTEGER NOT NULL DEFAULT 0,
            statut TEXT NOT NULL DEFAULT 'À faire'
        );

        CREATE TABLE IF NOT EXISTS stock_mouvements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produit_id INTEGER,
            type_mouvement TEXT NOT NULL,
            quantite INTEGER NOT NULL,
            commentaire TEXT DEFAULT '',
            date_mouvement TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produit_id) REFERENCES produits(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS settings (
            cle TEXT PRIMARY KEY,
            valeur TEXT NOT NULL
        );
        """
        with self.connect() as connection:
            connection.executescript(schema)
            connection.commit()
