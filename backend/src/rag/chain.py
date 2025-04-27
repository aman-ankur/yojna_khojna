"""Core RAG chain setup and execution logic."""

from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document
from typing import List, Dict, Any, Tuple
import spacy # Import spacy
import logging # Import logging
import re # Import re for regex

# Import the retriever function from our vector store module
from .vector_store import get_retriever
# Import the LLM initialization function
from .llm import get_chat_model

# LangChain Community/Integrations (if needed, e.g., specific retrievers/LLMs)
# (Keep existing imports if they are from here)

# LangChain Chains for orchestration
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

# --- Setup Logging ---
logger = logging.getLogger(__name__)

# --- Load spaCy Model --- #
# Load the multilingual model downloaded by the user
# Using a simple global variable for simplicity here.
# Consider a more robust approach (e.g., FastAPI lifespan event) for production.
_nlp = None
# Change from English-only model to multilingual model
SPACY_MODEL_NAME = "xx_ent_wiki_sm"  # Multilingual model that supports Hindi

# --- Domain-Specific Entity Dictionary --- #
# Comprehensive entity categories covering all government scheme domains
SCHEME_ENTITIES = {
    # Social welfare
    "HOUSING": [
        "आवास योजना", "housing scheme", "घर", "house", "मकान", "home",
        "प्रधानमंत्री आवास", "PM Awas", "इंदिरा आवास", "Indira Awas"
    ],
    
    # Healthcare
    "HEALTH": [
        "स्वास्थ्य", "health", "आयुष्मान भारत", "Ayushman Bharat", 
        "चिकित्सा", "medical", "बीमा", "insurance", "जननी सुरक्षा", "Janani Suraksha"
    ],
    
    # Education
    "EDUCATION": [
        "शिक्षा", "education", "छात्रवृत्ति", "scholarship", "मिड-डे मील", "mid-day meal",
        "स्कूल", "school", "कॉलेज", "college", "पढ़ाई", "study"
    ],
    
    # Employment
    "EMPLOYMENT": [
        "रोजगार", "employment", "नौकरी", "job", "मनरेगा", "MGNREGA",
        "प्रशिक्षण", "training", "स्किल", "skill", "कौशल विकास", "skill development"
    ],
    
    # Agriculture
    "AGRICULTURE": [
        "किसान", "farmer", "खेती", "farming", "फसल", "crop",
        "ट्रैक्टर", "tractor", "सिंचाई", "irrigation", "बीज", "seed"
    ],
    
    # Utilities and energy
    "UTILITIES": [
        "बिजली", "electricity", "पानी", "water", "गैस", "gas",
        "उज्ज्वला", "Ujjwala", "सौभाग्य", "Saubhagya", "उजाला", "Ujala"
    ],
    
    # Disaster relief
    "DISASTER": [
        "आपदा", "disaster", "बाढ़", "flood", "सूखा", "drought",
        "वज्रपात", "lightning", "भूकंप", "earthquake", "आग", "fire"
    ],
    
    # Special categories
    "SPECIAL_CATEGORIES": [
        "महिला", "women", "बच्चे", "children", "वृद्ध", "elderly",
        "दिव्यांग", "disabled", "विधवा", "widow", "अनुसूचित जाति", "SC",
        "अनुसूचित जनजाति", "ST", "पिछड़ा वर्ग", "OBC", "अल्पसंख्यक", "minority"
    ],
    
    # Financial assistance
    "FINANCIAL_ASSISTANCE": [
        "पेंशन", "pension", "मुआवजा", "compensation", "अनुदान", "grant",
        "राशि", "amount", "सब्सिडी", "subsidy", "लोन", "loan", "ऋण", "credit"
    ],
    
    # Documents and requirements
    "DOCUMENTS": [
        "आधार", "Aadhar", "राशन कार्ड", "ration card", "बैंक खाता", "bank account",
        "पहचान पत्र", "ID card", "प्रमाण पत्र", "certificate", "फॉर्म", "form"
    ],
    
    # Authorities
    "AUTHORITIES": [
        "पंचायत", "panchayat", "ब्लॉक", "block", "तहसील", "tehsil",
        "जिला", "district", "कार्यालय", "office", "मंत्रालय", "ministry"
    ],
    
    # Procedural terms
    "PROCEDURAL": [
        "आवेदन", "application", "पात्रता", "eligibility", "प्रक्रिया", "process",
        "अंतिम तिथि", "deadline", "समय सीमा", "time limit", "चयन", "selection"
    ]
}

