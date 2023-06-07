import csv
from logging import root
import os
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import keyboard
import psycopg2
import pywhatkit
conn = psycopg2.connect(
        host="localhost",
        database="Dhenusya",
        user="postgres",
        password="96528728")
pgcur=conn.cursor()

def Bills_Remainder():
    filenames = []
    for filepath in filedialog.askopenfilenames(initialdir='D:\\Dhenusya\\Bill Remainder CSV\\'):
        filename = os.path.basename(filepath)
        filenames.append(filename)
        with open(filepath, "r") as file:
            reader = csv.reader(file)
            headers = next(reader)
            first_column_data = []
            for row in reader:
                first_column_data.append(row[0])
                min_date = min(first_column_data)
            print(f"date for where candition:{min_date}")
            # for filename in filenames:
            print(filename)
            # Add a new column to the dataframe with the filename
            check_sql = f"SELECT COUNT(*) FROM do_f_uploaded_csv_files WHERE filename = '{filename}';"
            pgcur.execute(check_sql)
            count = pgcur.fetchone()[0]
            if count > 0:
                    # messagebox.showerror("Error", "File has already been uploaded, Do you want to over ride.")
                choice = messagebox.askyesno("Error", "File has already been uploaded, do you want to override?.Click Yes To Continue !")
                if choice == True:
                    Delete_sql = f"Delete  from public.consolidate_milksummar where month_year ='{min_date}'"
                    print(Delete_sql) 
                    pgcur.execute(Delete_sql)
                    messagebox.showwarning(f"Sucess","Previous CSV's file \n {} \n Data Deleted".format(filename))

                    copy_sql = f"COPY public.consolidate_milksummar FROM '{filepath}' DELIMITER ',' CSV HEADER;"
                    pgcur.execute(copy_sql)
                    messagebox.showinfo(f"Sucess","CSV's Files Uploaded to DataBase")

                    insert_sql = f"INSERT INTO do_f_uploaded_csv_files (filename) VALUES ('{filename}');"
                    pgcur.execute(insert_sql)
                    conn.commit()
                    messagebox.showinfo(f"Sucess","Filenames Are inserted")
                    return Delete_sql,min_date
                else:
                    continue
            else:
                copy_sql = f"COPY public.consolidate_milksummar FROM '{filepath}' DELIMITER ',' CSV HEADER;"
                pgcur.execute(copy_sql)
                messagebox.showinfo(f"Sucess","CSV's Files Uploaded to DataBase")
                insert_sql = f"INSERT INTO do_f_uploaded_csv_files (filename) VALUES ('{filename}');"
                pgcur.execute(insert_sql)
                conn.commit()
                messagebox.showinfo(f"Sucess","Filenames Are inserted") 
                pgcur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'consolidate_milksummar' ORDER BY ordinal_position")
                columns = [col[0] for col in pgcur.fetchall()]

                if set(headers) != set(columns):
                    print("The columns in the CSV file do not match the columns in the database.")
                else:
                    print("The columns match.")
                # Print the count and columns of the CSV
                print("CSV file columns: {} ({} columns)".format(headers, len(headers)))

                # Print the count and columns of the database
                print("Database columns: {} ({} columns)".format(columns, len(columns)))
                print('Upload Bills_Remainder CSV Done')
                

# Define a function to retrieve the status values from the database
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
    DropDown = f"SELECT * FROM public.consolidate_milksummar WHERE month_year = '{selected_month_year}' AND status = '{selected_status}';"

    # DropDown=f"SELECT * FROM public.consolidate_milksummar WHERE status = '{selected_status}';"
    pgcur.execute(DropDown)
    print(DropDown)
    Data = pgcur.fetchall()
    choice = messagebox.askyesno("Remainder", " Do You Want To Send Bill Remainders For Selected Status  Customer ?.Click Yes To Continue !")
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
        time.sleep(1)
        Status_Update = messagebox.askyesno("Remainder Status", " Do You Want To Update Bills of Remainders?.Click Yes To Continue !")

        if Status_Update == True:
            with open("Remainder.csv", "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(('month_year', 'contact_no', 'customer_name', 'address','cm_ltrs_qunatity',
                                'cm_price','cm_total','bm_ltrs_quantity','bm_price',
                                'bm_total','total_amount','status','variance','date_paid'))
                for row in Data:
                    writer.writerow(row)

            print("Remainder File For Bill Update as Remainder.csv file.")
            # os.system('output.csv')
            time.sleep(2)

            while True:
                os.system('Remainder.csv')
                exit_command = input("Type 'exit' to quit the program: ")
                if exit_command.lower() == 'exit':
                    break  # exit the while loop

            print("File Saved Sucessfully ")
            Delete_Remainder_old_Data =f"Delete  FROM public.consolidate_milksummar WHERE status = '{selected_status}';"
            pgcur.execute(Delete_Remainder_old_Data)
            print(Delete_Remainder_old_Data)

            Remainder_New_Data_Copy = f"COPY public.consolidate_milksummar FROM 'D:\\Python\\Remainder.csv' DELIMITER ',' CSV HEADER;"
            pgcur.execute(Remainder_New_Data_Copy)
            print(Remainder_New_Data_Copy)


root = tk.Tk()
root.geometry("600x800") 
# Create label for status_menu
status_label = tk.Label(root, text="Select Status:")
status_label.place(x=0, y=80)
status_var = tk.StringVar()
status_values = get_status_values()
status_menu = tk.OptionMenu(root, status_var, *status_values)
status_menu.place(x=0, y=120)
status_values = get_status_values()
# Create label for month_year_menu
month_year_label = tk.Label(root, text="Select month_year:")
month_year_label.place(x=0, y=30)
month_year_var = tk.StringVar()

month_year_values = get_month_year_values()
month_year_menu = tk.OptionMenu(root, month_year_var, *month_year_values)
month_year_menu.place(x=0, y=90)
# Create button to select data
select_button = tk.Button(root, text="Select Data", command=lambda: select_status(month_year_var.get(), status_var.get()))
select_button.place(x=0, y=170)
 
button3 = tk.Button(root, command=Bills_Remainder, text="Bills Remainder CSV Upload", bg="Orange Red")
# button3.place(x=0, y=50)
root.mainloop()
