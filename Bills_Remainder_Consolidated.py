
import csv
from logging import root
import os
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import keyboard
import psycopg2
import pywhatkit

conn = psycopg2.connect(
        host="localhost",
        database="Dhenusya",
        user="postgres",
        password="96528728")
pgcur=conn.cursor()
def get_status_values():
    
    # Query to retrieve the distinct status values from the do_f_bill_remainder table
    pgcur.execute("SELECT DISTINCT status FROM public.consolidate_milksummar")
    # Extract the status values from the cursor object
    status_values = [row[0] for row in pgcur.fetchall()]
    return status_values

def get_month_year_values():
    # Query to retrieve the distinct month_year values from the consolidate_milksummar table
    pgcur.execute("SELECT DISTINCT month_year FROM public.consolidate_milksummar")
    # Extract the month_year values from the cursor object
    month_year_values = [row[0] for row in pgcur.fetchall()]
    return month_year_values

# Define a function to retrieve the selected status value from the dropdown menu
def select_status(selected_month_year,selected_status):
    selected_month_year = month_year_var.get()
    selected_status = status_var.get()
    if selected_status:
        DropDown = f"SELECT * FROM public.consolidate_milksummar WHERE month_year = '{selected_month_year}' AND status = '{selected_status}';"
        print(DropDown)
    else:
        DropDown = f"SELECT * FROM public.consolidate_milksummar WHERE month_year = '{selected_month_year}';"
        print(DropDown)

    # DropDown=f"SELECT * FROM public.consolidate_milksummar WHERE status = '{selected_status}';"
    pgcur.execute(DropDown)
    Data = pgcur.fetchall()
    choice = messagebox.askyesno("Remainder", " Do You Want To Send Bill Remainders For Selected Status  Customers ?.Click Yes To Continue !")
    if choice == True:
        file_paths = filedialog.askopenfilenames(initialdir='D:\\Dhenusya\\Images')
        # Loop through the Data list and send only selected images to their respective phone numbers
        a=0
        for o in Data:
            # print(o)
            a+=1
            number = o[2]
            image_path = "D:/Dhenusya/Images/" + str(number) + ".JPEG"
            # print(a,":",image_path)
            if image_path in file_paths:
                print("image Path :",image_path)
                print("selected images file_paths :",file_paths)
                pywhatkit.sendwhats_image("+91" + str(number), image_path)
                time.sleep(10)
                keyboard.press_and_release('ctrl+w')
    else:
        messagebox.showinfo(f"Sucess","Whatsapp Remainders Are Not Sent")
        time.sleep(1)

    Status_Update = messagebox.askyesno("Remainder Status", " Do You Want To Update Bills of Remainders?\n If Yes \n NOTE: Please enter Exit in Terminal After CSV Update Done. \n Click Yes To Continue !")

    if Status_Update == True:
        with open("Remainder.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(('month_year', 'contact_no', 'customer_name', 'address','cm_ltrs_qunatity',
                            'cm_price','cm_total','bm_ltrs_quantity','bm_price',
                            'bm_total','total_amount','status','variance','date_paid'))
            for row in Data:
                writer.writerow(row)

        print("Remainder File For Bill Update is Created as Remainder.csv file.")
        # os.system('output.csv')
        time.sleep(2)
        os.system('Remainder.csv')

        print("File Saved Sucessfully ")
        if selected_status:

            Delete_Query =f"Delete FROM public.consolidate_milksummar WHERE month_year= '{selected_month_year}' and status = '{selected_status}';"
            time.sleep(2)

            print(Delete_Query)
        else:
            Delete_Query =f"Delete FROM public.consolidate_milksummar WHERE month_year= '{selected_month_year}' ;"
            time.sleep(2)
            print(Delete_Query)

        pgcur.execute(Delete_Query)
        conn.commit()
        Copy_Query = f"COPY public.consolidate_milksummar FROM 'D:\\Python\\Remainder.csv' DELIMITER ',' CSV HEADER;"
        time.sleep(2)
        pgcur.execute(Copy_Query)
        conn.commit()
        print(Copy_Query)
    # sys.exit()
# def get_data():
#     month_year = month_year_var.get()
#     status = status_var.get()
    
#     if status:
#         query = "SELECT * FROM consolidate_milksummar WHERE month_year = '%s' AND status = '%s';" % (month_year, status)
#         print(query)
    
#     else:
#         query = "SELECT * FROM consolidate_milksummar WHERE month_year = '%s';" % month_year
#         print(query)
#     try:
#         # conn = psycopg2.connect(database="your_database_name", user="your_username", password="your_password", host="your_host", port="your_port")
#         # cur = conn.cursor()
#         pgcur.execute(query)
#         rows = pgcur.fetchall()
        
#         messagebox.showinfo("Data", "Month_year Data")
#         # for i in rows:
#             # print(i)
#     except Exception as e:
#         messagebox.showerror("Error", e)
        
#     finally:
#         print("execution Completed")
#         # pgcur.close()
#         # conn.close()
    
# Create a Tkinter buttons
root = tk.Tk()
root.geometry("500x600") 
root.title("Dhenusya Organics")

label = tk.Label(root, text="Welcome to Dhenusya Organics UI design!")
label.pack()

# Create label for status_menu
status_label = tk.Label(root, text="Select Status:")
status_label.place(x=200, y=330)
status_var = tk.StringVar()
status_values = get_status_values()
status_menu = tk.OptionMenu(root, status_var, *status_values)
status_menu.configure(bg='Cadet Blue')

status_menu.place(x=310, y=330)
status_values = get_status_values()
# Create label for month_year_menu
month_year_label = tk.Label(root, text="Select month_year:")
month_year_label.place(x=50, y=330)
month_year_var = tk.StringVar()

month_year_values = get_month_year_values()
month_year_menu = tk.OptionMenu(root, month_year_var, *month_year_values)
month_year_menu.configure(bg='Cadet Blue')
month_year_menu.place(x=105, y=330)
# Create button to select data
select_button = tk.Button(root, text="Remainder & Consolidate", command=lambda: select_status(month_year_var.get(), status_var.get()),bg='Cadet Blue')
select_button.place(x=105, y=385)

# submit_button =tk.Button(root, text="Submit", command=get_data)
# submit_button.pack()
root.mainloop()