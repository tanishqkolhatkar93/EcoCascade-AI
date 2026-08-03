import time
import os

import requests
import streamlit as st

from smart_router import (
    GROQ_MODEL,
    OLLAMA_GENERAL_MODEL,
    OLLAMA_REASONING_MODEL,
    OLLAMA_SMALL_MODEL,
    OLLAMA_TINY_MODEL,
    call_ollama,
    choose_local_model,
    choose_route,
    score_prompt,
)


EXAMPLES = {
    "Grammar fix": "Fix grammar: i has a idea for save water",
    "Extract data": "Extract the email and phone number from: Ravi, ravi@example.com, 9876543210",
    "Short summary": "Summarize this short text: Data centers consume electricity and water for cooling.",
    "Complex plan": "Write a detailed technical architecture and business strategy report for this startup MVP",
}

APP_VERSION = "2026-06-26-code-routing-v3"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_TIMEOUT_SECONDS = int(os.getenv("GROQ_TIMEOUT_SECONDS", "120"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "220"))


def route_label(route):
    if route == "local":
        return "Local laptop AI"
    if route == "cloud":
        return "Groq cloud AI"
    return "Local fallback"


def show_model_map():
    st.subheader("Local model selection")
    st.write("The router uses the smallest useful installed model for each simple task.")

    rows = [
        ("Tiny tasks", OLLAMA_TINY_MODEL, "classification, extraction, labels, captions, titles"),
        ("Small writing fixes", OLLAMA_SMALL_MODEL, "grammar, spelling, rewrite, translation, short summary"),
        ("Local reasoning", OLLAMA_REASONING_MODEL, "logic, code explanation, offline fallback"),
        ("General writing", OLLAMA_GENERAL_MODEL, "open-ended writing, drafts, ideas, paragraphs"),
    ]

    for task_type, model, use_case in rows:
        left, middle, right = st.columns([1.2, 1.1, 2.2])
        left.write(f"**{task_type}**")
        middle.code(model, language=None)
        right.write(use_case)


def decide_route(prompt, offline, force_route):
    if force_route in {"local", "cloud"}:
        return force_route, [f"route manually forced to {force_route}"]
    return choose_route(prompt, offline=offline)


def run_selected_route(prompt, offline, force_route, allow_cloud_fallback):
    route, reasons = decide_route(prompt, offline=offline, force_route=force_route)

    if route == "local":
        model, model_reason = choose_local_model(prompt)
        output = call_ollama(prompt, model)
        return route, reasons + [f"local model is {model}: {model_reason}"], output

    try:
        output = call_groq_direct(prompt)
        return route, reasons, output
    except Exception as error:
        if not allow_cloud_fallback:
            raise RuntimeError(f"Groq cloud failed: {error}") from error

        output = call_ollama(prompt, OLLAMA_REASONING_MODEL)
        fallback_reasons = reasons + [
            f"cloud failed, falling back to Ollama: {error}",
            f"local fallback model is {OLLAMA_REASONING_MODEL}",
        ]
        return "local-fallback", fallback_reasons, output


def call_groq_direct(prompt):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "paste_your_groq_api_key_here":
        raise RuntimeError("GROQ_API_KEY is missing in .env")

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are EcoCascade AI. Give useful, concise answers.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": GROQ_MAX_TOKENS,
    }

    session = requests.Session()
    session.trust_env = False
    response = session.post(
        GROQ_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        timeout=GROQ_TIMEOUT_SECONDS,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"Groq HTTP {response.status_code}: {response.text[:500]}")

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def main():
    st.set_page_config(
        page_title="EcoCascade AI Router",
        page_icon="",
        layout="wide",
    )

    st.title("EcoCascade AI")
    st.caption("Hybrid AI router: simple prompts run on your laptop, complex prompts go to Groq.")
    st.caption(f"App build: {APP_VERSION}")

    with st.sidebar:
        st.header("Demo controls")
        route_mode = st.selectbox(
            "Routing mode",
            ["Auto", "Force Groq cloud", "Force local Ollama"],
        )
        offline = st.toggle("Offline-first mode", value=False)
        run_real_ai = st.toggle("Run the selected AI model", value=False)
        allow_cloud_fallback = st.toggle("Fallback to local if Groq fails", value=False)
        st.caption("Leave this off to show only the routing decision.")

        st.divider()
        st.write("Example prompts")
        selected_example = st.radio(
            "Choose one",
            list(EXAMPLES.keys()),
            label_visibility="collapsed",
        )

    default_prompt = EXAMPLES[selected_example]
    prompt = st.text_area(
        "Enter an AI prompt",
        value=default_prompt,
        height=150,
        placeholder="Ask something simple or complex...",
    )

    if not prompt.strip():
        st.info("Enter a prompt to see where EcoCascade AI routes it.")
        return

    force_route = None
    if route_mode == "Force Groq cloud":
        force_route = "cloud"
        offline = False
    elif route_mode == "Force local Ollama":
        force_route = "local"

    route, reasons = decide_route(prompt, offline=offline, force_route=force_route)
    score, _ = score_prompt(prompt)
    local_model, local_model_reason = choose_local_model(prompt)

    st.divider()

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Decision", route_label(route))
    metric_2.metric("Complexity score", score)
    metric_3.metric("Cloud model", GROQ_MODEL if route == "cloud" else "Not used")
    metric_4.metric("Local model", local_model if route == "local" else "Standby")

    if route == "local":
        st.success("This prompt is simple enough to run locally on the laptop.")
        st.write(f"Selected local model: `{local_model}`")
        st.write(local_model_reason)
    else:
        st.warning("This prompt is complex, so the router selected Groq cloud AI.")

    if route == "cloud":
        st.write("Groq will be called directly when you turn on real execution.")
        if not allow_cloud_fallback:
            st.write("Local fallback is off, so any Groq API error will be shown clearly.")

    st.subheader("Why this route was selected")
    for reason in reasons:
        st.write(f"- {reason}")

    show_model_map()

    st.subheader("Estimated impact")
    if route == "local":
        st.write("Cloud API call avoided: **yes**")
        st.write("Best story for demo: this saves cloud cost and avoids unnecessary data center compute.")
    else:
        st.write("Cloud API call avoided: **no**")
        st.write("Best story for demo: the router spends cloud compute only when the task needs it.")

    if not run_real_ai:
        st.info("Turn on 'Run the selected AI model' in the sidebar to generate the actual answer.")
        return

    st.subheader("AI answer")
    with st.spinner("Running selected route..."):
        start = time.perf_counter()
        try:
            final_route, final_reasons, output = run_selected_route(
                prompt,
                offline=offline,
                force_route=force_route,
                allow_cloud_fallback=allow_cloud_fallback,
            )
            elapsed = time.perf_counter() - start
        except Exception as error:
            st.error("The selected AI route did not finish successfully.")
            st.write(str(error))
            if route == "cloud":
                st.info("For Groq mode, check your API key, selected Groq model, and whether your network allows HTTPS requests to api.groq.com.")
            else:
                st.info("For local mode, make sure Ollama is running. Large local models can also need extra time on the first request.")
            return

    st.write(f"Final route: **{route_label(final_route)}**")
    st.write(f"Response time: **{elapsed:.2f} seconds**")

    if final_reasons != reasons:
        with st.expander("Final route details"):
            for reason in final_reasons:
                st.write(f"- {reason}")

    st.text_area("Output", value=output, height=260)


if __name__ == "__main__":
    main()
