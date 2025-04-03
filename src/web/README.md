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

For detailed instructions, see the [Firebase Setup Guide](../../docs/guides/firebase_setup.md).

### 2. Installation

1. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys**:
   - Create `anthropic-apikey` in the `secrets` directory with your Anthropic API key
   - Create `sciencedirect_apikey.txt` in the `secrets` directory with your Science Direct API key

3. **Initialize Firebase**:
   ```bash
   python src/web/init_firebase.py --admin-email your@email.com --admin-password your-password --admin-name "Your Name"
   ```

### 3. Running the Application

#### Locally

```bash
# Start the Streamlit app
streamlit run src/web/streamlit_app.py
```

#### Using Docker

```bash
# Navigate to the web directory
cd src/web

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Testing the Application

To test the application:

```bash
# Navigate to the tests directory
cd tests

# Run the test suite with Docker
docker-compose -f docker-compose.test.yml up
```

For more details on testing, see the [Testing Guide](../../tests/README.md).

### 5. Deploying to Streamlit Cloud

To deploy the application to Streamlit Cloud:

1. Create a Streamlit Cloud account at [streamlit.io](https://streamlit.io)
2. Connect your GitHub repository to Streamlit Cloud
3. Configure secrets in the Streamlit dashboard:
   - Add your Firebase credentials as a secret named `firebase_credentials`
   - Add any API keys as secrets
4. Deploy the application using `src/web/streamlit_app_cloud.py` as the main file

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
- **Docker Connection Issues**: Ensure Docker has proper network access and volumes are correctly mounted

## Security Considerations

- API keys are stored in Firestore, not in client-side code
- All API requests are logged for audit purposes
- User passwords are never stored in Firestore (handled by Firebase Authentication)
- Rate limiting is implemented to prevent API abuse
- Security rules in Firestore control access to collections

## Application Files

- `streamlit_app.py`: Main Streamlit application
- `streamlit_app_cloud.py`: Version adapted for Streamlit Cloud
- `init_firebase.py`: Firebase initialization script
- `Dockerfile`: Docker configuration
- `docker-compose.yml`: Docker Compose configuration