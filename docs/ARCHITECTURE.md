# AI Learning Management System - Architectural Overview

## 1. Introduction

This document outlines the architecture of the AI Learning Management System (LMS). The system is designed to provide a personalized and efficient learning experience by leveraging AI for content processing, quiz generation, and learning path optimization. It's a web-based application with distinct frontend and backend services, supported by various data stores and AI services.

## 2. Technology Stack

The system utilizes the following technologies:

*   **Frontend**: React (with Vite) + Tailwind CSS
*   **Backend**: Python + FastAPI
*   **Relational Data Store**: PostgreSQL (for structured data like user profiles, course metadata, quiz results)
*   **Vector Data Store**: Pinecone / Qdrant (for storing vector embeddings of knowledge points)
*   **Cache & Message Queue**: Redis
*   **AI Services**:
    *   OpenAI Embeddings API (for knowledge point vectorization)
    *   OpenAI GPT-4 API (for generating test questions, auto-grading, content summarization)
    *   Tesseract OCR (for extracting text from image-based documents)
*   **Object Storage & CDN**: AWS S3 (for storing uploaded documents, static assets) + AWS CloudFront (for content delivery)
*   **DevOps**:
    *   Containerization: Docker
    *   Orchestration: Kubernetes (e.g., AWS EKS)
    *   CI/CD: GitHub Actions
    *   Monitoring: Prometheus + Grafana
    *   Logging: ELK Stack (Elasticsearch, Logstash, Kibana)

## 3. High-Level Architecture Diagram

The following diagram illustrates the main components and their interactions:

```mermaid
graph TD
    User[End User Browser] -->|HTTPS| CDN[AWS CloudFront]
    User -->|HTTPS API Calls| APIGW[API Gateway / Load Balancer]

    CDN -->|Static Assets| S3Frontend[AWS S3 - Frontend Build]
    APIGW -->|Requests| Backend[FastAPI Backend Service on K8s]

    Backend -->|User Data, Metadata| PostgreSQL[PostgreSQL DB]
    Backend -->|Caching, Async Tasks| Redis[Redis]
    Backend -->|Vector Search/Store| VectorDB[Vector Database (Pinecone/Qdrant)]
    Backend -->|Document Storage| S3Docs[AWS S3 - Documents]
    
    Backend -->|Text Embeddings| OpenAIEmbed[OpenAI Embeddings API]
    Backend -->|Question Gen, Grading| OpenAIGPT[OpenAI GPT-4 API]
    Backend -->|OCR Processing| Tesseract[Tesseract OCR Service/Lambda]

    GitHub -->|CI/CD Triggers| GitHubActions[GitHub Actions]
    GitHubActions -->|Deploy| K8s[Kubernetes Cluster]
    GitHubActions -->|Build & Push Images| DockerRegistry[Docker Registry (e.g., ECR)]

    K8s -->|Metrics| Prometheus[Prometheus]
    Prometheus -->|Visualization| Grafana[Grafana]
    K8s -->|Logs| ELK[ELK Stack]

    subgraph "User Interface"
        User
    end

    subgraph "Content Delivery & Edge"
        CDN
    end
    
    subgraph "Application Layer (K8s)"
        APIGW
        Backend
        Tesseract % Assuming Tesseract might be a separate service if heavy
    end

    subgraph "Data Stores"
        PostgreSQL
        VectorDB
        Redis
    end

    subgraph "AI Services (External)"
        OpenAIEmbed
        OpenAIGPT
    end

    subgraph "Storage (AWS)"
        S3Frontend
        S3Docs
    end

    subgraph "DevOps & Monitoring"
        GitHub
        GitHubActions
        DockerRegistry
        K8s
        Prometheus
        Grafana
        ELK
    end
```

**Key Interactions:**

*   Users interact with the React SPA served via CloudFront (from S3).
*   The SPA makes API calls to the FastAPI backend.
*   The backend handles business logic, interacting with PostgreSQL for primary data, Redis for caching/queuing, and the Vector Database for semantic search on knowledge points.
*   For AI tasks, the backend calls OpenAI APIs and uses Tesseract OCR.
*   Documents are stored in S3.
*   DevOps tools manage the build, deployment, and monitoring of the system.

## 4. Component Descriptions

