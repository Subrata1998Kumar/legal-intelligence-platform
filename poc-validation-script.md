# Enterprise Legal Intelligence Platform - User Acceptance Testing (UAT) & Validation Guide

This document provides a step-by-step testing scenario to validate the complete multi-user workflow, role-based access control (RBAC), multi-format parser with OCR/table extraction, semantic metadata filtering, opinion drafting pipeline, and chat session isolation on the Enterprise Legal Platform.

---

## **Start Here: Clone and Start the Project**

### **Step 1: Install the Required Tools**
Before beginning the validation, install and verify:
* **Git**: Required to clone the project repository.
* **Docker Desktop**: Start Docker Desktop and confirm that the Docker engine is running.

```bash
git --version
docker --version
```

### **Step 2: Clone the Repository from GitHub**
Clone the project and change into its root directory:

```bash
git clone https://github.com/Subrata1998Kumar/legal-intelligence-platform.git
cd legal-intelligence-platform
```

### **Step 3: Start the Docker Services**
The Docker Compose file is stored in the `deployments` directory. Start the database, Ollama, backend, and frontend services:

```bash
cd deployments
docker compose up -d --build
```

Return to the project root when you need to run commands against files in the repository:

```bash
cd ..
```

### **Step 4: Pull the Required Local AI Models**
Download the local model weights into the Ollama container:

```bash
docker exec -it lip-ollama ollama pull granite4.1:3b
docker exec -it lip-ollama ollama pull paraphrase-multilingual:278m
```

### **Step 5: Verify the Services and Models**
Confirm that Ollama is running and both models are available:

```bash
docker exec -it lip-ollama ollama list 
curl http://localhost:11434/api/tags
```

The validation environment is ready when the containers are running and both `granite4.1:3b` and `paraphrase-multilingual:278m` appear in the model list.

### **Step 6: Check Database Readiness and Initialization**
Confirm that PostgreSQL is accepting connections and that the schema and pre-seeded user accounts were initialized successfully:

```bash
docker exec -it lip-db pg_isready -U postgres -d postgres
docker exec -it lip-db psql -U postgres -d postgres -c "SELECT id, username, role FROM users;"
```

**Expected Result:** The readiness check reports that PostgreSQL is accepting connections, and the SQL query returns the configured user accounts, including `admin`, `officer_1`, and `advisor_1`.

---

## **Validation Phase 1: Authentication & Account Directory**
### **Objective**: Verify that the pre-seeded accounts are loaded and that the system rejects invalid credentials.

1. **Step 1**: Open the Streamlit user portal at `http://localhost:8501`.
2. **Step 2**: Attempt to log in with an invalid user (e.g., `officer_fake` / `password`).
   * **Expected Result**: The interface displays a connection error: *"Authentication failed. Check credentials."*
3. **Step 3**: Log in as `officer_1` (Password: `officer_1`).
   * **Expected Result**: Successful authentication. The app displays: *"Authenticated as officer_1 (Legal_Officer)"*.
4. **Step 4**: Click **Log Out**.
   * **Expected Result**: All local memory values (chat messages, session identifiers) are cleared. The user is redirected to the login portal.

---

## **Validation Phase 2: Document Ingestion, Dropdown Lock, and OCR/Table Extraction**
### **Objective**: Verify that the admin can select document security levels, while other roles are locked to their own clearance tier. Validate multi-format parsing.

### **Test Scenario 2A: Uploading as an Administrator (Admin Role)**
1. **Step 1**: Log in as `admin` (Password: `admin`).
2. **Step 2**: Go to 👈 **Document Upload** in the sidebar.
3. **Step 3**: Upload a test document containing tables or scanned text (e.g., a PDF table or scanned PDF).
4. **Step 4**: Verify the **Assign Minimum Security Clearance** dropdown.
   * **Expected Result**: The dropdown is active and selectable. Choose `Senior_Advisor` for this document.
5. **Step 5**: Click **Ingest Document**.
   * **Expected Result**: The screen shows:
     - Text Chunks Generated: `> 0`
     - Table Chunks Extracted: `> 0` (if a table is present)
     - OCR Fallback Triggered: `False` (for text PDFs) or `True` (for scanned files).

### **Test Scenario 2B: Uploading as a Legal Officer (Role-Based Restriction)**
1. **Step 1**: Log in as `officer_1` (Password: `officer_1`).
2. **Step 2**: Go to 👈 **Document Upload** in the sidebar.
3. **Expected Result**: The **Assign Minimum Security Clearance** dropdown is **disabled (view-only)** and locked to `Legal_Officer`.
4. **Step 3**: Upload a standard Microsoft Word document (`.docx` or `.doc`) containing a formatted table.
5. **Step 4**: Click **Ingest Document**.
   * **Expected Result**: The parser successfully extracts paragraph blocks and native tables, converting tables into structured Markdown grids. The file integrity SHA-256 hash is generated.
   * **Backend Verification**: Even if the client-side dropdown is bypassed, the FastAPI backend intercepts the payload and enforces `security_clearance = "Legal_Officer"`.

