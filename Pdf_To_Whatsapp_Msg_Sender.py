# Importing Required Module
from reportlab.pdfgen import canvas     # To Generate Invoice format
import psycopg2                         # To Connect and Import data from PostgreSQL DataBase
from PyPDF2 import *                    # To Merge multiple pdf's to one PDF
from pdf2image import convert_from_path # To Convert PDF to Image
import pywhatkit                        # To Connect with WhatsApp WEB and send image
import time                             # To use libraries in TIME Module
import os                               # To get system files
  
conn = psycopg2.connect(database='Dhenushya',
                        user='postgres', password='root', 
                        host='localhost', port='5432'
)

conn.autocommit = True
cursor = conn.cursor()

sql1 = "select * from public.test;"
cursor.execute(sql1)
dec=list(cursor.fetchall())

a=0
for i in dec:
        customer = i[1]
        Contact_Number = i[0]
        Address = i[2]
        Cow_Quantity = i[7]
        Buff_Quantity = i[8]
        Cow_price = i[5] 

        Buff_Price = i[6]
        Cow_rate = i[9]
        Buff_rate = i[10]
        total_amount = i[11]

        a+=1
        # Creating Canvas
        c = canvas.Canvas(str(a)+'_'+str(Contact_Number) + '_' + str(customer) + '_' +'DEC_2022.pdf',pagesize=(200,250),bottomup=0)

        # Logo Section
        # Setting th origin to (10,40)
        c.translate(10,40)

        # Inverting the scale for getting mirror Image of logo
        c.scale(1,-1)

        # Inserting Logo into the Canvas at required position
        c.drawImage("dhenushyaorganics.png",0,0,width=55,height=40)

        # Title Section
        # Again Inverting Scale For strings insertion
        c.scale(1,-1)

        # Again Setting the origin back to (0,0) of top-left
        c.translate(-10,-40)

        # Setting the font for Name title of company
        c.setFont("Helvetica-Bold",10)

        # Inserting the name of the company
        c.drawCentredString(125,20,"Dhenusya Organics")

        # For under lining the title
        c.line(70,23,180,23)

        # Changing the font size for Specifying Address
        c.setFont("Helvetica-Bold",5)
        c.drawCentredString(125,30,"Plot No.1017, Road No.2/6 Matrusri Nagar Miyapur")
        c.drawCentredString(125,36,"Hyderabad - 500049, India")

        # Line Seprating the page header from the body
        c.line(5,45,195,45)

        # Document Information
        # Changing the font for Document title
        c.setFont("Courier-Bold",8)
        c.drawCentredString(100,55,"Dec_2022 INVOICE")
        # This Block Consist of Costumer Details
        c.roundRect(15,63,170,35,10,stroke=1,fill=0)
        c.setFont("Times-Bold",6)
        c.drawString(20,70,"CUSTOMER NAME : Mr/Mrs." + str(customer))
        c.drawString(20,80,"PHONE NUMBER : " + str(Contact_Number)[-4:].rjust(len(str(Contact_Number)), '*'))
        c.drawString(20,90,"ADDRESS : " + str(Address))
        
        # This Block Consist of Item Description
        c.roundRect(15,108,170,50,10,stroke=1,fill=0)
        c.line(15,120,185,120)
        c.drawCentredString(40,118,"Item")
        c.drawString(18,128,"Cow Milk")
        c.drawString(18,138,"Buffalo Milk")
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
        c.drawString(128,175,"+91 9160906064;")
        c.drawString(85,185,"Dhenusya Organics")
        c.drawImage("Venkatesh.png",128,210,width=55,height=20)
        # Saving the PDF
        c.save()

        print(a,Contact_Number,customer)
print("Invoice's Created")

merger = PdfMerger()
b = 0
for items in os.listdir():
        b+=1
        
        if items.endswith('.pdf'):
                print(b,items)
                merger.append(items)

merger.write("December_Invoice.pdf")
merger.close()
print("PDF DONE")

# Converting PDF to JPEG      

poppler_path = r"C:\Users\user\Downloads\poppler-22.12.0\Library\bin"
pdf_path = r"D:\Final Testing\December_Invoice.pdf"

pages = convert_from_path(pdf_path=pdf_path,poppler_path=poppler_path)

saving_folder = r"D:\Final Testing"
c = 1
for page in pages:
    img_name = f"img-{c}.JPEG"
    page.save(os.path.join(saving_folder,img_name),"JPEG")  
    c+=1

# To send each individual their own image in whatsapp 
path = "D:\Final Testing\Images/"
files = os.listdir(path)
abcd = []
for j in dec:
      abcd.append(j[0])
print(abcd)
a=0
for file in files:
      image_path = path + file
      if file.endswith(".JPEG"):
            print("+91"+str(abcd[a]),image_path)
            pywhatkit.sendwhats_image("+91"+str(abcd[a]),image_path)
            a+=1
            time.sleep(15)