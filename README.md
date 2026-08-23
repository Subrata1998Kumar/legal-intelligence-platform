# Sovereign Legal Intelligence Platform (v2)

An isolated, enterprise-grade, on-premise-ready legal intelligence platform and opinion assistant built specifically for the **Law Department of the Government Secretariat**. The platform provides secure, data-sovereign ingestion, semantic search, local LLM-powered auditing, and collaborative workflow management for highly sensitive legal documents.

---

## ⚖️ Project Overview & Workflow

The platform handles highly sensitive legal materials—such as Government Orders, draft bills, policy notes, and court judgments—without transmitting data outside the host machine. 

### Core Functional Workflow
1. **Secure Document Ingestion**: Users ingest files (.pdf, .docx, .doc, .txt, .md, .sql) into the system. Native layout-aware parsing extracts paragraphs and formatted tables, converting tabular data into high-fidelity Markdown representations. Scanned pages automatically trigger local Tesseract OCR.
2. **Dynamic Role-Based Access Control (RBAC)**: Documents are stamped with a security clearance. Users can query or retrieve document chunks *only if* their active role clearance is equal to or greater than the document's clearance.
3. **Semantic RAG QA Workspace**: Users engage in context-grounded conversations with a local LLM, which retrieves source-cited text passages directly from an on-premise PostgreSQL vector database.
4. **Interactive Opinion Workspace**:
   * **Draft Opinion**: Legal officers draft opinions on legal subjects.
   * **AI Compliance & Risk Audit**: The draft is automatically audited by a local LLM to flag *Precedent Compliance Issues*, *Conflicts of Interest*, and *Missing Legal References*, generating a deterministic Risk Score.
   * **Status Governance Pipeline**: Advisors and Admins review the drafted advice and update status levels: `Draft` ➔ `Under_Review` ➔ `Approved` or `Rejected`. 
   * **Strict Queue Isolation**: Legal Officers can only view and track the status of their own drafted opinions, whereas Advisors and Admins inspect the global queue.

### User Role Permissions Matrix

| User Role | Ingestion Clearance Tagging | Retrieval Bounds | Opinion Pipeline Workspace | Admin Dashboard Access |
| :--- | :--- | :--- | :--- | :--- |
| **Legal_Officer** | Locked to `Legal_Officer` clearance | Can only retrieve `Legal_Officer` documents | Draft new opinions; view and track *own* submissions only | ❌ Denied |
| **Senior_Advisor** | Locked to `Senior_Advisor` clearance | Can retrieve `Legal_Officer` and `Senior_Advisor` documents | Transition status (`Under_Review`, `Approved`, `Rejected`) for *all* opinions | ❌ Denied |
| **Admin** | Full dropdown choice (`Legal_Officer`, `Senior_Advisor`, `Admin`) | Full access to all document tiers | Full status management across all opinions |  Authorized |

---

## 🧠 Local AI Model Stack (Zero-Leakage Compliance)

To strictly satisfy the data sovereignty mandates of the Secretariat, all generative reasoning and embedding calculations run locally. No outbound internet telemetry is generated.

1. **Local LLM (`granite4.1:3b`)**: 
   * **Purpose**: Generates context-grounded chat responses and evaluates compliance audits in the risk-scoring pipeline.
   * **Hardware Optimization**: Built with a 3-billion-parameter architecture by IBM, optimized for legal-compliance reasoning with low memory footprint and locked to a low temperature (`0.1`) to ensure stable, non-hallucinatory output.
2. **Local Embedding Model (`paraphrase-multilingual:278m`)**: 
   * **Purpose**: Converts document chunks into dense 768-dimensional mathematical vector embeddings.
   * **Capabilities**: Multilingual support allows high-recall semantic vector matching across English and localized regional texts.

---

## 🛠️ Local Setup & Docker Deployment (Method 1)

This method deploys the entire decoupled platform locally inside a Docker Compose network.

### Prerequisites
Before running, make sure you have the following installed on your machine:
* **Docker Desktop**: 
  * [Download Docker Desktop](https://www.docker.com/products/docker-desktop/) for Windows, macOS, or Linux.
  * *Windows Users*: Ensure WSL2 is installed and enabled (`wsl --install`).
  * Check that Docker is active by running `docker --version` in your terminal.
* **Git**: To clone the repository.

---

### Step-by-Step Installation

#### 1. Clone the Project Repository
Clone the codebase and navigate into the workspace directory:
```bash
git clone https://github.com/Subrata1998Kumar/legal-intelligence-platform/tree/master
cd legal-intelligence-platform
```

#### 2. Navigate to the Deployment Folder
Enter the container deployment directory where the docker-compose orchestrator sits:
```bash
cd deployment
```

#### 3. Build and Run the Stack via Docker Compose
Run the following command to download images, install dependencies, and spin up all microservices:
```bash
docker-compose up -d --build
```

#### What is This Installing?
Docker Compose automatically sets up 4 separate containerized layers on an isolated virtual network bridge:
1. **`lip-db` (PostgreSQL + `pgvector`)**: Boots a database engine, enables the `vector` extension, creates relational tables, and sets up high-speed **HNSW cosine indexing**.
2. **`lip-ollama` (Local Model Server)**: Spins up the offline AI server, running isolated model weights without public API exposure.
3. **`lip-backend` (FastAPI API Service)**: Connects to the database and Ollama. Installs Python parsers (`pdfplumber`, `python-docx`, `pytesseract` OCR) and serves endpoint requests. It also reads the pre-seeded `users.json` registry on boot to insert the **6 default POC accounts**.
4. **`lip-frontend` (Streamlit UI)**: Exposes the secure, role-restricted dashboard interface.

---

### 4. Pull and Verify Local AI Models

Once the containers are running, download the exact localized AI weights into your Ollama container.

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

Confirm that PostgreSQL successfully mounted your schema scripts and pre-seeded your **6 default POC accounts**. Run this query directly inside the database container:

```bash
docker exec -it lip-db psql -U postgres -d postgres -c "SELECT id, username, role FROM users;"
```

Your terminal should display the following pre-configured POC credentials (all accounts are configured with the password `password`):

| Username | Password | Role Clearance |
| :--- | :--- | :--- |
| `admin` | `password` | **Admin** |
| `advisor_sara` | `password` | **Senior_Advisor** |
| `advisor_james` | `password` | **Senior_Advisor** |
| `officer_rahul` | `password` | **Legal_Officer** |
| `officer_priya` | `password` | **Legal_Officer** |
| `clerk_amit` | `password` | **Legal_Officer** |

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

> **Please Keep Patient**: Because this proof-of-concept is configured to run **100% locally** to enforce data sovereignty, your local CPU/GPU will handle the heavy lifting for multi-format text chunking, document vector embedding, and language model inference.
>
> * **Latency Expectation**: Depending on your system hardware (especially if running on CPU without dedicated GPU acceleration), operations such as document ingestion and chat queries may take between **10 to 45 seconds**.
> * **Timeouts**: If you encounter a database connection error or an HTTP timeout on your first document upload, please **wait a moment and try again**. The local containers might still be warming up or initializing neural weights.
