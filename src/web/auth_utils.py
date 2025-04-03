#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Firebase authentication utilities for Bibliometric Web App.
Handles user authentication, verification, and session management.
"""

import os
import json
import requests
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime, timedelta

# Constants
FIREBASE_CREDENTIALS_PATH = os.path.join("secrets", "firebase_credentials.json")
FIREBASE_WEB_API_KEY_PATH = os.path.join("secrets", "firebase_web_api_key.txt")

def get_firebase_web_api_key():
    """Get Firebase Web API Key from various sources"""
    # First try to get it from Streamlit secrets
    try:
        if 'firebase_web' in st.secrets and 'api_key' in st.secrets['firebase_web']:
            return st.secrets['firebase_web']['api_key']
    except (AttributeError, KeyError):
        pass
    
    # Then try to get it from the environment
    env_key = os.environ.get("FIREBASE_WEB_API_KEY")
    if env_key:
        return env_key
    
    # Then try to get it from the dedicated file
    if os.path.exists(FIREBASE_WEB_API_KEY_PATH):
        with open(FIREBASE_WEB_API_KEY_PATH, 'r') as f:
            key = f.read().strip()
            if key and key != "YOUR_FIREBASE_WEB_API_KEY_HERE":
                return key
    
    # Finally, try to extract it from the Firebase credentials file
    if os.path.exists(FIREBASE_CREDENTIALS_PATH):
        try:
            with open(FIREBASE_CREDENTIALS_PATH, 'r') as f:
                creds = json.load(f)
                
                # The API key might be in different places depending on the Firebase version
                if 'apiKey' in creds:
                    return creds['apiKey']
                elif 'api_key' in creds:
                    return creds['api_key']
                
                # Sometimes it's nested under 'client' or 'projects'
                for field in ['client', 'projects']:
                    if field in creds and isinstance(creds[field], list) and len(creds[field]) > 0:
                        if 'apiKey' in creds[field][0]:
                            return creds[field][0]['apiKey']
                        elif 'api_key' in creds[field][0]:
                            return creds[field][0]['api_key']
                
                # For newer Firebase format
                project_id = creds.get('project_id')
                if project_id:
                    # Save a placeholder API key that will be updated later
                    with open(FIREBASE_WEB_API_KEY_PATH, 'w') as f:
                        f.write(f"PLACEHOLDER_FOR_{project_id}")
                    st.info(f"Created placeholder for Firebase Web API Key. You'll need to update it with the actual key.")
        except Exception as e:
            st.error(f"Error extracting API key from credentials file: {str(e)}")
    
    return None

@st.cache_resource
def initialize_firebase_admin():
    """Initialize Firebase Admin SDK if not already initialized"""
    if not firebase_admin._apps:
        # First try to use Streamlit secrets
        try:
            if 'firebase_credentials' in st.secrets:
                cred_dict = st.secrets['firebase_credentials']
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                    json.dump(cred_dict, f)
                    temp_cred_path = f.name
                try:
                    cred = credentials.Certificate(temp_cred_path)
                    firebase_admin.initialize_app(cred)
                    # Clean up temporary file
                    os.unlink(temp_cred_path)
                    return True
                except Exception as e:
                    st.error(f"Error initializing Firebase with Streamlit secrets: {str(e)}")
                    if os.path.exists(temp_cred_path):
                        os.unlink(temp_cred_path)
        except (AttributeError, KeyError, Exception) as e:
            pass
            
        # Fall back to credentials file in secrets directory
        cred_path = os.path.join("secrets", "firebase_credentials.json")
        if os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                return True
            except Exception as e:
                st.error(f"Error initializing Firebase: {str(e)}")
                st.error("Make sure your firebase_credentials.json file is properly formatted and has the correct permissions.")
                return False
        else:
            st.error("Firebase credentials not found in Streamlit secrets or local file.")
            st.markdown("""
            ### Firebase Setup Instructions:
            
            1. Go to your [Firebase Console](https://console.firebase.google.com/)
            2. Select your project
            3. Click the gear icon ⚙️ (Project Settings)
            4. Go to "Service accounts" tab
            5. Click "Generate new private key"
            6. Save the JSON file as `firebase_credentials.json` in the `secrets` directory or add to Streamlit secrets
            """)
            return False
    return True

def get_firestore_db():
    """Get Firestore database instance"""
    if initialize_firebase_admin():
        return firestore.client()
    return None

def signup_with_email_password(email, password, display_name):
    """Create a new user using Firebase Authentication REST API"""
    # First, ensure Firebase Admin is initialized for creating the user document
    if not initialize_firebase_admin():
        return None, "Firebase initialization failed"
    
    # Get the Firebase Web API key
    api_key = get_firebase_web_api_key()
    if not api_key:
        return None, "Firebase Web API key not found"
    
    # Call Firebase Auth REST API to create user
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if 'error' in data:
            return None, data['error']['message']
        
        # User created successfully, now create Firestore document
        user_id = data['localId']
        id_token = data['idToken']
        refresh_token = data['refreshToken']
        
        # Create user document in Firestore
        db = get_firestore_db()
        if db:
            # Update Firebase Auth display name using Admin SDK
            auth.update_user(
                user_id,
                display_name=display_name
            )
            
            # Create user document
            db.collection('users').document(user_id).set({
                'email': email,
                'display_name': display_name,
                'created_at': firestore.SERVER_TIMESTAMP,
                'role': 'user',  # Default role
                'search_count': 0
            })
            
            # First user gets admin role
            check_and_set_first_user_as_admin(user_id)
            
            # Store tokens in session state
            st.session_state["user_id"] = user_id
            st.session_state["email"] = email
            st.session_state["display_name"] = display_name
            st.session_state["id_token"] = id_token
            st.session_state["refresh_token"] = refresh_token
            st.session_state["token_expiry"] = datetime.now() + timedelta(hours=1)
            
            return user_id, "Account created successfully"
        else:
            return None, "Failed to connect to Firestore"
    
    except Exception as e:
        return None, f"Error creating user: {str(e)}"

def sign_in_with_email_password(email, password):
    """Sign in a user using Firebase Authentication REST API"""
    # Get the Firebase Web API key
    api_key = get_firebase_web_api_key()
    if not api_key:
        return None, "Firebase Web API key not found"
    
    # Call Firebase Auth REST API to sign in user
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if 'error' in data:
            return None, data['error']['message']
        
        # User signed in successfully
        user_id = data['localId']
        id_token = data['idToken']
        refresh_token = data['refreshToken']
        
        # Initialize Firebase Admin if not already
        initialize_firebase_admin()
        
        # Get user data from Firestore
        db = get_firestore_db()
        if db:
            user_doc = db.collection('users').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                display_name = user_data.get('display_name', '')
                
                # Store in session state
                st.session_state["user_id"] = user_id
                st.session_state["email"] = email
                st.session_state["display_name"] = display_name
                st.session_state["id_token"] = id_token
                st.session_state["refresh_token"] = refresh_token
                st.session_state["token_expiry"] = datetime.now() + timedelta(hours=1)
                st.session_state["authenticated"] = True
                
                # Update last login timestamp
                db.collection('users').document(user_id).update({
                    'last_login': firestore.SERVER_TIMESTAMP
                })
                
                return user_id, "Login successful"
            else:
                # Create user document if it doesn't exist (might happen if user was created outside the app)
                user_info = auth.get_user(user_id)
                db.collection('users').document(user_id).set({
                    'email': email,
                    'display_name': user_info.display_name or email.split('@')[0],
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'role': 'user',
                    'search_count': 0,
                    'last_login': firestore.SERVER_TIMESTAMP
                })
                
                # Check if this is the first user
                check_and_set_first_user_as_admin(user_id)
                
                return user_id, "Login successful"
        else:
            return None, "Failed to connect to Firestore"
    
    except Exception as e:
        return None, f"Error signing in: {str(e)}"

def check_and_set_first_user_as_admin(user_id):
    """Check if this is the first user and set as admin if so"""
    db = get_firestore_db()
    if db:
        # Count all users
        users = list(db.collection('users').limit(2).stream())
        if len(users) == 1:
            # If only one user exists, make them admin
            db.collection('users').document(user_id).update({
                'role': 'admin'
            })

def refresh_auth_token():
    """Refresh the authentication token"""
    if "refresh_token" not in st.session_state:
        return False
    
    api_key = get_firebase_web_api_key()
    if not api_key:
        return False
    
    refresh_token = st.session_state["refresh_token"]
    
    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if 'error' in data:
            st.error(f"Error refreshing token: {data['error']['message']}")
            return False
        
        # Update tokens in session state
        st.session_state["id_token"] = data['id_token']
        st.session_state["refresh_token"] = data['refresh_token']
        st.session_state["token_expiry"] = datetime.now() + timedelta(seconds=int(data['expires_in']))
        
        return True
    except Exception as e:
        st.error(f"Error refreshing token: {str(e)}")
        return False

def is_token_expired():
    """Check if the current token is expired"""
    if "token_expiry" not in st.session_state:
        return True
    
    return datetime.now() > st.session_state["token_expiry"]

def ensure_auth_valid():
    """Ensure authentication is valid, refreshing if needed"""
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        return False
    
    if is_token_expired():
        return refresh_auth_token()
    
    return True

def sign_out():
    """Sign out the current user"""
    for key in ["user_id", "email", "display_name", "id_token", 
                "refresh_token", "token_expiry", "authenticated"]:
        if key in st.session_state:
            del st.session_state[key]
    
    return True

def get_user_role():
    """Get the current user's role"""
    if not ensure_auth_valid() or "user_id" not in st.session_state:
        return None
    
    db = get_firestore_db()
    if db:
        user_doc = db.collection('users').document(st.session_state["user_id"]).get()
        if user_doc.exists:
            return user_doc.to_dict().get('role')
    
    return None

def is_admin():
    """Check if the current user is an admin"""
    return get_user_role() == 'admin'

def get_user_document(user_id=None):
    """Get user document from Firestore"""
    if user_id is None:
        if "user_id" not in st.session_state:
            return None
        user_id = st.session_state["user_id"]
    
    db = get_firestore_db()
    if db:
        return db.collection('users').document(user_id)
    
    return None

def reset_password(email):
    """Send password reset email"""
    api_key = get_firebase_web_api_key()
    if not api_key:
        return False, "Firebase Web API key not found"
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if 'error' in data:
            return False, data['error']['message']
        
        return True, "Password reset email sent"
    except Exception as e:
        return False, f"Error sending password reset email: {str(e)}"