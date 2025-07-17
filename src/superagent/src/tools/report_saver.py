import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

def save_report_to_markdown(content: str, filename: str = None) -> str:
    """
    Save report content to a markdown file in the ./reports directory.
    
    Args:
        content (str): The markdown content to save
        filename (str, optional): Custom filename. If not provided, uses timestamp.
    
    Returns:
        str: The path to the saved file
    """
    # Create reports directory if it doesn't exist
    reports_dir = Path("./reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.md"
    
    # Ensure filename has .md extension
    if not filename.endswith('.md'):
        filename += '.md'
    
    # Full file path
    file_path = reports_dir / filename
    
    try:
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Report saved successfully to: {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Failed to save report to {file_path}: {e}")
        raise