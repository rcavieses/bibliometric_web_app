#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the Streamlit UI components in the web application.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))

# Import functions to test
from web.streamlit_app import (
    render_login_page,
    render_search_page,
    render_execution_page,
    render_results_page,
    render_profile_page,
    main
)

class TestStreamlitUI:
    """Tests for Streamlit UI components."""
    
    def test_render_login_page(self, mock_streamlit, mock_firebase_admin):
        """Test render_login_page function."""
        # Mock verify_user and signup_user
        with patch('web.streamlit_app.verify_user', return_value='test-user-id'), \
             patch('web.streamlit_app.signup_user', return_value='test-user-id'), \
             patch('streamlit.tabs') as mock_tabs, \
             patch('streamlit.session_state', {}):
            
            # Create mock tabs
            mock_tab1 = MagicMock()
            mock_tab2 = MagicMock()
            mock_tabs.return_value = [mock_tab1, mock_tab2]
            
            # Test successful login
            render_login_page()
            
            # Check that the title was set
            mock_streamlit['title'].assert_called_once()
            
            # Check that tabs were created for login and signup
            mock_tabs.assert_called_once()
    
    def test_render_search_page(self, mock_streamlit, mock_firebase_admin):
        """Test render_search_page function."""
        with patch('web.streamlit_app.log_search') as mock_log_search, \
             patch('web.streamlit_app.get_user_document') as mock_get_user_doc, \
             patch('web.streamlit_app.setup_pipeline_config') as mock_setup_config, \
             patch('streamlit.session_state', {'user_id': 'test-user-id'}):
            
            # Mock user document
            mock_user_doc = MagicMock()
            mock_user_doc.update = MagicMock()
            mock_get_user_doc.return_value = mock_user_doc
            
            # Mock form and form submit button
            mock_streamlit['form'].return_value.__enter__.return_value.form_submit_button.return_value = True
            
            # Test successful search form submission
            render_search_page()
            
            # Check that title was set and form was created
            mock_streamlit['title'].assert_called_once()
            mock_streamlit['form'].assert_called_once()
            
            # Check that functions were called for logging and setup
            mock_log_search.assert_called_once()
            mock_get_user_doc.assert_called_once_with('test-user-id')
            mock_setup_config.assert_called_once()
    
    def test_render_execution_page(self, mock_streamlit, mock_firebase_admin):
        """Test render_execution_page function."""
        with patch('web.streamlit_app.save_results_to_firebase') as mock_save_results, \
             patch('time.sleep'), \
             patch('streamlit.session_state', {
                'user_id': 'test-user-id',
                'search_params': {'max_results': 100, 'search_only': False},
                'pipeline_config': MagicMock()
             }):
            
            # Mock progress and status text
            mock_progress_bar = MagicMock()
            mock_status_text = MagicMock()
            mock_streamlit['progress'].return_value = mock_progress_bar
            mock_streamlit['empty'].return_value = mock_status_text
            
            # Test successful execution
            render_execution_page()
            
            # Check that the title was set
            mock_streamlit['title'].assert_called_once()
            
            # Check that progress bar and status text were used
            mock_streamlit['progress'].assert_called_once()
            mock_streamlit['empty'].assert_called_once()
            
            # Check that results were saved
            mock_save_results.assert_called_once()
    
    def test_render_results_page(self, mock_streamlit, mock_firebase_admin):
        """Test render_results_page function."""
        with patch('web.streamlit_app.get_user_results') as mock_get_results, \
             patch('pandas.DataFrame') as mock_df, \
             patch('streamlit.session_state', {'user_id': 'test-user-id'}):
            
            # Mock results
            mock_results = {
                'test_result': {
                    'timestamp': '2025-04-02',
                    'data': '{"test": "data"}'
                }
            }
            mock_get_results.return_value = mock_results
            
            # Mock DataFrame and charts
            mock_df.return_value = MagicMock()
            mock_streamlit['line_chart'] = MagicMock()
            mock_streamlit['bar_chart'] = MagicMock()
            mock_streamlit['pie_chart'] = MagicMock()
            
            # Mock tabs
            mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            with patch('streamlit.tabs', return_value=mock_tabs):
                # Test successful results rendering
                render_results_page()
                
                # Check that the title was set
                mock_streamlit['title'].assert_called_once()
                
                # Check that results were fetched
                mock_get_results.assert_called_once_with('test-user-id')
    
    def test_main(self, mock_streamlit, mock_firebase_admin):
        """Test main function."""
        with patch('web.streamlit_app.render_login_page') as mock_render_login, \
             patch('web.streamlit_app.render_search_page') as mock_render_search, \
             patch('streamlit.set_page_config') as mock_set_page_config, \
             patch('streamlit.session_state', {}):
            
            # Test unauthenticated state
            main()
            
            # Check that page config was set
            mock_set_page_config.assert_called_once()
            
            # Check that login page was rendered for unauthenticated user
            mock_render_login.assert_called_once()
            mock_render_search.assert_not_called()
        
        # Test authenticated state
        with patch('web.streamlit_app.render_login_page') as mock_render_login, \
             patch('web.streamlit_app.render_search_page') as mock_render_search, \
             patch('web.streamlit_app.get_user_document') as mock_get_user_doc, \
             patch('streamlit.set_page_config') as mock_set_page_config, \
             patch('streamlit.session_state', {
                'authenticated': True,
                'user_id': 'test-user-id',
                'page': 'search'
             }):
            
            # Mock user document
            mock_user_doc = MagicMock()
            mock_user_doc.get.return_value.to_dict.return_value = {
                'display_name': 'Test User'
            }
            mock_get_user_doc.return_value = mock_user_doc
            
            # Mock sidebar
            mock_streamlit['sidebar'].return_value.__enter__.return_value = MagicMock()
            
            # Test authenticated state with search page
            main()
            
            # Check that login page was not rendered for authenticated user
            mock_render_login.assert_not_called()
            # Check that search page was rendered
            mock_render_search.assert_called_once()