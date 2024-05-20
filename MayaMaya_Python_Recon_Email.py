import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import time
import pandas as pd
import sys, psycopg2
msg = MIMEMultipart()

time.sleep(120)
# Connect to the PostgreSQL database
pgconn=psycopg2.connect(host="localhost",
            database="MayaMaya_Prod",
            user="postgres",
            password="postgres")

# Create a pgcur object to interact with the database
pgcur=pgconn.cursor()
table = 'base_etl_recon'
location = "C:\MayaMaya_Python_Scripts"

time.sleep(120)
sql = "copy (SELECT * FROM base.base_etl_recon ) TO '{}/{}.csv' WITH CSV HEADER DELIMITER ',';".format(location,table)
time.sleep(120)
pgcur.execute(sql)

pgcur.close()
pgconn.commit()

time.sleep(120)

df = pd.read_csv("C:\MayaMaya_Python_Scripts\etl_recon.csv",sep=",")
print(df.to_string())

time.sleep(120)
MESSAGE_BODY=df.to_html()
body_part = MIMEText(MESSAGE_BODY,'html')
msg['Subject'] = 'MayaMaya_Prod ETL Recon'
msg['From'] = "MayaMaya_Load<noreplychromiumsolutions@gmail.com>"
msg['To'] = "suresh.telugu@chromiumsolutions.com"
msg['CC']="Venkatesh Gudipati <venkatesh.gudipati@chromiumsolutions.com>;sameer@catenate.io"
msg.attach(body_part)
sender_email = "noreplychromiumsolutions@gmail.com"
password = "bkmgbkyukavkcauv"
server = smtplib.SMTP('smtp.googlemail.com', 587)
server.starttls ()
server.login (sender_email, password)
server.send_message(msg)