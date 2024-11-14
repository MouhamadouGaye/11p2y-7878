
### IN THIS ONE WE LL ADD VIEW AND PRINT INCOICES
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
from calculator import open_calculator  # Import the calculator function
from gen_invoices import connect_db, generate_invoice
from products import products
from fpdf import FPDF
from decimal import Decimal



cart_items = []  # Store items in the cart

# Function to add a selected item to the cart
def add_to_cart(product, price):
    cart_listbox.insert(tk.END, f"{product:<30} - ${price:7.2f}")
    cart_items.append((product, price))
    update_total()

# Function to update total price
def update_total():
    total_price = sum(price for _, price in cart_items)
    total_label.config(text=f"Total: ${total_price:.2f}")


# Function to show payment summary in a new pop-up window
def checkout(payment_method):
    if not cart_items:
        messagebox.showwarning("Empty Cart", "No items in the cart to checkout.")
        return
    
    checkout_window = tk.Toplevel(fenetre)
    checkout_window.title("Checkout Summary")
    checkout_window.geometry("300x200")
    
    total_price = sum(price for _, price in cart_items)
    
    tk.Label(checkout_window, text=f"Total Amount: ${total_price:.2f}", font=("Arial", 14)).pack(pady=10)
    tk.Label(checkout_window, text=f"Payment Method: {payment_method}", font=("Arial", 12)).pack(pady=5)

    def finalize_checkout():
        if not cart_items:
            messagebox.showwarning("Empty Cart", "No items in the cart to checkout.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Insert transaction record
            total_price = sum(price for _, price in cart_items)
            cursor.execute(
                "INSERT INTO transactions (total, payment_method) VALUES (%s, %s) RETURNING id",
                (total_price, selected_payment.get())
            )
            transaction_id = cursor.fetchone()[0]

            # Insert each item in transaction_items
            for product, price in cart_items:
                cursor.execute("SELECT id FROM products WHERE name = %s", (product,))
                product_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO transaction_items (transaction_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (transaction_id, product_id, 1)  # Quantity is 1 for simplicity
                )
            
            conn.commit()
            messagebox.showinfo("Thank you!", "Payment successful. Transaction saved.")
            
            # Generate invoice after transaction
            generate_invoice(transaction_id)
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", "Failed to save transaction.")
            print("Error:", e)
        finally:
            conn.close()
            cart_listbox.delete(0, tk.END)
            cart_items.clear()
            update_total()



    tk.Button(checkout_window, text="Confirm Payment", command=finalize_checkout).pack(pady=20)



# Main POS window setup
fenetre = tk.Tk()
fenetre.title("Shop POS System")
fenetre.geometry("1000x750")
fenetre.config(bg="#F7F7F7")

# Menu bar
menu_bar = tk.Menu(fenetre)
fenetre.config(menu=menu_bar)
options_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Options", menu=options_menu)

# Add calculator to options menu
options_menu.add_command(label="Calculator", command=lambda: open_calculator(fenetre))


# Frame for products
product_frame = tk.Frame(fenetre, bg="#3d6464", width="600",  bd=1)
product_frame.pack(side=tk.LEFT, padx=15, pady=15, fill="both", expand=True)
tk.Label(product_frame, text="Choices", font=("Arial", 30, "bold"), bg="#3d6464", fg="white").pack()

for product, price in products.items():
    tk.Button(  
        product_frame, text=f"{product} - ${price:.2f}", 
        width=25, height=2, font=("Arial", 26),
        bg="#4CAF50", fg="black", bd=0, relief="flat",
        command=lambda p=product, pr=price: add_to_cart(p, pr)
    ).pack(pady=3)

# Cart frame setup 
cart_frame = tk.Frame(fenetre, bg="#3d6464", width="900",height="600", bd=1)
cart_frame.pack(side=tk.TOP, pady=20, fill="both", expand=True)
tk.Label(cart_frame, text="Cart", font=("Arial", 20, "bold"),bg="#3d6464", fg="#ffffff").pack()
cart_listbox = tk.Listbox(cart_frame, width=30, height=15, font=("Arial", 14))
cart_listbox.pack(padx=10, pady=10)

total_label = tk.Label(cart_frame, text="Total: $0.00", font=("Arial", 14, "bold"), bg="#F7F7F7", fg="#375578")
total_label.pack(pady=10, padx=20)

# Payment options setup
payment_frame = tk.Frame(fenetre, bg="#3d6464", width="900", height="600", bd=1 )
payment_frame.pack(side=tk.BOTTOM, pady=20, expand=True, fill="both")
tk.Label(payment_frame, text="Choose Payment Method:", font=("Arial", 20, "bold"), bg="#3d6464", fg="#ffffff").pack(pady=10)
selected_payment = tk.StringVar(value="Cash")

def create_payment_card(frame, image_path, text, value):
    img = Image.open(image_path)
    img = img.resize((120, 140), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(img)
    card = tk.Frame(frame, width=200, height=240, bg="white", bd=2, relief="raised")
    card.pack(side=tk.LEFT, padx=10)

    label_img = tk.Label(card, image=img, bg="white")
    label_img.image = img
    label_img.pack(pady=5)

    label_text = tk.Label(card, text=text, bg="white", font=("Arial", 20))
    label_text.pack()

    card.bind("<Button-1>", lambda e: checkout(value))

create_payment_card(payment_frame, "images/cash.png", "Cash", "Cash")
create_payment_card(payment_frame, "images/credit_card.png", "Credit Card", "Credit Card")
create_payment_card(payment_frame, "images/mobile_pay.png", "Mobile Pay", "Mobile Pay")

## THIS PART IS FOR OTHER FONCTIONALITIES
# Function to fetch historical invoices from the database
def fetch_invoices():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, total, payment_method, transaction_date FROM transactions ORDER BY transaction_date DESC")
    invoices = cursor.fetchall()
    conn.close()
    return invoices


# Function to open invoice window with "View" and "Print" buttons
def open_invoice_window():
    invoice_window = tk.Toplevel(fenetre)
    invoice_window.title("Invoice History")
    invoice_window.geometry("900x700")

    # Listbox to display historical invoices
    invoice_listbox = tk.Listbox(invoice_window, width=60, height=20, font=("Arial", 10))
    invoice_listbox.pack(pady=10)

    # Fetch invoices from the database and display them
    invoices = fetch_invoices()
    if not invoices:
        invoice_listbox.insert(tk.END, "No invoices available.")
    else:
        for invoice in invoices:
            invoice_id, total, payment_method, transaction_date = invoice
            invoice_listbox.insert(tk.END, f"Invoice ID: {invoice_id}, Total: ${total:.2f}, Method: {payment_method}, Date: {transaction_date}")

    # Function to enable buttons only if an invoice is selected
    def enable_buttons(event):
        selected_index = invoice_listbox.curselection()
        if selected_index:
            view_button.config(state="normal")
            print_button.config(state="normal")
        else:
            view_button.config(state="disabled")
            print_button.config(state="disabled")

    # Bind selection event to enable buttons
    invoice_listbox.bind("<<ListboxSelect>>", enable_buttons)

    # Define "View" button
    view_button = tk.Button(invoice_window, text="View", state="disabled", command=lambda: view_selected_invoice(invoice_listbox))
    view_button.pack(side=tk.LEFT, padx=20, pady=10)

    # Define "Print" button
    print_button = tk.Button(invoice_window, text="Print", state="disabled", command=lambda: print_selected_invoice(invoice_listbox))
    print_button.pack(side=tk.RIGHT, padx=20, pady=10)

# Function to view details of the selected invoice
def view_selected_invoice(invoice_listbox):
    selected_index = invoice_listbox.curselection()
    if not selected_index:
        return

    selected_invoice = invoice_listbox.get(selected_index)
    invoice_id = selected_invoice.split(",")[0].split(":")[1].strip()  # Extract invoice ID
    view_invoice_details(invoice_id)



# Function to print the selected invoice
def print_selected_invoice(invoice_listbox):
    selected_index = invoice_listbox.curselection()
    if not selected_index:
        return

    selected_invoice = invoice_listbox.get(selected_index)
    invoice_id = selected_invoice.split(",")[0].split(":")[1].strip()  # Extract invoice ID
    generate_invoice(invoice_id)  # Call print function
    messagebox.showinfo("Print Invoice", f"Invoice {invoice_id} has been sent to the printer.")

# Add invoice option to options menu. THis was a simple test. this was a simple test 

options_menu.add_command(label="Invoice", command=open_invoice_window)


# Function to view details of an invoice by ID
def view_invoice_details(invoice_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.name, products.price, transaction_items.quantity
        FROM transaction_items
        JOIN products ON transaction_items.product_id = products.id
        WHERE transaction_items.transaction_id = %s
    """, (invoice_id,))
    items = cursor.fetchall()
    conn.close()

    # Open a new window to display invoice details
    details_window = tk.Toplevel(fenetre)
    details_window.title(f"Invoice Details - ID {invoice_id}")
    details_window.geometry("400x300")

    tk.Label(details_window, text=f"Invoice ID: {invoice_id}", font=("Arial", 14)).pack(pady=10)
    item_listbox = tk.Listbox(details_window, width=50, height=15, font=("Arial", 10))
    item_listbox.pack(pady=10)

    # Display items in the invoice
    total = 0
    for name, price, quantity in items:
        line_total = price * quantity
        item_listbox.insert(tk.END, f"{name} x{quantity} - ${line_total:.2f}")
        total += line_total

    # Display total amount
    tk.Label(details_window, text=f"Total Amount: ${total:.2f}", font=("Arial", 12, "bold")).pack(pady=10)



# Im creating here a pdf invoice file 
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

fenetre.mainloop()
