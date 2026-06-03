"""Composants graphiques Matplotlib intégrables dans CustomTkinter."""

from __future__ import annotations

from typing import Any

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from app.config import COLORS


class ChartFactory:
    """Fabrique des graphiques harmonisés avec le thème sombre."""

    @staticmethod
    def finance_chart(parent: Any, monthly_rows: list[dict[str, Any]]) -> FigureCanvasTkAgg:
        """Crée un graphique revenus/dépenses mensuels."""
        figure = Figure(figsize=(7, 3.4), dpi=110, facecolor=COLORS["card"])
        axis = figure.add_subplot(111)
        axis.set_facecolor(COLORS["card"])

        labels = [row["mois"] for row in monthly_rows] or ["Aucune donnée"]
        revenues = [float(row["revenus"] or 0) for row in monthly_rows] or [0]
        expenses = [float(row["depenses"] or 0) for row in monthly_rows] or [0]

        axis.plot(labels, revenues, color=COLORS["accent"], marker="o", linewidth=2.5, label="Revenus")
        axis.plot(labels, expenses, color=COLORS["warning"], marker="o", linewidth=2.5, label="Dépenses")
        axis.fill_between(labels, revenues, color=COLORS["accent"], alpha=0.08)
        axis.tick_params(colors=COLORS["muted"], labelsize=8)
        axis.spines[:].set_color(COLORS["border"])
        axis.grid(color=COLORS["border"], alpha=0.3)
        axis.legend(facecolor=COLORS["panel"], edgecolor=COLORS["border"], labelcolor=COLORS["text"])
        figure.tight_layout()
        return FigureCanvasTkAgg(figure, master=parent)

    @staticmethod
    def bar_chart(parent: Any, title: str, labels: list[str], values: list[float]) -> FigureCanvasTkAgg:
        """Crée un histogramme premium pour les statistiques."""
        figure = Figure(figsize=(7, 3.4), dpi=110, facecolor=COLORS["card"])
        axis = figure.add_subplot(111)
        axis.set_facecolor(COLORS["card"])
        axis.bar(labels or ["Aucune donnée"], values or [0], color=COLORS["primary"])
        axis.set_title(title, color=COLORS["text"], fontsize=12, fontweight="bold")
        axis.tick_params(colors=COLORS["muted"], labelsize=8)
        axis.spines[:].set_color(COLORS["border"])
        axis.grid(axis="y", color=COLORS["border"], alpha=0.25)
        figure.tight_layout()
        return FigureCanvasTkAgg(figure, master=parent)
