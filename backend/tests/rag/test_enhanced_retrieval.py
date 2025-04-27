import unittest
from unittest.mock import patch, MagicMock
import pytest
from backend.src.rag.chain import enhanced_retrieval_step

class TestEnhancedRetrieval(unittest.TestCase):
    
    @patch('backend.src.rag.chain.extract_key_entities')
    @patch('backend.src.rag.chain.get_retriever')
    def test_enhanced_retrieval_end_to_end(self, mock_get_retriever, mock_extract_entities):
        """Test the complete enhanced retrieval pipeline."""
        # Setup mock for entity extraction
        mock_extract_entities.return_value = [
            "Pradhan Mantri Awas Yojana",
            "₹2.5 lakh"
        ]
        
        # Setup mock for document search
        mock_docs = [MagicMock(page_content=f"Doc {i}") for i in range(5)]
        
        # Setup retriever mock
        mock_retriever = MagicMock()
        mock_get_retriever.return_value = mock_retriever
        
        # Configure the retriever to return different documents based on the call order
        mock_retriever.invoke.side_effect = [
            mock_docs[:3],  # Initial search results
            [mock_docs[3]],  # Results for first entity
            [mock_docs[4]]   # Results for second entity
        ]
        
        # Test query
        query = "What benefits do I get under Pradhan Mantri Awas Yojana?"
        
        # Call enhanced retrieval
        retrieved_docs = enhanced_retrieval_step({"input": query})
        
        # Verify the pipeline execution
        mock_get_retriever.assert_called_once()
        self.assertEqual(mock_retriever.invoke.call_count, 3, "Should perform initial search plus one per entity")
        mock_extract_entities.assert_called_once()
        
        # Verify results - we should have some documents returned
        self.assertTrue(len(retrieved_docs) > 0, "Should return some results from searches")
    
    @patch('backend.src.rag.chain.extract_key_entities')
    @patch('backend.src.rag.chain.get_retriever')
    def test_enhanced_retrieval_no_entities(self, mock_get_retriever, mock_extract_entities):
        """Test retrieval when no entities are found."""
        # Setup mocks
        mock_extract_entities.return_value = []
        mock_docs = [MagicMock(page_content=f"Doc {i}") for i in range(3)]
        
        # Setup retriever mock
        mock_retriever = MagicMock()
        mock_get_retriever.return_value = mock_retriever
        mock_retriever.invoke.return_value = mock_docs
        
        # Test query
        query = "Tell me about government schemes"
        
        # Call enhanced retrieval
        retrieved_docs = enhanced_retrieval_step({"input": query})
        
        # Verify execution
        mock_get_retriever.assert_called_once()
        mock_extract_entities.assert_called_once()
        self.assertEqual(mock_retriever.invoke.call_count, 1, "Should only perform initial search")
        
        # Verify results - should return initial search results
        self.assertEqual(len(retrieved_docs), 3, "Should return only initial search results")
    
    @patch('backend.src.rag.chain.extract_key_entities')
    @patch('backend.src.rag.chain.get_retriever')
    def test_enhanced_retrieval_deduplication(self, mock_get_retriever, mock_extract_entities):
        """Test that duplicate documents are properly removed."""
        # Setup mocks
        mock_extract_entities.return_value = [
            "Pradhan Mantri Awas Yojana"
        ]
        
        # Create documents with some duplicates (same page_content)
        doc1 = MagicMock(page_content="Housing scheme details")
        doc2 = MagicMock(page_content="Eligibility criteria")
        doc3 = MagicMock(page_content="Housing scheme details")  # Duplicate of doc1
        
        # Setup retriever mock
        mock_retriever = MagicMock()
        mock_get_retriever.return_value = mock_retriever
        mock_retriever.invoke.side_effect = [
            [doc1, doc2],  # Initial search
            [doc3]          # Entity search (duplicate)
        ]
        
        # Test query
        query = "Housing scheme details"
        
        # Call enhanced retrieval
        retrieved_docs = enhanced_retrieval_step({"input": query})
        
        # Verify deduplication
        self.assertTrue(len(retrieved_docs) < 3, "Should deduplicate documents with same content")
        self.assertTrue(all(isinstance(d, MagicMock) for d in retrieved_docs), "Should return MagicMock objects") 