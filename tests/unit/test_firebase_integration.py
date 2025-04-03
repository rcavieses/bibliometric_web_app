#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the Firebase integration in the Streamlit web application.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))

# Import functions to test
from web.streamlit_app import (
    initialize_firebase,
    get_firestore_db,
    get_user_document,
    get_api_key,
    log_api_usage,
    log_search,
    save_results_to_firebase,
    get_user_results,
    signup_user,
    verify_user
)

class TestFirebaseIntegration:
    """Tests for Firebase integration functions."""
    
    def test_initialize_firebase(self, mock_firebase_admin):
        """Test initialize_firebase function."""
        with patch('os.path.exists', return_value=True):
            # Test successful initialization
            result = initialize_firebase()
            assert result is True
            mock_firebase_admin['cert'].assert_called_once()
            mock_firebase_admin['init_app'].assert_called_once()
        
        with patch('os.path.exists', return_value=False):
            # Test missing credentials file
            with patch('streamlit.error') as mock_error:
                result = initialize_firebase()
                assert result is False
                mock_error.assert_called_once()
    
    def test_get_firestore_db(self, mock_firebase_admin):
        """Test get_firestore_db function."""
        with patch('web.streamlit_app.initialize_firebase', return_value=True):
            # Test successful connection
            db = get_firestore_db()
            assert db is not None
            assert db == mock_firebase_admin['db']
        
        with patch('web.streamlit_app.initialize_firebase', return_value=False):
            # Test failed initialization
            db = get_firestore_db()
            assert db is None
    
    def test_get_user_document(self, mock_firebase_admin):
        """Test get_user_document function."""
        with patch('web.streamlit_app.get_firestore_db', return_value=mock_firebase_admin['db']):
            # Test getting a user document
            user_doc = get_user_document('test-user-id')
            assert user_doc is not None
            mock_firebase_admin['db'].collection.assert_called_with('users')
            mock_firebase_admin['db'].collection().document.assert_called_with('test-user-id')
        
        with patch('web.streamlit_app.get_firestore_db', return_value=None):
            # Test with no database connection
            user_doc = get_user_document('test-user-id')
            assert user_doc is None
    
    def test_get_api_key(self, mock_firebase_admin):
        """Test get_api_key function."""
        with patch('web.streamlit_app.get_firestore_db', return_value=mock_firebase_admin['db']), \
             patch('streamlit.session_state', {'user_id': 'test-user-id'}):
            # Test getting an API key
            api_key = get_api_key('anthropic')
            assert api_key == 'test-api-key'
            mock_firebase_admin['db'].collection.assert_called_with('api_keys')
            mock_firebase_admin['db'].collection().document.assert_called_with('anthropic')
        
        with patch('streamlit.session_state', {}):
            # Test with no user in session
            api_key = get_api_key('anthropic')
            assert api_key is None
    
    def test_log_api_usage(self, mock_firebase_admin):
        """Test log_api_usage function."""
        with patch('web.streamlit_app.get_firestore_db', return_value=mock_firebase_admin['db']):
            # Test logging API usage
            log_api_usage('anthropic', 'test-user-id')
            mock_firebase_admin['db'].collection.assert_called_with('api_usage')
            mock_firebase_admin['db'].collection().document.assert_called_once()
            mock_firebase_admin['db'].collection().document().set.assert_called_once()
    
    def test_signup_user(self, mock_firebase_admin):
        """Test signup_user function."""
        with patch('web.streamlit_app.initialize_firebase', return_value=True), \
             patch('web.streamlit_app.get_firestore_db', return_value=mock_firebase_admin['db']):
            # Test successful user creation
            user_id = signup_user('test@example.com', 'password', 'Test User')
            assert user_id == 'test-user-id'
            mock_firebase_admin['auth'].create_user.assert_called_with(
                email='test@example.com',
                password='password',
                display_name='Test User'
            )
            mock_firebase_admin['db'].collection().document().set.assert_called_once()
        
        with patch('web.streamlit_app.initialize_firebase', return_value=False):
            # Test with failed initialization
            user_id = signup_user('test@example.com', 'password', 'Test User')
            assert user_id is None
        
        with patch('web.streamlit_app.initialize_firebase', return_value=True), \
             patch('firebase_admin.auth.create_user', side_effect=Exception('Authentication error')), \
             patch('streamlit.error') as mock_error:
            # Test with authentication error
            user_id = signup_user('test@example.com', 'password', 'Test User')
            assert user_id is None
            mock_error.assert_called_once()
    
    def test_verify_user(self, mock_firebase_admin):
        """Test verify_user function."""
        # For this example, we'll simulate a very simple verification since real implementation
        # would use Firebase Auth REST API
        with patch('web.streamlit_app.get_firestore_db', return_value=mock_firebase_admin['db']):
            # Test successful verification (simulated for demo purposes)
            user_id = verify_user('test@example.com', 'password')
            assert user_id == 'test-user-id'
            mock_firebase_admin['db'].collection.assert_called_with('users')
            mock_firebase_admin['db'].collection().where.assert_called_with('email', '==', 'test@example.com')
        
        with patch('web.streamlit_app.get_firestore_db', return_value=None):
            # Test with no database connection
            user_id = verify_user('test@example.com', 'password')
            assert user_id is None