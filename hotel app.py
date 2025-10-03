import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import matplotlib.pyplot as plt
from collections import Counter

# ---------- DATABASE ----------
def createtable():
    conn = sqlite3.connect("hotel.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            bookingid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            proof TEXT NOT NULL,
            proofid TEXT NOT NULL,
            roomtype TEXT NOT NULL,
            checkin TEXT NOT NULL,
            checkout TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit(); conn.close()

def insert_booking(name,email,proof,proofid,roomtype,checkin,checkout,price):
    conn = sqlite3.connect("hotel.db")
    c = conn.cursor()
    c.execute('''INSERT INTO bookings (name,email,proof,proofid,roomtype,checkin,checkout,price)
                 VALUES (?,?,?,?,?,?,?,?)''',
                 (name,email,proof,proofid,roomtype,checkin,checkout,price))
    conn.commit(); conn.close()

def get_all_bookings():
    conn = sqlite3.connect("hotel.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bookings")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_booking(bookingid):
    conn = sqlite3.connect("hotel.db")
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE bookingid=?", (bookingid,))
    conn.commit(); conn.close()

def update_checkout(bookingid,new_checkout,new_price):
    conn = sqlite3.connect("hotel.db")
    c = conn.cursor()
    c.execute("UPDATE bookings SET checkout=?, price=? WHERE bookingid=?",
              (new_checkout,new_price,bookingid))
    conn.commit(); conn.close()

def search_booking(name):
    conn = sqlite3.connect("hotel.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bookings WHERE name LIKE ?",('%'+name+'%',))
    rows = c.fetchall()
    conn.close()
    return rows

# ---------- HELPER ----------
def calc_days(in_date,out_date):
    try:
        d1 = datetime.strptime(in_date,"%d-%m-%Y")
        d2 = datetime.strptime(out_date,"%d-%m-%Y")
        days = (d2 - d1).days
        if days <= 0: raise ValueError
        return days
    except:
        messagebox.showerror("Date Error","Invalid dates or checkout before checkin.")
        return 0

def get_rate(roomtype):
    rates={"Single":2500,"Double":4000,"King":5500,"Suite":8000}
    return rates.get(roomtype,0)

# ---------- PDF Receipt ----------
def generate_receipt():
    sel = tree.focus()
    if not sel:
        messagebox.showwarning("Select","Please select a booking first!")
        return
    bid, name, email, proof, proofid, room, checkin, checkout, price = tree.item(sel)['values']
    filename = f"Receipt_Booking{bid}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height-50, "ABC Groups, Chennai")
    c.setFont("Helvetica", 14)
    c.drawString(50, height-100, f"Booking ID: {bid}")
    c.drawString(50, height-130, f"Guest Name: {name}")
    c.drawString(50, height-160, f"Email: {email}")
    c.drawString(50, height-190, f"Proof Type: {proof}")
    c.drawString(50, height-220, f"Proof ID: {proofid}")
    c.drawString(50, height-250, f"Room Type: {room}")
    c.drawString(50, height-280, f"Check-In: {checkin}")
    c.drawString(50, height-310, f"Check-Out: {checkout}")
    c.drawString(50, height-340, f"Total Price: ₹{price}")
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(50, height-380, "Thank you for choosing ABC Groups!")
    c.save()
    messagebox.showinfo("Receipt Generated", f"Receipt saved as {os.path.abspath(filename)}")

# ---------- Revenue Report ----------
def show_revenue_report():
    bookings = get_all_bookings()
    if not bookings:
        messagebox.showinfo("No Data", "No bookings available to show report.")
        return
    total_income = sum([b[-1] for b in bookings])
    total_bookings = len(bookings)
    room_counts = Counter([b[5] for b in bookings])
    report_text = f"Total Bookings: {total_bookings}\nTotal Revenue: ₹{total_income}\n\nBookings per Room Type:\n"
    for room, count in room_counts.items():
        report_text += f"{room}: {count}\n"
    messagebox.showinfo("Revenue Report", report_text)
    # Pie chart
    plt.figure(figsize=(6,6))
    plt.pie(room_counts.values(), labels=room_counts.keys(), autopct='%1.1f%%', startangle=90)
    plt.title("Bookings Distribution by Room Type")
    plt.show()

# ---------- GUI ----------
createtable()
root=tk.Tk()
root.title("Hotel Management System")
root.geometry("1000x650")

tk.Label(root,text="ABC Groups, Chennai",
         font=("Arial",20,"bold"),fg="darkblue").pack(pady=10)

frm=tk.Frame(root); frm.pack(pady=5)
namevar=tk.StringVar(); emailvar=tk.StringVar()
proofvar=tk.StringVar(value="Select"); proofidvar=tk.StringVar()
roomvar=tk.StringVar(value="Select"); checkinvar=tk.StringVar(); checkoutvar=tk.StringVar()

def clear_form():
    namevar.set(""); emailvar.set(""); proofvar.set("Select"); proofidvar.set("")
    roomvar.set("Select"); checkinvar.set(""); checkoutvar.set("")

fields=[("Guest Name",namevar),("Email",emailvar),
        ("Proof Type",proofvar),("Proof ID Number",proofidvar),
        ("Room Type",roomvar),("Check-In (DD-MM-YYYY)",checkinvar),
        ("Check-Out (DD-MM-YYYY)",checkoutvar)]

for i,(lbl,var) in enumerate(fields):
    tk.Label(frm,text=lbl,font=("Arial",12)).grid(row=i,column=0,sticky="e",padx=8,pady=4)
    if lbl=="Proof Type":
        ttk.Combobox(frm,textvariable=var,values=["Aadhar","Passport","Driving ID"],state="readonly",width=28).grid(row=i,column=1)
    elif lbl=="Room Type":
        ttk.Combobox(frm,textvariable=var,values=["Single","Double","King","Suite"],state="readonly",width=28).grid(row=i,column=1)
    else:
        tk.Entry(frm,textvariable=var,width=30).grid(row=i,column=1,pady=4)

# --- Buttons ---
def add_booking():
    if not all([namevar.get(),emailvar.get(),proofvar.get()!="Select",proofidvar.get(),
                roomvar.get()!="Select",checkinvar.get(),checkoutvar.get()]):
        messagebox.showwarning("Input","All fields required"); return
    days = calc_days(checkinvar.get(),checkoutvar.get())
    if days==0: return
    total = days * get_rate(roomvar.get())
    insert_booking(namevar.get(),emailvar.get(),proofvar.get(),proofidvar.get(),
                   roomvar.get(),checkinvar.get(),checkoutvar.get(),total)
    messagebox.showinfo("Added",f"Booking Added. Total ₹{total}")
    clear_form(); load_table()

btnfrm=tk.Frame(root); btnfrm.pack(pady=5)
tk.Button(btnfrm,text="Add Booking",command=add_booking,bg="green",fg="white",width=15).grid(row=0,column=0,padx=5)
tk.Button(btnfrm,text="Delete Selected",command=lambda: delete_selected(),bg="red",fg="white",width=15).grid(row=0,column=1,padx=5)
tk.Button(btnfrm,text="Update Checkout",command=lambda: update_selected(),bg="orange",fg="black",width=15).grid(row=0,column=2,padx=5)
tk.Button(btnfrm,text="Generate Receipt",command=generate_receipt,bg="purple",fg="white",width=15).grid(row=0,column=3,padx=5)
tk.Button(btnfrm,text="Revenue Report",command=show_revenue_report,bg="darkcyan",fg="white",width=15).grid(row=0,column=4,padx=5)

# --- Search ---
searchvar=tk.StringVar()
searchfrm=tk.Frame(root); searchfrm.pack(pady=5)
tk.Entry(searchfrm,textvariable=searchvar,width=30).grid(row=0,column=0,padx=5)
tk.Button(searchfrm,text="Search by Name",command=lambda: search_table()).grid(row=0,column=1,padx=5)
tk.Button(searchfrm,text="Show All",command=lambda: load_table()).grid(row=0,column=2,padx=5)

# --- Table ---
cols=("ID","Name","Email","ProofType","ProofID","Room","CheckIn","CheckOut","Price")
tree=ttk.Treeview(root,columns=cols,show="headings",height=12)
for col in cols:
    tree.heading(col,text=col)
    tree.column(col,width=120)
tree.pack(padx=10,pady=10,fill="x")

def load_table():
    tree.delete(*tree.get_children())
    for row in get_all_bookings():
        tree.insert("",tk.END,values=row)

def delete_selected():
    sel = tree.focus()
    if not sel: messagebox.showwarning("Select","Choose a row"); return
    bid = tree.item(sel)['values'][0]
    if messagebox.askyesno("Delete","Are you sure?"):
        delete_booking(bid)
        load_table()

def update_selected():
    sel = tree.focus()
    if not sel: messagebox.showwarning("Select","Choose a row"); return
    bid,*rest = tree.item(sel)['values']
    cin = rest[5]; room = rest[4]  # indexes: CheckIn=5?, Room=4? adjust as per columns
    new_date = simpledialog.askstring("Update","Enter new Checkout (DD-MM-YYYY):")
    if not new_date: return
    days = calc_days(cin,new_date)
    if days==0: return
    new_price = days*get_rate(room)
    update_checkout(bid,new_date,new_price)
    load_table()
    messagebox.showinfo("Updated","Checkout updated successfully!")

def search_table():
    tree.delete(*tree.get_children())
    for row in search_booking(searchvar.get()):
        tree.insert("",tk.END,values=row)

load_table()
root.mainloop()
