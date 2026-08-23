# Enterprise Legal Intelligence Platform (v2)

An isolated, enterprise-grade, on-premises-ready legal intelligence platform and opinion assistant built specifically for the **Law Department of the Government Secretariat**. The platform provides secure data ingestion, semantic search, local LLM-powered auditing, and collaborative workflow management for highly sensitive legal documents.

---

## ⚖️ Project Overview & Workflow

The platform handles highly sensitive legal materials, such as Government Orders, draft bills, policy notes, and court judgments, without transmitting data outside the host machine.

### Core Functional Workflow
1. **Secure Document Ingestion**: Users ingest files (.pdf, .docx, .doc, .txt, .md, .sql) into the system. Native, layout-aware parsing extracts paragraphs and formatted tables, converting tabular data into high-fidelity Markdown representations. Scanned pages automatically trigger local Tesseract OCR.
2. **Dynamic Role-Based Access Control (RBAC)**: Documents are assigned a security clearance. Users can query or retrieve document chunks *only if* their active role clearance is equal to or greater than the document's clearance.
3. **Semantic RAG QA Workspace**: Users engage in context-grounded conversations with a local LLM that retrieves source-cited text passages directly from an on-premises PostgreSQL vector database.
4. **Interactive Opinion Workspace**:
   * **Draft Opinion**: Legal officers draft opinions on legal subjects.
   * **AI Compliance & Risk Audit**: A local LLM automatically audits each draft to flag *Precedent Compliance Issues*, *Conflicts of Interest*, and *Missing Legal References*, and generates a deterministic risk score.
   * **Status Governance Pipeline**: Advisors and Admins review drafted advice and update its status: `Draft` ➔ `Under_Review` ➔ `Approved` or `Rejected`.
   * **Strict Queue Isolation**: Legal Officers can view and track only the status of their own drafted opinions, while Advisors and Admins can inspect the global queue.

### User Role Permissions Matrix

| User Role | Ingestion Clearance Tagging | Retrieval Bounds | Opinion Pipeline Workspace | Admin Dashboard Access |
| :--- | :--- | :--- | :--- | :--- |
| **Legal_Officer** | Locked to `Legal_Officer` clearance | Can only retrieve `Legal_Officer` documents | Draft new opinions; view and track *own* submissions only | ❌ Denied |
| **Senior_Advisor** | Locked to `Senior_Advisor` clearance | Can retrieve `Legal_Officer` and `Senior_Advisor` documents | Transition status (`Under_Review`, `Approved`, `Rejected`) for *all* opinions | ❌ Denied |
| **Admin** | Full dropdown choice (`Legal_Officer`, `Senior_Advisor`, `Admin`) | Full access to all document tiers | Full status management across all opinions | Authorized |

---

## 🧠 Local AI Model Stack (Zero-Leakage Compliance)

To satisfy the Secretariat's enterprise data-protection requirements, all generative reasoning and embedding calculations run locally. No outbound internet telemetry is generated.

1. **Local LLM (`granite4.1:3b`)**:
   * **Purpose**: Generates context-grounded chat responses and evaluates compliance audits in the risk-scoring pipeline.
   * **Hardware Optimization**: Built by IBM with 3 billion parameters, it is optimized for legal-compliance reasoning with a low memory footprint and a low temperature setting (`0.1`) to produce stable output.
2. **Local Embedding Model (`paraphrase-multilingual:278m`)**:
   * **Purpose**: Converts document chunks into dense, 768-dimensional vector embeddings.
   * **Capabilities**: Multilingual support enables high-recall semantic vector matching across English and regional-language texts.

---

## 🛠️ Local Setup & Docker Deployment (Method 1)

This method deploys the entire decoupled platform locally inside a Docker Compose network.

