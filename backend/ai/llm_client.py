import os
import requests
import json
import time
from groq import Groq
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
env_path = os.path.join(backend_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    load_dotenv(override=True)



def call_llm(prompt, temperature=0.4, max_tokens=4096):
    errors = []
    
    # 1. Try Groq with active model fallbacks
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        groq_models = [
            "openai/gpt-oss-120b",
            "qwen/qwen3.6-27b",
            "groq/compound-mini",
            "openai/gpt-oss-20b",
            "groq/compound"
        ]
        try:
            client = Groq(api_key=groq_key)
            for model in groq_models:
                try:
                    print(f"[LLM Client] Trying Groq ({model})...")
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    content = response.choices[0].message.content
                    if content:
                        return content.strip()
                except Exception as e_model:
                    errors.append(f"Groq ({model}) failed: {e_model}")
        except Exception as e_client:
            errors.append(f"Groq client failed: {e_client}")

    # 2. Try Gemini with active model fallbacks and retry on 429 rate limit
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        gemini_models = [
            "gemini-flash-latest",
            "gemini-flash-lite-latest",
            "gemini-3.5-flash-lite",
            "gemini-2.5-flash"
        ]
        for model in gemini_models:
            try:
                print(f"[LLM Client] Trying Gemini ({model})...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens
                    }
                }
                res = requests.post(url, json=data, headers=headers, timeout=30)
                if res.status_code == 429:
                    print(f"[LLM Client] Gemini ({model}) hit rate limit (429), retrying in 2 seconds...")
                    time.sleep(2)
                    res = requests.post(url, json=data, headers=headers, timeout=30)
                res.raise_for_status()
                res_json = res.json()
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                if text:
                    return text.strip()
            except Exception as e:
                errors.append(f"Gemini ({model}) failed: {e}")

    # 3. Try OpenRouter with active free & paid model fallbacks
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        openrouter_models = [
            "nvidia/nemotron-3.5-lightning:free",
            "google/gemma-4-26b-a4b-it:free",
            "z-ai/glm-5.2:free",
            "meta-llama/llama-3.3-70b-instruct"
        ]
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json"
        }
        for model in openrouter_models:
            try:
                print(f"[LLM Client] Trying OpenRouter ({model})...")
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                res = requests.post(url, json=data, headers=headers, timeout=30)
                res.raise_for_status()
                res_json = res.json()
                content = res_json['choices'][0]['message']['content']
                if content:
                    return content.strip()
            except Exception as e:
                errors.append(f"OpenRouter ({model}) failed: {e}")

    raise RuntimeError(f"All LLM Providers failed. Errors: {'; '.join(errors)}")

