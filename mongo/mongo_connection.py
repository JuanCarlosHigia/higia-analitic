import streamlit as st
from pymongo import MongoClient

mode_local = st.secrets["LOCAL_MODE"]
username=st.secrets["MONGO_USER"]
password=st.secrets["MONGO_PASS"]
mongo_uri=st.secrets["MONGO_URL"]
if mode_local == "True":
    db_client = MongoClient(st.secrets["MONGO_HOST_LOCAL"])
else:
    db_client = MongoClient("mongodb://"+username+":"+password+"@"+mongo_uri+":27017/local?authSource=admin")

ddbb= db_client[st.secrets["COLLECTION"]]

mongoCollection = ddbb[st.secrets["MONGO_IACOLLECTION"]]


