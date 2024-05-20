# Sample Testing File
# MongoDB Basics Operations
import re
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['Dhenusya']
collection = db['Milk Delivery Boys']

# Insert a single document
document = {"name": "John", "age": 25}
result = collection.insert_one(document)
print("Inserted document ID:", result.inserted_id)

# Insert multiple documents
documents = [
    {"name": "Emily", "age": 30},
    {"name": "Michael", "age": 35}
]
result = collection.insert_many(documents)
print("Inserted document IDs:", result.inserted_ids)

# Find all documents
all_documents = collection.find()
for document in all_documents:
    print(document)

# Find documents with a specific condition
age_filter = {"age": {"$gt": 30}}  # Find documents where age is greater than 30
filtered_documents = collection.find(age_filter)
for document in filtered_documents:
    print(document)

# Update a single document
filter_condition = {"name": "John"}
update_data = {"$set": {"age": 26}}
result = collection.update_one(filter_condition, update_data)
print("Modified documents count:", result.modified_count)

# Find documents where name contains "Suresh"
pattern = re.compile("Shanthan", re.IGNORECASE)
query = {"Name": pattern}
matching_documents = collection.find(query)

for document in matching_documents:
    print(document)

# Update multiple documents
filter_condition = {"age": {"$lt": 30}}  # Update documents where age is less than 30
update_data = {"$inc": {"age": 1}}  # Increment age by 1
result = collection.update_many(filter_condition, update_data)
print("Modified documents count:", result.modified_count)


# Delete a single document
filter_condition = {"name": "John"}
result = collection.delete_one(filter_condition)
print("Deleted document count:", result.deleted_count)

# Delete multiple documents
filter_condition = {"age": {"$gt": 30}}  # Delete documents where age is greater than 30
result = collection.delete_many(filter_condition)
print("Deleted document count:", result.deleted_count)