def get_spacy_nlp():
    """Loads and returns the spaCy NLP model."""
    global _nlp
    if _nlp is None:
        try:
            logger.info(f"Loading spaCy model: {SPACY_MODEL_NAME}...")
            _nlp = spacy.load(SPACY_MODEL_NAME)
            logger.info(f"spaCy model '{SPACY_MODEL_NAME}' loaded successfully.")
        except OSError:
            logger.error(f"spaCy model '{SPACY_MODEL_NAME}' not found. ")
            logger.error(f"Please run: python -m spacy download {SPACY_MODEL_NAME}")
            # Depending on requirements, either raise an error or return None
            # Returning None will effectively disable NER-based entity extraction
            # raise RuntimeError(f"spaCy model '{SPACY_MODEL_NAME}' not found.")
            _nlp = None # Set explicitly to None on failure
            logger.warning("Proceeding without spaCy NER capabilities.")
        except Exception as e:
             logger.error(f"An unexpected error occurred loading spaCy model '{SPACY_MODEL_NAME}': {e}", exc_info=True)
             _nlp = None
             logger.warning("Proceeding without spaCy NER capabilities.")
    return _nlp

def extract_key_entities(query: str, documents: List[Document]) -> List[str]:
    """
    Extracts domain-specific key entities relevant to government welfare schemes
    from query and document content.
    """
    nlp = get_spacy_nlp()
    if not nlp:
        logger.warning("spaCy NLP model not available. Using regex-based entity extraction.")
        return regex_entity_extraction(query, documents)

    logger.debug(f"Running entity extraction on query and {len(documents)} documents.")
    
    # Combine query and document text for analysis
    # Limit document content to avoid processing very large texts
    text_to_process = query + "\n" + "\n".join([doc.page_content[:500] for doc in documents])
    
    # Process text with spaCy
    doc = nlp(text_to_process)
    
    entities = set()  # For automatic deduplication
    
    # 1. Extract standard NER entities
    relevant_labels = {"ORG", "PERSON", "GPE", "LOC", "MISC", "PRODUCT"}
    for ent in doc.ents:
        if ent.label_ in relevant_labels:
            ent_text = ent.text.strip()
            if len(ent_text) > 2 and not is_common_term(ent_text):
                entities.add(ent_text)
    
    # 2. Extract scheme names using pattern matching
    # This improves detection of scheme names that might not be recognized by general NER
    scheme_name_pattern = r'(?:[A-Za-z\s]+\s+)?(?:योजना|scheme|yojana)s?|(?:प्रधानमंत्री|मुख्यमंत्री|PM|CM)\s+[A-Za-z\s]+'
    scheme_matches = re.findall(scheme_name_pattern, text_to_process, re.IGNORECASE)
    for match in scheme_matches:
        if len(match.strip()) > 5:  # Filter out very short matches
            entities.add(match.strip())
    
    # 3. Extract domain-specific entities using pattern matching
    for category, terms in SCHEME_ENTITIES.items():
        for term in terms:
            if term.lower() in text_to_process.lower():
                entities.add(term)
                
                # Also add any bilingual equivalents from the same category
                term_index = terms.index(term)
                # If term is at an even index, add the following odd index term (Hindi → English)
                if term_index % 2 == 0 and term_index + 1 < len(terms):
                    entities.add(terms[term_index + 1])
                # If term is at an odd index, add the previous even index term (English → Hindi)
                elif term_index % 2 == 1 and term_index - 1 >= 0:
                    entities.add(terms[term_index - 1])
    
    # 4. Extract monetary amounts using regex
    amount_pattern = r'₹\s*[\d,]+|[\d,]+\s*(?:रूपये|रुपये|रुपए|rupees?|rs\.?)'
    amounts = re.findall(amount_pattern, text_to_process, re.IGNORECASE)
    for amount in amounts:
        entities.add(amount.strip())
                
    extracted_list = list(entities)
    logger.info(f"Extracted entities: {extracted_list}")
    
    # Prioritize entities by relevance to query
    prioritized_entities = prioritize_entities(extracted_list, query)
    
    # Limit to most relevant entities
    return prioritized_entities[:5]  # Return top 5 most relevant entities

def is_common_term(text: str) -> bool:
    """Check if a term is too common to be useful."""
    common_terms = {
        "scheme", "yojana", "योजना", "help", "details", "information",
        "government", "सरकार", "सरकारी", "जानकारी", "मदद", "सहायता"
    }
    return text.lower() in common_terms

