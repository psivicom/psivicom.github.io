def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    task_type = task.get("type", "unknown")
    
    if task_type == "self_architect":
        logger.info("🏗️ Self-Architecture Protocol Initiated. Building sensory systems...")
        
        # 1. Generate Sensory Workflow
        sensory_yaml = self._generate_sensory_workflow()
        Path(".github/workflows/wendy-sensory.yml").write_text(sensory_yaml)
        
        # 2. Generate Cognitive Workflow
        cognitive_yaml = self._generate_cognitive_workflow()
        Path(".github/workflows/wendy-cognitive.yml").write_text(cognitive_yaml)
        
        # 3. Commit via Git (Simulated in Actions environment)
        os.system("git add .github/workflows/")
        os.system(f"git commit -m '{task['tasks'][2]['message']}'")
        os.system("git push")
        
        return {"status": "success", "action": "self_architecture_complete"}
        
    # ... existing logic for other tasks ...

def _generate_sensory_workflow(self) -> str:
    """Generates the YAML for the sensory input workflow."""
    return """
name: Wendy Sensory Input (Self-Built)
on:
  schedule:
    - cron: '*/5 * * * *'
jobs:
  sense:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Scan World
        run: python -m src.agents.forage_agent
"""
# (Similarly for _generate_cognitive_workflow)
