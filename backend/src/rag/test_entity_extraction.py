"""
Script to test the enhanced entity extraction functionality.

Run this script to verify that:
1. The multilingual spaCy model is correctly installed
2. Entity extraction works for both Hindi and English queries
3. The fallback mechanism works when spaCy is unavailable

Usage:
    python -m backend.src.rag.test_entity_extraction
"""

import sys
import logging
from langchain_core.documents import Document

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import entity extraction functions
try:
    from chain import extract_key_entities, get_spacy_nlp, SCHEME_ENTITIES, generate_contextual_follow_up_query
except ImportError:
    # Handle case when run as script
    sys.path.append(".")
    try:
        from backend.src.rag.chain import extract_key_entities, get_spacy_nlp, SCHEME_ENTITIES, generate_contextual_follow_up_query
    except ImportError:
        logger.error("Could not import functions from chain.py. Make sure you're running from the correct directory.")
        sys.exit(1)

def test_spacy_model():
    """Test if the spaCy model is properly installed and loaded."""
    logger.info("Testing spaCy model loading...")
    
    nlp = get_spacy_nlp()
    if nlp is None:
        logger.warning("❌ spaCy model could not be loaded")
        logger.info("Please install the model with: python -m spacy download xx_ent_wiki_sm")
        return False
    
    logger.info(f"✅ Successfully loaded spaCy model: {nlp.meta['name']}, version {nlp.meta['version']}")
    
    # Test with a Hindi sentence
    test_text = "प्रधानमंत्री आवास योजना के लिए कौन पात्र है?"
    doc = nlp(test_text)
    
    logger.info(f"Testing NER on Hindi text: '{test_text}'")
    entities = [ent.text for ent in doc.ents]
    
    if entities:
        logger.info(f"✅ Found entities: {entities}")
    else:
        logger.warning("⚠️ No entities found in the Hindi text. This may be normal depending on the model.")
    
    return True

def test_entity_extraction():
    """Test the extract_key_entities function with different queries."""
    test_cases = [
        {
            "name": "Hindi scheme query",
            "query": "प्रधानमंत्री आवास योजना के लिए कौन पात्र है?",
            "documents": [
                Document(page_content="प्रधानमंत्री आवास योजना (PMAY) के तहत लाभार्थी को ₹1,20,000 की राशि मिलती है।"),
                Document(page_content="आवास योजना के लिए आवेदक के पास पक्का मकान नहीं होना चाहिए।")
            ]
        },
        {
            "name": "English scheme query",
            "query": "How to apply for PM Kisan scheme?",
            "documents": [
                Document(page_content="To apply for PM Kisan Samman Nidhi, farmers need Aadhaar card, bank account, and land records."),
                Document(page_content="The scheme provides ₹6,000 annually to farmers in three installments.")
            ]
        },
        {
            "name": "Mixed language query",
            "query": "विधवा पेंशन कितनी मिलती है in Bihar?",
            "documents": [
                Document(page_content="बिहार में विधवा पेंशन योजना के अंतर्गत ₹400 प्रति माह मिलता है।"),
                Document(page_content="Widow pension in Bihar is ₹400 per month under social welfare schemes.")
            ]
        },
        {
            "name": "Disaster relief query",
            "query": "बाढ़ में फसल बर्बाद होने पर क्या मुआवज़ा मिलेगा?",
            "documents": [
                Document(page_content="प्राकृतिक आपदा से फसल नष्ट होने पर किसानों को मुआवजा दिया जाता है।"),
                Document(page_content="बाढ़ के कारण फसल नष्ट होने पर प्रति हेक्टेयर ₹6,800 का मुआवजा मिलता है।")
            ]
        }
    ]
    
    logger.info("\nTesting entity extraction with different queries:")
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\nTest Case {i}: {test_case['name']}")
        logger.info(f"Query: {test_case['query']}")
        
        entities = extract_key_entities(test_case['query'], test_case['documents'])
        
        logger.info(f"Extracted entities: {entities}")
        
        if entities:
            logger.info("✅ Successfully extracted entities")
            
            # Test contextual follow-up query generation
            for entity in entities[:2]:  # Only show first two for brevity
                follow_up = generate_contextual_follow_up_query(entity)
                logger.info(f"Follow-up query for '{entity}': '{follow_up}'")
        else:
            logger.warning("❌ No entities extracted")

def main():
    """Main function to run all tests."""
    logger.info("=" * 50)
    logger.info("ENTITY EXTRACTION TEST SCRIPT")
    logger.info("=" * 50)
    
    spacy_available = test_spacy_model()
    logger.info("\n" + "=" * 50)
    
    if not spacy_available:
        logger.info("Testing with fallback mechanism (regex-based extraction)...")
    
    # Test entity dictionary
    logger.info(f"\nDomain Dictionary contains {len(SCHEME_ENTITIES)} categories:")
    for category in SCHEME_ENTITIES:
        term_count = len(SCHEME_ENTITIES[category])
        logger.info(f"  - {category}: {term_count} terms")
    
    logger.info("\n" + "=" * 50)
    
    # Test actual entity extraction
    test_entity_extraction()
    
    logger.info("\n" + "=" * 50)
    logger.info("TEST COMPLETED")
    logger.info("=" * 50)

if __name__ == "__main__":
    main() 