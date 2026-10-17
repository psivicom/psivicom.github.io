import ast
import re
from typing import Dict, Any, List

class PerceptionParser:
    def __init__(self):
        self.syntax_error_pattern = re.compile(r"SyntaxError: (.*)")

    """Parses raw telemetry, code AST, and mesh environmental inputs into structured cognitive tokens."""
    def parse_code(self, source_code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(source_code)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            return {
                "status": "success",
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "node_count": len(list(ast.walk(tree)))
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e)
            }

    def parse_telemetry(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        processed = {}
        for k, v in metrics.items():
            if "cpu" in k.lower():
                processed[k] = {"value": v, "category": "compute_pressure"}
            elif "memory" in k.lower():
                processed[k] = {"value": v, "category": "memory_pressure"}
            else:
                processed[k] = {"value": v, "category": "general"}
        return processed
