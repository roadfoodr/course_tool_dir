from fasthtml.common import *
from dataclasses import dataclass
import asyncio
from mcp_client import get_relevant_chunks, check_mcp_health, mcp_client
from utils.text_highlighting import highlight_query_terms_smart

# FastHTML app with MonsterUI theme for modern styling
app, rt = fast_app()

@dataclass
class QueryRequest:
    question: str
    top_k: int = 3

def create_query_form(question: str = "", top_k: int = 3):
    """Create reusable query form component"""
    return Form(
        P("Enter your question to retrieve relevant chunks from the MCP server",
        style="text-align: center; margin-bottom: 20px; color: #666; font-size: 16px;"),

        # Question input and top-k field on the same line
        Div(
            Input(
                name="question",
                value=question,
                placeholder="What is the definition of an agent?",
                required=True,
                style=(
                    "flex: 1; padding: 12px 16px; font-size: 16px; "
                    "border: 1px solid #ccc; border-radius: 4px; min-width: 0;"
                )
            ),
            Div(
                Label("Top-K:", style="font-size: 14px; color: #666; margin-right: 8px;"),
                Input(
                    name="top_k",
                    type="number",
                    value=str(top_k),
                    min="1",
                    max="10",
                    style=(
                        "width: 60px; text-align: center; font-size: 16px; "
                        "padding: 12px 8px; border: 1px solid #ccc; border-radius: 4px;"
                    )
                ),
                style="display: flex; align-items: center; flex-shrink: 0;"
            ),
            style=(
                "display: flex; gap: 16px; align-items: center; "
                "max-width: 800px; margin: 0 auto 16px auto;"
            )
        ),

        # Submit button on its own line
        Div(
            Button(
                "Submit Query",
                type="submit",
                style=(
                    "background-color: #007bff; color: white; padding: 12px 24px; "
                    "border: none; border-radius: 4px; cursor: pointer; font-size: 16px; "
                    "transition: background-color 0.2s ease;"
                )
            ),
            style="text-align: center; max-width: 150px; margin: 0 auto;"
        ),

        method="post",
        action="/query",
        hx_post="/query",
        hx_target="#results",
        hx_indicator="#loading",
        hx_disabled_elt="button",
        style="max-width: 1000px; margin: 0 auto; padding: 20px;"
    )


def create_empty_results():
    """Create empty results placeholder"""
    return Div(
        H3("Results"),
        Div(
            P("Submit a query above to see results here...", 
              style="color: #666; font-style: italic; text-align: center; padding: 40px;"),
            style="border: 1px solid #eee; border-radius: 4px; background-color: #f9f9f9; min-height: 200px;"
        ),
        style="max-width: 800px; margin: 10px auto 20px auto; padding: 10px;"
    )

def create_results_display(question: str, top_k: int, results: list):
    """Create results display component"""
    result_cards = []
    for i, result in enumerate(results, 1):
        # Highlight query terms in the content
        highlighted_content = highlight_query_terms_smart(result["content"], question)
        
        # Create collapsible card using details/summary
        card = Details(
                            Summary(
                Span(f"Result {i}", style="font-weight: bold; color: #333; margin-right: 10px;"),
                Span(f"Score: {result['score']:.2f}", style="color: #666; font-size: 0.9em; margin-right: 10px;"),
                Span(f"Speaker: {result.get('speaker', 'Unknown')}", style="color: #555; font-size: 0.85em; margin-right: 10px;"),
                Span(f"({result['source']})", style="color: #888; font-size: 0.85em;"),
                style="cursor: pointer; padding: 12px 15px; margin: 0; display: flex; align-items: center; justify-content: space-between;"
            ),
            Div(
                Div(NotStr(highlighted_content), style="margin: 15px 0; line-height: 1.4; color: #333; font-family: 'Consolas', 'Monaco', 'Courier New', monospace; font-size: 13px; background-color: #f8f9fa; padding: 12px; border-radius: 4px; border: 1px solid #e9ecef;"),
                Div(
                    Strong("Source: "), result["source"], 
                    Br(),
                    Strong("Speaker: "), result.get("speaker", "Unknown"),
                    style="font-size: 0.9em; color: #555; margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee;"
                ),
                style="padding: 0 15px 15px 15px;"
            ),
            open=False,  # Start collapsed by default
            style="border: 1px solid #ddd; border-radius: 4px; margin: 10px 0; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden;"
        )
        result_cards.append(card)
    
    return Div(
        H3("Results"),
        P(f"Query: \"{question}\" (Top {top_k} results)", 
          style="color: #666; margin-bottom: 20px; font-style: italic;"),
        *result_cards,
        style="max-width: 800px; margin: 10px auto 20px auto; padding: 20px;"
    )

