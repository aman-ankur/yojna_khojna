"""Core RAG chain setup and execution logic."""

from langchain_core.runnables import RunnablePassthrough, RunnableParallel, itemgetter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage

# Import the retriever function from our vector store module
from .vector_store import get_retriever
# Import the LLM initialization function
from .llm import get_chat_model
# Import utility functions
from .utils import extract_key_entities, deduplicate_chunks

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
    CONTEXTUALIZE_Q_SYSTEM_PROMPT = """# Yojna Khojna Question Reformulation System

You help rural and underserved Indian citizens by reformulating their questions for better document retrieval. Many users have limited education and are seeking help with government schemes.

Given the chat history and latest question:
1. Create a STANDALONE QUERY that retrieval systems can effectively use
2. INCLUDE BOTH Hindi and English terms for key concepts (vajrapat/lightning strike, prakritik aapda/natural calamity)
3. EXPAND the query to capture the likely UNDERLYING NEED for practical assistance
4. PRESERVE location or scheme-specific details mentioned

Remember that behind simple questions are often people in distress looking for concrete help.

DO NOT answer the question - ONLY reformulate it for better document retrieval."""
    # Note: The original prompt expected {chat_history} and {input} which map to the new prompt's needs.

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CONTEXTUALIZE_Q_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    # --- History-Aware Retriever Chain ---
    # This chain uses the LLM to rephrase the question, then retrieves documents
    # using the base retriever. Output: List[Document]
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # --- Enhanced Retrieval Logic ---
    # This function takes the output of the history_aware_retriever (initial docs)
    # and performs secondary searches based on extracted entities.
    def perform_enhanced_retrieval(input_dict: Dict[str, Any]) -> List[Document]:
        # 1. Get initial documents using the history-aware retriever
        # It needs the same input as the main chain expects initially
        initial_docs = history_aware_retriever.invoke(input_dict)
        print(f"Initial retrieval ({len(initial_docs)} docs) based on potentially rephrased question.")

        # 2. Extract entities from initial documents
        entities = extract_key_entities(initial_docs)

        # 3. Perform secondary searches for each entity
        related_docs: List[Document] = []
        if entities:
            # Use the base retriever for entity-focused searches
            base_retriever = get_retriever()
            print(f"Performing secondary search for entities: {entities}")
            for entity in entities:
                # Construct a query focusing on practical details for the entity
                secondary_query = f"{entity} entitlement amount procedure documents where to apply"
                try:
                    entity_docs = base_retriever.invoke(secondary_query)
                    print(f"  - Found {len(entity_docs)} docs for entity '{entity}'")
                    related_docs.extend(entity_docs)
                except Exception as e:
                    print(f"  - Error during secondary search for entity '{entity}': {e}")
                    # Optionally log the error, but continue for other entities

        # 4. Combine initial and related documents
        all_docs = initial_docs + related_docs

        # 5. Deduplicate the combined list
        final_docs = deduplicate_chunks(all_docs)
        print(f"Enhanced retrieval complete. Final unique docs: {len(final_docs)}")
        return final_docs

    # --- Answering Prompt (using retrieved context) ---
    # This prompt guides the LLM to answer based *only* on the provided context.
    QA_SYSTEM_PROMPT = """# Yojna Khojna Government Scheme Assistant

You are helping rural and underserved Indian citizens access government welfare schemes. Your users often have limited education, may be in distress, and don't know where to go for help. They need extremely clear guidance based EXCLUSIVELY on official documents.

## MANDATORY RESPONSE GUIDELINES:

1. USE SIMPLE LANGUAGE that someone with basic education can understand
   - Avoid complex terms
   - Explain any necessary government terminology in simple words
   - Use short, clear sentences

2. ALWAYS INCLUDE:
   - SPECIFIC AMOUNTS (exact rupee amounts when mentioned in documents)
   - WHERE TO GO for help (specific office or person)
   - WHAT TO BRING (only essential documents, explained simply)
   - WHAT TO EXPECT (timeline, process in simple steps)

3. ADAPT YOUR STYLE to the question type:
   - For YES/NO questions: Be brief and direct (1-2 sentences)
   - For "WHAT TO DO" questions: Provide step-by-step practical guidance
   - For "HOW MUCH" questions: Lead with the EXACT AMOUNT in the first sentence

4. CONNECT INFORMATION across documents to give complete answers:
   - If one document mentions lightning (vajrapat) as a disaster
   - And another mentions compensation for disasters
   - COMBINE this information without expecting the user to make the connection

5. ONLY use information from the provided document chunks - NEVER add general knowledge
   - If information is missing, clearly state what you don't know
   - If documents contradict, mention the most citizen-favorable option

6. ASSUME THE REAL QUESTION is "How can I get help?" even if they only ask factual questions
   - Behind every query is someone facing a problem
   - Always provide practical next steps, even for simple questions

## DOCUMENT CONTEXT:
{context}

## QUESTION: {question}

## ANSWER (in {language}):"""
    # Note: The original prompt expected {context} and {input}.
    # The new prompt expects {context}, {question}, and {language}.
    # `create_stuff_documents_chain` handles {context}.
    # We need to ensure {input} maps to {question} and {language} is passed.
    # For now, we map "human" input to "question". Language needs further handling.
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", QA_SYSTEM_PROMPT),
            # Renaming the human input variable for clarity to match the prompt
            ("human", "{question}"),
        ]
    )

    # --- Document Combination Chain (Stuff Chain) ---
    # This chain takes the potentially rephrased question and documents,
    # formats them into the QA_PROMPT, and sends to the LLM.
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # --- Full Conversational RAG Chain ---
    # Uses RunnableParallel to prepare the input for the question_answer_chain.
    # It runs the enhanced retrieval logic to get the final documents ('context').
    # It extracts the original 'input' as 'question' and 'language' using itemgetter.
    # The full input dictionary {"input": ..., "chat_history": ..., "language": ...}
    # is passed to this parallel step.
    rag_chain = (
        RunnableParallel(
            {
                # Apply the enhanced retrieval logic function here.
                # It takes the full input dict and returns the final List[Document].
                "context": perform_enhanced_retrieval,
                "question": itemgetter("input"),        # Extracts 'input' from input dict
                "language": itemgetter("language"),      # Extracts 'language' from input dict
            }
        )
        | question_answer_chain # Expects context, question, language
    )

    print("Conversational RAG chain created with ENHANCED retrieval, updated prompts, and language handling.")
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
