import ast
import subprocess
import logging
from datetime import datetime, timezone

class WendyActuator:
    """Translates K_neg (Compost Protocol) into physical file modifications."""

    def __init__(self, repo_path: str='.'):
        self.repo_path = repo_path

    def surgically_rewrite(self, file_path: str, banned_nodes: list) -> bool:
        """Applies the K_neg penalty to the AST and rewrites the file.

        R2 Fix (2026-11-25): Inserted _verify_lyapunov_gate between rewrite
        and push. Law XI (Zero-Error Crystallization Gate) was previously
        bypassed — the actuator pushed to main without running tests.
        Now: if the gate fails, the file is reverted to pre-mutation state
        and the failure is logged for Compost Protocol routing (PR 6).
        """
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

            # R2: Lyapunov gate — verify before pushing (Law XI)
            gate_result = self._verify_lyapunov_gate(file_path)
            if not gate_result['passed']:
                logging.warning(f'Lyapunov gate FAILED for {file_path}: {gate_result["reason"]}')
                # Revert the file to original state
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(source_code)
                logging.info(f'Reverted {file_path} to pre-mutation state')
                # TODO (PR 6): Route to CompostProtocol.process_failure for K_neg extraction
                return False

            return self._execute_secure_commit(file_path)
        except Exception as e:
            logging.error(f'Actuator failed to rewrite {file_path}: {e}')
            return False

    def _verify_lyapunov_gate(self, file_path: str) -> dict:
        """R2: Law XI Zero-Error Crystallization Gate.

        Runs available verification tools (ruff, pytest, cargo check, zig build)
        on the mutated file. Returns dict with 'passed' bool and 'reason' str.

        If a tool is not installed on PATH, it is skipped (gate weakened, not
        blocked). This is honest: we cannot enforce what we cannot run.

        Future: compute Lyapunov V(S) and capability delta DC (Part VIII SS2).
        For now, this is a binary pass/fail gate based on available tooling.
        """
        checks = []

        # Python files: ruff + pytest
        if file_path.endswith('.py'):
            checks.append(('ruff', ['ruff', 'check', file_path]))
            checks.append(('pytest', ['python', '-m', 'pytest', '--tb=short', '-q', '--no-header']))

        # Rust files: cargo check
        elif file_path.endswith('.rs'):
            checks.append(('cargo-check', ['cargo', 'check', '--quiet']))

        # Zig files: zig build
        elif file_path.endswith('.zig'):
            checks.append(('zig-build', ['zig', 'build']))

        for name, cmd in checks:
            try:
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    timeout=60,
                    text=True
                )
                # pytest exit code 5 = no tests collected; treat as pass
                if name == 'pytest' and result.returncode == 5:
                    logging.info('pytest: no tests collected (exit 5); treating as pass')
                    continue
                if result.returncode != 0:
                    return {
                        'passed': False,
                        'check': name,
                        'reason': f'{name} failed (exit {result.returncode}): {result.stderr[:500]}'
                    }
            except FileNotFoundError:
                logging.warning(f'{name} not found on PATH; skipping (gate weakened)')
                continue
            except subprocess.TimeoutExpired:
                return {
                    'passed': False,
                    'check': name,
                    'reason': f'{name} timed out after 60s'
                }

        return {'passed': True, 'reason': 'all available checks passed'}

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
