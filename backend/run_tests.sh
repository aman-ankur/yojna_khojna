#!/bin/bash
# Test Runner Script for Yojna Khojna Backend

set -e  # Exit on error

# Terminal colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== Yojna Khojna Backend Test Runner =====${NC}"

# Ensure we're in the backend directory
cd "$(dirname "$0")"
echo -e "${YELLOW}Running tests from $(pwd)${NC}"

# Check for Python environment
if [ -d "venv" ] || [ -d "../venv" ]; then
  echo -e "${GREEN}✓ Python virtual environment found${NC}"
else
  echo -e "${YELLOW}⚠ No virtual environment found. Creating one...${NC}"
  python -m venv venv
  echo -e "${GREEN}✓ Created virtual environment${NC}"
  source venv/bin/activate
  pip install -r requirements.txt
fi

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
  if [ -d "venv" ]; then
    source venv/bin/activate
  elif [ -d "../venv" ]; then
    source ../venv/bin/activate
  fi
  echo -e "${GREEN}✓ Activated virtual environment${NC}"
fi

# Verify spaCy models
echo -e "\n${BLUE}Verifying spaCy models...${NC}"
if [ -f "scripts/verify_spacy_models.py" ]; then
  python scripts/verify_spacy_models.py
else
  echo -e "${YELLOW}⚠ SpaCy verification script not found${NC}"
fi

# Run the unit tests first
echo -e "\n${BLUE}Running unit tests...${NC}"
python -m pytest tests/rag/test_chain.py tests/main/test_format_response.py -v

# Run the integration tests
echo -e "\n${BLUE}Running integration tests...${NC}"
python -m pytest tests/rag/test_enhanced_retrieval.py tests/integration/test_main_chat.py -v

# Run a comprehensive test of the entity extraction functionality
echo -e "\n${BLUE}Testing entity extraction...${NC}"
if [ -f "scripts/test_entity_extraction.py" ]; then
  python scripts/test_entity_extraction.py
else
  echo -e "${YELLOW}⚠ Entity extraction test script not found${NC}"
fi

echo -e "\n${GREEN}===== All tests completed! =====${NC}" 