"""
Text highlighting utilities for highlighting query terms in retrieved content.
"""
import re
from typing import List


def highlight_query_terms(text: str, query: str, highlight_class: str = "highlight") -> str:
    """
    Highlight all words from the query that appear in the text.
    
    This function finds all words from the search query and wraps them with
    <mark> tags for highlighting when they appear in the text content.
    
    Args:
        text: The text content to highlight
        query: The search query containing terms to highlight
        highlight_class: CSS class for highlighted terms (default: "highlight")
        
    Returns:
        HTML string with highlighted terms wrapped in <mark> tags
        
    Example:
        >>> highlight_query_terms("The agent performs tasks", "agent task")
        'The <mark class="highlight">agent</mark> performs <mark class="highlight">tasks</mark>'
    """
    if not text or not query:
        return text
    
    # Extract words from the query (split on whitespace and remove empty strings)
    query_words = extract_query_words(query)
    
    if not query_words:
        return text
    
    # Create a pattern that matches any of the query words (case-insensitive)
    # Use word boundaries to avoid partial matches
    pattern_parts = []
    for word in query_words:
        # Escape special regex characters in the word
        escaped_word = re.escape(word)
        pattern_parts.append(f"\\b{escaped_word}\\b")
    
    # Combine all patterns with OR operator
    pattern = f"({'|'.join(pattern_parts)})"
    
    # Replace matches with highlighted versions
    # Use a function to preserve the original case
    def replace_match(match):
        matched_text = match.group(0)
        return f'<mark class="{highlight_class}">{matched_text}</mark>'
    
    # Perform case-insensitive replacement while preserving original case
    highlighted_text = re.sub(pattern, replace_match, text, flags=re.IGNORECASE)
    
    return highlighted_text


def extract_query_words(query: str) -> List[str]:
    """
    Extract individual words from a search query.
    
    This function now treats hyphenated words as two separate words.
    
    Args:
        query: The search query string
        
    Returns:
        List of non-trivial lowercase words from the query
        
    Example:
        >>> extract_query_words("What is an agent?")
        ['what', 'agent']
        >>> extract_query_words("fine-tuning")
        ['fine', 'tuning']
    """
    if not query:
        return []
    
    # Treat hyphenated words as separate words
    query = query.replace('-', ' ')
    
    # Split on whitespace, convert to lowercase, remove punctuation, and filter out empty strings
    import string
    words = []
    for word in query.split():
        # Remove punctuation from the word
        clean_word = word.strip(string.punctuation).lower()
        if clean_word:
            words.append(clean_word)
    
    # Remove common stop words that probably shouldn't be highlighted
    stop_words = {'i', 'the', 'is', 'are', 'was', 'were', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                  'for', 'of', 'with', 'by', 'what', 'how', 'why', 'when', 'where', 'who', 'whom', 'whose', 
                  'which', 'that', 'this', 'these', 'those', 'tell', 'me', 'about', 'should', 'we', 'use'}
    filtered_words = [word for word in words if word not in stop_words]
    
    return filtered_words


def highlight_query_terms_smart(text: str, query: str, highlight_class: str = "highlight") -> str:
    """
    Smart highlighting that excludes common stop words.
    
    This version uses extract_query_words to filter out common stop words
    before highlighting, resulting in more meaningful highlights.
    
    Args:
        text: The text content to highlight
        query: The search query containing terms to highlight
        highlight_class: CSS class for highlighted terms (default: "highlight")
        
    Returns:
        HTML string with highlighted terms wrapped in <mark> tags
    """
    if not text or not query:
        return text
    
    # Get meaningful words from the query (excluding stop words)
    query_words = extract_query_words(query)
    
    if not query_words:
        return text
    
    # Create a pattern that matches any of the query words (case-insensitive)
    pattern_parts = []
    for word in query_words:
        # Escape special regex characters in the word
        escaped_word = re.escape(word)
        pattern_parts.append(f"\\b{escaped_word}\\b")
    
    # Combine all patterns with OR operator
    pattern = f"({'|'.join(pattern_parts)})"
    
    # Replace matches with highlighted versions
    def replace_match(match):
        matched_text = match.group(0)
        return f'<mark class="{highlight_class}">{matched_text}</mark>'
    
    # Perform case-insensitive replacement while preserving original case
    highlighted_text = re.sub(pattern, replace_match, text, flags=re.IGNORECASE)
    
    return highlighted_text