### Prerequisites
Before running the platform, make sure the following tools are installed on your machine:
* **Docker Desktop**:
  * [Download Docker Desktop](https://www.docker.com/products/docker-desktop/) for Windows, macOS, or Linux.
  * *Windows Users*: Ensure WSL2 is installed and enabled (`wsl --install`).
  * Check that Docker is active by running `docker --version` in your terminal.
* **Git**: To clone the repository.

---

### Step-by-Step Installation

#### 1. Clone the Project Repository
Clone the codebase and navigate to the workspace directory:
```bash
git clone https://github.com/Subrata1998Kumar/legal-intelligence-platform/tree/master
cd legal-intelligence-platform
```

#### 2. Navigate to the Deployment Folder
Enter the container deployment directory, which contains the Docker Compose orchestration file:
```bash
cd deployment
```

#### 3. Build and Run the Stack via Docker Compose
Run the following command to download images, install dependencies, and start all microservices:
```bash
docker-compose up -d --build
```

#### What is This Installing?
Docker Compose automatically sets up four separate containerized services on an isolated virtual network bridge:
1. **`lip-db` (PostgreSQL + `pgvector`)**: Boots a database engine, enables the `vector` extension, creates relational tables, and sets up high-speed **HNSW cosine indexing**.
2. **`lip-ollama` (Local Model Server)**: Spins up the offline AI server, running isolated model weights without public API exposure.
3. **`lip-backend` (FastAPI API Service)**: Connects to the database and Ollama. Installs Python parsers (`pdfplumber`, `python-docx`, `pytesseract` OCR), serves API requests, and reads the pre-seeded `users.json` registry on startup to insert the **10 default POC accounts**.
4. **`lip-frontend` (Streamlit UI)**: Exposes the secure, role-restricted dashboard interface.

---

### 4. Pull and Verify Local AI Models

Once the containers are running, download the required local AI model weights into your Ollama container.

**Pull the LLM and Embedding Models:**
```bash
# Pull the IBM Granite legal-reasoning model (3B parameters)
docker exec -it lip-ollama ollama pull granite4.1:3b

# Pull the high-performance multilingual embedding model (278M parameters)
docker exec -it lip-ollama ollama pull paraphrase-multilingual:278m
```

**Verify the Models are Downloaded and Loaded Successfully:**
```bash
# Check Ollama's local model list
docker exec -it lip-ollama ollama list

# Verify the API is healthy on the host machine
curl http://localhost:11434/api/tags
```
Both models (`granite4.1:3b` and `paraphrase-multilingual:278m`) should appear in the terminal output.

---

### 5. Verify Database Initialization & Pre-seeded Users

Confirm that PostgreSQL successfully mounted the schema scripts and pre-seeded your **10 default POC accounts**. Run this query directly inside the database container:

```bash
docker exec -it lip-db psql -U postgres -d postgres -c "SELECT id, username, role FROM users;"
```

Your terminal should display the following pre-configured POC credentials. Each account uses the same value for its username and password, as defined in `users.json`:

| Username | Password | Role Clearance |
| :--- | :--- | :--- |
| `admin` | `admin` | **Admin** |
| `officer_1` | `officer_1` | **Legal_Officer** |
| `officer_2` | `officer_2` | **Legal_Officer** |
| `officer_3` | `officer_3` | **Legal_Officer** |
| `advisor_1` | `advisor_1` | **Senior_Advisor** |
| `advisor_2` | `advisor_2` | **Senior_Advisor** |
| `advisor_3` | `advisor_3` | **Senior_Advisor** |
| `clerk_1` | `clerk_1` | **Legal_Officer** |
| `clerk_2` | `clerk_2` | **Legal_Officer** |
| `review_1` | `review_1` | **Senior_Advisor** |

---

## 🚦 System Validation & Testing

Once the installation is complete, launch the secure user portal:

* **Frontend Web Dashboard**: [http://localhost:8501](http://localhost:8501)
* **Backend API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Detailed Validation Scenarios
To systematically test the role restrictions, multi-format parsing, semantic filters, and session-state isolation, refer to the official validation playbook in the project tree:
👉 [Official POC Validation Playbook](https://github.com/Subrata1998Kumar/legal-intelligence-platform/blob/master/poc-validation-script.md)

---

## ⚠️ Important Hardware Performance Note

> **Please Be Patient**: Because this proof of concept is configured to run **100% locally** to protect data confidentiality, your local CPU/GPU will handle the heavy lifting for multi-format text chunking, document vector embedding, and language model inference.
>
> * **Latency Expectation**: Depending on your system hardware, especially when running on a CPU without dedicated GPU acceleration, operations such as document ingestion and chat queries may take between **10 and 45 seconds**.
> * **Timeouts**: If you encounter a database connection error or an HTTP timeout during your first document upload, please **wait a moment and try again**. The local containers may still be warming up or initializing model weights.
