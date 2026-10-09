from config.mongodb import db


business_collection = db["business_data"]

business_collection.insert_one({
    "product": "Laptop",
    "region": "South",
    "sales": 85000,
    "profit": 12000
})

print("Business data inserted successfully!")