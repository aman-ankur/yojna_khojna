"""Core RAG chain setup and execution logic."""

from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage

# Import the retriever function from our vector store module
from .vector_store import get_retriever
# Import the LLM initialization function
from .llm import get_chat_model

# LangChain Community/Integrations (if needed, e.g., specific retrievers/LLMs)
# (Keep existing imports if they are from here)

# LangChain Chains for orchestration
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

def create_conversational_rag_chain():
    """
    Builds and returns a conversational RAG chain that considers chat history.

    The chain consists of two main parts:
    1. History-Aware Retriever: Takes history and current input, rephrases the
       input into a standalone question, and retrieves relevant documents.
    2. Question-Answering Chain: Takes the rephrased question and retrieved
       documents to generate the final answer.
    """
    llm = get_chat_model()
    retriever = get_retriever()

    # --- Contextualization Prompt (for rephrasing question based on history) ---
    # This prompt helps the LLM understand the flow of conversation.
    CONTEXTUALIZE_Q_SYSTEM_PROMPT = """Given a chat history and the latest user question \\
    which might reference context in the chat history, formulate a standalone question \\
    which can be understood without the chat history. Do NOT answer the question, \\
    just reformulate it if needed and otherwise return it as is."""

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CONTEXTUALIZE_Q_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    # --- History-Aware Retriever Chain ---
    # This chain uses the LLM to rephrase the question, then retrieves documents.
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # --- Answering Prompt (using retrieved context) ---
    # This prompt guides the LLM to answer based *only* on the provided context.
    QA_SYSTEM_PROMPT = """You are an assistant for question-answering tasks for the Yojna Khojna project. \\
    Use the following pieces of retrieved context to answer the question. \\
    If you don't know the answer, just say that you don't know. \\
    Use three sentences maximum and keep the answer concise.

    Context:
    {context}
    """
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", QA_SYSTEM_PROMPT),
            ("human", "{input}"),
        ]
    )

    # --- Document Combination Chain (Stuff Chain) ---
    # This chain takes the potentially rephrased question and documents,
    # formats them into the QA_PROMPT, and sends to the LLM.
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # --- Full Conversational RAG Chain ---
    # Pipelines the history-aware retriever and the question-answering chain.
    # Input: {"input": "...", "chat_history": [...]}
    # Output: String answer
    rag_chain = history_aware_retriever | question_answer_chain

    print("Conversational RAG chain created with history awareness.")
    # Note: The final output parser is now implicitly handled by create_stuff_documents_chain
    # which returns the message content (string) by default with ChatModels.
    # If you needed the AIMessage object, you wouldn't pipe to StrOutputParser.

    return rag_chain

# Kept original get_rag_chain for potential compatibility, but marked as deprecated
# or potentially to be removed later. The main usage should shift to
# create_conversational_rag_chain.
# def get_rag_chain():
#     \"\"\"Builds and returns the original (non-conversational) RAG chain.\"\"\"
#     # --- Prompt Template Definition ---\n    template = \"\"\"
#     Answer the question based only on the following context:\n    {context}\n\n    Question: {question}\n    \"\"\"\n    prompt = ChatPromptTemplate.from_template(template)\n\n    # --- Initialize Components ---\n    retriever = get_retriever()\n    llm = get_chat_model()      # Initialize the LLM\n\n    # --- RAG Chain Definition ---\n    rag_chain = (\n        {\"context\": retriever | format_docs, \"question\": RunnablePassthrough()}\n        | prompt\n        | llm\n        | StrOutputParser()\n    )\n    print(\"Original (non-conversational) RAG chain created.\")\n    return rag_chain

# Example usage (updated for conversational chain)
# if __name__ == '__main__':
#     chain = create_conversational_rag_chain()
#     chat_history = [] # Maintain history outside the function
#     try:
#         print("\\n--- Invoking Conversational RAG Chain ---")
#         query1 = "What is Abua Awaas Yojana?"
#         print(f"User: {query1}")
#         result1 = chain.invoke({"input": query1, "chat_history": chat_history})
#         print(f"AI: {result1}")
#         chat_history.extend([HumanMessage(content=query1), AIMessage(content=result1)])

#         print("\\n--- Follow-up Question ---")
#         query2 = "Who is eligible for it?"
#         print(f"User: {query2}")
#         result2 = chain.invoke({"input": query2, "chat_history": chat_history})
#         print(f"AI: {result2}")
#         chat_history.extend([HumanMessage(content=query2), AIMessage(content=result2)])

#         print("\\n------------------------------------\\n")

#     except Exception as e:
#         print(f"Error invoking conversational RAG chain: {e}") 