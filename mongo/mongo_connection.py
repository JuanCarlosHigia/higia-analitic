from pymongo import MongoClient

import os
from dotenv import load_dotenv

load_dotenv()

# db_client = MongoClient("mongodb://"+os.getenv("MONGO_HOST")+":"+str(os.getenv("MONGO_PORT")))
mode_local = os.getenv("LOCAL_MODE")
username=os.getenv("MONGO_USER")
password=os.getenv("MONGO_PASS")
mongo_uri=os.getenv("MONGO_URL")
if mode_local == "True":
    db_client = MongoClient(os.getenv("MONGO_HOST_LOCAL"))
else:
    db_client = MongoClient("mongodb://"+username+":"+password+"@"+mongo_uri+":27017/local?authSource=admin")

ddbb= db_client[os.getenv("SINTETICA")]

mongoCollection = ddbb[os.getenv("MONGO_IACOLLECTION")]


