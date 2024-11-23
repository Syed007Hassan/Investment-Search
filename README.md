# Company Search & Ranking System with Hybrid Search

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