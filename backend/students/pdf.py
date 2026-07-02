from reportlab.pdfgen import canvas

def generate_pdf():

    pdf = canvas.Canvas("report.pdf")

    pdf.drawString(
        100,
        750,
        "Student Report"
    )

    pdf.save()