#!/usr/bin/env python3
"""
Manual Test Script for Entity Extraction

This script allows testing the entity extraction functionality in the RAG pipeline
with real-world examples to verify it's working correctly.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path for easier imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.rag.chain import extract_key_entities, extract_key_entities_ner, generate_contextual_follow_up_query
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_entity_extraction_with_examples():
    """Test entity extraction with sample queries and document passages."""
    
    # Sample test cases
    test_cases = [
        {
            "name": "Housing Scheme Query",
            "query": "प्रधानमंत्री आवास योजना में कितना पैसा मिलता है?",
            "documents": [
                Document(page_content="प्रधानमंत्री आवास योजना (PMAY) के तहत शहरी क्षेत्रों में मकान निर्माण के लिए ₹2.5 लाख की सहायता प्रदान की जाती है।"),
                Document(page_content="ग्रामीण क्षेत्रों में PMAY-G के अंतर्गत ₹1.20 लाख तक की राशि मिलती है।")
            ]
        },
        {
            "name": "Farmer Support Query",
            "query": "PM Kisan Yojana benefits for small farmers in Bihar",
            "documents": [
                Document(page_content="PM-KISAN Scheme provides small and marginal farmers with up to 2 hectares land with Rs. 6,000 per year in three installments."),
                Document(page_content="In Bihar, over 50 lakh farmers have benefited from PM Kisan Samman Nidhi Yojana.")
            ]
        },
        {
            "name": "Disaster Relief Query",
            "query": "बाढ़ पीड़ितों के लिए सरकारी सहायता",
            "documents": [
                Document(page_content="राष्ट्रीय आपदा राहत कोष (NDRF) से बाढ़ पीड़ितों को ₹3,200 प्रति परिवार की तत्काल सहायता राशि प्रदान की जाती है।"),
                Document(page_content="गंभीर रूप से क्षतिग्रस्त घरों के लिए ₹95,100 तक की आर्थिक सहायता उपलब्ध है।")
            ]
        },
        {
            "name": "Mixed Hindi/English Query",
            "query": "Widow pension scheme के लिए क्या documents चाहिए?",
            "documents": [
                Document(page_content="विधवा पेंशन योजना के लिए आधार कार्ड, राशन कार्ड, बैंक खाता विवरण और मृत्यु प्रमाण पत्र की आवश्यकता होती है।"),
                Document(page_content="National Social Assistance Programme provides Rs. 500 per month to widows under Widow Pension Scheme.")
            ]
        }
    ]
    
    # Run tests for each case
    for test_case in test_cases:
        logger.info(f"\n{'='*80}\nTesting: {test_case['name']}\n{'='*80}")
        logger.info(f"Query: {test_case['query']}")
        logger.info("Documents:")
        for i, doc in enumerate(test_case['documents']):
            logger.info(f"  Doc {i+1}: {doc.page_content[:100]}...")
        
        # Extract entities using the complete function
        entities = extract_key_entities(test_case['query'], test_case['documents'])
        logger.info(f"\nExtracted Entities ({len(entities)}):")
        for entity in entities:
            logger.info(f"  • '{entity}'")
            
            # Generate follow-up query for each entity
            follow_up = generate_contextual_follow_up_query(entity)
            logger.info(f"    → Follow-up Query: '{follow_up}'")
        
        # Also test the NER-specific function
        combined_text = test_case['query'] + " " + " ".join([doc.page_content for doc in test_case['documents']])
        ner_entities = extract_key_entities_ner(combined_text)
        logger.info(f"\nNER-Specific Entities ({len(ner_entities)}):")
        for entity in ner_entities:
            logger.info(f"  • '{entity['text']}' ({entity['type']})")

def test_language_detection():
    """Test language detection for mixed queries."""
    queries = [
        "What are documents needed for PM Kisan?",
        "प्रधानमंत्री किसान योजना के लिए क्या दस्तावेज़ चाहिए?",
        "PM Kisan के लिए documents क्या हैं?",
        "How to apply for आवास योजना?",
        "बाढ़ relief के लिए compensation कितना मिलता है?"
    ]
    
    logger.info("\n\nLanguage Detection Test\n" + "="*80)
    for query in queries:
        # Simple language detection heuristic (similar to what we use in main.py)
        language = "en"  # Default
        if any(char in query for char in "अआइईउऊएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"):
            language = "hi"
            
        logger.info(f"Query: {query}")
        logger.info(f"Detected Language: {language}")

def main():
    """Run the test script."""
    logger.info("Running Entity Extraction Test Script")
    
    # Test entity extraction
    test_entity_extraction_with_examples()
    
    # Test language detection
    test_language_detection()
    
    logger.info("\nTests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 