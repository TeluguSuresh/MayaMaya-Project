
# Importing Required Modules from Python Libraries.....
from logging import root
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
        print('sql Drop View done')

        sql1 = f"create View vw_dummy as(select * from vw_transaction where date Between '{from_date}' AND '{to_date}');"
        pgcur.execute(sql1)
        print('sql1 vw_dummy done')

        sql2 = "Drop view if exists vw_transaction_month cascade;"
        pgcur.execute(sql2)
        print('sql2 Drop vw_transaction_month done')

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
        GROUP BY vw_dummy.contact_no, vw_dummy.customer_name, vw_dummy.address, vw_dummy.cm_price, vw_dummy.bm_price;'''
        pgcur.execute(sql3)
        print('sql3 Create vw_transaction_month done')

        sql4='''SELECT *
                FROM vw_transaction_month 
                GROUP BY month_year,contact_no,customer_name,address, 
                cm_ltrs_qunatity,cm_price,cm_total,bm_ltrs_quantity,bm_price,bm_total,total_amount,
                status,variance,date_paid;'''
        pgcur.execute(sql4)
        print('sql4 Select vw_transaction_month done')
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
            Building_name = i[3]
            Cow_Quantity = i[4] 
            Cow_price = i[5]   
            Cow_rate = i[6]     
            Buff_Quantity = i[7]
            Buff_Price = i[8]
            Buff_rate = i[9]
            total_amount = i[0]
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
            c.drawString(20,90,"ADDRESS : " + str(Building_name))
            
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
        sql4='''SELECT *
                FROM vw_transaction_month 
                GROUP BY month_year,contact_no,customer_name,address, 
                cm_ltrs_qunatity,cm_price,cm_total,bm_ltrs_quantity,bm_price,bm_total,total_amount,
                status,variance,date_paid;'''
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
        # sys.exit() here
# Create a Tkinter buttons
root = tk.Tk()
root.geometry("600x850") 
root.title("Dhenusya Organics") 

label = tk.Label(root, text="Welcome to Dhenusya Organics UI design!")
label.pack()
# Print a message after the file is closed
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
# generate Invoice Button
button2 = tk.Button(root, command=generate_invoice, text="Generate Invoice  ", bg="Green Yellow")
button2.place(x=50, y=155)

root.mainloop()