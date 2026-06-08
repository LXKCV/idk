# ERP Premium Python

ERP Premium Python est une application ERP locale avec interface graphique sombre, développée en Python 3 avec CustomTkinter, SQLite, Matplotlib et ReportLab. Elle permet de gérer une activité depuis un tableau de bord unique : stock, clients, comptabilité, factures PDF, statistiques, agenda et paramètres d'entreprise.

## Fonctionnalités

### Tableau de bord

- Affichage des indicateurs clés : chiffre d'affaires, nombre de clients, nombre de produits et produits en stock faible.
- Graphique revenus/dépenses/bénéfices mensuels.
- Liste rapide des dernières factures.
- Liste rapide des produits dont la quantité est inférieure ou égale au seuil d'alerte.

### Gestion du stock

- Ajout, modification et suppression de produits.
- Recherche dans les produits par nom, catégorie ou fournisseur.
- Champs produits : nom, catégorie, quantité, prix d'achat, prix de vente, fournisseur et seuil de stock faible.
- Journalisation automatique d'une entrée de stock lors de la création d'un produit.
- Alertes de stock faible basées sur le seuil configuré pour chaque produit.

### Gestion des clients

- Ajout, modification et suppression de fiches clients.
- Recherche dans les clients par nom, prénom, téléphone ou email.
- Champs clients : prénom, nom, téléphone, email, adresse et notes.
- Données clients réutilisées lors de la création des factures.

### Comptabilité

- Suivi des revenus, dépenses et bénéfices.
- Ajout rapide d'une opération en revenu ou en dépense.
- Catégorisation des opérations comptables.
- Synthèse comptable affichée sous forme de cartes.
- Graphique d'évolution mensuelle des revenus et dépenses.

### Factures PDF

- Création de factures depuis l'interface.
- Sélection d'un client existant.
- Saisie du total TTC et de la TVA.
- Génération automatique d'un numéro de facture.
- Export PDF professionnel avec les informations de l'entreprise, du client, de la TVA et du total.
- Stockage des PDF générés dans le dossier `pdf/`.

### Statistiques

- Graphique du chiffre d'affaires par mois.
- Graphique des produits les plus vendus.
- Visualisations intégrées à l'interface avec Matplotlib.

### Agenda

- Ajout d'événements, tâches et rendez-vous.
- Date d'événement au format `YYYY-MM-DD HH:MM`.
- Suivi du type d'événement et du statut.
- Affichage des événements triés par date.

### Paramètres

- Configuration de l'identité de l'entreprise : nom, adresse, téléphone et email.
- Configuration du taux de TVA.
- Sauvegarde manuelle de la base de données depuis l'interface.
- Paramètres persistants enregistrés dans SQLite.

### Base de données et sauvegardes

- Base de données SQLite locale créée automatiquement au lancement.
- Tables créées automatiquement : produits, clients, ventes, lignes de vente, factures, revenus, dépenses, agenda, mouvements de stock et paramètres.
- Données de démonstration ajoutées au premier lancement si la base est vide.
- Sauvegardes horodatées de la base SQLite dans le dossier `backups/`.

## Prérequis

- Windows recommandé pour utiliser `setup.bat`.
- Python 3.10 ou plus récent conseillé.
- `pip` disponible dans l'installation Python.

## Lancement rapide sur Windows

Double-cliquez sur le fichier :

```bat
setup.bat
```

Le script se place automatiquement dans le dossier du projet, installe les dépendances avec :

```bat
pip install -r requirements.txt
```

puis lance l'application avec :

```bat
python main.py
```

## Lancement manuel

Si vous préférez lancer l'application manuellement :

```bash
pip install -r requirements.txt
python main.py
```

## Dépendances

Les dépendances sont listées dans `requirements.txt` :

- `customtkinter` : interface graphique moderne.
- `matplotlib` : graphiques et statistiques.
- `reportlab` : génération des factures PDF.
- `pillow` : support image utilisé par l'interface graphique.

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
├── setup.bat
└── README.md
```

## Dossiers générés et utilisés

- `database/` : contient la base SQLite principale `erp.sqlite3`.
- `pdf/` : contient les factures PDF générées.
- `backups/` : contient les copies de sauvegarde horodatées.
- `assets/` : prévu pour les ressources visuelles de l'application.
- `tests/` : prévu pour les tests futurs.

## Notes d'utilisation

- Au premier lancement, l'application crée automatiquement la base de données et insère quelques données de démonstration.
- Les factures PDF sont générées uniquement après création d'une facture depuis l'onglet `Factures`.
- Les informations affichées sur les factures proviennent de l'onglet `Paramètres`.
- Pour conserver vos données, gardez le dossier `database/` et pensez à créer des sauvegardes depuis l'onglet `Paramètres`.
