import os
import random
import urllib.parse
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class AccountManager:
    def __init__(self, accounts_file: str, client_id: int):
        self.accounts_file = accounts_file
        self.client_id = client_id
        
        # MongoDB settings from env
        mongo_user = os.getenv("MONGO_USER")
        mongo_pass = os.getenv("MONGO_PASS")
        mongo_host = os.getenv("MONGO_HOST")
        mongo_port = os.getenv("MONGO_PORT")
        self.mongo_db = os.getenv("MONGO_DB_ACCOUNT", "linkedin_account")
        self.mongo_col = os.getenv("MONGO_COLLECTION_ACCOUNT", "medmon")
        
        # Build connection string
        if mongo_user and mongo_pass:
            username_esc = urllib.parse.quote_plus(mongo_user)
            password_esc = urllib.parse.quote_plus(mongo_pass)
            uri = f"mongodb://{username_esc}:{password_esc}@{mongo_host}:{mongo_port}/{self.mongo_db}?authSource=admin"
        else:
            uri = f"mongodb://{mongo_host}:{mongo_port}/{self.mongo_db}"
            
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[self.mongo_db]
        self.col = self.db[self.mongo_col]

    def load_accounts(self) -> list:
        try:
            return list(self.col.find({}))
        except Exception as e:
            print(f"[ERROR] Failed to load accounts from MongoDB: {e}")
            return []

    def save_accounts(self, accounts: list):
        try:
            for acc in accounts:
                username = acc.get("username")
                if username:
                    update_data = {k: v for k, v in acc.items() if k != "_id"}
                    self.col.update_one({"username": username}, {"$set": update_data})
        except Exception as e:
            print(f"[ERROR] Failed to save accounts to MongoDB: {e}")

    def get_available_account(self) -> dict:
        accounts = self.load_accounts()
        candidates = [
            acc for acc in accounts
            if acc.get("available") is True
            and acc.get("in_use") is False
            and int(acc.get("client_id")) == int(self.client_id)
        ]
        if candidates:
            return random.choice(candidates)
        return None

    def release_account(self, username: str):
        if not username:
            return
        try:
            accounts = self.load_accounts()
            for acc in accounts:
                if acc.get("username") == username:
                    acc["in_use"] = False
            self.save_accounts(accounts)
        except Exception as e:
            print(f"[ERROR] Failed to release account: {e}")

    def mark_account_failed(self, username: str):
        if not username:
            return
        try:
            accounts = self.load_accounts()
            for acc in accounts:
                if acc.get("username") == username:
                    acc["available"] = False
            self.save_accounts(accounts)
        except Exception as e:
            print(f"[ERROR] Failed to mark account failed: {e}")
