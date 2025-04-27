"""Unit tests for RAG utility functions."""

import pytest
from langchain_core.documents import Document

# Assuming the utils file is in backend/src/rag/
# Adjust the import path based on your project structure and how pytest discovers tests
from backend.src.rag.utils import (
    extract_key_entities,
    deduplicate_chunks,
    format_response,
    KEY_ENTITIES # Import for potential use in tests if needed
)

# --- Tests for extract_key_entities ---

def test_extract_key_entities_no_docs():
    """Test entity extraction with an empty list of documents."""
    assert extract_key_entities([]) == set()

def test_extract_key_entities_no_matches():
    """Test entity extraction when documents contain no predefined entities."""
    docs = [Document(page_content="Some random text without relevant keywords.")]
    assert extract_key_entities(docs) == set()

def test_extract_key_entities_single_match_english():
    """Test finding a single English entity."""
    docs = [Document(page_content="Information about disaster compensation.")]
    assert extract_key_entities(docs) == {"disaster", "compensation"} # Matches are lowercased

def test_extract_key_entities_single_match_hindi():
    """Test finding a single Hindi entity."""
    docs = [Document(page_content="योजना की पात्रता (patrata) क्या है?")]
    assert extract_key_entities(docs) == {"patrata"}

def test_extract_key_entities_multiple_matches_mixed_case():
    """Test finding multiple entities with mixed casing."""
    docs = [
        Document(page_content="Need details on Abua Awaas Yojana amount."),
        Document(page_content="What is the PROCEDURE for Prakritik Aapda relief?")
    ]
    expected_entities = {"abua awaas yojana", "amount", "procedure", "prakritik aapda"}
    assert extract_key_entities(docs) == expected_entities

def test_extract_key_entities_partial_words_ignored():
    """Test that partial words matching entities are ignored due to word boundaries."""
    docs = [Document(page_content="This document mentions documentation but not the entity.")]
    # "documentation" should not match "document" because of the regex word boundaries
    assert extract_key_entities(docs) == set()

def test_extract_key_entities_duplicates_in_docs():
    """Test that duplicate entities across documents result in a unique set."""
    docs = [
        Document(page_content="Need compensation details."),
        Document(page_content="More info on compensation (muavja).")
    ]
    assert extract_key_entities(docs) == {"compensation", "muavja"}

# --- Tests for deduplicate_chunks ---

def test_deduplicate_chunks_empty_list():
    """Test deduplication with an empty list."""
    assert deduplicate_chunks([]) == []

def test_deduplicate_chunks_no_duplicates():
    """Test deduplication when all documents are unique."""
    docs = [
        Document(page_content="Content A"),
        Document(page_content="Content B"),
        Document(page_content="Content C"),
    ]
    assert deduplicate_chunks(docs) == docs

def test_deduplicate_chunks_with_duplicates():
    """Test deduplication when some documents have identical content."""
    doc1 = Document(page_content="Content A")
    doc2 = Document(page_content="Content B")
    doc3 = Document(page_content="Content A") # Duplicate of doc1
    doc4 = Document(page_content="Content C")
    docs = [doc1, doc2, doc3, doc4]
    expected_docs = [doc1, doc2, doc4]
    assert deduplicate_chunks(docs) == expected_docs

def test_deduplicate_chunks_all_duplicates():
    """Test deduplication when all documents are identical."""
    doc1 = Document(page_content="Content X")
    doc2 = Document(page_content="Content X")
    doc3 = Document(page_content="Content X")
    docs = [doc1, doc2, doc3]
    expected_docs = [doc1]
    assert deduplicate_chunks(docs) == expected_docs

def test_deduplicate_chunks_metadata_ignored():
    """Test that deduplication only considers page_content."""
    doc1 = Document(page_content="Content A", metadata={"source": "doc1"})
    doc2 = Document(page_content="Content B", metadata={"source": "doc2"})
    doc3 = Document(page_content="Content A", metadata={"source": "doc3"}) # Different metadata
    docs = [doc1, doc2, doc3]
    expected_docs = [doc1, doc2] # doc3 is removed as content matches doc1
    assert deduplicate_chunks(docs) == expected_docs


# --- Tests for format_response ---

def test_format_response_no_amount():
    """Test formatting when the response contains no monetary amount."""
    response = "Please visit the local office for details."
    assert format_response(response, language="en") == response
    assert format_response(response, language="hi") == response

def test_format_response_amount_already_prominent_en():
    """Test formatting when amount is already in the first sentence (English)."""
    response = "You can get ₹4,00,000 as compensation. Apply at the Tehsil office."
    assert format_response(response, language="en") == response

def test_format_response_amount_already_prominent_hi():
    """Test formatting when amount is already in the first sentence (Hindi)."""
    response = "आपको ₹4,00,000 मिल सकते हैं। तहसील कार्यालय में आवेदन करें।"
    assert format_response(response, language="hi") == response

def test_format_response_amount_needs_highlighting_en():
    """Test formatting when amount needs to be moved to the front (English)."""
    response = "The scheme provides support. The maximum amount is ₹50,000. Contact the BDO."
    expected = "You may be eligible for an amount of ₹50,000. The scheme provides support. The maximum amount is ₹50,000. Contact the BDO."
    assert format_response(response, language="en") == expected

def test_format_response_amount_needs_highlighting_hi():
    """Test formatting when amount needs to be moved to the front (Hindi)."""
    response = "यह योजना सहायता प्रदान करती है। अधिकतम राशि ₹50,000 है। बीडीओ से संपर्क करें।"
    expected = "आपको ₹50,000 की राशि मिल सकती है। यह योजना सहायता प्रदान करती है। अधिकतम राशि ₹50,000 है। बीडीओ से संपर्क करें।"
    assert format_response(response, language="hi") == expected

def test_format_response_multiple_amounts_needs_highlighting():
    """Test formatting highlights the *first* found amount if needed."""
    response = "Support includes ₹10,000 for seeds and ₹25,000 for equipment."
    # Amount is already in the first sentence part, so no reformatting needed
    assert format_response(response, language="en") == response

    response_needs_reformat = "First apply, then you get ₹10,000, later maybe ₹25,000."
    expected_en = "You may be eligible for an amount of ₹10,000. First apply, then you get ₹10,000, later maybe ₹25,000."
    expected_hi = "आपको ₹10,000 की राशि मिल सकती है। First apply, then you get ₹10,000, later maybe ₹25,000."
    assert format_response(response_needs_reformat, language="en") == expected_en
    assert format_response(response_needs_reformat, language="hi") == expected_hi

def test_format_response_amount_with_commas_and_decimals():
    """Test formatting with amounts containing commas and decimals."""
    response = "The total grant is ₹1,50,000.50 for this phase."
    # Already prominent
    assert format_response(response, language="en") == response

    response_needs_reformat = "Submit form X. You will receive ₹1,50,000.50 later."
    expected_en = "You may be eligible for an amount of ₹1,50,000.50. Submit form X. You will receive ₹1,50,000.50 later."
    assert format_response(response_needs_reformat, language="en") == expected_en
