# EcoCascade AI - Smart Routing Brain Laptop MVP

This folder contains a laptop version of the EcoCascade AI routing brain.

It decides whether an AI prompt should run:

- locally on Ollama, for simple low-cost tasks
- on Groq, for complex high-performance tasks

The plain-language routing rules are in `ROUTING_PARAMETERS_SIMPLE.md`.

## Files

- `ROUTING_PARAMETERS_SIMPLE.md` - simple explanation of routing parameters
- `smart_router.py` - Python MVP router
- `streamlit_app.py` - web app for showcasing the router
- `.env.example` - example environment variables

## Requirements

Your installed Ollama models are used like this:

- `gemma3:270m` - tiny tasks like extraction, classification, titles, and captions
- `qwen2.5:0.5b` - grammar, rewrite, translation, and short summaries
- `qwen3:4b` - local reasoning and cloud fallback
- `llama3:latest` - general writing

Run Ollama locally:

```powershell
ollama serve
```

Add your Groq API key in `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The `.env` file also controls local model timeout and response length:

```env
OLLAMA_TIMEOUT_SECONDS=240
OLLAMA_NUM_PREDICT=180
```

Install Streamlit if needed:

```powershell
pip install -r requirements.txt
```

## Run Command Line Demo

```powershell
python .\smart_router.py "Fix grammar: i has a idea for save water"
```

```powershell
python .\smart_router.py "Write a detailed technical architecture for this startup MVP with backend, frontend, database, and deployment plan"
```

## Run Web Demo

```powershell
streamlit run .\streamlit_app.py
```

Then open the local URL shown by Streamlit.

## Offline Mode

If the internet is not available, the router will try Ollama only.

```powershell
python .\smart_router.py --offline "Summarize this short text: Water is precious."
```
