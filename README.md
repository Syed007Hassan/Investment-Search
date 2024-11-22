# Company Search & Ranking System with Hybrid Search

## Overview
This application implements an advanced company search and ranking system using a hybrid search approach that combines vector similarity search (using PgVector) and traditional full-text search in PostgreSQL. This dual approach ensures both semantic relevance and keyword accuracy in search results, making it particularly effective for company discovery and ranking.

## Description
The system leverages a sophisticated hybrid search architecture that:
- Uses OpenAI embeddings to convert company descriptions into vector representations
- Implements PostgreSQL's full-text search capabilities for keyword matching
- Combines both approaches with a weighted scoring system for optimal ranking
- Utilizes Groq's LLM for intelligent search result processing and summarization

This hybrid approach provides more accurate and contextually relevant results compared to traditional keyword-only search systems.

## Technologies Used
- **Backend**: FastAPI
- **Database**: PostgreSQL with pgvector extension
- **Vector Embeddings**: OpenAI API
- **LLM Processing**: Groq
- **Frontend**: React
- **Containerization**: Docker
- **ORM**: SQLAlchemy

## Key Features
- Hybrid search combining vector similarity and full-text search
- Real-time company ranking based on search relevance
- Company information management (add/search)
- Asynchronous streaming responses
- Docker-based deployment
- Intelligent result summarization using Groq

## Getting Started

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- Groq API key

### Quick Start with Docker Compose

1. Clone the repository:
   ```bash
   git clone **https://github.com/Syed007Hassan/Investment-Search.git**
   cd Backend
   ```

2. Create a `.env` file in the root directory:
   ```bash
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000