# Company Search & Ranking System with Hybrid Search

<img width="1354" alt="image" src="https://github.com/user-attachments/assets/ee369f55-6585-4888-8418-007487a48f8f">

## Overview
This application implements an advanced company search and ranking system using a hybrid search approach that combines vector similarity search (using PgVector) and traditional full-text search in PostgreSQL. This dual approach ensures both semantic relevance and keyword accuracy in search results, making it particularly effective for company discovery and ranking.

## Description
The system leverages a sophisticated hybrid search architecture that:
- Uses OpenAI embeddings to convert company descriptions into vector representations
- Implements PostgreSQL's full-text search capabilities for keyword matching
- Combines both approaches with a weighted scoring system for optimal ranking
- Utilizes GPT-4o for intelligent search result processing and summarization
- Utilizes Redis for caching frequently accessed data to improve performance

This hybrid approach provides more accurate and contextually relevant results compared to traditional keyword-only search systems.

## Technologies Used
- **Backend**: FastAPI
- **Database**: PostgreSQL with pgvector extension, Redis for caching
- **Vector Embeddings**: OpenAI API
- **LLM Processing**: GPT-4o
- **Frontend**: React
- **Containerization**: Docker
- **ORM**: SQLAlchemy

## Key Features
- Hybrid search combining vector similarity and full-text search
- Real-time company ranking based on search relevance
- Company information management (add/search) and retrieval
- LLM powered tool calling
- Docker-based application deployment

## Getting Started

### Prerequisites
- Docker and Docker Compose
- OpenAI API key (for embeddings generation and LLM processing)

### Environment Setup

1. Create a `.env` file in the Backend directory with the following variables:
   ```bash
   DATABASE_NAME=your_database_name
   DATABASE_USER=your_database_user
   DATABASE_PASSWORD=your_database_password
   DATABASE_URL=localhost
   DATABASE_PORT=5432
   OPENAI_API_KEY=your_openai_api_key
   ```

### Quick Start with Docker Compose

1. Clone the repository:
   ```bash
   git clone https://github.com/Syed007Hassan/Investment-Search.git
   cd Backend
   ```

2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

Note: The default docker-compose configuration does not include initial data loading. If you want to load initial sample data, you can modify the command in docker-compose.yml to:
   ```yaml
   command: >
     bash -c "
       python scripts/load_data.py &&
       uvicorn main:app --host 0.0.0.0 --port 8000 --reload
     "
   ```
   If you don't want to load initial sample data, you can modify the command in docker-compose.yml to:
   ```yaml
   command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Technical Implementation

### Hybrid Search Architecture

The system implements a sophisticated hybrid search approach combining two powerful search methodologies:

1. **Vector Similarity Search (Semantic Search)**
   - Uses OpenAI's text-embedding-3-small model to convert company descriptions into 1536-dimensional vectors
   - Stores these vectors in PostgreSQL using the pgvector extension
   - Enables semantic understanding of search queries

2. **Full-Text Search (Keyword Search)**
   - Utilizes PostgreSQL's built-in full-text search capabilities
   - Performs exact and partial keyword matching

### Search & Ranking Process

Let's break down this hybrid search query step by step:

1. **First CTE (Common Table Expression) - Vector Search:**
   ```sql
   WITH vector_search AS (
       SELECT id, 
              RANK () OVER (ORDER BY embedding <=> :embedding) AS rank
       FROM "Company"
       ORDER BY embedding <=> :embedding
       LIMIT 20
   )
   ```
   - Creates a temporary result set named `vector_search`
   - `embedding <=> :embedding`: Calculates cosine distance between stored embeddings and query embedding
   - `RANK() OVER`: Assigns ranks based on similarity (lower distance = better rank)
   - `LIMIT 20`: Takes top 20 most similar vectors
   - Vector distance ranges from 0-2, where 0 means vectors are identical and 2 means opposite

2. **Second CTE - Full-text Search:**
   ```sql
   fulltext_search AS (
       SELECT id, 
              RANK () OVER (ORDER BY ts_rank_cd(to_tsvector('english', content), query) DESC) 
       FROM "Company", 
            plainto_tsquery('english', :query) query
       WHERE to_tsvector('english', content) @@ query
       ORDER BY ts_rank_cd(to_tsvector('english', content), query) DESC
       LIMIT 20
   )
   ```
   - Creates another temporary result set named `fulltext_search`
   - `to_tsvector('english', content)`: Converts content to searchable tokens
   - `plainto_tsquery('english', :query)`: Converts search query to search terms
   - `@@`: Text search match operator
   - `ts_rank_cd`: Calculates text search relevancy score (higher score means better match)
   - `LIMIT 20`: Takes top 20 best text matches

3. **Final Combined Query:**
   ```sql
   SELECT
       COALESCE(vector_search.id, fulltext_search.id) AS id,
       COALESCE(1.0 / (:k + vector_search.rank), 0.0) +
       COALESCE(1.0 / (:k + fulltext_search.rank), 0.0) AS score
   FROM vector_search
   FULL OUTER JOIN fulltext_search ON vector_search.id = fulltext_search.id
   ORDER BY score DESC
   LIMIT 20
   ```
   - `FULL OUTER JOIN`: Combines results from both searches, keeping all matches from either
   - `COALESCE` for IDs: Ensures we capture matches from either search method
   - `COALESCE` for scoring: Handles cases where an item only matches one search type (defaults to 0)
   - Score calculation uses k=60 as normalization factor to:
     - Prevent division by zero
     - Normalize scores to a comparable range
     - Reduce impact of small rank differences
   - `ORDER BY score DESC`: Ranks final results by combined score
   - `LIMIT 20`: Returns top 20 combined results

**Ranking Process:**
1. Vector ranking:
   - Lower cosine distance = better rank
   - Score = 1/(60 + rank)
   - Example: Rank 1 = 1/61 ≈ 0.0164
   - Lower distance is better because:
     - Cosine distance measures how far apart two vectors are in high-dimensional space
     - Distance of 0: Vectors are identical (perfect semantic match)
     - Distance of 1: Vectors are perpendicular (unrelated content)
     - Distance of 2: Vectors point in opposite directions (opposite meaning)
     - Therefore, smaller distances indicate closer semantic similarity

2. Text ranking:
   - Higher ts_rank_cd = better rank
   - Score = 1/(60 + rank)
   - Example: Rank 2 = 1/62 ≈ 0.0161
   - Higher ts_rank_cd is better because:
     - It counts the number of matching terms
     - Considers term frequency (how often terms appear)
     - Weighs term proximity (how close terms are to each other)
     - Accounts for term importance in the document
     - Therefore, more matches and better quality matches result in higher scores

3. Final ranking:
   - Combined score = vector_score + text_score
   - Higher combined score = better overall match
   - Normalization ensures fair combination despite different scoring scales

### Example
Consider the following example to illustrate the ranking process:

- Item A: vector_rank=1, text_rank=2
  - Score = 1/61 + 1/62 ≈ 0.0328
- Item B: vector_rank=5, text_rank=1
  - Score = 1/65 + 1/61 ≈ 0.0317
- Result: Item A ranks higher than Item B

This hybrid approach ensures that results are ranked considering both semantic similarity (vectors) and keyword relevance (text), providing a more comprehensive search result.

### Demo

https://github.com/user-attachments/assets/bce8fc3b-45ef-4ae7-b94e-aad6b4dcc089


