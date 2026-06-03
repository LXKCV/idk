"""Génération de factures PDF professionnelles avec ReportLab."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import PDF_DIR


class InvoicePDFGenerator:
    """Produit des factures PDF prêtes à envoyer au client."""

    def __init__(self, output_dir: Path = PDF_DIR) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, invoice: dict[str, Any], company: dict[str, str], client: dict[str, Any] | None) -> Path:
        """Génère une facture avec coordonnées, TVA, total et style premium."""
        invoice_number = invoice["numero"]
        output_path = self.output_dir / f"{invoice_number}.pdf"
        document = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(f"<b>{company.get('company_name', 'Entreprise')}</b>", styles["Title"]))
        story.append(Paragraph(company.get("company_address", ""), styles["Normal"]))
        story.append(Paragraph(company.get("company_email", ""), styles["Normal"]))
        story.append(Spacer(1, 24))
        story.append(Paragraph(f"<b>Facture {invoice_number}</b>", styles["Heading1"]))
        story.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]))
        story.append(Spacer(1, 16))

        client_name = "Client non renseigné"
        if client:
            client_name = f"{client.get('prenom', '')} {client.get('nom', '')}".strip()
        story.append(Paragraph(f"<b>Client :</b> {client_name}", styles["Heading3"]))
        if client:
            story.append(Paragraph(client.get("adresse", ""), styles["Normal"]))
            story.append(Paragraph(client.get("email", ""), styles["Normal"]))
        story.append(Spacer(1, 20))

        total = float(invoice.get("total", 0))
        vat = float(invoice.get("tva", 0))
        ht = total - vat
        table = Table(
            [
                ["Description", "Montant"],
                ["Prestations / produits", f"{ht:,.2f} €"],
                ["TVA", f"{vat:,.2f} €"],
                ["Total TTC", f"{total:,.2f} €"],
            ],
            colWidths=[340, 120],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#7C3AED")),
                    ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("PADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 28))
        story.append(Paragraph("Merci pour votre confiance.", styles["Italic"]))
        document.build(story)
        return output_path
