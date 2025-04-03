# Firebase Setup Guide

This guide will walk you through the process of setting up Firebase for the Bibliometric Web App.

## Prerequisites

- A Google account
- Basic familiarity with Firebase and Google Cloud Platform

## Step 1: Create a Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click on "Add project"
3. Enter a project name (e.g., "bibliometric-web-app")
4. Choose whether to enable Google Analytics (recommended)
5. Accept the terms and conditions
6. Click "Create project"
7. Wait for the project to be created, then click "Continue"

## Step 2: Set Up Authentication

1. In the Firebase Console, select your project
2. From the left sidebar, click on "Authentication"
3. Click on "Get started"
4. Select the "Sign-in method" tab
5. Enable the following providers:
   - Email/Password: Click on it, toggle the "Enable" switch, and click "Save"
   - Google: Click on it, toggle the "Enable" switch, add your support email, and click "Save"

## Step 3: Create a Firestore Database

1. From the left sidebar, click on "Firestore Database"
2. Click "Create database"
3. Choose "Start in test mode" for development (you'll change this to production rules later)
4. Select a region closest to your users
5. Click "Enable"

## Step 4: Set Up Collections

The application requires the following collections in Firestore:

1. `users`: Stores user information
2. `api_keys`: Stores API keys for external services
3. `search_logs`: Tracks search activities
4. `api_usage`: Monitors API usage

You don't need to create these collections manually. They will be created automatically when the application first uses them.

## Step 5: Generate Service Account Key and Web API Key

1. **Service Account Key:**
   - In the Firebase Console, go to Project Settings (the gear icon in the top left)
   - Select the "Service accounts" tab
   - Click on "Generate new private key" under the Firebase Admin SDK section
   - Save the downloaded JSON file as `firebase_credentials.json` in the `secrets` directory of the project

2. **Web API Key:**
   - In Project Settings, go to the "General" tab
   - Look for "Web API Key" in the project settings
   - Copy this key and save it in a file called `firebase_web_api_key.txt` in the `secrets` directory

The Web API Key is needed for client-side authentication functions like sign-in and sign-up through the REST API.

## Step 6: Set Up Security Rules

For production use, you should set up proper security rules for Firestore:

1. From the left sidebar, click on "Firestore Database"
2. Select the "Rules" tab
3. Replace the default rules with the following:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read their own document, but not others'
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Only admins can read/write API keys
    match /api_keys/{apiKey} {
      allow read: if request.auth != null && 
                   get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
      allow write: if request.auth != null && 
                    get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    // Users can read their own search logs and api usage
    match /search_logs/{logId} {
      allow read: if request.auth != null && resource.data.user_id == request.auth.uid;
      allow write: if request.auth != null;
    }
    
    match /api_usage/{usageId} {
      allow read: if request.auth != null && resource.data.user_id == request.auth.uid;
      allow write: if request.auth != null;
    }
    
    // User results collections
    match /users/{userId}/results/{resultId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

4. Click "Publish" to apply the rules

## Step 7: Initialize Firebase in Your Application

After setting up Firebase, you need to initialize it in your application:

1. Make sure `firebase_credentials.json` is in the `secrets` directory
2. Run the initialization script:

```bash
python src/web/init_firebase.py --admin-email your@email.com --admin-password your-password --admin-name "Your Name"
```

This will:
- Initialize Firebase
- Create the required collections
- Set up an admin user
- Store API keys in Firebase if they are available in the `secrets` directory

## Step 8: Run the Application

Now you can run the application with Firebase integration:

```bash
streamlit run src/web/streamlit_app.py
```

Or using Docker:

```bash
cd src/web
docker-compose up -d
```

## Step 9: Testing the Application

To test your Firebase integration, follow these steps:

1. Run the test suite:

```bash
cd tests
docker-compose -f docker-compose.test.yml up
```

This will:
- Build a Docker image using the test configuration
- Run the test suite against your Firebase setup
- Verify all Firebase-related functionality works correctly

2. Check the test results to ensure that:
   - Authentication works properly
   - Database operations succeed
   - API key management functions correctly

## Step 10: Deploying to Streamlit Cloud

To deploy your application to Streamlit Cloud:

1. Create a Streamlit account at [streamlit.io](https://streamlit.io)
2. Connect your GitHub repository to Streamlit
3. Configure secrets in the Streamlit dashboard:
   - Add your `firebase_credentials.json` content as a secret
   - Add any other API keys needed by your application
4. Deploy your application by specifying `src/web/streamlit_app.py` as the main file

Note: When deploying to Streamlit Cloud, you'll need to modify the Firebase initialization code to read credentials from Streamlit secrets instead of a local file.

## Troubleshooting

### Authentication Issues

- Make sure your `firebase_credentials.json` file is correct and contains all the necessary information
- Check that you've enabled the authentication methods in the Firebase Console
- Make sure your API key in the Firebase Console is not restricted to specific domains or IPs

### Firestore Access Issues

- Check your security rules in the Firebase Console
- Make sure you're signed in and have the correct permissions
- Look for errors in the application logs
- Check that the user exists in the `users` collection with the correct role

### API Key Issues

- Make sure your API keys are correctly stored in the `api_keys` collection
- Check that the user making the request has admin privileges

### Streamlit Cloud Deployment Issues

- Verify all secrets are properly configured in the Streamlit dashboard
- Check the Streamlit logs for any Firebase initialization errors
- Ensure your Firebase project allows requests from the Streamlit Cloud domain