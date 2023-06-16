import re
import pymongo as mng
import sys
import pandas as pd

# Create a MongoClient object
Client = mng.MongoClient("mongodb://localhost:27017")

# Connect to your MongoDB server
db = Client['Zitisi']

# Create a new collection
# collection=db.create_collection('Employees')
collection=db.Employees

if 'Zitisi' in Client.list_database_names():
    print(Client.list_database_names())
else:
    print("Failed to Create Zitisi Database")

# Create a new document
document = [{'Name': 'Kumar', 'Date Of Birth':8112000},{'Name': 'paladi', 'Date Of Birth':12019102}]

# db.Employees.insert_many(document)

# Find documents where name contains "Suresh"
pattern = re.compile("Shanthan", re.IGNORECASE)
query = {"Name": pattern}
matching_documents = collection.find(query)

for document in matching_documents:
    print(document)

Client.close()