def prioritize_entities(entities: List[str], query: str) -> List[str]:
    """Prioritize entities based on relevance to the query and domain context."""
    # Simple scoring based on presence in query and importance
    scored_entities = []
    for entity in entities:
        score = 0
        # Entities present in query get higher priority
        if entity.lower() in query.lower():
            score += 5
            
        # Scheme names get high priority
        if any(term in entity.lower() for term in ["योजना", "scheme", "yojana"]):
            score += 4
            
        # Monetary amounts get high priority
        if re.search(r'₹|रूपये|रुपये|rupees|rs\.?', entity.lower()):
            score += 4
            
        # Category-based scoring
        if any(term in entity.lower() for term in ["पात्रता", "eligibility", "योग्य", "eligible"]):
            score += 3
        if any(term in entity.lower() for term in ["आवेदन", "application", "apply", "process", "प्रक्रिया"]):
            score += 3
        if any(term in entity.lower() for term in ["document", "दस्तावेज", "certificate", "प्रमाण"]):
            score += 2
            
        # Add entity with its score
        scored_entities.append((entity, score))
    
    # Sort by score (descending)
    scored_entities.sort(key=lambda x: x[1], reverse=True)
    
    # Return just the entities, without scores
    return [entity for entity, score in scored_entities]

def regex_entity_extraction(query: str, documents: List[Document]) -> List[str]:
    """Fallback entity extraction using regex patterns when spaCy is unavailable."""
    # Combine text for analysis, limiting document length to avoid processing very large texts
    text = query + "\n" + "\n".join([doc.page_content[:500] for doc in documents])
    entities = set()
    
    # Extract entities using the scheme terminology
    for category, terms in SCHEME_ENTITIES.items():
        for term in terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                entities.add(term)
    
    # Extract scheme names
    scheme_pattern = r'(?:[A-Za-z\s]+\s+)?(?:योजना|scheme|yojana)s?|(?:प्रधानमंत्री|मुख्यमंत्री|PM|CM)\s+[A-Za-z\s]+'
    schemes = re.findall(scheme_pattern, text, re.IGNORECASE)
    for scheme in schemes:
        if len(scheme.strip()) > 5:
            entities.add(scheme.strip())
    
    # Extract monetary amounts
    amount_pattern = r'₹\s*[\d,]+|[\d,]+\s*(?:रूपये|रुपये|रुपए|rupees?|rs\.?)'
    amounts = re.findall(amount_pattern, text, re.IGNORECASE)
    for amount in amounts:
        entities.add(amount.strip())
    
    entity_list = list(entities)
    
    # Prioritize the extracted entities
    prioritized_entities = prioritize_entities(entity_list, query)
    
    return prioritized_entities[:5]  # Return top 5 most relevant entities

def deduplicate_chunks(documents: List[Document]) -> List[Document]:
    """Deduplicates LangChain Documents based on page_content."""
    seen_content = set()
    deduplicated = []
    for doc in documents:
        if doc.page_content not in seen_content:
            deduplicated.append(doc)
            seen_content.add(doc.page_content)
    print(f"Deduplicated {len(documents)} chunks to {len(deduplicated)}.")
    return deduplicated

def enhanced_retrieval_step(input_dict: Dict[str, Any]) -> List[Document]:
    """Performs initial retrieval, entity extraction, follow-up retrieval, and deduplication."""
    query = input_dict["input"]  # The reformulated query from history_aware_retriever
    retriever = get_retriever()  # Get the base retriever
    
    print(f"Enhanced Retrieval: Initial search for query: '{query}'")
    initial_results = retriever.invoke(query)
    print(f"Enhanced Retrieval: Found {len(initial_results)} initial results.")
    
    # Extract domain-specific entities
    entities = extract_key_entities(query, initial_results)
    
    related_chunks = []
    if entities:
        print(f"Enhanced Retrieval: Performing follow-up searches for entities: {entities}")
        for entity in entities:
            # Create contextual follow-up queries based on entity type
            follow_up_query = generate_contextual_follow_up_query(entity)
            print(f"Enhanced Retrieval: Follow-up query: '{follow_up_query}'")
            
            try:
                # Use a slightly smaller k for related searches
                related = retriever.invoke(follow_up_query)
                print(f"Enhanced Retrieval: Found {len(related)} results for entity '{entity}'")
                related_chunks.extend(related)
            except Exception as e:
                print(f"Enhanced Retrieval: Error during follow-up search for entity '{entity}': {e}")
                # Continue with other entities if one fails
        
    # Combine and deduplicate
    all_chunks = initial_results + related_chunks
    final_chunks = deduplicate_chunks(all_chunks)
    print(f"Enhanced Retrieval: Returning {len(final_chunks)} final chunks.")
    
    return final_chunks

