
# - Register Products with Barcodes:
# Provide an interface in your POS software to register new products.
# For each new product, ask the user to input the product name, price, and scan the product’s barcode (or manually enter it if needed).
# Save this data to the database using an SQL INSERT command.
from gen_invoices import connect_db
import tkinter as tk
from tkinter import messagebox
from pos_main import add_to_cart, fenetre


def register_product(name, price, barcode):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, price, barcode)
        VALUES (%s, %s, %s)
    """, (name, price, barcode))
    conn.commit()
    conn.close()
    print("Product registered successfully.")



# - Integrate Barcode Scanner for Product Lookup:
# Barcode scanners typically act as input devices, sending scanned codes to the computer as text, followed by an "Enter" keypress.
# Set up a text entry field in the POS interface where the scanner can "input" scanned data.
# When the scanner inputs a barcode, the system searches for a matching product in the database and adds it to the cart.
# Here’s an example of how you might implement this in Tkinter:

# Function to search product by barcode
def find_product_by_barcode(barcode):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products WHERE barcode = %s", (barcode,))
    product = cursor.fetchone()
    conn.close()
    return product  # Returns a tuple (name, price) or None if not found

# Function to handle barcode scanning
def handle_barcode_scan(event):
    barcode = barcode_entry.get()  # Get barcode from entry field
    product = find_product_by_barcode(barcode)
    barcode_entry.delete(0, tk.END)  # Clear entry after scanning

    if product:
        name, price = product
        add_to_cart(name, price)  # Add product to cart
    else:
        messagebox.showerror("Error", "Product not found.")

# Set up barcode entry field and bind Enter key
barcode_entry = tk.Entry(fenetre, font=("Arial", 14))
barcode_entry.pack(pady=10)
barcode_entry.bind("<Return>", handle_barcode_scan)