*   **Frontend (React SPA)**: The user interface, built as a single-page application. Handles user interactions, displays learning content, and communicates with the backend API.
*   **Backend API (Python/FastAPI)**: The core application logic. Provides RESTful APIs for the frontend, manages users, documents, learning paths, quizzes, and integrates with AI services and data stores.
*   **PostgreSQL**: Primary relational database storing structured data like user accounts, document metadata, learning path structures, quiz scores, and relationships between entities.
*   **Vector Database (Pinecone/Qdrant)**: Stores vector embeddings of document content (knowledge points). Enables semantic search and similarity matching for finding relevant information and building learning paths.
*   **Redis**: In-memory data store used for caching frequently accessed data (e.g., user sessions, popular content) and as a message broker for asynchronous tasks (e.g., document processing after upload).
*   **AI Services**:
    *   **OpenAI Embeddings API**: Converts text chunks (knowledge points) into numerical vector representations.
    *   **OpenAI GPT-4 API**: Used for generating diverse quiz questions (multiple choice, short answer, essay), providing automated grading assistance for subjective questions, and potentially summarizing content.
    *   **Tesseract OCR**: Extracts text from uploaded image files or image-based PDFs, making their content searchable and processable.
*   **AWS S3 & CloudFront**:
    *   **S3 (Simple Storage Service)**: Used to store user-uploaded documents (PDFs, Word docs, images) and the static built assets of the frontend application.
    *   **CloudFront**: Content Delivery Network (CDN) to serve the frontend static assets and potentially cached S3 content globally with low latency.
*   **DevOps Infrastructure**:
    *   **Docker**: Containerizes the frontend and backend applications for consistent environments.
    *   **Kubernetes (K8s)**: Orchestrates containerized applications, managing deployment, scaling, and networking. AWS EKS is a potential managed service.
    *   **GitHub Actions**: Automates CI/CD pipelines (build, test, lint, deploy).
    *   **Prometheus & Grafana**: Collect metrics and provide dashboards for monitoring system health and performance.
    *   **ELK Stack**: Centralized logging solution for collecting, searching, and analyzing logs from all services.

## 5. Data Flow Examples (Conceptual)

### 5.1. User Registration/Login

1.  **Frontend**: User submits registration/login form.
2.  **Backend API**: Receives credentials.
    *   **Registration**: Hashes password, creates user record in PostgreSQL.
    *   **Login**: Validates credentials against PostgreSQL, generates JWT tokens (access & refresh).
3.  **Frontend**: Stores JWT tokens, updates UI to authenticated state.

### 5.2. Document Upload and Processing

1.  **Frontend**: User selects and uploads a file (PDF, DOCX, image).
2.  **Backend API**: Receives file.
    *   Stores raw file to **AWS S3**.
    *   (Async Task via Redis Queue):
        1.  If image or PDF with images: Use **Tesseract OCR** to extract text.
        2.  Parse text content (identify chapters, sections, paragraphs).
        3.  For each relevant chunk (knowledge point):
            *   Call **OpenAI Embeddings API** to get vector embedding.
            *   Store knowledge point metadata in **PostgreSQL** (linking to original document).
            *   Store embedding in **Vector Database** (Pinecone/Qdrant) with reference to PostgreSQL KP ID.
        4.  Update document status in **PostgreSQL** (e.g., to 'completed' or 'failed').
3.  **Frontend**: Polls for status or receives notification (e.g., via WebSockets later) about processing completion.

### 5.3. Generating a Quiz for a Knowledge Point

1.  **Frontend**: User requests a quiz for a specific knowledge point.
2.  **Backend API**: Receives request.
    *   Retrieves knowledge point details (summary, content) from **PostgreSQL**.
    *   Constructs a prompt for **OpenAI GPT-4 API** including the content/summary and desired question types/difficulty.
    *   Sends prompt to GPT-4 API.
3.  **OpenAI GPT-4 API**: Generates quiz questions and answers.
4.  **Backend API**: Receives generated quiz, formats it, and sends it to the frontend.
    *   (Optionally) Stores generated questions in a temporary cache (Redis) or a dedicated question bank table in PostgreSQL for reuse.
5.  **Frontend**: Displays the quiz questions to the user.

---
This architecture is designed to be scalable, maintainable, and leverage modern AI capabilities for an enhanced learning experience.
