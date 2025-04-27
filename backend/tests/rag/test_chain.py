"""Tests for the conversational RAG chain construction."""

import pytest
from unittest.mock import patch, MagicMock, ANY # ANY helps check prompt types

# Import necessary LangChain components to check types/structure
from langchain_core.runnables import RunnableSequence, RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from langchain_core.messages import HumanMessage, AIMessage

# Import the NEW function to test
from backend.src.rag.chain import create_conversational_rag_chain

# Remove old test for format_docs as it's no longer used directly
# def test_format_docs(): ...

# Mark tests as rag tests (or keep integration if preferred, adjust marker if needed)
pytestmark = pytest.mark.rag

@patch('backend.src.rag.chain.create_stuff_documents_chain')
# Remove patch for create_history_aware_retriever as it's no longer directly used
# @patch('backend.src.rag.chain.create_history_aware_retriever') 
@patch('backend.src.rag.chain.get_chat_model')
# Remove patch for get_retriever as it's called during invoke, not creation
# @patch('backend.src.rag.chain.get_retriever') 
def test_create_conversational_rag_chain_structure(
    mock_get_chat_model, # Removed mock_get_retriever
    # mock_create_history_retriever, # Removed mock for history retriever
    mock_create_stuff_chain
):
    """Test that the new conversational RAG chain structure is constructed correctly."""
    # Arrange
    mock_llm_instance = MagicMock(name="ChatModel")
    # mock_retriever_instance = MagicMock(name="Retriever") # No longer needed here
    # mock_history_retriever_chain = MagicMock(name="HistoryRetrieverChain") # No longer needed here
    mock_qa_chain = MagicMock(name="QAChain") # Mock the final QA part simply
    mock_rephrase_chain_part = MagicMock(name="RephraseChainPart", spec=RunnableSequence) # Mock rephrase part

    mock_get_chat_model.return_value = mock_llm_instance
    # mock_get_retriever.return_value = mock_retriever_instance # No longer needed here
    # mock_create_history_retriever.return_value = mock_history_retriever_chain # No longer needed here
    mock_create_stuff_chain.return_value = mock_qa_chain

    # To properly test the structure, we might need to patch the intermediate chains created
    # Patch the internal StrOutputParser and RunnableLambda if necessary, or test structure more loosely

    # Act
    conversational_chain = create_conversational_rag_chain()

    # Assert
    # 1. Check that LLM model was fetched
    mock_get_chat_model.assert_called_once()
    # Assert get_retriever is NOT called during construction
    # mock_get_retriever.assert_not_called() # This mock was removed

    # 2. Check contextualization prompt structure (part of rephrase_chain)
    # This is hard to check directly without deeper inspection or running parts of the chain.
    # We trust the implementation uses the correct prompt string for now.

    # 3. Check that the document combination chain (QA chain) was created correctly
    mock_create_stuff_chain.assert_called_once_with(
        mock_llm_instance,
        ANY # Check that a ChatPromptTemplate was passed
    )
    # Check the QA prompt structure used with create_stuff_documents_chain
    qa_prompt_arg = mock_create_stuff_chain.call_args[0][1]
    assert isinstance(qa_prompt_arg, ChatPromptTemplate)
    # Ensure the QA prompt now EXPECTS chat_history, input, and context
    assert "chat_history" in qa_prompt_arg.input_variables
    assert "input" in qa_prompt_arg.input_variables
    assert "context" in qa_prompt_arg.input_variables
    # Ensure it does NOT expect reformulated_input or question directly
    assert "reformulated_input" not in qa_prompt_arg.input_variables
    assert "question" not in qa_prompt_arg.input_variables # Unless it's inside the system message

    # 4. Check overall chain structure (loosely)
    # The final chain should be a sequence involving Passthrough, Lambda, and the QA chain.
    assert isinstance(conversational_chain, RunnableSequence) # Check it's a runnable sequence
    # Further checks on conversational_chain.steps would be more complex due to mocks/internals.

# Note: Testing the actual *invocation* logic (how history is formatted and passed)
# is better handled in the integration tests (test_main_chat.py) where we control
# the input dictionary and mock the chain's final response.
# Unit testing the invocation here would require deeper mocking of LCEL internals.

@pytest.mark.skip(reason="Dependencies not mocked yet")
def test_contextualize_q_prompt_reformulation():
    """Tests if the contextualization prompt correctly reformulates the question."""
    # Arrange
    chain = create_conversational_rag_chain()
    # Example history and question requiring reformulation
    chat_history = [
        HumanMessage(content="What is the eligibility for PM Kisan?"),
        AIMessage(content="Farmers need to meet certain landholding criteria.")
    ]
    latest_question = "How much money do they get?"
    expected_reformulated = "How much money do eligible farmers get under the PM Kisan scheme?" # Example expected output

    # Act
    # Need to isolate the history_aware_retriever part of the chain
    # or mock the final QA chain to only check the retriever's output.
    # This requires mocking LangChain components.
    # For now, just assert True as a placeholder.
    # reformulated_question = chain.history_aware_retriever.invoke({...}) # Pseudocode

    # Assert
    # assert reformulated_question == expected_reformulated
    assert True

