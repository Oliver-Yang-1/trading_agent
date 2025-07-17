"""
Test suite for Algogene documentation reader tool.
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.tools.algogene_docs_reader import AlgogeneDocsReader


class TestAlgogeneDocsReader(unittest.TestCase):
    """Test cases for AlgogeneDocsReader tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = AlgogeneDocsReader()
    
    def test_tool_initialization(self):
        """Test that tool initializes correctly."""
        self.assertEqual(self.reader.name, "algogene_docs_reader")
        self.assertIsNotNone(self.reader.description)
        self.assertIsNotNone(self.reader.docs_dir)
    
    def test_get_doc_files(self):
        """Test getting list of documentation files."""
        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test markdown files
            test_files = ['01-test.md', '02-test.md', 'README.md', 'not-md.txt']
            for file in test_files:
                with open(os.path.join(temp_dir, file), 'w') as f:
                    f.write("Test content")
            
            # Patch the docs_dir to use our temp directory
            with patch.object(self.reader, 'docs_dir', temp_dir):
                files = self.reader._get_doc_files()
                
                # Should only return .md files, sorted
                expected_files = ['01-test.md', '02-test.md', 'README.md']
                self.assertEqual(files, expected_files)
    
    def test_read_existing_file(self):
        """Test reading an existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = 'test.md'
            test_content = "# Test Content\nThis is a test file."
            with open(os.path.join(temp_dir, test_file), 'w') as f:
                f.write(test_content)
            
            # Patch the docs_dir
            with patch.object(self.reader, 'docs_dir', temp_dir):
                content = self.reader._read_file(test_file)
                self.assertEqual(content, test_content)
    
    def test_read_nonexistent_file(self):
        """Test reading a non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(self.reader, 'docs_dir', temp_dir):
                content = self.reader._read_file('nonexistent.md')
                self.assertIn("not found", content)
    
    def test_search_in_files(self):
        """Test searching for content in files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files with different content
            files_content = {
                'api.md': "API Functions\nThis file contains API documentation\nOrder placement is important",
                'overview.md': "Overview\nGeneral information about the platform",
                'examples.md': "Examples\nCode examples and API usage"
            }
            
            for filename, content in files_content.items():
                with open(os.path.join(temp_dir, filename), 'w') as f:
                    f.write(content)
            
            # Patch the docs_dir and doc_files
            with patch.object(self.reader, 'docs_dir', temp_dir):
                with patch.object(self.reader, 'doc_files', list(files_content.keys())):
                    results = self.reader._search_in_files('API')
                    
                    # Should find matches in api.md and examples.md
                    self.assertIn('api.md', results)
                    self.assertIn('examples.md', results)
                    self.assertNotIn('overview.md', results)
    
    def test_format_search_results(self):
        """Test formatting search results."""
        test_results = {
            'api.md': 'API Functions\nOrder placement',
            'examples.md': 'Code examples\nAPI usage'
        }
        
        formatted = self.reader._format_search_results(test_results)
        
        self.assertIn('# Algogene Documentation Search Results', formatted)
        self.assertIn('## From api.md:', formatted)
        self.assertIn('## From examples.md:', formatted)
        self.assertIn('API Functions', formatted)
    
    def test_format_empty_results(self):
        """Test formatting empty search results."""
        formatted = self.reader._format_search_results({})
        self.assertIn('No relevant documentation found', formatted)
    
    def test_get_file_suggestions(self):
        """Test getting file suggestions based on keywords."""
        # Test various keyword suggestions
        suggestions = self.reader._get_file_suggestions('API functions')
        self.assertIn('07-api-functions.md', suggestions)
        
        suggestions = self.reader._get_file_suggestions('overview')
        self.assertIn('01-overview.md', suggestions)
        
        suggestions = self.reader._get_file_suggestions('backtest')
        self.assertIn('08-backtest-history.md', suggestions)
    
    def test_run_with_specific_file(self):
        """Test running the tool with a specific file request."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_content = "# Test File\nThis is test content."
            with open(os.path.join(temp_dir, 'test.md'), 'w') as f:
                f.write(test_content)
            
            # Patch the necessary attributes
            with patch.object(self.reader, 'docs_dir', temp_dir):
                with patch.object(self.reader, 'doc_files', ['test.md']):
                    result = self.reader._run(query='test', specific_file='test.md')
                    
                    self.assertIn('# Content from test.md', result)
                    self.assertIn(test_content, result)
    
    def test_run_with_search_query(self):
        """Test running the tool with a search query."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = {
                'api.md': 'API Functions\nOrder placement documentation',
                'overview.md': 'Overview\nGeneral platform information'
            }
            
            for filename, content in test_files.items():
                with open(os.path.join(temp_dir, filename), 'w') as f:
                    f.write(content)
            
            # Patch the necessary attributes
            with patch.object(self.reader, 'docs_dir', temp_dir):
                with patch.object(self.reader, 'doc_files', list(test_files.keys())):
                    result = self.reader._run(query='API')
                    
                    self.assertIn('# Algogene Documentation Search Results', result)
                    self.assertIn('api.md', result)
    
    def test_run_with_no_matches(self):
        """Test running the tool when no matches are found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file without matching content
            with open(os.path.join(temp_dir, 'test.md'), 'w') as f:
                f.write("No matching content here")
            
            # Patch the necessary attributes
            with patch.object(self.reader, 'docs_dir', temp_dir):
                with patch.object(self.reader, 'doc_files', ['test.md']):
                    result = self.reader._run(query='nonexistent')
                    
                    # Should provide suggestions or available files
                    self.assertTrue(
                        'Available documentation files' in result or
                        'You might want to check' in result
                    )
    
    def test_error_handling(self):
        """Test error handling in the tool."""
        # Test with non-existent docs directory
        with patch.object(self.reader, 'docs_dir', '/nonexistent/path'):
            files = self.reader._get_doc_files()
            self.assertEqual(files, [])
    
    def test_tool_integration(self):
        """Test the tool as it would be used by the agent."""
        # This is an integration test that uses the actual tool structure
        if os.path.exists(self.reader.docs_dir):
            # Test with actual documentation if available
            result = self.reader._run(query='API')
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
        else:
            # Skip if documentation directory doesn't exist
            self.skipTest("Documentation directory not found")


if __name__ == '__main__':
    unittest.main()