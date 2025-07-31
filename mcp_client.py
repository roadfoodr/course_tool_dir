"""
MCP Client wrapper for retrieving relevant chunks from the deployed MCP server.
Based on the patterns from test_mcp_server.py but designed for production use.
"""
import os
import asyncio
import json
from typing import List, Dict, Any, Optional
import httpx
from dotenv import load_dotenv
from fastmcp import Client

# Load environment variables from .env file
load_dotenv()

class MCPClient:
    """
    Async MCP client wrapper for retrieving chunks from the deployed server.
    
    Expected MCP Server Response Structure:
    {
        'chunks': [
            {
                'id': 'WS6_e09bae45-b2aa-4ae1-8119-843fb6a5b46b',
                'text': 'The actual content text of the chunk...',
                'workshop': 'WS6',
                'timestamp': 'Chunk 5',
                'speaker': 'Unknown',
                'position': 4,
                'relevance': 1.0
            },
            ...
        ],
        'total_chunks': 3
    }
    """
    
    def __init__(self):
        self.server_url = os.getenv("BWAI_MCP_SERVER_URL")
        if not self.server_url:
            raise ValueError("BWAI_MCP_SERVER_URL not found in environment variables")
        
        self.mcp_endpoint = f"{self.server_url.rstrip('/')}/mcp/"  # trailing slash is necessary
        self.health_endpoint = f"{self.server_url.rstrip('/')}/health"
    
    async def health_check(self) -> tuple[bool, dict]:
        """
        Test the health check endpoint of the deployed server.
        Returns (is_healthy, response_data) tuple.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.health_endpoint)
                response.raise_for_status()
                response_data = response.json()
                return True, response_data
        except Exception as e:
            print(f"Health check failed: {e}")
            return False, {"error": str(e), "status_code": getattr(e, 'response', {}).get('status_code', 'unknown')}
    
    async def get_chunks(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from the MCP server for a given question.
        
        Args:
            question: The question to search for
            top_k: Number of top results to return (default: 3)
            
        Returns:
            List of chunk dictionaries with content, source, and score
            
        Raises:
            Exception: If the MCP call fails
        """
        try:
            async with Client(self.mcp_endpoint) as client:
                # Call the get_relevant_chunks tool
                result = await client.call_tool("get_relevant_chunks", {
                    "question": question,
                    "top_k": top_k
                })
                
                # Debug: Print the actual response structure (can be removed later)
                # print(f"MCP Response: {result.data}")
                
                # Extract chunks from the response
                # The response structure is: {'chunks': [...], 'total_chunks': N}
                chunks_data = result.data.get("chunks", [])
                
                # Normalize the chunk data to match our UI expectations
                normalized_chunks = []
                for chunk in chunks_data:
                    if isinstance(chunk, dict):
                        # Map the MCP server fields to our display format
                        normalized_chunk = {
                            "content": chunk.get("text", ""),  # 'text' field contains the content
                            "source": f"{chunk.get('workshop', 'Unknown')} - {chunk.get('timestamp', 'Unknown')}",  # Combine workshop and timestamp
                            "score": chunk.get("relevance", 0.0),  # 'relevance' field is the score
                            "speaker": chunk.get("speaker", "Unknown")  # Include speaker information
                        }
                        normalized_chunks.append(normalized_chunk)
                    else:
                        # Fallback for unexpected data structure
                        normalized_chunks.append({
                            "content": str(chunk),
                            "source": "unknown",
                            "score": 0.0,
                            "speaker": "Unknown"
                        })
                
                return normalized_chunks
                
        except Exception as e:
            print(f"MCP tool call failed: {e}")
            raise Exception(f"Failed to retrieve chunks: {str(e)}")
    
    async def get_chunks_with_fallback(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Get chunks with fallback to placeholder data if MCP call fails.
        This provides a more robust user experience.
        
        Args:
            question: The question to search for
            top_k: Number of top results to return (default: 3)
            
        Returns:
            List of chunk dictionaries with content, source, and score
        """
        try:
            # First try to get real results from MCP server
            return await self.get_chunks(question, top_k)
            
        except Exception as e:
            print(f"MCP call failed, using fallback data: {e}")
            
            # Return placeholder results as fallback
            placeholder_results = [
                {
                    "content": f"[MCP Server Unavailable] This is a placeholder result for the query: '{question}'. The MCP server could not be reached.",
                    "source": "fallback_placeholder.txt", 
                    "score": 0.0,
                    "speaker": "System"
                },
                {
                    "content": f"[Error Response] Unable to retrieve real chunks from the MCP server. Please check server connectivity and try again.",
                    "source": "error_fallback.txt",
                    "score": 0.0,
                    "speaker": "System"
                },
                {
                    "content": f"[Debug Info] Original query: '{question}', Requested top_k: {top_k}. Error: {str(e)}",
                    "source": "debug_info.txt",
                    "score": 0.0,
                    "speaker": "System"
                }
            ]
            
            # Limit results to requested number
            return placeholder_results[:top_k]

# Singleton instance for use across the application
mcp_client = MCPClient()

# Convenience functions for direct use
async def get_relevant_chunks(question: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function to get relevant chunks.
    Uses the singleton MCP client instance.
    """
    return await mcp_client.get_chunks_with_fallback(question, top_k)

async def check_mcp_health() -> tuple[bool, dict]:
    """
    Convenience function to check MCP server health.
    Uses the singleton MCP client instance.
    Returns (is_healthy, response_data) tuple.
    """
    return await mcp_client.health_check()