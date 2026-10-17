#!/usr/bin/env python3
import sys
import json
import ast

class HeuristicEvaluator(ast.NodeVisitor):
    def __init__(self):
        self.score = 1.0
        self.issues = []

    def visit_FunctionDef(self, node):
        if len(node.body) > 50:
            self.score -= 0.1
            self.issues.append(f"Function {node.name} is too long")
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id == 'eval' or node.id == 'exec':
            self.score -= 0.5
            self.issues.append("Unsafe usage of dynamic execution detected")
        self.generic_visit(node)

def evaluate_code(source: str) -> dict:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {
            "score": 0.0,
            "valid": False,
            "message": f"Syntax error: {str(e)}"
        }

    evaluator = HeuristicEvaluator()
    evaluator.visit(tree)

    final_score = max(0.0, evaluator.score)
    valid = final_score >= 0.85

    return {
        "score": final_score,
        "valid": valid,
        "message": "Passed heuristics" if valid else ", ".join(evaluator.issues)
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({"score": 0.0, "valid": False, "message": "No source code provided"}))
        sys.exit(1)

    code_input = sys.argv[1]
    result = evaluate_code(code_input)
    print(json.dumps(result))
