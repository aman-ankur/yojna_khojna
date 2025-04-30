#!/usr/bin/env python3
"""
Test script for the conversational RAG chain.
This ensures that the chain is correctly handling all parameters including the language parameter.
"""

from src.rag.chain import test_conversational_rag_chain
import time
import sys

if __name__ == "__main__":
    print("=" * 80)
    print("YOJNA KHOJNA RAG CHAIN TEST")
    print("=" * 80)
    print("\nThis test verifies that the conversational RAG chain:")
    print("1. Accepts and processes queries in both English and Hindi")
    print("2. Properly handles the language parameter")
    print("3. Correctly processes financial information queries with verification")
    print("4. Returns well-formatted responses according to the prompt guidelines")
    print("\nStarting test...")
    
    start_time = time.time()
    success = test_conversational_rag_chain()
    end_time = time.time()
    
    print("\n" + "=" * 80)
    if success:
        print(f"✅ TEST PASSED in {end_time - start_time:.2f} seconds")
        print("The conversational RAG chain is working correctly!")
    else:
        print(f"❌ TEST FAILED after {end_time - start_time:.2f} seconds")
        print("Please check the errors above and fix the issues.")
        sys.exit(1)
    print("=" * 80) 