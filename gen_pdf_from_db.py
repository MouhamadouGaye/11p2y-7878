import psycopg2
from fpdf import FPDF
from decimal import Decimal  # Make sure to import Decimal

# Function to connect to the database
def connect_db():
    # Replace these with your actual database connection details
    return psycopg2.connect(
        host="your_host",
        database="your_database",
        user="your_user",
        password="your_password"
    )

# Function to generate the invoice
def generate_invoice(invoice_id):
    # Connect to the database and fetch items for the invoice
    conn = connect_db()
    cursor = conn.cursor()

    # Execute the SQL query to fetch invoice data
    cursor.execute("""
        SELECT products.name, products.price, transaction_items.quantity
        FROM transaction_items
        JOIN products ON transaction_items.product_id = products.id
        WHERE transaction_items.transaction_id = %s
    """, (invoice_id,))
    items = cursor.fetchall()
    conn.close()

    # Calculate totals and other invoice data
    subtotal = Decimal(0)  # Use Decimal for precision
    for item in items:
        price = Decimal(item[1])  # Convert price to Decimal
        quantity = item[2]
        subtotal += price * quantity  # Perform multiplication with Decimal

    # Tax rate should also be a Decimal for precision
    tax_rate = Decimal('0.05')  # 5% tax rate as a Decimal
    tax = subtotal * tax_rate
    total = subtotal + tax

    # Create the PDF document
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="INVOICE", ln=True, align="C")

    # Invoice information
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Transaction ID: {invoice_id}", ln=True)
    pdf.ln(10)

    # Table headers
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "Item", border=1, align="C")
    pdf.cell(30, 10, "Quantity", border=1, align="C")
    pdf.cell(30, 10, "Price", border=1, align="C")
    pdf.cell(30, 10, "Total", border=1, align="C")
    pdf.ln()

    # Table content
    pdf.set_font("Arial", size=12)
    for item in items:
        name, price, quantity = item
        price = Decimal(price)  # Ensure price is a Decimal
        line_total = price * quantity  # Multiply with Decimal
        pdf.cell(80, 10, name, border=1)
        pdf.cell(30, 10, str(quantity), border=1, align="C")
        pdf.cell(30, 10, f"${price:.2f}", border=1, align="C")
        pdf.cell(30, 10, f"${line_total:.2f}", border=1, align="C")
        pdf.ln()

    # Footer (totals)
    pdf.ln(10)
    pdf.cell(140, 10, "Subtotal", border=1)
    pdf.cell(30, 10, f"${subtotal:.2f}", border=1, align="C")
    pdf.ln()

    pdf.cell(140, 10, f"Tax (5%)", border=1)
    pdf.cell(30, 10, f"${tax:.2f}", border=1, align="C")
    pdf.ln()

    pdf.cell(140, 10, "Total Amount", border=1)
    pdf.cell(30, 10, f"${total:.2f}", border=1, align="C")

    # Output the PDF to a file
    pdf.output(f"Invoice_{invoice_id}.pdf")

    print(f"Invoice saved as Invoice_{invoice_id}.pdf")

# Example of usage
invoice_id = 12345  # Replace this with the actual invoice ID
generate_invoice(invoice_id)
