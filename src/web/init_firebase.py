#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Firebase initialization script for Bibliometric Web App.
Sets up collections and initial data in Firestore.
"""

import os
import json
import argparse
import firebase_admin
from firebase_admin import credentials, firestore, auth

def initialize_firebase():
    """Initialize Firebase Admin SDK using service account credentials"""
    cred_path = os.path.join("secrets", "firebase_credentials.json")
    if not os.path.exists(cred_path):
        print(f"Error: Firebase credentials not found at {cred_path}")
        print("Please create this file following the instructions in the README.")
        return None
    
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully.")
        return True
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
        return None

def create_initial_collections():
    """Create initial collections in Firestore"""
    try:
        db = firestore.client()
        
        # Create collections if they don't exist by adding and then deleting a dummy document
        collections = ["users", "api_keys", "search_logs", "api_usage"]
        
        for collection in collections:
            # Check if collection exists by trying to get a document
            docs = list(db.collection(collection).limit(1).stream())
            
            if not docs:
                print(f"Creating collection: {collection}")
                # Add a temporary document
                temp_ref = db.collection(collection).document("temp")
                temp_ref.set({"temp": True})
                # Delete the temporary document
                temp_ref.delete()
            else:
                print(f"Collection {collection} already exists")
        
        return True
    except Exception as e:
        print(f"Error creating collections: {str(e)}")
        return False

def read_api_keys():
    """Read API keys from files and store in Firestore"""
    try:
        db = firestore.client()
        
        # Anthropic API Key
        anthropic_path = os.path.join("secrets", "anthropic-apikey")
        if os.path.exists(anthropic_path):
            with open(anthropic_path, 'r') as f:
                key = f.read().strip()
                if key:
                    db.collection("api_keys").document("anthropic").set({
                        "key": key,
                        "updated_at": firestore.SERVER_TIMESTAMP,
                        "updated_by": "system_init"
                    })
                    print("Anthropic API key stored in Firestore")
        else:
            print(f"Warning: Anthropic API key file not found at {anthropic_path}")
        
        # Science Direct API Key
        sciencedirect_path = os.path.join("secrets", "sciencedirect_apikey.txt")
        if os.path.exists(sciencedirect_path):
            with open(sciencedirect_path, 'r') as f:
                key = f.read().strip()
                if key:
                    db.collection("api_keys").document("sciencedirect").set({
                        "key": key,
                        "updated_at": firestore.SERVER_TIMESTAMP,
                        "updated_by": "system_init"
                    })
                    print("Science Direct API key stored in Firestore")
        else:
            print(f"Warning: Science Direct API key file not found at {sciencedirect_path}")
        
        return True
    except Exception as e:
        print(f"Error storing API keys: {str(e)}")
        return False

def create_admin_user(email, password, display_name):
    """Create an admin user"""
    try:
        # Create the user in Firebase Auth
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        
        # Store user in Firestore
        db = firestore.client()
        db.collection("users").document(user.uid).set({
            "email": email,
            "display_name": display_name,
            "created_at": firestore.SERVER_TIMESTAMP,
            "role": "admin",
            "search_count": 0
        })
        
        print(f"Admin user created with email: {email}")
        return True
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Initialize Firebase for Bibliometric Web App")
    parser.add_argument("--admin-email", required=True, help="Email for the admin user")
    parser.add_argument("--admin-password", required=True, help="Password for the admin user")
    parser.add_argument("--admin-name", required=True, help="Display name for the admin user")
    
    args = parser.parse_args()
    
    print("Initializing Firebase...")
    if initialize_firebase():
        # Create collections
        if create_initial_collections():
            print("Collections created successfully")
        else:
            print("Failed to create collections")
            return
        
        # Store API keys
        if read_api_keys():
            print("API keys stored successfully")
        else:
            print("Failed to store API keys")
        
        # Create admin user
        if create_admin_user(args.admin_email, args.admin_password, args.admin_name):
            print("Admin user created successfully")
        else:
            print("Failed to create admin user")
    else:
        print("Failed to initialize Firebase")

if __name__ == "__main__":
    main()