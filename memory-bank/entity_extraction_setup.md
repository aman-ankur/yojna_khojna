# Setting Up Enhanced Entity Extraction

This guide explains how to install and set up the required dependencies for the enhanced entity extraction functionality in Yojna Khojna.

## Installing the Multilingual spaCy Model

The enhanced entity extraction uses the `xx_ent_wiki_sm` multilingual spaCy model, which supports Hindi and other Indian languages. Follow these steps to install it:

### 1. Ensure spaCy is installed

First, make sure spaCy is installed in your environment:

```bash
pip install spacy
```

This dependency is already included in the `requirements.txt` file.

### 2. Download the multilingual model

Download and install the multilingual entity recognition model:

```bash
python -m spacy download xx_ent_wiki_sm
```

This model is much more effective for Hindi text than the default English model.

### 3. Optional: Install the full Hindi model

For even better Hindi language support, you may also install the dedicated Hindi model:

```bash
python -m spacy download hi_core_web_sm
```

Note: In the current implementation, we use `xx_ent_wiki_sm` as it provides good multilingual support while being relatively lightweight.

## Fallback Mechanisms

The enhanced entity extraction includes a robust fallback system that uses regex pattern matching when the spaCy model is unavailable. This ensures the system can still function effectively even if:

- The spaCy model fails to load
- The server environment doesn't have the model installed
- There are memory constraints

The fallback mechanism uses the same dictionary of domain terms and regex patterns, ensuring consistent entity extraction regardless of which method is used.

## Verifying the Installation

To verify that the spaCy model is properly installed and working, you can run:

```python
import spacy
try:
    nlp = spacy.load("xx_ent_wiki_sm")
    print("spaCy model loaded successfully!")
    
    # Test with a Hindi sentence
    doc = nlp("प्रधानमंत्री आवास योजना के लिए कौन पात्र है?")
    print("Entities found:")
    for ent in doc.ents:
        print(f"  - {ent.text} ({ent.label_})")
except Exception as e:
    print(f"Error loading spaCy model: {e}")
```

## Docker Considerations

If running in a Docker environment, you'll need to ensure the spaCy model is installed in the container. Add the following to your Dockerfile:

```dockerfile
# Install spaCy and download the model
RUN pip install spacy && \
    python -m spacy download xx_ent_wiki_sm
```

## Memory Optimization

The multilingual model uses more memory than the English-only model. To optimize memory usage:

1. We limit document text processing to the first 500 characters of each document
2. We only process the most relevant 5 entities for follow-up searches
3. We implement caching for spaCy model loading

These optimizations ensure the enhanced entity extraction performs well even on servers with limited memory. 