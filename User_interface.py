# Importing Required Modules from Python Libraries.....
import sys
import tkinter as tk
from tkinter import PhotoImage, filedialog,ttk
from tkinter import messagebox
import tkcalendar as tcal
import psycopg2
from PyPDF2 import * 
from reportlab.pdfgen import canvas
from pdf2image import convert_from_path
import pywhatkit
import os
import time
import keyboard
import csv

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
def show_data(from_date, to_date):
    #  Query to get Dates From table 
    sql=f"SELECT date FROM public.do_f_daily_milk_tracker  WHERE date BETWEEN '{from_date}' AND '{to_date}'"
    pgcur.execute(sql)
    data = pgcur.fetchall()
    for row in data:
        print(row)
    print(sql)

    pgcur.close()
    conn.close()

def show_dates():
    global from_date
    from_date = calendar_from.get_date()
    global to_date
    to_date = calendar_to.get_date()
    show_data(from_date, to_date)


def generate_invoice():

        from_date=calendar_from.get_date()
        to_date =calendar_to.get_date()

        # Fetching Data For PostgreSQL
        sql = "Drop view if exists vw_dummy cascade;"
        pgcur.execute(sql)
        conn.commit()
        print('sql : Drop View done')

        sql1 = f"create View vw_dummy as(select * from vw_transaction where date Between '{from_date}' AND '{to_date}');"
        pgcur.execute(sql1)
        conn.commit()
        print('Sql1 : Create vw_dummy done \n',sql1)

        sql2 = "Drop view if exists vw_transaction_month cascade;"
        pgcur.execute(sql2)
        conn.commit()
        print('sql2 : Drop vw_transaction_month done')

        sql3 = '''CREATE OR REPLACE VIEW public.vw_transaction_month AS
        SELECT null as Month_Year,
            vw_dummy.contact_no,
            vw_dummy.customer_name,
            vw_dummy.address,
            sum(vw_dummy.cm_in_ltrs) AS cm_ltrs_qunatity,
            vw_dummy.cm_price,
            sum(vw_dummy.cm_total) AS cm_total,
            sum(vw_dummy.bm_in_ltrs) AS bm_ltrs_quantity,
            vw_dummy.bm_price,
            sum(vw_dummy.bm_total) AS bm_total,
            sum(vw_dummy.total) AS total_amount,
            NULL as Status,
            NULL AS Variance,
            NULL AS Date_paid
        FROM vw_dummy
        GROUP BY vw_dummy.contact_no, vw_dummy.customer_name, vw_dummy.address, vw_dummy.cm_price, vw_dummy.bm_price
        HAVING sum(vw_dummy.total) > 0;'''
        pgcur.execute(sql3)
        conn.commit()
        print('sql3 : Create vw_transaction_month done\n',sql3)

        sql4='''select * from public.vw_transaction_month
            where contact_no not in
            (select contact_no from 
            (select contact_no,count(contact_no) from public.do_d_customer_details
            group by contact_no
            having count(contact_no)>1) as a);'''
        pgcur.execute(sql4)
        conn.commit()
        print('sql4 : Select vw_transaction_month done \n',sql4)
        global Data
        Data=list(pgcur.fetchall())
        
        # Creating a Canvas Object to save the pdf as
        s = 'D:\\Dhenusya\\' + 'Invoice.pdf'
        # Creating Canvas
        c = canvas.Canvas(s,pagesize=(200,250),bottomup=0)

        # Intiating to create invoice
        a=0
        for i in Data:
            # Assigning the Fetched Data to respected variable
            Contact_Number = i[1]
            customer = i[2]
            address = i[3]
            Cow_Quantity = i[4] 
            Cow_price = i[5]   
            Cow_rate = i[6]     
            Buff_Quantity = i[7]
            Buff_Price = i[8]
            Buff_rate = i[9]
            total_amount = i[10]
            a+=1
            
            # Logo Section

            # Setting th origin to (10,40)
            c.translate(10,40)

            # Inverting the scale for getting mirror Image of logo
            c.scale(1,-1)

            # Inserting Logo into the Canvas at required position
            c.drawImage("Dhenusya.png",0,0,width=55,height=40)

            # Title Section
            
            # Again Inverting Scale For strings insertion
            c.scale(1,-1)

            # Again Setting the origin back to (0,0) of top-left
            c.translate(-10,-40)

            # Setting the font for Name title of company
            c.setFont("Helvetica-Bold",10)
            c.setFillColor('blue')
            # Inserting the name of the company
            c.drawCentredString(125,20,"Dhenusya Organics")

            # For under lining the title
            c.line(70,23,180,23)

            # Changing the font size for Specifying Address
            c.setFont("Helvetica-Bold",5)
            c.setFillColor('black')
            c.drawCentredString(125,30,"H.no:1017,street no:2/6,Matrusri Nagar")
            c.drawCentredString(125,36,"Miyapur,Telangana, India-500049")

            # Line Seprating the page header from the body
            c.line(5,45,195,45)

            # Document Information
            # Changing the font for Document title
            c.setFont("Courier-Bold",8)
            c.drawCentredString(100,55,"INVOICE")

            # Creating a Block that Consist of Costumer Details
            c.roundRect(15,63,170,35,10,stroke=1,fill=0)
            c.setFont("Times-Bold",6)
            c.drawString(20,70,"CUSTOMER NAME : Mr/Ms." + str(customer))
            c.drawString(20,80,"PHONE NUMBER : " + str(Contact_Number)[-4:].rjust(len(str(Contact_Number)), '*'))
            c.drawString(20,90,"ADDRESS : " + str(address))
            
            # This Block Consist of Item Description
            c.roundRect(15,108,170,50,10,stroke=1,fill=0)
            c.line(15,120,185,120)
            c.drawCentredString(40,118,"ITEM")
            c.drawString(18,128,"COW_MILK")
            c.drawString(18,138,"BUFFALO_MILK")
            c.drawCentredString(87,118,"Qty(Liters)")
            c.drawCentredString(87,128,str(Cow_Quantity))
            c.drawCentredString(87,138,str(Buff_Quantity))
            c.drawCentredString(115,118,"RATE")
            c.drawCentredString(115,128,str(Cow_price))
            c.drawCentredString(115,138,str(Buff_Price))
            c.drawCentredString(156,118,"TOTAL AMOUNT")
            c.drawCentredString(156,128,str(Cow_rate))
            c.drawCentredString(156,138,str(Buff_rate))
            c.drawCentredString(156,154,str(total_amount))
            c.drawCentredString(110,154,"TOTAL")

            # Drawing table for Item Description
            c.line(15,145,185,145)
            c.line(70,108,70,145)
            c.line(105,108,105,145)
            c.line(125,108,125,158)

            # Declaration and Signature
            c.line(15,165,185,165)
            c.drawString(30,175,"Please pay via GPay/PhonePe/Paytm: ")
            c.drawString(45,185,"Display Name: ")
            c.drawString(45,195,"Let us know if there is any variance.")
            c.drawString(26,205,"Note: Kindly share the payment screenshot once paid,")
            c.drawString(42,213,"it will help us to update our records.")
            c.drawRightString(180,235,"Authorised Signature")
            c.setFont("Times-Bold",7)
            c.setFillColor("red")
            c.drawString(128,175,"+91 9160906064")
            c.drawString(85,185,"Dhenusya Organics")
            c.drawImage("Venkatesh.png",128,215,width=55,height=15)


            # End the Page and Start with new
            c.showPage()

        # Saving the PDF
        c.save()

        print("Invoice PDF Created....")

        images=convert_from_path(s,poppler_path=r'C:\Program Files\poppler-23.01.0\Library\bin')
        saving_folder = r'D:\Dhenusya\Images'
        sql4='''select * from public.vw_transaction_month
                where contact_no not in
                (select contact_no from 
                (select contact_no,count(contact_no) from public.do_d_customer_details
                group by contact_no
                having count(contact_no)>1) as a);'''
        pgcur.execute(sql4)
        print('sql4 Select vw_transaction_month done')
        Data=list(pgcur.fetchall())
        H=0
        for image,j in zip(images,Data):
                H+=1
                contact=j[1]
                img_name = str(contact)+".JPEG"
                print(H,":",img_name)
                image.save(os.path.join(saving_folder,img_name),"JPEG")  
        print('Images Created....')

        messagebox.showinfo('Invoice Generated',"Invoice PDF and Images are Generated")
        return
        
