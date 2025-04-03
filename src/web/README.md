# Bibliometric Web App - Streamlit Interface with Firebase Integration

This directory contains the Streamlit web interface for the Bibliometric Analysis Tool with Firebase integration for user management, authentication, and secure API key handling.

## Features

- **User Authentication**: Secure login and registration using Firebase Authentication
- **User Management**: Admin dashboard for managing users and permissions
- **API Key Management**: Centralized and secure storage of API keys
- **Search Interface**: User-friendly interface for configuring and running searches
- **Results Visualization**: Interactive charts and data visualization
- **Usage Tracking**: Comprehensive tracking of search and API usage

## Setup Instructions

### 1. Firebase Setup

1. **Create a Firebase Project**:
   - Go to the [Firebase Console](https://console.firebase.google.com/)
   - Create a new project
   - Enable Firebase Authentication
   - Create a Firestore database

2. **Set up Authentication**:
   - In the Firebase Console, navigate to Authentication
   - Enable Email/Password sign-in method
   - Optionally enable Google sign-in

3. **Set up Firestore Database**:
   - Create the following collections:
     - `users`
     - `api_keys`
     - `search_logs`
     - `api_usage`

4. **Generate Service Account Key**:
   - In the Firebase Console, go to Project Settings > Service Accounts
   - Click "Generate New Private Key"
   - Save the JSON file as `firebase_credentials.json` in the `secrets` directory

### 2. Installation

1. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys**:
   - Create `anthropic-apikey` in the `secrets` directory with your Anthropic API key
   - Create `sciencedirect_apikey.txt` in the `secrets` directory with your Science Direct API key

### 3. Running the Application

1. **Start the Streamlit app**:
   ```bash
   streamlit run src/web/streamlit_app.py
   ```

2. **First-time setup**:
   - When first accessing the app, you'll need to register a user
   - The first user is automatically assigned admin privileges
   - Use the admin dashboard to manage other users

## Firestore Data Structure

### Collections

1. **users**
   - Document ID: `<user_id>`
   - Fields:
     - `email`: string
     - `display_name`: string
     - `created_at`: timestamp
     - `role`: string ('user' or 'admin')
     - `search_count`: number
     - `last_search`: timestamp

2. **api_keys**
   - Document ID: Service name (e.g., 'anthropic', 'sciencedirect')
   - Fields:
     - `key`: string
     - `updated_at`: timestamp
     - `updated_by`: string (user_id)

3. **search_logs**
   - Document ID: auto-generated
   - Fields:
     - `user_id`: string
     - `params`: map (search parameters)
     - `timestamp`: timestamp

4. **api_usage**
   - Document ID: auto-generated
   - Fields:
     - `service`: string
     - `user_id`: string
     - `timestamp`: timestamp

## User Roles and Permissions

1. **User**
   - Can perform searches
   - Can view their own results
   - Can modify their profile

2. **Admin**
   - All user permissions
   - Can manage API keys
   - Can manage users
   - Can view system-wide statistics

## Troubleshooting

- **Firebase Authentication Issues**: Ensure your Firebase project is properly configured and the service account key is correct
- **API Key Issues**: Verify that the API keys in Firestore are correct
- **Streamlit Errors**: Check that all required packages are installed and that the Python version is 3.8+

## Security Considerations

- API keys are stored in Firestore, not in client-side code
- All API requests are logged for audit purposes
- User passwords are never stored in Firestore (handled by Firebase Authentication)
- Rate limiting is implemented to prevent API abuse

## Future Improvements

- Implement Firebase Storage for storing result files
- Add real-time collaboration features
- Implement OAuth 2.0 for more robust authentication
- Add export/import functionality for search configurations