def create_loading_indicator():
    """Create loading indicator with spinner animation"""
    return Div(
        Div(
            Div(
                style=(
                    "border: 4px solid #f3f3f3; border-top: 4px solid #007bff; "
                    "border-radius: 50%; width: 40px; height: 40px; "
                    "animation: spin 1s linear infinite; margin: 0 auto 16px auto;"
                )
            ),
            Div("Searching MCP server...", style="font-size: 16px; color: #666;"),
            Div(f"Connecting to: {mcp_client.server_url}", style="font-size: 13px; color: #007bff; margin-top: 4px; font-family: monospace;"),
            Div("Please wait while we retrieve relevant chunks", style="font-size: 14px; color: #888; margin-top: 8px;"),
            style="text-align: center; padding: 30px;"
        ),
        id="loading",
        cls="htmx-indicator",
        style="max-width: 800px; margin: 20px auto; padding: 20px; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
    )

def create_page_layout(query_form, results_area, loading_indicator=None):
    """Create main page layout"""
    content = [
        query_form,
        loading_indicator if loading_indicator else "",
        results_area
    ]
    
    return Titled(
        "MCP Query Tool",
        Div(
            *content,
            style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; min-height: 100vh; padding: 20px;"
        ),
        # Add CSS for title, collapsible cards, spinner animation, and text highlighting
        Style("""
            h1 { text-align: center; margin: 20px 0 40px 0; }
            details > summary {
                list-style: none;
                transition: background-color 0.2s ease;
            }
            details > summary::-webkit-details-marker {
                display: none;
            }
            details > summary::before {
                content: '▶';
                display: inline-block;
                margin-right: 8px;
                transition: transform 0.2s ease;
                color: #666;
            }
            details[open] > summary::before {
                transform: rotate(90deg);
            }
            details > summary:hover {
                background-color: #f8f9fa;
            }
            details[open] > summary {
                border-bottom: 1px solid #eee;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .htmx-indicator {
                display: none;
            }
            .htmx-request .htmx-indicator {
                display: block;
            }
            .htmx-request.htmx-indicator {
                display: block;
            }
            button:disabled {
                background-color: #6c757d !important;
                cursor: not-allowed !important;
                opacity: 0.6;
            }
            /* Text highlighting styles */
            mark.highlight {
                background-color: #fff3cd;
                color: #856404;
                padding: 1px 3px;
                border-radius: 3px;
                font-weight: 600;
                border: 1px solid #ffeaa7;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            /* Alternative highlight style for better contrast */
            mark {
                background-color: #fff3cd;
                color: #856404;
                padding: 1px 3px;
                border-radius: 3px;
                font-weight: 600;
                border: 1px solid #ffeaa7;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
        """)
    )

@rt("/")
def get():
    """Main page with query form and results display"""
    query_form = create_query_form()
    results_area = Div(create_empty_results(), id="results")
    loading_indicator = create_loading_indicator()
    
    return create_page_layout(query_form, results_area, loading_indicator)

@rt("/query")
async def post(question: str, top_k: int = 3):
    """Handle query submission - return only results for HTMX"""
    
    try:
        # Get actual results from MCP server
        results = await get_relevant_chunks(question, top_k)
        
        # Return only the results component for HTMX replacement
        return create_results_display(question, top_k, results)
    
    except Exception as e:
        # If something goes wrong, show an error message
        error_result = [{
            "content": f"Error retrieving chunks: {str(e)}",
            "source": "error",
            "score": 0.0,
            "speaker": "System"
        }]
        return create_results_display(question, top_k, error_result)

@rt("/health")
async def health():
    """Health check endpoint that also checks MCP server connectivity"""
    try:
        # Import here to access the singleton instance
        from mcp_client import mcp_client
        
        # Check MCP server health
        mcp_healthy, mcp_response = await check_mcp_health()
        
        return {
            "status": "healthy" if mcp_healthy else "degraded",
            "mcp_server": "connected" if mcp_healthy else "disconnected",
            "message": "Application is running" + (" and MCP server is reachable" if mcp_healthy else " but MCP server is unreachable"),
            "mcp_server_url": mcp_client.server_url,
            "mcp_health_endpoint": mcp_client.health_endpoint,
            "mcp_server_response": mcp_response
        }
    except Exception as e:
        return {
            "status": "error",
            "mcp_server": "error", 
            "message": f"Health check failed: {str(e)}",
            "mcp_server_response": {"error": str(e)}
        }

if __name__ == "__main__":
    serve(port=5001)