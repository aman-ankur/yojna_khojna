# Enhanced Entity Extraction Strategy for Yojna Khojna

This document outlines the enhanced domain-specific entity extraction approach for Yojna Khojna to better serve our rural and underserved Indian audience.

## Motivation

The existing entity extraction approach has several limitations:
- Uses an English-only spaCy model (`en_core_web_sm`) that can't effectively recognize Hindi entities
- Only extracts generic entity types (ORG, PERSON, GPE, LOC, MISC) that don't capture domain-specific government scheme concepts
- Uses basic filtering that doesn't account for the specialized vocabulary in welfare schemes
- Lacks awareness of bilingual terms and synonyms

## Enhanced Approach

Our enhanced entity extraction strategy includes:

1. **Multilingual Model Support**: Replacing the English-only model with `xx_ent_wiki_sm` to better support Hindi entities

2. **Comprehensive Domain Dictionary**: A categorized dictionary covering all government scheme domains:
   - Social welfare (housing, etc.)
   - Healthcare benefits
   - Education support
   - Employment programs
   - Agricultural assistance
   - Utilities and subsidies
   - Disaster relief
   - Special category benefits
   - Financial assistance terms
   - Document requirements
   - Authorities and offices
   - Procedural terms

3. **Multi-Strategy Extraction**:
   - Standard NER from spaCy for general entities
   - Pattern matching for scheme names and common formats
   - Dictionary lookup for domain-specific terms
   - Special handling for monetary amounts
   - Bilingual equivalence matching (Hindi-English term pairs)

4. **Entity Prioritization**:
   - Scoring based on presence in original query
   - Higher weights for scheme names and monetary amounts
   - Contextual relevance to eligibility, application process, and documentation

5. **Graceful Degradation**:
   - Fallback to regex pattern matching when spaCy is unavailable
   - Ensures entity extraction works even with minimal dependencies

## Enhanced Follow-up Queries

The extracted entities are used to build more effective follow-up queries:
- Scheme-specific queries focus on eligibility and benefits
- Benefit-specific queries focus on amounts and application processes
- Beneficiary-specific queries focus on available schemes
- Context-aware query formulation based on entity type

## Implementation

The implementation replaces the existing `extract_key_entities` function in `backend/src/rag/chain.py` with a more comprehensive version that:
1. Uses domain-specific dictionaries for entity extraction
2. Handles bilingual entity matching
3. Prioritizes entities based on relevance to government schemes
4. Constructs more contextual follow-up queries

This enhancement significantly improves the RAG system's ability to find relevant information for users' queries about government welfare schemes, especially when user queries contain Hindi terms or domain-specific terminology. 