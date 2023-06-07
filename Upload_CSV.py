import csv
import os
import sys
import tkinter as tk
from tkinter import PhotoImage, filedialog, messagebox
from tkinter import ttk

import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="Dhenusya",
        user="postgres",
        password="96528728")
pgcur=conn.cursor()
def upload():
    filenames = []
    for filepath in filedialog.askopenfilenames():
        filename = os.path.basename(filepath)
        filenames.append(filename)
    
        with open(filepath, "r") as file:
            reader = csv.reader(file)
            headers = next(reader)

            min_date=min([row[0] for row in reader])
            # first_column_data = []
            # for row in reader:
            #     first_column_data.append(row[0])
            #     min_date = min(first_column_data)
            
            print(f"date for where candition:{min_date}")

            print(filename)
            # Add a new column to the dataframe with the filename
            check_sql = f"SELECT COUNT(*) FROM do_f_uploaded_csv_files WHERE filename = '{filename}';"
            pgcur.execute(check_sql)
            count = pgcur.fetchone()[0]
            if count > 0:
                # messagebox.showerror("Error", "File has already been uploaded, Do you want to over ride.")
                choice = messagebox.askyesno(f"Error", "File has already been uploaded, do you want to override?.\n{}\nClick Yes To Continue !".format(filename))
                if choice == True:
                    Delete_sql = f"Delete  from do_f_daily_milk_tracker where date ='{min_date}'"
                    print(Delete_sql) 
                    pgcur.execute(Delete_sql)
                    messagebox.showwarning(f"Sucess","Previous CSV's file \n {} Data Deleted".format(filename))

                    copy_sql = f"COPY do_f_daily_milk_tracker FROM '{filepath}' DELIMITER ',' CSV HEADER;"
                    pgcur.execute(copy_sql)
                    messagebox.showinfo(f"Sucess","CSV's Files Uploaded to DataBase")

                    insert_sql = f"INSERT INTO do_f_uploaded_csv_files (filename) VALUES ('{filename}');"
                    pgcur.execute(insert_sql)
                    conn.commit()
                    messagebox.showinfo(f"Sucess","Filenames Are inserted")
                else:
                    continue
            else:
                copy_sql = f"COPY do_f_daily_milk_tracker FROM '{filepath}' DELIMITER ',' CSV HEADER;"
                pgcur.execute(copy_sql)
                messagebox.showinfo(f"Sucess","CSV's Files Uploaded to DataBase")
                insert_sql = f"INSERT INTO do_f_uploaded_csv_files (filename) VALUES ('{filename}');"
                pgcur.execute(insert_sql)
                conn.commit()
                messagebox.showinfo(f"Sucess","Filenames Are inserted") 
            pgcur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'do_f_daily_milk_tracker' ORDER BY ordinal_position")
            columns = [col[0] for col in pgcur.fetchall()]

            if set(headers) != set(columns):
                print("The columns in the CSV file do not match the columns in the database.")
            else:
                print("The columns match.")
            # Print the count and columns of the CSV
            print("CSV file columns: {} ({} columns)".format(headers, len(headers)))

            # Print the count and columns of the database
            print("Database columns: {} ({} columns)".format(columns, len(columns)))
        
    return 
# Create a Tkinter buttons
root = tk.Tk()
root.geometry("600x800") 
root.title("Dhenusya Organics") 

label = tk.Label(root, text="Welcome to Dhenusya Organics UI design!")
label.pack()

background_image = PhotoImage(file="D:/Python/Dhenusya.png")
img =background_image.zoom(int(round(2)), int(round(2)))
background_label = tk.Label(root, image=img)

# Create a label to display the image
label = ttk.Label(root, image=img)
background_label.pack(fill="both", expand=True, side=tk.BOTTOM, anchor="sw")


# upload csv button
button1 = tk.Button(root, command=upload, text="Daily CSV Upload!!", bg="Deep Sky Blue")
button1.place(x=50, y=30)
root.mainloop()