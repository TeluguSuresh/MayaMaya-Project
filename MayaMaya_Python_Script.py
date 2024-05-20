from ast import While
import datetime
from logging import exception
from msilib.schema import Error
import pymongo as mng
import pandas as pd
import subprocess
import sys, psycopg2    
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import sys,traceback
import sys, psycopg2

max_attempts = 2  # Maximum number of attempts to run the script
attempt = 1  # Current attempt number

while attempt <= max_attempts:
    try:
        # Initialize database connection and cursor
        connection = mng.MongoClient("mongodb://localhost:27017")
        db = connection['mayamaya']

        with psycopg2.connect(host="localhost",
                database="MayaMaya_Prod",
                user="postgres",
                password="postgres") as pgconn:
                pgcur=pgconn.cursor()

        def export_table(table):
            # file = table + ".csv"
            
            if(len(list(db[table].find()))!=0):
                allKeys=db[table].find()[0]
                if(table == "user_profile"):
                    fieldlist = "_id,userId,name,email,location,userPhoto,createdDate,role,orgCode,department,designation,accountId,updatedDate,country,gender,region,veterans,ethnicity,specialConsiderations,age"
                elif(table == "user_results"):
                    fieldlist = "_id,userId,sprintId,resultDateTime,spiritResult.quadScore,spiritResult.quadDisplay,spiritResult.blurb,spiritResult.fullAnswerGrades,spiritResult.countOfQuestionsAnswered,professionResult.quadScore,professionResult.quadDisplay,professionResult.blurb,professionResult.fullAnswerGrades,professionResult.countOfQuestionsAnswered,purposeResult.quadScore,purposeResult.quadDisplay,purposeResult.blurb,purposeResult.fullAnswerGrades,purposeResult.countOfQuestionsAnswered,rewardsResult.quadScore,rewardsResult.quadDisplay,rewardsResult.blurb,rewardsResult.fullAnswerGrades,rewardsResult.countOfQuestionsAnswered"        
                elif(table == "user_courses"):
                    fieldlist = "_id,userId,resultId,courseMasterId,courseCode,courseName,headline,appTextScanner,appTextReader,appTextMiner,courseImage,textOfRoi,traits,courseCatalog,relatedJobs,salaryRange,summary,isKeep,countOfInstitutes,createdDate,updatedDate,keepStartDate,keepEndDate,keepStartDateHistory,keepEndDateHistory,keepCount,unKeepCount,countOfCourseProviders"
                else:
                    fieldlist = ",".join(allKeys)

                cmd = "mongodb://localhost:27017\" --db mayamaya --collection "+table +" --type csv --fields " + fieldlist + " --out C:\\MayaMaya_Python_Scripts\\tmp\\" + table.replace(".","_") + ".csv " 
                time.sleep(5)
                
                # subprocess.Popen(cmd, shell=True)
                process = subprocess.Popen(cmd, shell=True)
                process.wait()  # Wait for the process to finish before proceeding
                
                print("exporting done")
                time.sleep(10)

        def import_table(table):
            file = table + ".csv"
            if(len(list(db[table].find()))!=0):
                allKeys=db[table].find()[0]
                if(table == "user_profile"):
                    fieldlist = "_id,userId,name,email,location,userPhoto,createdDate,role,orgCode,department,designation,accountId,updatedDate,country,gender,region,veterans,ethnicity,specialConsiderations,age"
                elif(table == "user_results"):
                    fieldlist = '_id,userId,sprintId,resultDateTime,"spiritResult.quadScore","spiritResult.quadDisplay","spiritResult.blurb","spiritResult.fullAnswerGrades","spiritResult.countOfQuestionsAnswered","professionResult.quadScore","professionResult.quadDisplay","professionResult.blurb","professionResult.fullAnswerGrades","professionResult.countOfQuestionsAnswered","purposeResult.quadScore","purposeResult.quadDisplay","purposeResult.blurb","purposeResult.fullAnswerGrades","purposeResult.countOfQuestionsAnswered","rewardsResult.quadScore","rewardsResult.quadDisplay","rewardsResult.blurb","rewardsResult.fullAnswerGrades","rewardsResult.countOfQuestionsAnswered"'
                elif(table == "user_courses"):
                    fieldlist = "_id,userId,resultId,courseMasterId,courseCode,courseName,headline,appTextScanner,appTextReader,appTextMiner,courseImage,textOfRoi,traits,courseCatalog,relatedJobs,salaryRange,summary,isKeep,countOfInstitutes,createdDate,updatedDate,keepStartDate,keepEndDate,keepStartDateHistory,keepEndDateHistory,keepCount,unKeepCount,countOfCourseProviders"
                else:
                    fieldlist = ",".join(allKeys)
                
            table = table.replace(".","_")
            trunc_sql = "TRUNCATE TABLE public."+table+";"
            print(trunc_sql)
            pgcur.execute(trunc_sql)
            print('Table Truncate')
            filepath = 'C:\\MayaMaya_Python_Scripts\\tmp\\'+table +'.csv'
            print("***", filepath, "***")

            copy_sql = "copy public." + table + "(" + fieldlist + ")" + " from '" + filepath + "' DELIMITER ',' csv header;"
            print(copy_sql)
            pgcur.execute(copy_sql)

            print("importing done")
            time.sleep(30)
            
        def recon_table(table):
            
            sql = 'SELECT count(*) from '+table.replace(".","_")
            print(sql)
            data=[]
    
            pgcur.execute(sql,data)
            results = pgcur.fetchone()
            a=0
            for tgt_record_count in results:
                a+=1
                tgt_sql = "insert into public.etl_recon select etl_batch_id,'"+table+"' as table_name,src_record_count,tgt_record_count,(src_record_count-tgt_record_count) as difference,now() as etl_insert_timestamp from(select "+str(src_record_count)+" as src_record_count,"+str(tgt_record_count)+" as tgt_record_count)t cross join public.mm_etl_batch etl where etl.etl_status = 'Started'"
                print(tgt_sql)
                pgcur.execute(tgt_sql)
                pgconn.commit()        
            
        if __name__=='__main__':
            # Get the table argument from the command line 
            table = sys.argv[1]
            src_record_count = db[table].count_documents({})

            starting = datetime.datetime.now()
            print("execution starting time :",starting)
            
            # Export Table
            print("exporting ",table)
            export_table(table)
            print("exported ",table)

            time.sleep(20)

            #Import Table
            print("importing ",table)
            import_table(table)
            print("imported ",table)

            time.sleep(20)

            #Reconciliation
            print("Reconciliation Started...")
            recon_table(table)
            print("Reconciliation Completed")

            ending = datetime.datetime.now()
            print("Execution Ending date :",ending)
            print('Duration: {}'.format(ending - starting))

        pgcur.close()
        pgconn.commit()
        break  # If the code above executes successfully, break out of the loop

    except Exception as ex:
        if attempt < max_attempts:
            print(f"Attempting again... (Attempt {attempt + 1})")
            attempt += 1
        else:
            print(f"Maximum number of attempts reached. Exiting...")
            time.sleep(10)
            error_message = traceback.format_exc()
            print("Error occurred during execution:\n", error_message)
            time.sleep(10)
            error_message = traceback.format_exc()
            print("Error occurred during execution:\n", error_message)

            # Read the contents of the log file
            log_file = "C:\\MayaMaya_Python_Scripts\\Parallel_log\\"+table+"_log.log"
            with open(log_file, 'r') as file:
                log_contents = file.read()

            msg = MIMEMultipart()
            msg['Subject'] = table + " Failed"
            msg['From'] = "MayaMaya_Load"
            msg['To'] = "telugusuresh.1998@gmail.com"
            msg['CC'] = "telugusuresh.1998@gmail.com"
            msg.attach(MIMEText(error_message, 'plain'))
            msg.attach(MIMEText(log_contents, 'plain'))

            sender_email = "telugupersonal45@gmail.com"
            password = "bkmgbkyukavkcauv"
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
            server.quit()
            break
        