def generate_contextual_follow_up_query(entity: str) -> str:
    """Generate a context-appropriate follow-up query based on entity type."""
    
    # Check entity type and build appropriate query
    # For schemes, focus on eligibility and benefits
    if any(keyword in entity.lower() for keyword in ["योजना", "yojana", "scheme", "प्रधानमंत्री", "PM"]):
        return f"{entity} पात्रता लाभ eligibility benefits entitlement documents"
    
    # For benefit types, focus on amount and process
    elif any(keyword in entity.lower() for keyword in ["पेंशन", "pension", "सब्सिडी", "subsidy", "लोन", "loan", "मुआवजा", "compensation"]):
        return f"{entity} राशि amount application process documents procedure"
    
    # For beneficiary categories, focus on available schemes
    elif any(keyword in entity.lower() for keyword in ["किसान", "farmer", "विधवा", "widow", "छात्र", "student", "महिला", "women"]):
        return f"{entity} schemes योजना available eligibility benefits"
    
    # For document types, focus on requirements and procedures
    elif any(keyword in entity.lower() for keyword in ["आधार", "aadhar", "राशन", "ration", "प्रमाण", "certificate"]):
        return f"{entity} requirement application process procedure"
    
    # For monetary amounts, focus on which schemes provide this amount
    elif re.search(r'₹|रूपये|रुपये|rupees|rs\.?', entity.lower()):
        return f"{entity} scheme योजना eligibility criteria who gets"
    
    # For disaster relief, focus on compensation and emergency assistance
    elif any(keyword in entity.lower() for keyword in ["आपदा", "disaster", "बाढ़", "flood", "सूखा", "drought"]):
        return f"{entity} relief राहत compensation emergency assistance"
    
    # Generic follow-up query for other types
    else:
        return f"{entity} entitlement amount procedure documents eligibility welfare scheme योजना"

def create_conversational_rag_chain():
    """
    Builds and returns a conversational RAG chain that considers chat history
    AND uses an enhanced retrieval step.
    """
    llm = get_chat_model()
    # Base retriever is now used *inside* enhanced_retrieval_step
    # retriever = get_retriever()

    # --- Contextualization Prompt (for rephrasing question based on history) ---
    # This prompt helps the LLM understand the flow of conversation.
    CONTEXTUALIZE_Q_SYSTEM_PROMPT = """# Yojna Khojna Question Reformulation System

You help rural and underserved Indian citizens by reformulating their questions for better document retrieval. Many users have limited education and are seeking help with government schemes.

Given the chat history and the latest question:
1. Create a STANDALONE QUERY that retrieval systems can effectively use
2. INCLUDE BOTH Hindi and English terms for key concepts (vajrapat/lightning strike, prakritik aapda/natural calamity)
3. EXPAND the query to capture the likely UNDERLYING NEED for practical assistance
4. PRESERVE location or scheme-specific details mentioned

Remember that behind simple questions are often people in distress looking for concrete help.

DO NOT answer the question - ONLY reformulate it for better document retrieval.

Chat History:
{chat_history}

Latest Question: {input}

Reformulated Question:"""

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CONTEXTUALIZE_Q_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    # --- History-Aware Reformulator (Outputs Reformulated Query) ---
    # We need the reformulated query first. We'll use the LLM part of create_history_aware_retriever.
    # Note: create_history_aware_retriever normally outputs Documents. We need the intermediate query.
    # Let's build the rephrasing chain manually.
    rephrase_chain = contextualize_q_prompt | llm | StrOutputParser()

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

## QUESTION: {input}

## ANSWER:"""
    # NOTE: The {language} variable was removed from the prompt.
    # We also need to pass the original {input} (user question) and {chat_history}.
    # The QA prompt now expects {input}, {chat_history}, and {context}.

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", QA_SYSTEM_PROMPT),
            # Use the *original* human input for the final answer prompt
            MessagesPlaceholder(variable_name="chat_history"), # Pass history to final prompt too
            ("human", "{input}"), # Changed from {question} to {input}
        ]
    )

    # --- Document Combination Chain (Stuff Chain) ---
    # Now needs 'input' and 'chat_history' along with 'context'
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # --- Full Conversational RAG Chain with Enhanced Retrieval ---
    # 1. Prepare input for rephrasing (includes history and latest input)
    # 2. Rephrase the input question using the LLM -> reformulated_query
    # 3. Pass the reformulated_query to the enhanced_retrieval_step -> final_documents
    # 4. Pass the final_documents and the *original* input/history to the question_answer_chain

    conversational_rag_chain = (
        RunnablePassthrough.assign(
            # Step 2: Rephrase based on history
            reformulated_input=rephrase_chain 
        )
        | RunnablePassthrough.assign(
            # Step 3: Retrieve docs using the reformulated input
            context=RunnableLambda(lambda x: enhanced_retrieval_step({"input": x["reformulated_input"]}))
        )
        # Step 4: Generate answer using original input, history, and retrieved context
        | question_answer_chain 
    )

    print("Conversational RAG chain created with history awareness AND enhanced retrieval.")
    return conversational_rag_chain

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