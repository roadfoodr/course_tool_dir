from fasthtml.common import *
from dataclasses import dataclass

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
        # Create collapsible card using details/summary
        card = Details(
            Summary(
                Span(f"Result {i}", style="font-weight: bold; color: #333; margin-right: 10px;"),
                Span(f"Score: {result['score']:.2f}", style="color: #666; font-size: 0.9em; margin-right: 10px;"),
                Span(f"({result['source']})", style="color: #888; font-size: 0.85em;"),
                style="cursor: pointer; padding: 12px 15px; margin: 0; display: flex; align-items: center; justify-content: space-between;"
            ),
            Div(
                P(result["content"], style="margin: 15px 0; line-height: 1.4; color: #333; font-family: 'Consolas', 'Monaco', 'Courier New', monospace; font-size: 13px; background-color: #f8f9fa; padding: 12px; border-radius: 4px; border: 1px solid #e9ecef;"),
                Div(
                    Strong("Source: "), result["source"],
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
    """Create loading indicator"""
    return Div(
        Div(
            "🔄 Searching...",
            style="text-align: center; padding: 20px; font-style: italic; color: #666;"
        ),
        id="loading",
        style="display: none; max-width: 800px; margin: 20px auto; padding: 20px;"
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
        # Add CSS for title and collapsible cards
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
def post(question: str, top_k: int = 3):
    """Handle query submission - return only results for HTMX"""
    
    # Placeholder results - this will be replaced with actual MCP calls
    placeholder_results = [
        {
            "content": "This is a placeholder result chunk that would normally come from the MCP server. It contains relevant information about your query.",
            "source": "placeholder_document_1.txt", 
            "score": 0.95
        },
        {
            "content": "Another example chunk showing how results would be displayed. The actual implementation will call the MCP server to retrieve real content.",
            "source": "placeholder_document_2.txt",
            "score": 0.87  
        },
        {
            "content": "A third result demonstrating the layout. Each chunk will show content, source, and relevance score when connected to the real MCP server.",
            "source": "placeholder_document_3.txt",
            "score": 0.79
        }
    ]
    
    # Limit results to requested number
    results = placeholder_results[:top_k]
    
    # Return only the results component for HTMX replacement
    return create_results_display(question, top_k, results)

if __name__ == "__main__":
    serve(port=5001)