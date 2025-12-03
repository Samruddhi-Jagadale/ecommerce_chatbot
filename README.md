# 🛍️ End-to-End MLOps AI Agent Project  
## **"Customer Service Chatbot for an E-commerce Clothing Brand"**  
### **LLM-powered RAG Chatbot | Apache Airflow Orchestration | Full MLOps Pipeline**

---

## 🚀 **Live Demo**
🌐 **Live Application:** *Deployed & Running*

👉 **Access the Web App Here**  
🔄 *Note:* First load may take **1–2 minutes**. After loading, refresh once for best performance.

---

## 🤖 **Project Summary**
A fully automated **RAG-based Ecommerce Customer Service Chatbot**, powered by:

- **LLaMA 3.3 70B (via Groq)**
- **NVIDIA nv-embedqa-mistral-7b-v2 embeddings**
- **Pinecone vector store**
- **LangChain retrieval pipeline**
- **Flask frontend**
- **Apache Airflow MLOps pipeline**

The chatbot handles **product recommendations, order processing, shipment tracking, FAQs**, and maintains **conversational memory** — delivering a realistic customer support experience.

---

## 🎯 **Features**
### 🛒 **E-Commerce Chatbot Capabilities**
- Product Q&A  
- Budget-based recommendations  
- Order placement + invoice breakdown  
- Shipment & order tracking  
- Multi-item cart logic  
- Conversation memory  
- Human-like natural language responses  

### ⚙️ **MLOps + Automation**
Powered by **Apache Airflow** DAGs:

1. **Data Collection DAG** – Automated Amazon product scraping (Selenium)  
2. **Data Cleaning DAG** – Preprocessing & missing value handling  
3. **Vector Store DAG** – Generate embeddings + upload to Pinecone  
4. **Chatbot Builder DAG** – Rebuild & redeploy RAG pipeline  
5. **Daily Scheduled Runs** – Keeps chatbot updated with new data  

---

## 🧠 **End-to-End Workflow**

### **1️⃣ Data Collection**
Scraped real Hunnit product pages using Selenium.

Categories scraped:
-Best Seller Women wears
-GYM Wears for women

Captured attributes:
- Brand  
- Product name  
- Rating  
- Rating count  
- MRP  
- Discount price  
- Savings %  

---

### **2️⃣ Data Cleaning & Preprocessing**
Performed:
- Null handling  
- Type conversions  
- Category normalization  
- Mode imputation for categorical values  

---

### **3️⃣ Vector Embedding**
Using **NVIDIA nv-embedqa-mistral-7b-v2**  
✔ Top scoring model on **MTEB leaderboard**  
✔ Fast, high-quality semantic embeddings  

Managed via **LangChain Embeddings API**.

---

### **4️⃣ Pinecone Vector Database**
- Created index programmatically  
- Uploaded normalized embeddings  
- Configured similarity search (cosine)  
- Integrated as RAG retriever  

---

### **5️⃣ LLM: LLaMA 3.3 70B (Groq)**
- Ultra-low latency inference  
- Better reasoning and conversational memory  
- Optimized system prompts for:
  - Product search  
  - Context-aware replies  
  - Order handling logic  

---

### **6️⃣ RAG Pipeline**
- Pinecone retriever  
- Document chain  
- Conversational memory with LangGraph  
- Full retrieval + response pipeline  

---

### **7️⃣ Flask Web Application**
- E-commerce styled UI  
- Integrated chatbot widget  
- Responsive layout  
- JS-based message handling  
- Smooth chat animation  

---

### **8️⃣ Apache Airflow MLOps Pipeline**
- Automated DAG workflows  
- Modular task definitions  
- Monitoring + retries  
- Versioning  
- Daily auto-training  

---

## 🏗️ **Tech Stack**

### **Backend**
- Python  
- Flask  
- LangChain  
- Pinecone  
- Selenium  
- Groq API  
- NVIDIA Embeddings  

### **MLOps**
- Apache Airflow  
- Docker  
- Docker Compose  

### **Frontend**
- HTML  
- CSS  
- JavaScript  

---
📦 Ecommerce-Chatbot-Project
│
├── 📂 dags # Airflow DAGs for pipeline automation
├── 📂 artifacts # Generated embeddings, vector data, logs
├── 📂 data # Raw Amazon scraped data
├── 📂 readme_images # Screenshots used in README
│
├── 📂 src
│ ├── main.py # Run chatbot locally
│ ├── 📂 components # Core logic modules
│ ├── 📂 utils # Utility functions
│
├── 📂 static
│ ├── 📂 css # Stylesheets
│ ├── 📂 images # Web images
│ ├── 📂 js # Chat scripts
│
├── 📂 templates # HTML templates
│
├── app.py # Flask application
├── requirements.txt
├── docker-compose.yml # Airflow multi-container setup
├── Dockerfile # Custom Airflow image
├── setup.py
├── .gitignore
└── LICENSE


---

## 🛠️ **Installation & Setup**

### **1️⃣ Clone Repository**
```bash
git clone https://github.com/Samruddhi-Jagadale/RAG_Ecommerce.git
cd RAG_Ecommerce

2️⃣ Create Virtual Environment
conda create -p envi python==3.9 -y
conda activate envi

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create .env file:

NVIDIA_API_KEY=your_key
PINECONE_API_KEY=your_key
GROQ_API_KEY=your_key

5️⃣ Run the Flask App
python app.py


Visit:
http://127.0.0.1:5000

6️⃣ Run Apache Airflow Pipeline
docker-compose up --build


Access Airflow:
➡ http://localhost:8080

Trigger DAGs manually or set schedule intervals.

🌐 Usage Guide
Open Chatbot:

Click the chat icon at the bottom-right of the screen.

Try Queries Like:

💬 “What can you do?”
💬 “Recommend a gymwear under ₹1500”
💬 “Tell me about this product…”
💬 “I want to order it”
💬 “Give me invoice for my order”
💬 “Track my order status”

Screenshots

<img width="1896" height="765" alt="Screenshot2" src="https://github.com/user-attachments/assets/c3cc87c7-5ed0-4c02-a9e7-224f49a2de18" />
<img width="1886" height="918" alt="Screenshot1" src="https://github.com/user-attachments/assets/7e157541-db1f-414f-b026-696c82531df4" />


## 📂 **Project Structure**

