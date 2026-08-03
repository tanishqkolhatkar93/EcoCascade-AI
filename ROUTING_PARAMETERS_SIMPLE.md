# EcoCascade AI Laptop Routing Parameters

This file explains, in simple language, when the laptop router should use the local Ollama model and when it should send the prompt to the Groq cloud API.

## Route To Local Ollama

Use the local Ollama model when the task is small, private, and easy enough for a laptop model.

Examples:

- Fix spelling or grammar in a short sentence.
- Rewrite a short paragraph.
- Translate a short message.
- Classify text into simple labels like urgent, normal, spam, or feedback.
- Answer a simple factual question.
- Summarize a small paragraph.
- Extract names, dates, phone numbers, or emails from short text.
- Generate a short reply, caption, title, or checklist.

Local task limits:

- The prompt is short.
- The answer expected is short.
- The task does not require deep reasoning.
- The task does not require current internet knowledge.
- The user is not asking for long code, long documents, or detailed research.

## Local Ollama Model Choice

The laptop has several local models installed. The router chooses the smallest useful model for the job.

Use `gemma3:270m` for tiny tasks:

- Classify text.
- Extract emails, names, dates, or phone numbers.
- Generate a title or caption.
- Give a very short answer.

Use `qwen2.5:0.5b` for small writing tasks:

- Fix grammar.
- Fix spelling.
- Rewrite a short paragraph.
- Translate short text.
- Summarize a short paragraph.

Use `qwen3:4b` for stronger local work:

- Explain something step by step.
- Do simple reasoning.
- Help with local code explanation.
- Act as the fallback model if Groq cloud fails.

Use `llama3:latest` for general local writing:

- Draft a paragraph.
- Generate ideas.
- Write a short blog section.
- Create open-ended text that is still not complex enough for Groq.

## Route To Groq Cloud

Use Groq when the task is too complex, too long, or needs stronger reasoning.

Examples:

- Summarize a long document or many pages.
- Write or debug code or a full program.
- Analyze legal, financial, medical, or high-risk information.
- Compare many options and make a detailed recommendation.
- Do multi-step reasoning or planning.
- Generate a long report, proposal, article, or presentation.
- Answer questions that need recent or external knowledge.
- Handle prompts with very large pasted text.

Cloud task triggers:

- The prompt is very long.
- The user asks for a long answer.
- The prompt contains words like report, research, strategy, architecture, debug, legal, medical, financial, latest, today, current, compare, or detailed.
- The prompt asks to write code, Python, a program, or a function.
- The task asks for complex code or multi-file changes.
- The local model fails or returns an error.

## Laptop Health Rules

Even if a task is simple, send it to Groq when the laptop should avoid extra local work.

Use Groq if:

- Battery is below 15 percent.
- CPU temperature is too high.
- Local Ollama is not running.
- The selected local model is not installed.

For this MVP, battery and temperature checks are written as simple settings. Later, they can be connected to real laptop sensors.

## Offline Rule

If the internet is unavailable, use Offline-First Edge Mode.

In Offline-First Edge Mode:

- Try the local Ollama model first.
- Do not call Groq.
- If Ollama is not available, return a clear error message telling the user that both cloud and local AI are unavailable.

## MVP Decision Score

The router uses a simple score:

- Start at 0.
- Add points when the prompt looks complex.
- If the score is low, use Ollama.
- If the score is high, use Groq.

Simple prompts usually score below 4.

Complex prompts usually score 4 or higher.
