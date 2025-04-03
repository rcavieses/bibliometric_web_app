#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration file for pytest. Contains fixtures and setup for testing.
"""

import os
import sys
import json
import tempfile
import pytest
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Firebase Admin
@pytest.fixture
def mock_firebase_admin():
    """Mock Firebase Admin SDK for testing"""
    with patch('firebase_admin.initialize_app') as mock_init_app, \
         patch('firebase_admin.credentials.Certificate') as mock_cert, \
         patch('firebase_admin.firestore.client') as mock_firestore_client, \
         patch('firebase_admin.auth') as mock_auth:
        
        # Mock Firestore document reference
        mock_doc = MagicMock()
        mock_doc.get.return_value.to_dict.return_value = {
            'key': 'test-api-key',
            'updated_at': 'mock-timestamp',
            'updated_by': 'test-user-id'
        }
        mock_doc.set = MagicMock()
        mock_doc.update = MagicMock()
        
        # Mock Firestore collection reference
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc
        mock_collection.where.return_value.limit.return_value.stream.return_value = [mock_doc]
        
        # Mock Firestore client
        mock_db = MagicMock()
        mock_db.collection.return_value = mock_collection
        mock_firestore_client.return_value = mock_db
        
        # Mock auth user
        mock_user = MagicMock()
        mock_user.uid = 'test-user-id'
        mock_auth.create_user.return_value = mock_user
        
        yield {
            'init_app': mock_init_app,
            'cert': mock_cert,
            'db': mock_db,
            'auth': mock_auth
        }

@pytest.fixture(autouse=True)
def mock_firebase_admin_import():
    """Mock the firebase_admin module import"""
    firebase_admin_mock = MagicMock()
    firebase_admin_mock.credentials = MagicMock()
    firebase_admin_mock.initialize_app = MagicMock()
    firebase_admin_mock.firestore = MagicMock()
    firebase_admin_mock.auth = MagicMock()
    
    with patch.dict('sys.modules', {
        'firebase_admin': firebase_admin_mock,
        'firebase_admin.credentials': firebase_admin_mock.credentials,
        'firebase_admin.firestore': firebase_admin_mock.firestore,
        'firebase_admin.auth': firebase_admin_mock.auth
    }):
        yield firebase_admin_mock

@pytest.fixture
def test_config():
    """Create temporary files and configuration for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create domain CSV files
        domain1_path = os.path.join(temp_dir, "Domain1.csv")
        with open(domain1_path, 'w') as f:
            f.write("artificial intelligence\nmachine learning\ndeep learning")
        
        domain2_path = os.path.join(temp_dir, "Domain2.csv")
        with open(domain2_path, 'w') as f:
            f.write("fishery\naquaculture\nmarine resources")
        
        # Create questions file
        questions_path = os.path.join(temp_dir, "questions.json")
        questions = [
            {
                "text": "Is it an application of AI/ML/DL to fisheries/aquaculture/marine resources?",
                "response_format": "1 or 0",
                "field_name": "is_ai_fishery_application",
                "answer_type": "int",
                "default_value": 0
            }
        ]
        with open(questions_path, 'w') as f:
            json.dump(questions, f)
        
        # Create API key files
        anthropic_key_path = os.path.join(temp_dir, "anthropic-apikey")
        with open(anthropic_key_path, 'w') as f:
            f.write("test-anthropic-api-key")
        
        sciencedirect_key_path = os.path.join(temp_dir, "sciencedirect_apikey.txt")
        with open(sciencedirect_key_path, 'w') as f:
            f.write("test-sciencedirect-api-key")
        
        # Create output directories
        os.makedirs(os.path.join(temp_dir, "outputs"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "figures"), exist_ok=True)
        
        # Return test configuration
        yield {
            'temp_dir': temp_dir,
            'domain1_path': domain1_path,
            'domain2_path': domain2_path,
            'questions_path': questions_path,
            'anthropic_key_path': anthropic_key_path,
            'sciencedirect_key_path': sciencedirect_key_path,
            'outputs_dir': os.path.join(temp_dir, "outputs"),
            'figures_dir': os.path.join(temp_dir, "figures")
        }

@pytest.fixture
@patch('streamlit.text')
@patch('streamlit.title')
@patch('streamlit.header')
@patch('streamlit.subheader')
@patch('streamlit.markdown')
@patch('streamlit.write')
@patch('streamlit.button')
@patch('streamlit.form')
@patch('streamlit.selectbox')
@patch('streamlit.text_input')
@patch('streamlit.text_area')
@patch('streamlit.checkbox')
@patch('streamlit.expander')
@patch('streamlit.progress')
@patch('streamlit.empty')
@patch('streamlit.success')
@patch('streamlit.error')
@patch('streamlit.warning')
@patch('streamlit.info')
@patch('streamlit.download_button')
@patch('streamlit.sidebar')
@patch('streamlit.session_state', {})
def mock_streamlit(mock_session_state, mock_sidebar, mock_download, mock_info, 
                  mock_warning, mock_error, mock_success, mock_empty, mock_progress,
                  mock_expander, mock_checkbox, mock_text_area, mock_text_input,
                  mock_selectbox, mock_form, mock_button, mock_write, mock_markdown,
                  mock_subheader, mock_header, mock_title, mock_text):
    """Mock Streamlit for testing the web application"""
    # Configure mocks
    mock_button.return_value = True
    mock_form.return_value.__enter__.return_value = MagicMock()
    mock_form.return_value.__enter__.return_value.form_submit_button.return_value = True
    mock_text_input.return_value = "test-input"
    mock_text_area.return_value = "test-area"
    mock_selectbox.return_value = "test-option"
    mock_checkbox.return_value = True
    mock_expander.return_value.__enter__.return_value = MagicMock()
    mock_empty.return_value = MagicMock()
    mock_sidebar.return_value.__enter__.return_value = MagicMock()
    
    return {
        'text': mock_text,
        'title': mock_title,
        'header': mock_header,
        'subheader': mock_subheader,
        'markdown': mock_markdown,
        'write': mock_write,
        'button': mock_button,
        'form': mock_form,
        'selectbox': mock_selectbox,
        'text_input': mock_text_input,
        'text_area': mock_text_area,
        'checkbox': mock_checkbox,
        'expander': mock_expander,
        'progress': mock_progress,
        'empty': mock_empty,
        'success': mock_success,
        'error': mock_error,
        'warning': mock_warning,
        'info': mock_info,
        'download': mock_download,
        'sidebar': mock_sidebar
    }