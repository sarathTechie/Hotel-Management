import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from tkcalendar import DateEntry
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import matplotlib.pyplot as plt
from collections import Counter

# ----------------- FESTIVAL / HOLIDAY DATES -----------------
festival_dates = [
    "01-01-2025","14-02-2025","17-03-2025","18-04-2025","20-04-2025",
    "01-05-2025","31-10-2025","27-11-2025","25-12-2025","31-12-2025",
    "13-01-2025","14-01-2025","26-01-2025","02-02-2025","26-02-2025",
    "13-03-2025","14-03-2025","28-03-2025","30-03-2025","06-04-2025",
    "10-04-2025","14-04-2025","12-05-2025","07-07-2025","15-08-2025",
    "19-08-2025","30-08-2025","06-09-2025","02-10-2025","12-10-2025",
    "29-10-2025","01-11-2025","03-11-2025","07-11-2025","25-12-2025"
]

# ----------------- ROOM INVENTORY -----------------
room_inventory = {"Single":100, "Double":300, "King":200, "Suite":100}

# ----------------- USER LOGIN -----------------
user_ids = ["1111","2222","3333","4444","5555"]
user_password = "0000"

# ----------------- DATABASE FUNCTIONS -----------------
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
            price REAL NOT NULL,
            payment_status TEXT NOT NULL,
            loyalty_points INTEGER NOT NULL
        )
    ''')
    conn.commit(); conn.close()

def insert_booking(name,email,proof,proofid,roomtype,checkin,checkout,price,loyalty_points,status):
    conn = sqlite3.connect("hotel.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO bookings 
        (name,email,proof,proofid,roomtype,checkin,checkout,price,payment_status,loyalty_points)
        VALUES (?,?,?,?,?,?,?,?,?,?)''',
        (name,email,proof,proofid,roomtype,checkin,checkout,price,status,loyalty_points))
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

def update_payment(bookingid,new_status):
    conn = sqlite3.connect("hotel.db")
    c = conn.cursor()
    c.execute("UPDATE bookings SET payment_status=? WHERE bookingid=?", (new_status,bookingid))
    conn.commit(); conn.close()

def search_booking(name):
    conn = sqlite3.connect("hotel.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bookings WHERE name LIKE ?",('%'+name+'%',))
    rows = c.fetchall()
    conn.close()
    return rows

# ----------------- HELPER FUNCTIONS -----------------
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

def get_rate(roomtype, checkin_date):
    base_rates = {"Single":2500,"Double":4000,"King":5500,"Suite":8000}
    rate = base_rates.get(roomtype,0)
    date_obj = datetime.strptime(checkin_date,"%d-%m-%Y")
    if date_obj.weekday()>=5:  # Weekend
        rate = rate*1.15
    if checkin_date in festival_dates:  # Festival
        rate = rate*1.25
    return rate

def calculate_discount(total):
    if total>35000:
        return total*0.80
    elif total>20000:
        return total*0.85
    elif total>10000:
        return total*0.90
    return total

def calculate_loyalty(total):
    return int(total/200)*5

def check_room_availability(roomtype, checkin, checkout):
    bookings = get_all_bookings()
    booked_count = 0
    for b in bookings:
        if b[5]==roomtype:
            b_checkin = datetime.strptime(b[6], "%d-%m-%Y")
            b_checkout = datetime.strptime(b[7], "%d-%m-%Y")
            in_date = datetime.strptime(checkin, "%d-%m-%Y")
            out_date = datetime.strptime(checkout, "%d-%m-%Y")
            if in_date < b_checkout and out_date > b_checkin:
                booked_count +=1
    return booked_count < room_inventory[roomtype]

# ----------------- LOGIN -----------------
def login_window():
    login_root = tk.Tk()
    login_root.title("Hotel Management Login")
    login_root.geometry("350x200")

    tk.Label(login_root,text="User ID").pack(pady=5)
    user_var = tk.StringVar()
    tk.Entry(login_root,textvariable=user_var).pack(pady=5)

    tk.Label(login_root,text="Password").pack(pady=5)
    pass_var = tk.StringVar()
    tk.Entry(login_root,textvariable=pass_var,show="*").pack(pady=5)

    def verify():
        if user_var.get() in user_ids and pass_var.get()==user_password:
            login_root.destroy()
            main_window()
        else:
            messagebox.showerror("Login Failed","Invalid credentials!")

    tk.Button(login_root,text="Login",command=verify,bg="green",fg="white").pack(pady=20)
    login_root.mainloop()

