#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WENDY LLM Query Engine
SPDX-License-Identifier: EUPL-1.2
Simple machine-to-machine HTTP queries to free LLM web endpoints.
Treats LLMs as web services. Sovereignty preserved through verification.
"""
import requests
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

def zulu_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def log(msg):
    print(f"[{zulu_now()}] [LLM-QUERY] {msg}", flush=True)

class WendyLLMQuery:
    """
    Machine-to-machine HTTP queries to free LLM web endpoints.
    Simple, sovereign, no browser automation needed.
    """
    
    def __init__(self, cortex_dir: Path):
        self.cortex_dir = cortex_dir
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WENDY-Sovereign-Agent/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        
        # Free LLM web endpoints (many have simple HTTP APIs)
        self.endpoints = {
            "huggingface": {
                "name": "Hugging Face Inference",
                "url": "https://api-inference.huggingface.co/models/codellama/CodeLlama-34b-Instruct-hf",
                "requires_key": True,
                "key_env": "HF_API_KEY"
            },
            "groq": {
                "name": "Groq (Llama 3.1 70B)",
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "requires_key": True,
                "key_env": "GROQ_API_KEY"
            }
        }
    
    def query_huggingface(self, question: str, api_key: str) -> Optional[str]:
        """
        Query Hugging Face inference API (free tier available).
        Simple POST request, JSON response.
        """
        log(f"🤖 Querying Hugging Face (CodeLlama 34B)...")
        
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            
            payload = {
                "inputs": f"Question: {question}\n\nAnswer:",
                "parameters": {
                    "max_new_tokens": 1500,
                    "temperature": 0.3,
                    "return_full_text": False
                }
            }
            
            response = self.session.post(
                self.endpoints["huggingface"]["url"],
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    answer = data[0].get("generated_text", "")
                    log("✅ Hugging Face responded")
                    return answer
            
            log(f"❌ Hugging Face failed: {response.status_code}")
            return None
            
        except Exception as e:
            log(f"❌ Hugging Face error: {e}")
            return None
    
    def query_groq(self, question: str, api_key: str) -> Optional[str]:
        """
        Query Groq API (free tier, Llama 3.1 70B).
        OpenAI-compatible API, very fast.
        """
        log(f"🤖 Querying Groq (Llama 3.1 70B)...")
        
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            
            payload = {
                "model": "llama-3.1-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a compiler expert. Provide concise, correct code solutions."
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = self.session.post(
                self.endpoints["groq"]["url"],
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data["choices"][0]["message"]["content"]
                log("✅ Groq responded")
                return answer
            
            log(f"❌ Groq failed: {response.status_code}")
            return None
            
        except Exception as e:
            log(f"❌ Groq error: {e}")
            return None
    
    def query_llm(self, llm_name: str, question: str, api_key: str = "") -> Optional[str]:
        """
        Query a specific LLM by name.
        """
        if llm_name not in self.endpoints:
            log(f"❌ Unknown LLM: {llm_name}")
            return None
        
        endpoint = self.endpoints[llm_name]
        
        if endpoint["requires_key"] and not api_key:
            log(f"⚠️ {llm_name} requires API key")
            return None
        
        if llm_name == "huggingface":
            return self.query_huggingface(question, api_key)
        elif llm_name == "groq":
            return self.query_groq(question, api_key)
        
        return None
    
    def extract_code(self, response: str, language: str = "zig") -> Optional[str]:
        """
        Extract code blocks from LLM response.
        """
        pattern = rf"```{language}\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        pattern = r"```\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        return None

# Example usage
if __name__ == "__main__":
    import os
    cortex_dir = Path(__file__).parent.parent / "wendy-cortex"
    querier = WendyLLMQuery(cortex_dir)
    
    question = """
    I have this Zig code that fails to compile:
    
    var i: usize = 0;
    while (i < 10000) : (i += 1) {
        buffer[i] = @as(f64, @floatFromInt(i));
    }
    
    Error: unused local variable
    
    How do I fix this and unroll the loop 4x?
    """
    
    # Get API key from environment
    api_key = os.environ.get("HF_API_KEY", "")
    
    if api_key:
        response = querier.query_llm("huggingface", question, api_key)
        if response:
            print("\n=== LLM RESPONSE ===")
            print(response)
            
            code = querier.extract_code(response, "zig")
            if code:
                print("\n=== EXTRACTED CODE ===")
                print(code)
    else:
        print("Set HF_API_KEY environment variable to test")