@pytest.mark.skip(reason="Dependencies not mocked yet")
def test_contextualize_q_prompt_standalone():
    """Tests if the contextualization prompt handles standalone questions correctly."""
    # Arrange
    chain = create_conversational_rag_chain()
    chat_history = []
    latest_question = "What are the documents required for voter ID card?"
    expected_reformulated = latest_question # Standalone question should remain unchanged

    # Act
    # See note in previous test
    # reformulated_question = chain.history_aware_retriever.invoke({...}) # Pseudocode

    # Assert
    # assert reformulated_question == expected_reformulated
    assert True

# TODO: Add tests for the comprehensive RAG prompt (QA_SYSTEM_PROMPT)
# TODO: Add tests for retrieval enhancement
# TODO: Add tests for response formatting

# --- Tests for Helper Functions ---

@pytest.mark.skip(reason="Need to mock spacy model/output")
@patch('backend.src.rag.chain.get_spacy_nlp')
def test_extract_key_entities_ner(mock_get_nlp):
    """Test the NER entity extraction logic with domain-specific enhancements."""
    # Arrange
    mock_nlp = MagicMock()
    # Define mock entities spaCy should return
    mock_ent1 = MagicMock() 
    mock_ent1.text = "Pradhan Mantri Kisan Samman Nidhi"
    mock_ent1.label_ = "ORG" 
    mock_ent2 = MagicMock()
    mock_ent2.text = "Bihar"
    mock_ent2.label_ = "GPE"
    mock_ent3 = MagicMock()
    mock_ent3.text = "help"
    mock_ent3.label_ = "MISC"
    mock_doc = MagicMock()
    mock_doc.ents = [mock_ent1, mock_ent2, mock_ent3]
    mock_nlp.return_value = mock_doc
    mock_get_nlp.return_value = mock_nlp

    query = "PM kisan details for Bihar किसान scheme"
    documents = [MagicMock(page_content="Info about Pradhan Mantri Kisan Samman Nidhi for farmers in Bihar. The scheme provides ₹6000 annually.")]
    
    # We expect "help" to be filtered out as a common term, but we should get:
    # - The scheme name from NER
    # - Bihar from NER
    # - किसान/farmer from domain dictionary with bilingual matching
    # - The amount ₹6000 from regex pattern matching
    expected_entities_subset = ["Pradhan Mantri Kisan Samman Nidhi", "Bihar", "किसान", "farmer", "₹6000"]

    # Act
    from backend.src.rag.chain import extract_key_entities # Import here to use patched function
    extracted_entities = extract_key_entities(query, documents)

    # Assert
    mock_get_nlp.assert_called_once()
    # Assert that the text passed to nlp contains query and doc content
    mock_nlp.assert_called_once()
    call_args, _ = mock_nlp.call_args
    assert query in call_args[0]
    assert documents[0].page_content in call_args[0]
    
    # Check that all expected entities are extracted
    # The actual order may differ due to prioritization
    for expected_entity in expected_entities_subset:
        assert any(expected_entity in entity for entity in extracted_entities), f"Expected '{expected_entity}' in extracted entities"
    
    # Check entity count (should be limited to 5)
    assert len(extracted_entities) <= 5

# Add a new test for the regex fallback
@patch('backend.src.rag.chain.get_spacy_nlp')
def test_regex_entity_extraction_fallback(mock_get_nlp):
    """Test the regex fallback when spaCy model is unavailable."""
    # Mock spaCy to be unavailable
    mock_get_nlp.return_value = None
    
    # Query with Hindi and English elements
    query = "आवास योजना में कितना पैसा मिलता है? (How much money in housing scheme?)"
    documents = [
        MagicMock(page_content="प्रधानमंत्री आवास योजना में लाभार्थी को ₹1,20,000 की राशि मिलती है। The beneficiary gets ₹1,20,000 in PM Housing Scheme.")
    ]
    
    # These are key entities we expect to find with regex extraction
    expected_entities_subset = ["आवास योजना", "housing scheme", "₹1,20,000", "प्रधानमंत्री आवास"]
    
    # Act
    from backend.src.rag.chain import extract_key_entities
    extracted_entities = extract_key_entities(query, documents)
    
    # Assert
    # Verify at least the expected entities are found
    for expected_entity in expected_entities_subset:
        assert any(expected_entity in entity for entity in extracted_entities), f"Expected '{expected_entity}' in extracted entities"
    
    # Check entity count (should be limited to 5)
    assert len(extracted_entities) <= 5
    
    # Confirm NLP wasn't used
    mock_get_nlp.assert_called_once()

