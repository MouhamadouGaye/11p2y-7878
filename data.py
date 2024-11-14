
import psycopg2
from tkinter import messagebox



# Function to connect to the PostgreSQL database
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="XXXXX",
            user="XXXXXXX",
            password="XXXXXX",
            host="localhost",
            port="XXXX"
        )
        return conn
    except Exception as e:
        print("Error connecting to database:", e)
        return None

# Function to generate an invoice
def generate_invoice(transaction_id):
    conn = connect_db()
    if conn is None:
        messagebox.showerror("Database Error", "Failed to connect to the database.")
        return
    
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT products.name, products.price, transaction_items.quantity
        FROM transaction_items
        JOIN products ON transaction_items.product_id = products.id
        WHERE transaction_items.transaction_id = %s
        """,
        (transaction_id,)
    )
    items = cursor.fetchall()
    conn.close()

    # Write invoice to a file
    with open(f"Invoice_{transaction_id}.txt", "w") as f:
        f.write("INVOICE\n")
        f.write(f"Transaction ID: {transaction_id}\n\n")
        f.write("Items:\n")
        total = 0
        for name, price, quantity in items:
            line_total = price * quantity
            f.write(f"{name} x{quantity} - ${line_total:.2f}\n")
            total += line_total
        f.write("\n")
        f.write(f"Total Amount: ${total:.2f}\n")
    messagebox.showinfo("Invoice Generated", f"Invoice_{transaction_id}.txt created.")
