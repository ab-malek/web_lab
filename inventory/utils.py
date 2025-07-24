from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from django.utils import timezone


def generate_invoice_pdf(invoice):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("PHARMACY INVOICE", title_style))
    
    # Invoice details
    invoice_info = [
        ['Invoice Number:', invoice.invoice_number],
        ['Date:', invoice.created_at.strftime('%Y-%m-%d %H:%M')],
        ['Customer:', invoice.customer_name or 'Walk-in Customer'],
        ['Served by:', invoice.created_by.get_full_name() or invoice.created_by.username],
    ]
    
    invoice_table = Table(invoice_info, colWidths=[2*inch, 3*inch])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(invoice_table)
    story.append(Spacer(1, 20))
    
    # Sales items
    data = [['Medicine', 'Batch', 'Quantity', 'Unit Price', 'Total']]
    
    for sale in invoice.sales.all():
        data.append([
            sale.medicine.name,
            sale.medicine.batch_number,
            str(sale.quantity_sold),
            f"Tk{sale.unit_price:.2f}",
            f"Tk{sale.total_amount:.2f}"
        ])
    
    # Add total row
    data.append(['', '', '', 'TOTAL:', f"Tk{invoice.total_amount:.2f}"])
    
    table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    # Footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1
    )
    story.append(Paragraph("Thank you for your business!", footer_style))
    
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
