"""Core RAG chain setup and execution logic."""

from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import the retriever function from our vector store module
from .vector_store import get_retriever
# Import the LLM initialization function
from .llm import get_chat_model

def format_docs(docs):
    """Formats retrieved documents for the prompt."""
    return "\n\n".join(doc.page_content for doc in docs)

def get_rag_chain():
    """Builds and returns the RAG chain integrating the retriever and LLM."""

    # --- Prompt Template Definition ---
    template = """
    Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # --- Initialize Components ---
    retriever = get_retriever()
    llm = get_chat_model()      # Initialize the LLM

    # --- RAG Chain Definition ---
    # Flow: Retrieve context -> Format documents -> Format prompt -> Call LLM -> Parse output
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm # Integrate the LLM
        | StrOutputParser() # Parse the LLM output to a string
    )

    print("RAG chain created with Weaviate retriever and Anthropic LLM.")
    return rag_chain # Return the actual chain

# Example usage (primarily for testing, main usage will be via API)
# if __name__ == '__main__':
#     chain = get_rag_chain()
#     try:
#         result = chain.invoke("What are some key features of Claude 3?") # Example question
#         print("\n--- RAG Chain Output ---")
#         print(result)
#         print("------------------------\n")
#     except Exception as e:
#         print(f"Error invoking RAG chain: {e}") 