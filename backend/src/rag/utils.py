"""Utility functions for the RAG pipeline."""

import re
from typing import List, Set
from langchain_core.documents import Document

# Define known key entities/concepts, including bilingual terms
# This list should be expanded based on common query patterns and scheme details
KEY_ENTITIES = [
    "vajrapat", "lightning strike",
    "prakritik aapda", "natural calamity", "disaster",
    "compensation", "muavja",
    "eligibility", "patrata",
    "document", "dastavez",
    "apply", "aavedan",
    "procedure", "prakriya",
    "amount", "rashi",
    "deadline", "antim tithi",
    "contact", "sampark",
    "office", "karyalay",
    "abua awaas yojana", # Example specific scheme
    # Add more common scheme names, locations, or concepts here
]

# Compile regex pattern for efficiency
# Using word boundaries (\b) to match whole words/phrases
# Case-insensitive matching (?i)
ENTITY_REGEX = re.compile(r"\b(" + "|".join(re.escape(e) for e in KEY_ENTITIES) + r")\b", re.IGNORECASE)

def extract_key_entities(documents: List[Document]) -> Set[str]:
    """
    Extracts predefined key entities from the content of retrieved documents
    using a simple regex approach.

    Args:
        documents: A list of LangChain Document objects from initial retrieval.

    Returns:
        A set of unique entities found in the documents' content.
    """
    found_entities: Set[str] = set()
    if not documents:
        return found_entities

    combined_text = " ".join([doc.page_content for doc in documents])
    matches = ENTITY_REGEX.findall(combined_text)

    # Normalize to lowercase for uniqueness
    found_entities.update(match.lower() for match in matches)
    print(f"Found entities for secondary search: {found_entities}")
    return found_entities

def deduplicate_chunks(documents: List[Document]) -> List[Document]:
    """
    Removes duplicate documents from a list based on page content.

    Args:
        documents: A list of LangChain Document objects.

    Returns:
        A list of unique Document objects.
    """
    unique_docs = []
    seen_content = set()
    for doc in documents:
        if doc.page_content not in seen_content:
            unique_docs.append(doc)
            seen_content.add(doc.page_content)
    print(f"Deduplicated chunks: {len(documents)} -> {len(unique_docs)}")
    return unique_docs

def format_response(llm_response: str, language: str = "en") -> str:
    """
    Formats the LLM response to prioritize practical information,
    specifically highlighting monetary amounts if present but not prominent.

    Args:
        llm_response: The raw string response from the LLM.
        language: The language code ('en' or 'hi') for formatting. Defaults to 'en'.

    Returns:
        The potentially reformatted response string.
    """
    # Extract entitlement amounts with regex (finds ₹ symbol followed by digits/commas)
    amounts = re.findall(r'₹\s*[\d,]+(?:\.\d+)?', llm_response) # Added optional decimal part

    # Check if amounts exist and the first sentence doesn't already contain one
    # Uses a simple split by '.' and checks the first part. Might need refinement
    # for more complex sentence structures or languages without '.' sentence terminators.
    first_sentence = llm_response.split('.')[0]
    if amounts and not re.search(r'₹\s*[\d,]+(?:\.\d+)?', first_sentence):
        # Restructure to highlight the first found entitlement amount at the beginning
        if language == "hi":
            prefix = f"आपको {amounts[0]} की राशि मिल सकती है।"
        else: # Default to English or handle other languages if needed
            prefix = f"You may be eligible for an amount of {amounts[0]}."

        formatted_response = f"{prefix} {llm_response}"
        print(f"Response reformatted for language '{language}' to highlight amount: {amounts[0]}")
        return formatted_response
    else:
        # Return original response if no amount found or if already prominent
        return llm_response
