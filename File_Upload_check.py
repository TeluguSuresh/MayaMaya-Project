import tkinter as tk
from tkinter import filedialog,messagebox
import pandas as pd
import psycopg2
import os
import csv
conn = psycopg2.connect(
        host="localhost",
        database="Dhenusya",
        user="postgres",
        password="96528728")
pgcur = conn.cursor()
def upload():
    filenames = []
    for filepath in filedialog.askopenfilenames():
        filename = os.path.basename(filepath)
        filenames.append(filename)
        with open(filepath, "r") as file:
            reader = csv.reader(file)
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
                        Delete_sql = f"Delete  from do_f_daily_milk_tracker where date ='{min_date}'"
                        print(Delete_sql) 
                        pgcur.execute(Delete_sql)
                        messagebox.showerror(f"Sucess","Previous CSV's file Data Deleted")

                        copy_sql = f"COPY do_f_daily_milk_tracker FROM '{filepath}' DELIMITER ',' CSV HEADER;"
                        pgcur.execute(copy_sql)
                        messagebox.showerror(f"Sucess","CSV's Files Copied to DataBase")

                        insert_sql = f"INSERT INTO do_f_uploaded_csv_files (filename) VALUES ('{filename}');"
                        pgcur.execute(insert_sql)
                        conn.commit()
                        messagebox.showerror(f"Sucess","File_names Are inserted")
                        return Delete_sql,min_date
                    else:
                        continue
                else:
                    copy_sql = f"COPY do_f_daily_milk_tracker FROM '{filepath}' DELIMITER ',' CSV HEADER;"
                    pgcur.execute(copy_sql)
                    messagebox.showerror(f"Sucess","CSV's Files Copied to DataBase")
                    insert_sql = f"INSERT INTO do_f_uploaded_csv_files (filename) VALUES ('{filename}');"
                    pgcur.execute(insert_sql)
                    conn.commit()
                    messagebox.showerror(f"Sucess","Filenames Are inserted")
       

root = tk.Tk()
button = tk.Button(root, text="Upload CSV", command=upload)
button.pack()
root.mainloop()


# import tkinter as tk
# from tkinter import filedialog,messagebox
# import pandas as pd
# import psycopg2
# import os
# def upload():
#     filenames = []
#     for filepath in filedialog.askopenfilenames():
#         filename = os.path.basename(filepath)
#         filenames.append(filename)

#     print(filenames)

#     conn = psycopg2.connect(
#         host="localhost",
#         database="Dhenusya",
#         user="postgres",
#         password="96528728")
#     pgcur = conn.cursor()

#     for filename in filenames:
#         check_sql = f"SELECT COUNT(*) FROM do_f_uploaded_csv_files WHERE file_name = '{filename}';"
#         pgcur.execute(check_sql)
#         count = pgcur.fetchone()[0]

#         if count > 0:
#             #  messagebox.showerror("Error", str(error))
#             messagebox.showerror(f"Error","The file {filename} has already been uploaded.")

#             print(f"The file {filename} has already been uploaded.")
#         else:
#             copy_sql = f"COPY do_f_daily_milk_tracker FROM '{filepath}' DELIMITER ',' CSV HEADER;"
#             pgcur.execute(copy_sql)
#             messagebox.showerror(f"Sucess","CSV's Files Copied to DataBase")

#             insert_sql = f"INSERT INTO do_f_uploaded_csv_files (file_name) VALUES ('{filename}');"
#             pgcur.execute(insert_sql)
#             conn.commit()
#             messagebox.showerror(f"Sucess","File_names Are inserted")


#     pgcur.close()
#     conn.close()
#     # Create a Tkinter button
# root = tk.Tk()
# button = tk.Button(root, text="Upload CSV", command=upload)
# button.pack()
# root.mainloop()
