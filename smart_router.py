import argparse
import json
import os
import socket
import sys
import urllib.error
import urllib.request

try:
    import requests
except ImportError:
    requests = None


def load_env_file(path=".env"):
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


load_env_file()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
OLLAMA_TINY_MODEL = os.getenv("OLLAMA_TINY_MODEL", "gemma3:270m")
OLLAMA_SMALL_MODEL = os.getenv("OLLAMA_SMALL_MODEL", "qwen2.5:0.5b")
OLLAMA_REASONING_MODEL = os.getenv("OLLAMA_REASONING_MODEL", "qwen3:4b")
OLLAMA_GENERAL_MODEL = os.getenv("OLLAMA_GENERAL_MODEL", "llama3:latest")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "240"))
GROQ_TIMEOUT_SECONDS = int(os.getenv("GROQ_TIMEOUT_SECONDS", "120"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "180"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "220"))


COMPLEX_KEYWORDS = {
    "architecture",
    "business plan",
    "build an app",
    "code",
    "compare",
    "current",
    "debug",
    "detailed",
    "financial",
    "latest",
    "legal",
    "medical",
    "multi-file",
    "proposal",
    "python",
    "report",
    "research",
    "strategy",
    "summarize this document",
    "today",
}

SIMPLE_KEYWORDS = {
    "caption",
    "classify",
    "email",
    "extract",
    "fix grammar",
    "grammar",
    "rewrite",
    "short reply",
    "spelling",
    "summarize this short",
    "title",
    "translate",
}


TINY_MODEL_KEYWORDS = {
    "caption",
    "classify",
    "email",
    "extract",
    "label",
    "phone",
    "spam",
    "title",
}

SMALL_MODEL_KEYWORDS = {
    "fix grammar",
    "grammar",
    "rewrite",
    "short reply",
    "spelling",
    "summarize this short",
    "translate",
}

REASONING_MODEL_KEYWORDS = {
    "explain",
    "logic",
    "math",
    "reason",
    "step by step",
    "why",
}

GENERAL_MODEL_KEYWORDS = {
    "blog",
    "draft",
    "idea",
    "paragraph",
    "story",
    "write",
}


def env_flag(name):
    return os.getenv(name, "false").strip().lower() in {"1", "true", "yes", "on"}


def score_prompt(prompt):
    text = prompt.lower()
    words = text.split()
    score = 0
    reasons = []

    if len(words) > 180:
        score += 3
        reasons.append("prompt is long")
    elif len(words) > 80:
        score += 2
        reasons.append("prompt is medium length")

    complex_hits = sorted(keyword for keyword in COMPLEX_KEYWORDS if keyword in text)
    if complex_hits:
        score += min(4, len(complex_hits) * 2)
        reasons.append("complex keywords found: " + ", ".join(complex_hits))

    simple_hits = sorted(keyword for keyword in SIMPLE_KEYWORDS if keyword in text)
    if simple_hits:
        score -= min(2, len(simple_hits))
        reasons.append("simple keywords found: " + ", ".join(simple_hits))

    if "?" in prompt and len(words) < 25:
        score -= 1
        reasons.append("short question")

    if not reasons:
        reasons.append("default simple task")

    return score, reasons


def choose_route(prompt, offline=False, force_route=None):
    if force_route in {"local", "cloud"}:
        return force_route, [f"route manually forced to {force_route}"]

    if offline:
        return "local", ["offline-first edge mode"]

    if env_flag("LOW_BATTERY"):
        return "cloud", ["laptop battery is below the safe local-processing limit"]

    if env_flag("OVERHEATING"):
        return "cloud", ["laptop is overheating"]

    score, reasons = score_prompt(prompt)
    route = "cloud" if score >= 4 else "local"
    reasons.insert(0, f"complexity score is {score}")
    return route, reasons


def choose_local_model(prompt):
    text = prompt.lower()
    words = text.split()

    if "code" in text or "python" in text or "program" in text or "function" in text:
        return OLLAMA_GENERAL_MODEL, "general local model because it gives better code output than the reasoning model"

    if any(keyword in text for keyword in TINY_MODEL_KEYWORDS) and len(words) <= 80:
        return OLLAMA_TINY_MODEL, "tiny local model for classification, extraction, labels, captions, or titles"

    if any(keyword in text for keyword in SMALL_MODEL_KEYWORDS) and len(words) <= 140:
        return OLLAMA_SMALL_MODEL, "small local model for grammar, rewrite, translate, or short summary"

    if any(keyword in text for keyword in REASONING_MODEL_KEYWORDS):
        return OLLAMA_REASONING_MODEL, "stronger local model for reasoning-style local work"

    if any(keyword in text for keyword in GENERAL_MODEL_KEYWORDS):
        return OLLAMA_GENERAL_MODEL, "general local model for writing and open-ended text"

    if len(words) <= 40:
        return OLLAMA_TINY_MODEL, "tiny local model because the prompt is very short"

    if len(words) <= 120:
        return OLLAMA_SMALL_MODEL, "small local model because the prompt is short"

    return OLLAMA_REASONING_MODEL, "stronger local model because the local prompt is longer"