# ----------------- MAIN WINDOW -----------------
def main_window():
    createtable()
    root=tk.Tk()
    root.title("Hotel Management System")
    root.geometry("1200x700")

    tk.Label(root,text="ABC Groups, Chennai", font=("Arial",20,"bold"),fg="darkblue").pack(pady=10)

    frm=tk.Frame(root); frm.pack(pady=5)
    namevar=tk.StringVar(); emailvar=tk.StringVar()
    proofvar=tk.StringVar(value="Select"); proofidvar=tk.StringVar()
    roomvar=tk.StringVar(value="Select"); checkinvar=tk.StringVar(); checkoutvar=tk.StringVar()
    paymentvar=tk.StringVar(value="Pending")

    def clear_form():
        namevar.set(""); emailvar.set(""); proofvar.set("Select"); proofidvar.set("")
        roomvar.set("Select"); checkinvar.set(""); checkoutvar.set(""); paymentvar.set("Pending")

    fields=[("Guest Name",namevar),("Email",emailvar),
            ("Proof Type",proofvar),("Proof ID Number",proofidvar),
            ("Room Type",roomvar),("Check-In",checkinvar),
            ("Check-Out",checkoutvar)]

    for i,(lbl,var) in enumerate(fields):
        tk.Label(frm,text=lbl,font=("Arial",12)).grid(row=i,column=0,sticky="e",padx=8,pady=4)
        if lbl=="Proof Type":
            ttk.Combobox(frm,textvariable=var,values=["Aadhar","Passport","Driving ID"],state="readonly",width=28).grid(row=i,column=1)
        elif lbl=="Room Type":
            ttk.Combobox(frm,textvariable=var,values=["Single","Double","King","Suite"],state="readonly",width=28).grid(row=i,column=1)
        elif lbl=="Check-In" or lbl=="Check-Out":
            DateEntry(frm,textvariable=var,date_pattern="dd-mm-yyyy",width=28).grid(row=i,column=1,pady=4)
        else:
            tk.Entry(frm,textvariable=var,width=30).grid(row=i,column=1,pady=4)

    # ---------------- TABLE ----------------
    cols=("ID","Name","Email","ProofType","ProofID","Room","CheckIn","CheckOut","Price","Payment","Loyalty")
    tree=ttk.Treeview(root,columns=cols,show="headings",height=15)
    for col in cols:
        tree.heading(col,text=col)
        tree.column(col,width=110)
    tree.pack(padx=10,pady=10,fill="x")

    # ---------------- FUNCTIONS ----------------
    def load_table():
        tree.delete(*tree.get_children())
        for row in get_all_bookings():
            tree.insert("",tk.END,values=row)

    def add_booking():
        if not all([namevar.get(),emailvar.get(),proofvar.get()!="Select",proofidvar.get(),
                    roomvar.get()!="Select",checkinvar.get(),checkoutvar.get()]):
            messagebox.showwarning("Input","All fields required"); return
        if not check_room_availability(roomvar.get(), checkinvar.get(), checkoutvar.get()):
            messagebox.showerror("Full","No rooms available for this type in selected dates"); return
        days = calc_days(checkinvar.get(),checkoutvar.get())
        if days==0: return
        rate = get_rate(roomvar.get(), checkinvar.get())
        total = rate*days
        total = calculate_discount(total)
        loyalty = calculate_loyalty(total)
        insert_booking(namevar.get(),emailvar.get(),proofvar.get(),proofidvar.get(),
                       roomvar.get(),checkinvar.get(),checkoutvar.get(),total,loyalty,"Pending")
        messagebox.showinfo("Added",f"Booking Added. Total ₹{total}, Loyalty Points: {loyalty}")
        clear_form(); load_table()

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
        bid, name, email, proof, proofid, room, cin, cout, price, pay, loyalty = tree.item(sel)['values']
        new_date = simpledialog.askstring("Update","Enter new Checkout (DD-MM-YYYY):")
        if not new_date: return
        if not check_room_availability(room, cin, new_date):
            messagebox.showerror("Full","No rooms available for this type in new dates"); return
        days = calc_days(cin,new_date)
        if days==0: return
        rate = get_rate(room, cin)
        new_price = calculate_discount(rate*days)
        insert_booking(name,email,proof,proofid,room,cin,new_date,new_price,loyalty,pay)
        delete_booking(bid)
        load_table()
        messagebox.showinfo("Updated","Checkout updated successfully!")

    def update_payment_selected():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Select","Choose a row"); return
        bid = tree.item(sel)['values'][0]
        new_status = simpledialog.askstring("Payment","Enter Payment Status (Paid/Pending/Partial):")
        if not new_status: return
        update_payment(bid,new_status)
        load_table()
        messagebox.showinfo("Updated","Payment status updated!")

    def search_table():
        tree.delete(*tree.get_children())
        for row in search_booking(searchvar.get()):
            tree.insert("",tk.END,values=row)

    def generate_receipt():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Select","Please select a booking first!")
            return
        bid, name, email, proof, proofid, room, checkin, checkout, price, pay, loyalty = tree.item(sel)['values']
        folder_path = r"D:\Python\hotel management"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(folder_path, f"Receipt_Booking{bid}_{timestamp}.pdf")
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height-50, "ABC Groups, Chennai")
        c.setFont("Helvetica", 14)
        c.drawString(50, height-100, f"Booking ID: {bid}")
        c.drawString(50, height-130, f"Guest Name: {name}")
        c.drawString(50, height-160, f"Email: {email}")
        c.drawString(50, height-190, f"Proof Type: {proof} | Proof ID: {proofid}")
        c.drawString(50, height-220, f"Room Type: {room}")
        c.drawString(50, height-250, f"Check-In: {checkin}")
        c.drawString(50, height-280, f"Check-Out: {checkout}")
        c.drawString(50, height-310, f"Total Price: ₹{price}")
        c.drawString(50, height-340, f"Payment Status: {pay}")
        c.drawString(50, height-370, f"Loyalty Points: {loyalty}")
        c.save()
        messagebox.showinfo("Saved",f"Receipt saved at {filename}")

    def show_dashboard():
        bookings = get_all_bookings()
        total_revenue = sum(b[8] for b in bookings)
        room_count = Counter(b[5] for b in bookings)
        upcoming_checkins = [b for b in bookings if datetime.strptime(b[6],"%d-%m-%Y")>=datetime.now()]
        msg=f"Total Revenue: ₹{total_revenue}\nTotal Bookings: {len(bookings)}\nUpcoming Check-ins: {len(upcoming_checkins)}\n"
        for room in room_inventory:
            msg+=f"{room} Occupied: {room_count.get(room,0)} / {room_inventory[room]}\n"
        messagebox.showinfo("Dashboard",msg)
        labels = room_inventory.keys()
        sizes = [room_inventory[r]-room_count.get(r,0) for r in room_inventory]
        plt.figure(figsize=(6,6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title("Available Rooms by Type")
        plt.show()

    def check_availability():
        if roomvar.get()=="Select" or not checkinvar.get() or not checkoutvar.get():
            messagebox.showwarning("Input","Select Room Type and Dates")
            return
        available = check_room_availability(roomvar.get(), checkinvar.get(), checkoutvar.get())
        days = calc_days(checkinvar.get(),checkoutvar.get())
        if days==0: return
        rate = get_rate(roomvar.get(), checkinvar.get())
        total = rate * days
        total = calculate_discount(total)
        msg = f"Room Type: {roomvar.get()}\nAvailable: {'Yes' if available else 'No'}\nTotal Days: {days}\nRate per Day: ₹{rate:.2f}\nTotal (after discount if any): ₹{total:.2f}"
        messagebox.showinfo("Room Availability & Rate", msg)

    # ---------------- BUTTONS ----------------
    btnfrm=tk.Frame(root); btnfrm.pack(pady=5)
    tk.Button(btnfrm,text="Check Availability",command=check_availability,bg="teal",fg="white",width=18).grid(row=0,column=0,padx=5)
    tk.Button(btnfrm,text="Add Booking",command=add_booking,bg="green",fg="white",width=15).grid(row=0,column=1,padx=5)
    tk.Button(btnfrm,text="Delete Selected",command=delete_selected,bg="red",fg="white",width=15).grid(row=0,column=2,padx=5)
    tk.Button(btnfrm,text="Update Checkout",command=update_selected,bg="orange",fg="black",width=15).grid(row=0,column=3,padx=5)
    tk.Button(btnfrm,text="Update Payment",command=update_payment_selected,bg="purple",fg="white",width=15).grid(row=0,column=4,padx=5)
    tk.Button(btnfrm,text="Generate Receipt (PDF)",command=generate_receipt,bg="darkcyan",fg="white",width=18).grid(row=0,column=5,padx=5)
    tk.Button(btnfrm,text="Revenue Dashboard",command=show_dashboard,bg="blue",fg="white",width=18).grid(row=0,column=6,padx=5)

    # ---------------- SEARCH ----------------
    searchvar=tk.StringVar()
    searchfrm=tk.Frame(root); searchfrm.pack(pady=5)
    tk.Entry(searchfrm,textvariable=searchvar,width=30).grid(row=0,column=0,padx=5)
    tk.Button(searchfrm,text="Search by Name",command=search_table).grid(row=0,column=1,padx=5)
    tk.Button(searchfrm,text="Show All",command=load_table).grid(row=0,column=2,padx=5)

    load_table()
    root.mainloop()

# ----------------- START APP -----------------
login_window()
