import ast
import re
from typing import Dict, Any, List

class PerceptionParser:
    def __init__(self):
        self.patterns = [
            (re.compile(r'\b(error|fail|exception)\b', re.IGNORECASE), 'CRITICAL_ERROR'),
            (re.compile(r'\b(optimize|speed|fast|perf)\b', re.IGNORECASE), 'PERFORMANCE_INTENT'),
            (re.compile(r'\b(security|vulnerab|auth)\b', re.IGNORECASE), 'SECURITY_INTENT')
        ];

    def parse_text(self, text: str) -> List[str]:
        tags = []
        for pattern, tag in self.patterns:
            if pattern.search(text):
                tags.append(tag)
        return tags

    def parse_code_ast(self, source_code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return {"valid": False, "error": str(e), "functions": [], "classes": []}
        
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
                
        return {
            "valid": True,
            "functions": functions,
            "classes": classes,
            "node_count": len(list(ast.walk(tree)))
        }
