# ERP Premium Python

ERP professionnel local développé en Python 3 avec CustomTkinter, SQLite, Matplotlib et ReportLab.

## Arborescence

```text
.
├── app/
│   ├── __init__.py
│   ├── backup.py
│   ├── charts.py
│   ├── config.py
│   ├── database.py
│   ├── pdf_generator.py
│   ├── services.py
│   └── ui.py
├── assets/
│   └── .gitkeep
├── backups/
│   └── .gitkeep
├── database/
│   └── .gitkeep
├── pdf/
│   └── .gitkeep
├── exports/
│   └── exports CSV générés
├── tests/
│   └── .gitkeep
├── main.py
├── requirements.txt
└── README.md
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Fonctionnalités incluses

- Interface sombre premium inspirée SaaS.
- Navigation latérale : Dashboard, Stock, Ventes, Clients, Comptabilité, Factures, Statistiques, Agenda, Paramètres.
- Création automatique des tables SQLite.
- Gestion produits, clients, comptabilité, factures PDF, agenda et paramètres.
- Module ventes avec panier, décrément automatique du stock, génération de revenu et facture PDF optionnelle.
- Suivi stock avancé : valeur d'achat, valeur de vente, seuils faibles, corrections entrée/sortie et historique des mouvements.
- Exports CSV sur les tableaux principaux pour réutiliser les données hors de l'application.
- Graphiques Matplotlib intégrés.
- Sauvegarde automatique de la base SQLite avec intervalle paramétrable.
- Architecture orientée objet, modulaire et commentée.
