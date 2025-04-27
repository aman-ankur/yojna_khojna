# spaCy Model Installation Guide

Instructions for installing and verifying the required spaCy models for Yojna Khojna.

## Required Models

- xx_ent_wiki_sm (multilingual entity recognition)
- en_core_web_sm (English language model)
- hi_core_web_sm (Hindi language model, if available)

## Installation Instructions

```bash
# With the virtual environment activated
python -m spacy download xx_ent_wiki_sm
python -m spacy download en_core_web_sm
python -m spacy download hi_core_web_sm  # Optional
```

## Verification

Run the verification script to check model installation:

```bash
python backend/scripts/verify_spacy_models.py
```

## Troubleshooting

If you encounter issues with model installation:

1. Ensure you have the correct Python environment activated
2. Check for internet connectivity issues
3. Verify you have permission to install packages
4. Try installing with pip directly:
   ```bash
   pip install https://github.com/explosion/spacy-models/releases/download/xx_ent_wiki_sm-3.5.0/xx_ent_wiki_sm-3.5.0-py3-none-any.whl
   ```

## Docker Configuration

If using Docker, ensure your Dockerfile includes these installations:

```dockerfile
# Install spaCy models
RUN python -m spacy download xx_ent_wiki_sm
RUN python -m spacy download en_core_web_sm
``` 