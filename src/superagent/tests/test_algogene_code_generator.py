"""
Test suite for Algogene code generator tool.
"""

import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.tools.algogene_code_generator import AlgogeneCodeGenerator


class TestAlgogeneCodeGenerator(unittest.TestCase):
    """Test cases for AlgogeneCodeGenerator tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = AlgogeneCodeGenerator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_tool_initialization(self):
        """Test that tool initializes correctly."""
        self.assertEqual(self.generator.name, "algogene_code_generator")
        self.assertIsNotNone(self.generator.description)
        self.assertIsNotNone(self.generator.base_dir)
        self.assertIsNotNone(self.generator.strategies_dir)
        self.assertIsNotNone(self.generator.utils_dir)
    
    def test_ensure_directories(self):
        """Test directory creation."""
        with patch.object(self.generator, 'base_dir', self.temp_dir):
            with patch.object(self.generator, 'strategies_dir', os.path.join(self.temp_dir, 'strategies')):
                with patch.object(self.generator, 'utils_dir', os.path.join(self.temp_dir, 'utils')):
                    self.generator._ensure_directories()
                    
                    # Check that directories were created
                    self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'strategies')))
                    self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'utils')))
                    self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'strategies', 'market_making')))
                    self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'strategies', 'trend_following')))
    
    def test_generate_market_making_strategy(self):
        """Test market making strategy generation."""
        parameters = {
            'spread': 0.02,
            'volume': 0.05,
            'trade_interval_hours': 12
        }
        
        code = self.generator._generate_market_making_strategy(
            'test_market_making',
            'Test market making strategy',
            parameters
        )
        
        # Check that generated code contains expected elements
        self.assertIn('class AlgoEvent:', code)
        self.assertIn('def __init__(self):', code)
        self.assertIn('def on_marketdatafeed(self, md, ab):', code)
        self.assertIn('self.spread = 0.02', code)
        self.assertIn('self.volume = 0.05', code)
        self.assertIn('self.trade_interval_hours = 12', code)
    
    def test_generate_moving_average_strategy(self):
        """Test moving average strategy generation."""
        parameters = {
            'short_window': 5,
            'long_window': 20,
            'volume': 0.1
        }
        
        code = self.generator._generate_moving_average_strategy(
            'test_moving_average',
            'Test moving average strategy',
            parameters
        )
        
        # Check that generated code contains expected elements
        self.assertIn('class AlgoEvent:', code)
        self.assertIn('self.short_window = 5', code)
        self.assertIn('self.long_window = 20', code)
        self.assertIn('self.volume = 0.1', code)
        self.assertIn('collections.deque', code)
    
    def test_generate_custom_strategy(self):
        """Test custom strategy generation."""
        parameters = {'volume': 0.03}
        
        code = self.generator._generate_custom_strategy(
            'test_custom',
            'Test custom strategy',
            parameters
        )
        
        # Check that generated code contains expected elements
        self.assertIn('class AlgoEvent:', code)
        self.assertIn('self.volume = 0.03', code)
        self.assertIn('TODO: Implement your trading strategy logic here', code)
    
    def test_generate_code_by_type(self):
        """Test code generation based on strategy type."""
        parameters = {'volume': 0.01}
        
        # Test market making
        code = self.generator._generate_code(
            'test_strategy', 'market_making', 'Test description', parameters
        )
        self.assertIn('place_limit_order', code)
        
        # Test trend following
        code = self.generator._generate_code(
            'test_strategy', 'trend_following', 'Test description', parameters
        )
        self.assertIn('moving averages', code)
        
        # Test custom
        code = self.generator._generate_code(
            'test_strategy', 'custom', 'Test description', parameters
        )
        self.assertIn('TODO: Implement', code)
    
    def test_save_code(self):
        """Test saving generated code to file."""
        test_code = "# Test generated code\nprint('Hello, World!')"
        
        with patch.object(self.generator, 'strategies_dir', os.path.join(self.temp_dir, 'strategies')):
            # Create the strategies directory
            os.makedirs(os.path.join(self.temp_dir, 'strategies', 'market_making'))
            
            # Save the code
            filepath = self.generator._save_code(test_code, 'test_strategy', 'market_making')
            
            # Check that file was created
            self.assertTrue(os.path.exists(filepath))
            
            # Check that content was saved correctly
            with open(filepath, 'r') as f:
                saved_content = f.read()
            self.assertEqual(saved_content, test_code)
            
            # Check that filename contains strategy name and timestamp
            filename = os.path.basename(filepath)
            self.assertIn('test_strategy', filename)
            self.assertTrue(filename.endswith('.py'))
    
    def test_create_readme(self):
        """Test README creation."""
        with patch.object(self.generator, 'strategies_dir', os.path.join(self.temp_dir, 'strategies')):
            # Create test directory and file
            strategy_dir = os.path.join(self.temp_dir, 'strategies', 'market_making')
            os.makedirs(strategy_dir)
            test_file = os.path.join(strategy_dir, 'test_strategy.py')
            with open(test_file, 'w') as f:
                f.write("# Test code")
            
            # Create README
            self.generator._create_readme(
                'test_strategy',
                'market_making',
                'Test strategy description',
                test_file
            )
            
            # Check that README was created
            readme_path = os.path.join(strategy_dir, 'test_strategy_README.md')
            self.assertTrue(os.path.exists(readme_path))
            
            # Check README content
            with open(readme_path, 'r') as f:
                readme_content = f.read()
            self.assertIn('# test_strategy', readme_content)
            self.assertIn('market_making', readme_content)
            self.assertIn('Test strategy description', readme_content)
    
    def test_run_with_generated_code(self):
        """Test running the tool with code generation."""
        with patch.object(self.generator, 'base_dir', self.temp_dir):
            with patch.object(self.generator, 'strategies_dir', os.path.join(self.temp_dir, 'strategies')):
                with patch.object(self.generator, 'utils_dir', os.path.join(self.temp_dir, 'utils')):
                    # Ensure directories exist
                    self.generator._ensure_directories()
                    
                    # Run the tool
                    result = self.generator._run(
                        strategy_name='test_strategy',
                        strategy_type='market_making',
                        description='Test market making strategy',
                        parameters={'spread': 0.01, 'volume': 0.05}
                    )
                    
                    # Check that result indicates success
                    self.assertIn('generated successfully', result)
                    self.assertIn('test_strategy', result)
                    self.assertIn('market_making', result)
                    
                    # Check that file was actually created
                    market_making_dir = os.path.join(self.temp_dir, 'strategies', 'market_making')
                    files = os.listdir(market_making_dir)
                    py_files = [f for f in files if f.endswith('.py')]
                    self.assertGreater(len(py_files), 0)
    
    def test_run_with_provided_code(self):
        """Test running the tool with provided code content."""
        test_code = "# Custom provided code\nprint('Custom strategy')"
        
        with patch.object(self.generator, 'base_dir', self.temp_dir):
            with patch.object(self.generator, 'strategies_dir', os.path.join(self.temp_dir, 'strategies')):
                with patch.object(self.generator, 'utils_dir', os.path.join(self.temp_dir, 'utils')):
                    # Ensure directories exist
                    self.generator._ensure_directories()
                    
                    # Run the tool with provided code
                    result = self.generator._run(
                        strategy_name='custom_strategy',
                        strategy_type='custom',
                        description='Custom strategy with provided code',
                        code_content=test_code
                    )
                    
                    # Check that result indicates success
                    self.assertIn('saved successfully', result)
                    
                    # Check that file was created with correct content
                    custom_dir = os.path.join(self.temp_dir, 'strategies', 'custom')
                    files = os.listdir(custom_dir)
                    py_files = [f for f in files if f.endswith('.py')]
                    self.assertGreater(len(py_files), 0)
                    
                    # Check file content
                    with open(os.path.join(custom_dir, py_files[0]), 'r') as f:
                        saved_code = f.read()
                    self.assertEqual(saved_code, test_code)
    
    def test_error_handling(self):
        """Test error handling in the tool."""
        # Test with invalid parameters
        with patch.object(self.generator, '_save_code', side_effect=Exception("Test error")):
            result = self.generator._run(
                strategy_name='test_strategy',
                strategy_type='market_making',
                description='Test strategy'
            )
            self.assertIn('Error generating code', result)
    
    def test_parameter_defaults(self):
        """Test that default parameters are handled correctly."""
        # Test with None parameters
        code = self.generator._generate_code(
            'test_strategy', 'market_making', 'Test description', None
        )
        self.assertIn('class AlgoEvent:', code)
        
        # Test with empty parameters
        code = self.generator._generate_code(
            'test_strategy', 'market_making', 'Test description', {}
        )
        self.assertIn('class AlgoEvent:', code)
    
    def test_directory_structure(self):
        """Test that proper directory structure is created."""
        with patch.object(self.generator, 'base_dir', self.temp_dir):
            with patch.object(self.generator, 'strategies_dir', os.path.join(self.temp_dir, 'strategies')):
                with patch.object(self.generator, 'utils_dir', os.path.join(self.temp_dir, 'utils')):
                    self.generator._ensure_directories()
                    
                    # Check all expected directories exist
                    expected_dirs = [
                        'strategies',
                        'utils',
                        'strategies/market_making',
                        'strategies/trend_following',
                        'strategies/mean_reversion',
                        'strategies/arbitrage',
                        'strategies/custom'
                    ]
                    
                    for dir_path in expected_dirs:
                        full_path = os.path.join(self.temp_dir, dir_path)
                        self.assertTrue(os.path.exists(full_path), f"Directory {dir_path} was not created")


if __name__ == '__main__':
    unittest.main()