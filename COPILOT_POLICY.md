# COPILOT_POLICY.md

This repository is a deterministic scientific and engineering research repository. It is not a paid-API or “Coke machine” automation project.

**Core policy** “WENDY ❤️ IS NOT A COKE MACHINE ASKING DO YOU HAVE MONEY ?”

• No paid LLM APIs or paid model providers may be introduced without explicit maintainer approval.

• No billing keys, API keys, or secrets may be committed to the repository or checked into git history.

• No scheduled or auto-triggered workflow may create GitHub issues or comments as a default behavior unless explicitly approved by maintainers.

• All research workflows must produce deterministic, reviewable, provenance-bearing artifacts in a controlled data/ or reports/ location.

• All code changes involving model access, external APIs, issue automation, or workflow permissions require maintainer review.

• Prefer local or volunteer-hosted inference, local vector/indexing, and reproducible pipelines.

• Any dependency that requires a paid account, billable key, or external cloud LLM must be treated as a project exception and documented in a change request.

Allowed patterns

• Local open-source models or self-hosted services

• Deterministic scripts and data pipelines

• Controlled artifact generation

• Reproducible research reports and metadata

• Volunteer node compute without cloud billing

Forbidden patterns

• Direct calls to paid LLM providers (e.g. OpenAI, Gemini, Anthropic, Azure OpenAI, etc.) in repo code or workflows without explicit exception

• Secrets, tokens, AWS/GCP keys, SSH private keys, or PATs checked into git

• Auto-issue creation or comment spam from scheduled workflows

• Self-modifying workflow code that changes repository state without human review and provenance

• “AI personality” workflows that produce noise rather than research artifacts

Review requirements

• Changes to .github/workflows, src/agents, src/kernel, model adapters, and external API code require human review and pass CI checks before merge.

• All workflow changes must be traceable and must not create issue/comment spam by default.

This policy applies to code generation, workflow creation, infrastructure scaffolding, and repo operation.EOF