---

## **Validation Phase 3: Semantic Retrieval with Metadata Filtering**
### **Objective**: Verify that a user can only retrieve search context at or below their security clearance.

### **Setup for Search**:
* File A is uploaded by `admin` with `Admin` clearance (e.g., "Highly Sensitive Cabinet Briefing.txt").
* File B is uploaded by `admin` or `advisor_1` with `advisor_1` clearance (e.g., "Judgement_PropertyDispute.txt").
* File C is uploaded by `officer_1` or `admin` with `Legal_Officer` clearance (e.g., "Government_Order_LeavePolicy.txt").

### **Test Scenario 3A: Search as a Legal Officer**
1. **Step 1**: Log in as `officer_1` / `officer_1`.
2. **Step 2**: Go to 👈 **Search & Retrieval**.
3. **Step 3**: Submit queries targeting content in File A (Admin-only), File B (Advisor-only), and File C (Legal Officer).
   * **Expected Result**: Chunks from File A and File B **are completely ignored and excluded from retrieval**. Only matching chunks from File C are displayed in the grounded references expander.

### **Test Scenario 3B: Search as a Senior Advisor**
1. **Step 1**: Log in as `advisor_1` / `advisor_1`.
2. **Step 2**: Go to 👈 **Search & Retrieval** and submit the same queries.
   * **Expected Result**: The advisor retrieves relevant context from File B and File C. The highly sensitive File A remains completely hidden.

---

## **Validation Phase 4: Chat History Isolation & Multi‑User Partitioning**
### **Objective**: Verify that chat conversations are strictly separated between users.

1. **Step 1**: Log in as `officer_1` / `officer_1`. Go to 👈 **Search & Retrieval**.  
   * The sidebar shows `officer_1`’s conversation history (e.g., *Revision of Leave Policy details*).  
   * Messages reference grounded citations such as **General_Administrative_Memo.docx** and **Government_Order_LeavePolicy.txt**.

2. **Step 2**: Review the chat workspace.  
   * Example: *“The revision of the Leave Policy, as ordered by the Governor on 18‑Aug‑2026, includes the following changes effective 01‑Sep‑2026: Annual leave increased to 25 days, emergency leave capped at 7 days, sick leave requires medical certification.”*  
   * These changes are detailed in **Government_Order_LeavePolicy.txt (Order No.: GO/LP/2026/07)**.

3. **Step 3**: Click **Log Out**.

4. **Step 4**: Log in as `officer_3` / `officer_3`. Go to 👈 **Search & Retrieval**.  
   * **Expected Result**: The workspace is blank. The sidebar does not list `officer_1`’s previous chat history.  
   * Only the “➕ Start New Conversation” option is available.

5. **Step 5**: Start a new chat as `officer_3`.  
   * The workspace initializes fresh, isolated from `officer_1`.

---

## **Validation Phase 5: Legal Opinion Workspace & Approval Status Flow**
### **Objective**: Verify the drafting, autonomous auditing, peer isolation, and advisor approval workflow.

### **Test Scenario 5A: Drafting and Risk Audit**
1. **Step 1**: Log in as `officer_1` / `officer_1`. Go to 👈 **Opinion Workspace**.
2. **Step 2**: Enter a title and draft opinion content (e.g., *"Taking Leave"*).
3. **Step 3**: Click **Submit for Risk Audit**.
   * **Expected Result**: The local AI service (`RiskService`) analyzes the text against database precedents and generates an interactive, detailed **AI Legal Risk Report** covering compliance issues, missing citations, conflicts, and a risk score.
4. **Step 4**: Go to **Review Opinion Pipelines**.
   * **Expected Result**: The newly drafted opinion is listed. Its status is set to `Draft`. The status change dropdown is invisible to `officer_1` (Legal Officers cannot self-approve).

### **Test Scenario 5B: Peer Isolation Check**
1. **Step 1**: Log in as `officer_2` / `officer_2`. Go to 👈 **Opinion Workspace** -> **Review Opinion Pipelines**.
   * **Expected Result**: The list is empty. `officer_2` cannot view or access the opinion drafted by `officer_1`.

### **Test Scenario 5C: Review & Status Transition**
1. **Step 1**: Log in as `advisor_2` / `advisor_2`. Go to 👈 **Opinion Workspace** -> **Review Opinion Pipelines**.
   * **Expected Result**: The advisor can view the drafts submitted by both `officer_1` and any other user.
2. **Step 2**: Inspect `officer_1`'s opinion draft and expand the AI Legal Risk Report.
3. **Step 3**: Use the status dropdown to change the state to `Approved`.
4. **Step 4**: Click **Commit Status Update**.
   * **Expected Result**: Screen refreshes and shows status updated to `Approved`.

### **Test Scenario 5D: Officer Verification**
1. **Step 1**: Log in back as `officer_1` / `officer_1`. Go to 👈 **Opinion Workspace** -> **Review Opinion Pipelines**.
   * **Expected Result**: `officer_1`'s opinion status has been updated to `Approved` in real time, confirming a successful human-in-the-loop review chain.