def post_json(url, payload, headers=None, timeout=120):
    if requests is not None:
        try:
            session = requests.Session()
            session.trust_env = False
            response = session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json", **(headers or {})},
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as error:
            raise RuntimeError(f"request timed out after {timeout} seconds") from error
        except requests.exceptions.HTTPError as error:
            message = error.response.text[:500] if error.response is not None else str(error)
            raise RuntimeError(f"HTTP {error.response.status_code}: {message}") from error
        except requests.exceptions.RequestException as error:
            raise RuntimeError(f"request failed: {error}") from error

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (TimeoutError, socket.timeout) as error:
        raise RuntimeError(f"request timed out after {timeout} seconds") from error


def call_ollama(prompt, model):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": OLLAMA_NUM_PREDICT,
            "temperature": 0.2,
        },
    }
    response = post_json(OLLAMA_URL, payload, timeout=OLLAMA_TIMEOUT_SECONDS)
    output = response.get("response", "").strip()
    if not output and model != OLLAMA_GENERAL_MODEL:
        fallback_response = post_json(
            OLLAMA_URL,
            {
                "model": OLLAMA_GENERAL_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": OLLAMA_NUM_PREDICT,
                    "temperature": 0.2,
                },
            },
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
        output = fallback_response.get("response", "").strip()
    if not output:
        raise RuntimeError(f"Ollama model {model} returned an empty answer")
    return output


def call_groq(prompt):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

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
    response = post_json(
        GROQ_URL,
        payload,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=GROQ_TIMEOUT_SECONDS,
    )
    return response["choices"][0]["message"]["content"].strip()


def answer(prompt, offline=False, force_route=None, allow_cloud_fallback=True):
    route, reasons = choose_route(prompt, offline=offline, force_route=force_route)

    try:
        if route == "local":
            model, model_reason = choose_local_model(prompt)
            return route, reasons + [f"local model is {model}: {model_reason}"], call_ollama(prompt, model)
        return route, reasons, call_groq(prompt)
    except (urllib.error.URLError, RuntimeError, KeyError, OSError) as error:
        if route == "cloud" and allow_cloud_fallback:
            fallback_reasons = reasons + [
                f"cloud failed, falling back to Ollama: {error}",
                f"local fallback model is {OLLAMA_REASONING_MODEL}",
            ]
            try:
                return "local-fallback", fallback_reasons, call_ollama(prompt, OLLAMA_REASONING_MODEL)
            except (urllib.error.URLError, RuntimeError, OSError) as fallback_error:
                raise RuntimeError(f"cloud failed and local fallback also failed: {fallback_error}") from fallback_error
        if route == "cloud":
            raise RuntimeError(f"Groq cloud failed: {error}") from error
        raise RuntimeError(f"local Ollama failed: {error}") from error


def main():
    parser = argparse.ArgumentParser(description="EcoCascade AI laptop smart router")
    parser.add_argument("prompt", nargs="+", help="Prompt to route")
    parser.add_argument("--offline", action="store_true", help="Disable cloud routing")
    parser.add_argument("--dry-run", action="store_true", help="Only show the route decision")
    parser.add_argument("--force-local", action="store_true", help="Force Ollama local route")
    parser.add_argument("--force-cloud", action="store_true", help="Force Groq cloud route")
    parser.add_argument("--no-cloud-fallback", action="store_true", help="Do not fall back to Ollama if Groq fails")
    args = parser.parse_args()

    prompt = " ".join(args.prompt)
    force_route = None
    if args.force_local and args.force_cloud:
        print("\nError: choose only one of --force-local or --force-cloud", file=sys.stderr)
        sys.exit(1)
    if args.force_local:
        force_route = "local"
    if args.force_cloud:
        force_route = "cloud"

    route, reasons = choose_route(prompt, offline=args.offline, force_route=force_route)

    print(f"Route: {route}")
    print("Reasons:")
    for reason in reasons:
        print(f"- {reason}")
    if route == "local":
        model, model_reason = choose_local_model(prompt)
        print(f"Local model: {model}")
        print(f"Model reason: {model_reason}")

    if args.dry_run:
        return

    try:
        final_route, final_reasons, output = answer(
            prompt,
            offline=args.offline,
            force_route=force_route,
            allow_cloud_fallback=not args.no_cloud_fallback,
        )
        if final_route != route:
            print(f"\nFinal route: {final_route}")
            print("Final reasons:")
            for reason in final_reasons:
                print(f"- {reason}")
        print("\nAnswer:")
        print(output)
    except RuntimeError as error:
        print(f"\nError: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
