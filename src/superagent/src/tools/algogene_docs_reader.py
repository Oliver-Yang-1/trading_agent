import os
import logging
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from .decorators import log_io

logger = logging.getLogger(__name__)

class AlgogeneDocsSearchInput(BaseModel):
    """Input for Algogene documentation search."""
    query: str = Field(description="Search query or keywords to find relevant documentation")
    specific_file: Optional[str] = Field(default=None, description="Specific documentation file to read (e.g., '01-overview.md')")

class AlgogeneDocsReader(BaseTool):
    """Tool for reading and searching Algogene platform documentation."""
    
    name: str = "algogene_docs_reader"
    description: str = (
        "Search and read Algogene platform documentation. "
        "Can search by keywords (e.g., 'API functions', 'order placement', 'backtest') "
        "or read specific files by name (e.g., '01-overview.md', '07-api-functions.md'). "
        "Returns relevant documentation content to help with understanding the platform."
    )
    args_schema: type = AlgogeneDocsSearchInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _get_docs_dir(self):
        """Get documentation directory path."""
        return os.path.join(
            os.path.dirname(__file__), 
            "algogene_archieve_docs"
        )
        
    def _get_doc_files(self) -> List[str]:
        """Get list of available documentation files."""
        try:
            docs_dir = self._get_docs_dir()
            if not os.path.exists(docs_dir):
                logger.error(f"Documentation directory not found: {docs_dir}")
                return []
            
            files = [f for f in os.listdir(docs_dir) if f.endswith('.md')]
            return sorted(files)
        except Exception as e:
            logger.error(f"Error getting documentation files: {str(e)}")
            return []
    
    def _read_file(self, filename: str) -> str:
        """Read content from a specific documentation file."""
        try:
            docs_dir = self._get_docs_dir()
            file_path = os.path.join(docs_dir, filename)
            if not os.path.exists(file_path):
                return f"File {filename} not found."
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
        except Exception as e:
            logger.error(f"Error reading file {filename}: {str(e)}")
            return f"Error reading file {filename}: {str(e)}"
    
    def _search_in_files(self, query: str) -> Dict[str, str]:
        """Search for query keywords in all documentation files."""
        results = {}
        query_lower = query.lower()
        doc_files = self._get_doc_files()
        
        for filename in doc_files:
            content = self._read_file(filename)
            if query_lower in content.lower():
                # Get relevant excerpts around the search term
                lines = content.split('\n')
                relevant_lines = []
                
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        # Include context lines (2 before and 2 after)
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        context = lines[start:end]
                        relevant_lines.extend(context)
                        relevant_lines.append("---")
                
                if relevant_lines:
                    results[filename] = '\n'.join(relevant_lines)
        
        return results
    
    def _format_search_results(self, results: Dict[str, str]) -> str:
        """Format search results for display."""
        if not results:
            return "No relevant documentation found for your query."
        
        formatted_results = []
        formatted_results.append("# Algogene Documentation Search Results\n")
        
        for filename, content in results.items():
            formatted_results.append(f"## From {filename}:\n")
            formatted_results.append(content)
            formatted_results.append("\n" + "="*50 + "\n")
        
        return '\n'.join(formatted_results)
    
    def _get_file_suggestions(self, query: str) -> List[str]:
        """Get file suggestions based on query keywords."""
        suggestions = []
        query_lower = query.lower()
        
        keyword_map = {
            'overview': ['01-overview.md'],
            'library': ['02-library-support.md'],
            'data': ['03-data-source.md', '06-data-stream.md'],
            'architecture': ['04-architecture.md'],
            'environment': ['05-environment-setup.md'],
            'api': ['07-api-functions.md'],
            'backtest': ['08-backtest-history.md'],
            'example': ['09-example1-maket_making.md', '10-example2-moving_average.md'],
            'order': ['07-api-functions.md'],
            'trading': ['07-api-functions.md', '09-example1-maket_making.md', '10-example2-moving_average.md'],
            'market': ['09-example1-maket_making.md'],
            'moving average': ['10-example2-moving_average.md'],
        }
        
        for keyword, files in keyword_map.items():
            if keyword in query_lower:
                suggestions.extend(files)
        
        return list(set(suggestions))  # Remove duplicates
    
    @log_io
    def _run(self, query: str, specific_file: Optional[str] = None) -> str:
        """Execute the documentation search or file reading."""
        try:
            doc_files = self._get_doc_files()
            
            # If specific file is requested, read it directly
            if specific_file:
                if specific_file in doc_files:
                    content = self._read_file(specific_file)
                    return f"# Content from {specific_file}\n\n{content}"
                else:
                    available_files = ", ".join(doc_files)
                    return f"File '{specific_file}' not found. Available files: {available_files}"
            
            # Search through all files
            search_results = self._search_in_files(query)
            
            if search_results:
                return self._format_search_results(search_results)
            else:
                # Provide suggestions if no direct matches
                suggestions = self._get_file_suggestions(query)
                if suggestions:
                    suggestion_text = ", ".join(suggestions)
                    return f"No direct matches found for '{query}'. You might want to check these files: {suggestion_text}"
                else:
                    available_files = ", ".join(doc_files)
                    return f"No matches found for '{query}'. Available documentation files: {available_files}"
        
        except Exception as e:
            logger.error(f"Error in algogene_docs_reader: {str(e)}")
            return f"Error searching documentation: {str(e)}"

# Create the tool instance
algogene_docs_reader_tool = AlgogeneDocsReader()