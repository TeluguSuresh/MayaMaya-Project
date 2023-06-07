
import csv
from logging import root
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import psycopg2


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
            for filename in filenames:
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
    sys.exit()
# Create a Tkinter buttons
root = tk.Tk()
root.geometry("600x850") 
root.title("Dhenusya Organics") 

label = tk.Label(root, text="Welcome to Dhenusya Organics UI design!")
label.pack() 
# Bill remainder button
button3 = tk.Button(root, command=Bills_Remainder, text="Bills Remainder Upload", bg="Orange Red")
button3.place(x=380, y=155)
root.mainloop()