"""Point d'entrée de l'ERP Premium.

Lancer avec :
    python main.py
"""

from app.ui import PremiumERPApp


def main() -> None:
    """Initialise et lance la boucle principale de l'interface."""
    app = PremiumERPApp()
    app.mainloop()


if __name__ == "__main__":
    main()
