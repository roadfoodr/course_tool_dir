from fasthtml.common import *
from dataclasses import dataclass

# FastHTML app with MonsterUI theme for modern styling
app, rt = fast_app()

@dataclass
class QueryRequest:
    question: str
    top_k: int = 3

@rt("/")
def get():
    """Main page with query form and results display"""
    
    # Query form section
    query_form = Form(
        H2("Enter your question to retrieve relevant chunks from the MCP server"),
        Div(
            Input(
                name="question", 
                placeholder="What is the definition of an agent?",
                style="width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px;"
            ),
            Br(),
            Input(
                name="top_k", 
                type="number", 
                value="3",
                min="1",
                max="10",
                style="width: 80px; padding: 5px; margin: 5px; border: 1px solid #ddd; border-radius: 4px;"
            ),
            Label(" Results", style="margin-left: 5px; color: #666;"),
            Br(),
            Button(
                "Submit Query", 
                type="submit",
                style="background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px;"
            ),
            style="margin: 20px 0;"
        ),
        method="post",
        action="/query",
        style="max-width: 800px; margin: 0 auto; padding: 20px;"
    )
    
    # Results display area
    results_area = Div(
        H3("Results"),
        Div(
            P("Submit a query above to see results here...", 
              style="color: #666; font-style: italic; text-align: center; padding: 40px;"),
            style="border: 1px solid #eee; border-radius: 4px; background-color: #f9f9f9; min-height: 200px;"
        ),
        id="results",
        style="max-width: 800px; margin: 20px auto; padding: 20px;"
    )
    
    return Titled(
        "MCP Query Tool",
        Div(
            H1("MCP Query Tool", style="text-align: center; color: #333; margin-bottom: 30px;"),
            query_form,
            results_area,
            style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; min-height: 100vh; padding: 20px;"
        )
    )

@rt("/query")
def post(question: str, top_k: int = 3):
    """Handle query submission - placeholder for now"""
    
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
    
    # Generate result cards
    result_cards = []
    for i, result in enumerate(results, 1):
        card = Div(
            H4(f"Result {i}", style="margin: 0 0 10px 0; color: #333;"),
            P(result["content"], style="margin: 10px 0; line-height: 1.6;"),
            Div(
                Strong("Source: "), result["source"],
                Span(f" | Score: {result['score']:.2f}", style="color: #666; margin-left: 10px;"),
                style="font-size: 0.9em; color: #555; margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee;"
            ),
            style="border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin: 10px 0; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
        )
        result_cards.append(card)
    
    # Results display
    results_area = Div(
        H3("Results"),
        P(f"Query: \"{question}\" (Top {top_k} results)", 
          style="color: #666; margin-bottom: 20px; font-style: italic;"),
        *result_cards,
        style="max-width: 800px; margin: 20px auto; padding: 20px;"
    )
    
    # Return the same page layout but with results
    query_form = Form(
        H2("Enter your question to retrieve relevant chunks from the MCP server"),
        Div(
            Input(
                name="question", 
                value=question,
                placeholder="What is the definition of an agent?",
                style="width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px;"
            ),
            Br(),
            Input(
                name="top_k", 
                type="number", 
                value=str(top_k),
                min="1",
                max="10",
                style="width: 80px; padding: 5px; margin: 5px; border: 1px solid #ddd; border-radius: 4px;"
            ),
            Label(" Results", style="margin-left: 5px; color: #666;"),
            Br(),
            Button(
                "Submit Query", 
                type="submit",
                style="background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px;"
            ),
            style="margin: 20px 0;"
        ),
        method="post",
        action="/query",
        style="max-width: 800px; margin: 0 auto; padding: 20px;"
    )
    
    return Titled(
        "MCP Query Tool",
        Div(
            H1("MCP Query Tool", style="text-align: center; color: #333; margin-bottom: 30px;"),
            query_form,
            results_area,
            style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; min-height: 100vh; padding: 20px;"
        )
    )

if __name__ == "__main__":
    serve(port=5001)