def send_whatsapp():
    # Code to get phone numbers from database goes here
    sql4 = '''select * from public.vw_transaction_month
            where contact_no not in
            (select contact_no from 
            (select contact_no,count(contact_no) from public.do_d_customer_details
            group by contact_no
            having count(contact_no)>1) as a);'''
    pgcur.execute(sql4)
    print('sql4 Select vw_transaction_month done')
    global Data
    Data = list(pgcur.fetchall())
    file_paths = filedialog.askopenfilenames(initialdir='D:\\Dhenusya\\Images\\')
    # Loop through the Data list and send only selected images to their respective phone numbers
    a=0
    for o in Data:
        a+=1
        number = o[1]
        image_path = "D:/Dhenusya/Images/" + str(number) + ".JPEG"
        # print(a,":",image_path)
        if image_path in file_paths:
            print("Image Path :",image_path)
            # print("Selected Images file_paths :",file_paths)
            # pywhatkit.sendwhats_image("+91" + str(number), image_path)
            # time.sleep(10)
            # keyboard.press_and_release('ctrl+w')
            print(a,":",str(number))
    
    messagebox.showinfo("WhatsApp Message Sent","Invoice's Sent to the customer.")
    Status_Update = messagebox.askyesno("Remainder Generation", " Do You Want To Generate Consolidate CSV ?.Click Yes To Continue !")

    if Status_Update == True:
        messagebox.showinfo("Consolidate Generation"," NOTE:Please Update Month_year Column.")
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

        os.system('Remainder.csv')
            
        messagebox.showinfo("Consolidate Generation","Consoliadate CSV is Created")

        Copy_Query = f"COPY public.consolidate_milksummar FROM 'D:\\Python\\Remainder.csv' DELIMITER ',' CSV HEADER;"
        time.sleep(2)
        pgcur.execute(Copy_Query)
        conn.commit()
        print(Copy_Query)
        print("Remainder File For Bill Update is Uploaded In PostgreSQL.")

        messagebox.showinfo("Consolidate Update","Consoliadate CSV is Uploaded To PostgreSQL")


    else:
        messagebox.showinfo("Consolidate Generation","Consoliadate CSV is Not Created")
    return

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
    return
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
def select_status_MILK(selected_month_year,selected_status):
    selected_month_year = month_year_var.get()
    selected_status = status_var.get()
    print("MONTH_YEAR",selected_month_year)
    if selected_month_year and selected_status:
        DropDown = f"SELECT * FROM public.consolidate_milksummar WHERE month_year = '{selected_month_year}' AND status = '{selected_status}';"
        print(DropDown)
    elif selected_status:
        DropDown = f"SELECT * FROM public.consolidate_milksummar WHERE status = '{selected_status}';"
        print(DropDown)
    else:
        DropDown = f"SELECT * FROM public.consolidate_milksummar WHERE month_year = '{selected_month_year}';"
        print(DropDown)

    # DropDown=f"SELECT * FROM public.consolidate_milksummar WHERE status = '{selected_status}';"
    pgcur.execute(DropDown)
    Data = pgcur.fetchall()
    # ---------------------------
    choice = messagebox.askyesno("Remainder", " Do You Want To Generate Bills for  Remainders For Selected Status  Customers ?.Click Yes To Continue !")
    if choice == True:
        # Creating a Canvas Object to save the pdf as
        s = 'D:\\Dhenusya\\' + 'Invoice.pdf'
        # Creating Canvas
        c = canvas.Canvas(s,pagesize=(200,250),bottomup=0)

        # Intiating to create invoice
        a=0
        for i in Data:
            # Assigning the Fetched Data to respected variable
            Contact_Number = i[1]
            customer = i[2]
            address = i[3]
            Cow_Quantity = i[4] 
            Cow_price = i[5]   
            Cow_rate = i[6]     
            Buff_Quantity = i[7]
            Buff_Price = i[8]
            Buff_rate = i[9]
            total_amount = i[10]
            # status=i[11]
            a+=1
            
            # Logo Section

            # Setting th origin to (10,40)
            c.translate(10,40)

            # Inverting the scale for getting mirror Image of logo
            c.scale(1,-1)

            # Inserting Logo into the Canvas at required position
            c.drawImage("Dhenusya.png",0,0,width=55,height=40)

            # Title Section
            
            # Again Inverting Scale For strings insertion
            c.scale(1,-1)

            # Again Setting the origin back to (0,0) of top-left
            c.translate(-10,-40)

            # Setting the font for Name title of company
            c.setFont("Helvetica-Bold",10)
            # c.setFillColor('blue')
            # Inserting the name of the company
            c.drawCentredString(125,20,"Dhenusya Organics")

            # For under lining the title
            c.line(70,23,180,23)

            # Changing the font size for Specifying Address
            c.setFont("Helvetica-Bold",5)
            c.setFillColor('black')
            c.drawCentredString(125,30,"H.no:1017,street no:2/6,Matrusri Nagar")
            c.drawCentredString(125,36,"Miyapur,Telangana, India-500049")

            # Line Seprating the page header from the body
            c.line(5,45,195,45)

            # Document Information
            # Changing the font for Document title
            c.setFont("Courier-Bold",8)
            c.drawCentredString(100,55,"FEB_2023 INVOICE")

            # Creating a Block that Consist of Costumer Details
            c.roundRect(15,63,170,35,10,stroke=1,fill=0)
            c.setFont("Times-Bold",6)
            c.drawString(20,70,"Customer Name : Mr/Ms." + str(customer))
            c.drawString(20,80,"Phone Number : " + str(Contact_Number))
            c.drawString(20,90,"Address : " + str(address))
            
            # This Block Consist of Item Description
            c.roundRect(15,108,170,50,10,stroke=1,fill=0)
            c.line(15,120,185,120)
            c.drawCentredString(40,118,"Item")
            c.drawString(18,128,"Cow_Milk")
            c.drawString(18,138,"Buffalo_Milk")
            c.drawCentredString(87,118,"Qty(Liters)")
            c.drawCentredString(87,128,str(Cow_Quantity))
            c.drawCentredString(87,138,str(Buff_Quantity))
            c.drawCentredString(115,118,"Rate")
            c.drawCentredString(115,128,str(Cow_price))
            c.drawCentredString(115,138,str(Buff_Price))
            c.drawCentredString(156,118,"Total Amount")
            c.drawCentredString(156,128,str(Cow_rate))
            c.drawCentredString(156,138,str(Buff_rate))
            c.drawCentredString(156,154,str(total_amount))
            c.drawCentredString(110,154,"Total")

            # Drawing table for Item Description
            c.line(15,145,185,145)
            c.line(70,108,70,145)
            c.line(105,108,105,145)
            c.line(125,108,125,158)

            # Declaration and Signature
            c.line(15,165,185,165)
            c.drawString(30,175,"Please pay via GPay/PhonePe/Paytm: ")
            c.drawString(45,185,"Display Name: ")
            c.drawString(45,195,"Let us know if there is any variance.")
            c.drawString(26,205,"Note: Kindly share the payment screenshot once paid,")
            c.drawString(42,213,"it will help us to update our records.")
            c.drawRightString(180,235,"Authorised Signature")
            c.setFont("Times-Bold",7)
            c.setFillColor("red")
            c.drawString(128,175,"+91 9160906064")
            c.drawString(85,185,"Dhenusya Organics")
            c.drawImage("Venkatesh.png",128,215,width=55,height=15)


            # End the Page and Start with new
            c.showPage()

        # Saving the PDF
        c.save()

        print("Invoice PDF Created....")

        images=convert_from_path(s,poppler_path=r'C:\Program Files\poppler-23.01.0\Library\bin')
        saving_folder = r'D:\Dhenusya\Images'
        # sql4='''select * from public.vw_transaction_month
        #         where contact_no not in
        #         (select contact_no from 
        #         (select contact_no,count(contact_no) from public.do_d_customer_details
        #         group by contact_no
        #         having count(contact_no)>1) as a);'''
        # pgcur.execute(sql4)
        # print('sql4 Select vw_transaction_month done')
        # Data=list(pgcur.fetchall())
        H=0
        for image,j in zip(images,Data):
                H+=1
                contact=j[1]
                
                print(contact)
                img_name = str(contact)+".JPEG"
                print(H,":",img_name)
                image.save(os.path.join(saving_folder,img_name),"JPEG")  
        print('Images Created....')

        messagebox.showinfo('Invoice Generated',"Invoice PDF and Images are Generated")

    # -----------------------------
    choice = messagebox.askyesno("Remainder", " Do You Want To Send Bill Remainders For Selected Status  Customers ?.Click Yes To Continue !")
    if choice == True:
        file_paths = filedialog.askopenfilenames(initialdir='D:\\Dhenusya\\Images')
        # Loop through the Data list and send only selected images to their respective phone numbers
        a=0
        for o in Data:
            a+=1
            number = o[1]
            
            image_path = "D:/Dhenusya/Images/" + str(number) + ".JPEG"
            # print(a,":",image_path)
            if image_path in file_paths:
                print(a,number)
                print(a,"image Path :",image_path)
                # print("selected images file_paths :",file_paths)
                # pywhatkit.sendwhats_image("+91" + str(number), image_path)
                # time.sleep(10)
                # keyboard.press_and_release('ctrl+w')
    else:
        messagebox.showinfo(f"Sucess","Whatsapp Remainders Are Not Sent")
        time.sleep(1)

    Status_Update = messagebox.askyesno("Remainder Status", " Do You Want To Update Bills of Remainders? If Yes Click Yes To Continue !")

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
        if selected_month_year and selected_status:
            Delete_Query =f"Delete FROM public.consolidate_milksummar WHERE month_year= '{selected_month_year}' and status = '{selected_status}';"
            time.sleep(2)
            print(Delete_Query)
        elif selected_status:
            Delete_Query =f"Delete FROM public.consolidate_milksummar WHERE status= '{selected_status}' ;"
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
# generate Invoice Button
button2 = tk.Button(root, command=generate_invoice, text="Generate Invoice  ", bg="Green Yellow")
button2.place(x=50, y=155)
# whatsapp images sender button
button3 = tk.Button(root, command=send_whatsapp, text="Monthly Bill's Sender", bg="Lime Green")
button3.place(x=205, y=155)
# Bill remainder button
button3 = tk.Button(root, command=Bills_Remainder, text="Bill Remainder Upload", bg="Orange Red")
button3.place(x=380, y=155)

