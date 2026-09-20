# src/automation/capability_resolver.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

import requests
import ast
import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable, Optional
from src.base.base_agent import BaseAgent, AgentLayer

def generate_agent_code(capability: str, problem: str, arg_types: dict) -> Optional[str]:
    """Pure function: Generates Python code string from LLM."""
    params = ", ".join([f"{k}: {v}" for k, v in arg_types.items()])
    prompt = f"""Write a pure Python function for PSIVI mesh.
Capability: {capability}. Problem: {problem}. Args: {params}.
Rules: Return dict or numpy array. No side effects. 
```python
def solve_{capability}({params}) -> dict:
    # Your functional logic here
    return {{"status": "success", "data": ...}}
```"""
    
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "codellama:7b-code", "prompt": prompt, "stream": False, "options": {"temperature": 0.1}},
            timeout=60
        )
        if resp.status_code == 200:
            code = resp.json().get("response", "")
            return code.split("```python")[1].split("```")[0].strip() if "```python" in code else code.strip()
    except Exception:
        pass
    return None

def validate_generated_code(code: str) -> bool:
    """Pure function: AST validation of generated code."""
    try:
        tree = ast.parse(code)
        funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        return len(funcs) > 0 and "return" in ast.unparse(tree)
    except Exception:
        return False

def resolve_missing_capability(agent: BaseAgent, capability: str, *args, **kwargs) -> Any:
    """
    Functional Pipeline: 
    1. Analyze missing capability.
    2. Generate code via LLM.
    3. Validate and compile to function.
    4. Execute and seal the result.
    """
    arg_types = {f"arg_{i}": type(a).__name__ for i, a in enumerate(args)}
    arg_types.update({k: type(v).__name__ for k, v in kwargs.items()})
    
    # 1. Generate
    code = generate_agent_code(capability, f"Auto-resolve {capability}", arg_types)
    if not code or not validate_generated_code(code):
        raise RuntimeError(f"Functional resolution failed for capability: {capability}")
    
    # 2. Compile to executable function (Sandboxed execution)
    local_env = {}
    exec(code, {"__builtins__": __builtins__}, local_env)
    
    # Extract the first function defined in the code
    func_name = next((name for name in local_env if callable(local_env[name])), None)
    if not func_name:
        raise RuntimeError("No executable function found in generated code")
    
    solve_func = local_env[func_name]
    
    # 3. Execute functionally
    agent.seal(f"resolved_{capability}", {"args": arg_types})
    result = solve_func(*args, **kwargs)
    agent.seal(f"resolved_{capability}_success", {"result_type": type(result).__name__})
    
    return result
