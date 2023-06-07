from logging import root
import os
import time
import keyboard
import psycopg2
import pywhatkit
import tkinter as tk
from tkinter import filedialog



# Function to send WhatsApp messages with selected images
conn = psycopg2.connect(
        host="localhost",
        database="Dhenusya",
        user="postgres",
        password="96528728")
pgcur=conn.cursor()
# # Create a Tkinter button   
# root = tk.Tk()
# root.geometry("600x800") 
# root.title("Dhenusya Organics") 



def send_selected_images():

    # Code to get phone numbers from database goes here
    sql4 = "select * from vw_transaction_month;"
    pgcur.execute(sql4)
    print('sql4 Select vw_transaction_month done')
    global Data
    Data = list(pgcur.fetchall())
    
    file_paths = filedialog.askopenfilenames()
    # Loop through the Data list and send only selected images to their respective phone numbers
    a=0
    for o in Data:
        a+=1
        number = o[0]
        image_path = "D:/Dhenusya/Images/" + str(number) + ".JPEG"
        # print(a,":",image_path)
        if image_path in file_paths:
            print("image Path :",image_path)
            print("selected images file_paths :",file_paths)
            pywhatkit.sendwhats_image("+91" + str(number), image_path)
            time.sleep(10)
            keyboard.press_and_release('ctrl+w')

button3 = tk.Button(root, command=send_selected_images, text="Whatsapp Images", bg="Lime Green")
button3.place(x=205, y=155)
root.mainloop()