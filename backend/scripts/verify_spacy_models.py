#!/usr/bin/env python3
"""
SpaCy Model Verification Script for Yojna Khojna

This script verifies that the required spaCy models are properly installed
and accessible for the entity extraction functionality in the Yojna Khojna backend.
"""

import sys
import importlib
import subprocess
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

REQUIRED_MODELS = [
    "en_core_web_sm",  # English model
    "xx_ent_wiki_sm",  # Multilingual entity recognition model
    "hi_core_web_sm",  # Hindi model (if available)
]

def check_spacy_installation():
    """Verify spaCy is installed."""
    try:
        import spacy
        logger.info(f"spaCy version {spacy.__version__} is installed")
        return True
    except ImportError:
        logger.error("spaCy is not installed. Please install it with: pip install spacy")
        return False

def check_model_installation(model_name):
    """Check if a specific spaCy model is installed and loadable."""
    try:
        importlib.import_module(model_name)
        logger.info(f"✅ {model_name} is installed and importable")
        
        # Try to load the model to verify it works
        import spacy
        nlp = spacy.load(model_name)
        test_text = "Pradhan Mantri Awas Yojana provides ₹2.5 lakh for housing"
        doc = nlp(test_text)
        logger.info(f"   Successfully processed text with {model_name}")
        
        return True
    except ImportError:
        logger.warning(f"❌ {model_name} is not importable")
        return False
    except OSError as e:
        logger.error(f"❌ {model_name} found but failed to load: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error loading {model_name}: {e}")
        return False

def install_model(model_name):
    """Attempt to install a missing spaCy model."""
    logger.info(f"Attempting to install {model_name}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "spacy", "download", model_name],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Installation successful: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Installation failed: {e.stderr}")
        return False

def main():
    """Main verification function."""
    if not check_spacy_installation():
        logger.error("Please install spaCy first")
        sys.exit(1)
    
    all_models_present = True
    for model_name in REQUIRED_MODELS:
        if not check_model_installation(model_name):
            all_models_present = False
            
            # Ask user if they want to install the missing model
            if input(f"Would you like to install {model_name}? (y/n): ").lower() == 'y':
                if install_model(model_name):
                    # Verify installation was successful
                    if check_model_installation(model_name):
                        logger.info(f"Successfully installed {model_name}")
                    else:
                        logger.error(f"Failed to verify {model_name} after installation")
                else:
                    logger.error(f"Failed to install {model_name}")
            else:
                logger.warning(f"Skipping installation of {model_name}")
    
    if all_models_present:
        logger.info("✅ All required spaCy models are installed and working properly!")
        return 0
    else:
        logger.warning("⚠️ Some spaCy models are missing or not working properly")
        logger.info("Please install the missing models manually with:\n" + 
                   "\n".join([f"python -m spacy download {model}" for model in REQUIRED_MODELS]))
        return 1

if __name__ == "__main__":
    sys.exit(main()) 