# Create label for status_menu
status_label = tk.Label(root, text="Select Status:")
status_label.place(x=300, y=630)
status_var = tk.StringVar()
status_values = get_status_values()
status_menu = tk.OptionMenu(root, status_var, *status_values)
status_menu.configure(bg='Cadet Blue')

status_menu.place(x=410, y=630)
# Create label for month_year_menu
month_year_label = tk.Label(root, text="Select month_year:")
month_year_label.place(x=50, y=630)
month_year_var = tk.StringVar()

month_year_values = get_month_year_values()
month_year_menu = tk.OptionMenu(root, month_year_var, *month_year_values)
month_year_menu.configure(bg='Cadet Blue')
month_year_menu.place(x=205, y=630)
# Create button to select data
select_button = tk.Button(root, text="Re-Remainder & Consolidate", command=lambda: select_status_MILK(month_year_var.get(), status_var.get()),bg='Cadet Blue')
select_button.place(x=205, y=685)

calendar_from = tcal.DateEntry(root, width=12, background='Royal Blue', foreground='Alice Blue', borderwidth=4)
calendar_to = tcal.DateEntry(root, width=12, background='Royal Blue', foreground='Alice Blue', borderwidth=4)
# place holder of callenders Dates
calendar_from.place(x=50, y=110)
calendar_to.place(x=205, y=110)
#callenders Button
From = tk.Label(root, text="From")
From.place(x=50, y=80)
To = tk.Label(root, text="To")
To.place(x=205, y=80)

root.mainloop()