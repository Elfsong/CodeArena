#coding: utf-8

import os
import json
import pickle
import hashlib

def get_auth():
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PASSWORD")
    return username, password

def get_db_info():
    db_name = os.getenv("MONGO_DBNAME")
    db_port = os.getenv("MONGO_PORT")
    return db_name, db_port

def get_hash(text):
    return hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()

def get_json(raw_data):
    return json.loads(raw_data)
