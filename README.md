# conversational-ai-helper-tools
A library of tools to help with conversational-ai development


## EmbeddingIOFile User Guide

### Motivation
The EmbeddingIOFile class provides a standardized way to store and retrieve text embeddings along with their associated text data. This is particularly useful for:

- Persisting embeddings generated from language models
- Storing metadata about the embeddings
- Managing large collections of text-embedding pairs
- Maintaining a simple, human-readable file format

### File Format
The file format follows a structured pattern with distinct sections:

```
BEGIN META

{
    "JSON formatted metadata"
}

END META

BEGIN EMBEDDING

[0.1, 0.2, 0.3, ...] // Vector representation

END EMBEDDING

BEGIN PAYLOAD

Your actual text content goes here

END PAYLOAD
```

Multiple embedding-payload pairs can exist in a single file, following the same pattern.

### Basic Usage
#### Writing Embeddings

```python
from pathlib import Path
from conversational_ai_helper_tools.embedding_io_file import EmbeddingIOFile

# Create metadata
metadata = {
    "model": "text-embedding-ada-002",
    "version": "1.0",
    "created_at": "2024-03-04"
}

# Create embedding-text pairs
embeddings = [
    ([0.1, 0.2, 0.3], "This is the first text"),
    ([0.4, 0.5, 0.6], "This is the second text")
]

# Write to file
file_path = Path("embeddings.eio")
EmbeddingIOFile.dump(file_path, metadata, embeddings)
```

#### Reading Embeddings

```python
from pathlib import Path
from conversational_ai_helper_tools.embedding_io_file import EmbeddingIOFile

# Read from file
file_path = Path("embeddings.eio")
metadata, embeddings = EmbeddingIOFile.parse(file_path)

# Access the data
print(f"Metadata: {metadata}")
for embedding, text in embeddings:
    print(f"Text: {text}")
    print(f"Embedding vector: {embedding[:5]}...")  # Show first 5 values
```

#### Sequential Writing

```python
from pathlib import Path
from conversational_ai_helper_tools.embedding_io_file import EmbeddingIOFile

# Initialize file with metadata
file_path = Path("embeddings.eio")
eio_file = EmbeddingIOFile(file_path, metadata={"version": "1.0"})

# Add embeddings one at a time
eio_file.write_text_data([0.1, 0.2, 0.3], "First text")
eio_file.write_text_data([0.4, 0.5, 0.6], "Second text")
```

### Best Practices
Always include relevant metadata (model information, creation date, etc.)
Use descriptive file paths with the .eio extension
Handle the file paths using the Path object from pathlib
Close files properly (the class handles this automatically)
Use error handling when reading files that might not exist

### File Format Details
- **META**: JSON-formatted metadata about the embeddings
- **EMBEDDING**: List of floating-point numbers representing the embedding vector
- **PAYLOAD**: The actual text content associated with the embedding
- Each section is clearly marked with BEGIN and END tags
- Multiple newlines (\n) separate sections for readability