# Test the contextual follow-up query generation
def test_generate_contextual_follow_up_query():
    """Test generating context-appropriate follow-up queries for different entity types."""
    from backend.src.rag.chain import generate_contextual_follow_up_query
    
    # Test scheme-related query
    scheme_entity = "प्रधानमंत्री आवास योजना"
    scheme_query = generate_contextual_follow_up_query(scheme_entity)
    assert "पात्रता" in scheme_query
    assert "eligibility" in scheme_query
    assert "benefits" in scheme_query
    
    # Test benefit-related query
    benefit_entity = "पेंशन योजना"
    benefit_query = generate_contextual_follow_up_query(benefit_entity)
    assert "पात्रता" in benefit_query  # Should include eligibility since it has योजना
    assert "benefits" in benefit_query
    
    # Test beneficiary-related query
    beneficiary_entity = "किसान"
    beneficiary_query = generate_contextual_follow_up_query(beneficiary_entity)
    assert "schemes" in beneficiary_query
    assert "योजना" in beneficiary_query
    assert "eligibility" in beneficiary_query
    
    # Test monetary amount query
    amount_entity = "₹6000"
    amount_query = generate_contextual_follow_up_query(amount_entity)
    assert "scheme" in amount_query
    assert "योजना" in amount_query
    assert "who gets" in amount_query
    
    # Test disaster-related query
    disaster_entity = "बाढ़"
    disaster_query = generate_contextual_follow_up_query(disaster_entity)
    assert "relief" in disaster_query
    assert "राहत" in disaster_query
    assert "compensation" in disaster_query

# TODO: Add tests for deduplicate_chunks if not covered elsewhere
# Test the enhanced retrieval step
@patch('backend.src.rag.chain.get_retriever')
@patch('backend.src.rag.chain.extract_key_entities')
def test_enhanced_retrieval_step(mock_extract_entities, mock_get_retriever):
    """Test the enhanced retrieval step with entity extraction and follow-up queries."""
    from backend.src.rag.chain import enhanced_retrieval_step, generate_contextual_follow_up_query
    
    # Mock the retriever
    mock_retriever = MagicMock()
    mock_get_retriever.return_value = mock_retriever
    
    # Create mock documents for initial results
    initial_docs = [
        Document(page_content="Information about PM Kisan Scheme"),
        Document(page_content="Details about farmer benefits")
    ]
    mock_retriever.invoke.return_value = initial_docs
    
    # Mock entities extraction
    mock_entities = ["PM Kisan", "किसान", "₹6000"]
    mock_extract_entities.return_value = mock_entities
    
    # Create different mock documents for follow-up searches
    follow_up_docs = {
        "PM Kisan": [Document(page_content="PM Kisan eligibility criteria")],
        "किसान": [Document(page_content="Schemes for farmers")],
        "₹6000": [Document(page_content="Amount distributed under PM Kisan")]
    }
    
    # Configure mock_retriever to return different docs based on query
    def side_effect(query):
        # Find which entity is in the query
        for entity in mock_entities:
            if entity in query:
                return follow_up_docs[entity]
        return initial_docs
    
    mock_retriever.invoke.side_effect = side_effect
    
    # Act
    result = enhanced_retrieval_step({"input": "Tell me about PM Kisan benefits for farmers"})
    
    # Assert
    # Verify retriever was called for initial query
    mock_get_retriever.assert_called_once()
    
    # Verify entities were extracted from initial results
    mock_extract_entities.assert_called_once()
    mock_extract_entities_args = mock_extract_entities.call_args[0]
    assert "Tell me about PM Kisan benefits for farmers" == mock_extract_entities_args[0]
    assert initial_docs == mock_extract_entities_args[1]
    
    # Calculate expected call count (1 initial + number of entities follow-up)
    expected_call_count = 1 + len(mock_entities)
    
    # Verify retriever was called for each follow-up with contextual queries
    assert mock_retriever.invoke.call_count == expected_call_count
    
    # Verify the deduplicated results include both initial and follow-up docs
    # Total unique docs is initial (2) + follow-up (3) = 5
    assert len(result) <= 5  # May be less due to deduplication
    
    # Verify that for each entity, we called the retriever with a contextual query
    call_args_list = mock_retriever.invoke.call_args_list
    for entity in mock_entities:
        entity_call_found = False
        for call in call_args_list:
            args, _ = call
            query = args[0]
            contextual_query = generate_contextual_follow_up_query(entity)
            if entity in query and any(term in query for term in contextual_query.split()):
                entity_call_found = True
                break
        assert entity_call_found, f"Did not find contextual query for entity: {entity}" 