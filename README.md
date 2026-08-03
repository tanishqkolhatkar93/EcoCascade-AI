#  🌿 EcoCascade AI — Smart Hybrid AI Router for Sustainable Inference

> **Energy-Aware • Cost-Aware • Privacy-Aware • Edge-First AI**

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLMs-green)
![Groq](https://img.shields.io/badge/Groq-Cloud-purple)

---

# 📖 Overview

EcoCascade AI is a hybrid AI routing system that intelligently decides whether a user's prompt should run on a **local LLM (Ollama)** or a **cloud LLM (Groq)**.

Instead of sending every request to a powerful cloud model, EcoCascade AI analyzes prompt complexity and routes simple tasks locally while reserving cloud models for advanced reasoning.

---

# 🌍 Why This Project Matters

Large Language Models are increasingly deployed in cloud data centers that consume significant amounts of electricity and cooling resources. Many everyday AI requests—such as grammar correction, summarization, text classification, and rewriting—do not require a large cloud-hosted model.

EcoCascade AI introduces an intelligent routing layer that analyzes each prompt and decides whether it should be executed locally using lightweight Ollama models or sent to a cloud model such as Groq for advanced reasoning.

By avoiding unnecessary cloud inference for simple tasks, EcoCascade AI demonstrates a more efficient and sustainable approach to AI deployment. The project focuses on reducing cloud dependency, improving privacy, lowering inference cost, supporting offline AI workflows, and encouraging edge-first AI architectures.


Modern AI assistants frequently send **every prompt** to cloud-hosted models, even when the task is simple.

This leads to:

- Higher inference cost
- Increased latency
- Reduced privacy
- Internet dependency
- Greater demand on centralized AI infrastructure

EcoCascade AI demonstrates a smarter, **local-first** approach.

> **Important:** This project does **not** claim to directly measure or eliminate water consumption in AI data centers. Instead, it reduces unnecessary cloud inference requests, encouraging more efficient and sustainable AI deployment.

---

# 🚀 Features

- ✅ Hybrid AI Routing
- ✅ Prompt Complexity Analysis
- ✅ Local Ollama Integration
- ✅ Groq Cloud Integration
- ✅ Automatic Fallback
- ✅ Offline-first Execution
- ✅ Streamlit Dashboard
- ✅ CLI Support
- ✅ Configurable Routing Rules

---

# 🏗️ Architecture

```text
                User Prompt
                     │
                     ▼
          Prompt Analysis Engine
                     │
                     ▼
          Complexity Scoring Layer
             ┌────────┴────────┐
             ▼                 ▼
      Local Ollama        Groq Cloud
             └────────┬────────┘
                      ▼
               Final Response
```

---

# 📊 Routing Strategy

### Local Models
- Grammar correction
- Translation
- Text rewriting
- Keyword extraction
- Summarization
- Classification

### Cloud Models
- Coding
- Research
- Long-form reasoning
- System design
- Medical reasoning
- Business strategy

---

# 📷 Demo



- Home Dashboard
  
  ![Alt Text](https://github.com/tanishqkolhatkar93/EcoCascade-AI/blob/main/Screenshot%202026-08-03%20124144.png)
- Route Selection
  
  ![Alt Text](https://github.com/tanishqkolhatkar93/EcoCascade-AI/blob/main/Screenshot%202026-08-03%20124119.png)
  
- Final Response
  
  ![Alt Text](https://github.com/tanishqkolhatkar93/EcoCascade-AI/blob/main/Screenshot%202026-08-03%20124129.png)

---

# 📁 Project Structure

```text
EcoCascadeAI/
│── streamlit_app.py
│── smart_router.py
│── router.py
│── requirements.txt
│── .env.example
│── README.md
```

---

# ⚙️ Installation

```bash
git clone https://github.com/yourusername/EcoCascadeAI.git
cd EcoCascadeAI

pip install -r requirements.txt

ollama serve

streamlit run streamlit_app.py
```

---

# 💻 Example

**Prompt**

```
Correct the grammar:
"I has completed my project."
```

**Router Decision**

- Complexity: Low
- Model: Ollama
- Reason: Lightweight NLP task

---

**Prompt**

```
Design a scalable AI architecture for a hospital.
```

**Router Decision**

- Complexity: High
- Model: Groq
- Reason: Multi-step reasoning required

---

# 📈 Potential Impact

✅ Reduce unnecessary cloud inference

✅ Lower API cost

✅ Improve response latency

✅ Improve privacy

✅ Enable offline AI

✅ Encourage Edge AI

✅ Demonstrate sustainable AI engineering


---

# 🔮 Future Roadmap

- Multi-Agent AI Routing
- ML-based Routing Model
- Carbon/Energy Estimation
- Cost Analytics Dashboard
- RAG Integration
- Multi-cloud Support
- Enterprise Deployment

---

# 🛠️ Tech Stack

- Python
- Streamlit
- Ollama
- Groq API
- Requests
- dotenv

---

# 👨‍💻 Author

**Tanishq Kolhatkar**

AI • Machine Learning • Explainable AI • Edge AI

GitHub: https://github.com/tanishqkolhatkar93
linkedln : https://www.linkedin.com/in/tanishq93/

---

# ⭐ Support

If you like this project:

- ⭐ Star the repository
- 🍴 Fork it
- 📢 Share it

---

# 📄 License

MIT License

---

## 🙏 Acknowledgements

EcoCascade AI is an engineering prototype that explores efficient hybrid AI inference by combining local and cloud models. It aims to improve efficiency, privacy, cost-effectiveness, and sustainable AI practices through intelligent routing.
