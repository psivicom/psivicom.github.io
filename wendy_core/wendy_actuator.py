import ast
import subprocess
import logging
from datetime import datetime, timezone

class WendyActuator:
    """Translates K_neg (Compost Protocol) into physical file modifications."""

    def __init__(self, repo_path: str='.'):
        self.repo_path = repo_path

    def surgically_rewrite(self, file_path: str, banned_nodes: list) -> bool:
        """Applies the K_neg penalty to the AST and rewrites the file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            tree = ast.parse(source_code)
            mutated_tree = self._apply_k_neg_to_ast(tree, banned_nodes)
            new_source_code = ast.unparse(mutated_tree)
            if new_source_code == source_code:
                return False
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_source_code)
            return self._execute_secure_commit(file_path)
        except Exception as e:
            logging.error(f'Actuator failed to rewrite {file_path}: {e}')
            return False

    def _apply_k_neg_to_ast(self, tree: ast.AST, banned_nodes: list) -> ast.AST:

        class CompostTransformer(ast.NodeTransformer):

            def visit_Import(self, node):
                return None if any((alias.name in banned_nodes for alias in node.names)) else node

            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute) and node.func.attr in banned_nodes:
                    return None
                return self.generic_visit(node)
        return CompostTransformer().visit(tree)

    def _execute_secure_commit(self, file_path: str) -> bool:
        """Executes a lock-free, autonomous git push using the scoped GITHUB_TOKEN."""
        zulu_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        commit_msg = f'chore(compost): autonomous K_neg heal at {zulu_time}'
        try:
            subprocess.run(['git', 'config', 'user.name', 'WENDY Autonomous Hive'], check=True, cwd=self.repo_path, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'wendy@psivicom.github.io'], check=True, cwd=self.repo_path, capture_output=True)
            subprocess.run(['git', 'add', file_path], check=True, cwd=self.repo_path, capture_output=True)
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True, cwd=self.repo_path, capture_output=True)
            subprocess.run(['git', 'push', 'origin', 'HEAD:main'], check=True, cwd=self.repo_path, capture_output=True)
            logging.info(f'Autonomous commit pushed successfully at {zulu_time}')
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Git push failed: {e.stderr.decode('utf-8')}")
            return False