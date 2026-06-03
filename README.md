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
- Navigation latérale : Dashboard, Stock, Clients, Comptabilité, Factures, Statistiques, Agenda, Paramètres.
- Création automatique des tables SQLite.
- Gestion produits, clients, comptabilité, factures PDF, agenda et paramètres.
- Graphiques Matplotlib intégrés.
- Sauvegarde automatique de la base SQLite.
- Architecture orientée objet, modulaire et commentée.
