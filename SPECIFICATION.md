# Agent-0 Specification

## Overview

Agent-0 is a human-orchestrated, local-first AI development system for project definition, software engineering, quality assurance, deployment, and maintenance.

Agent-0 emphasizes reproducible execution, strict environment boundaries, transparent audit trails, and human-verifiable outputs under the operational principle: **"Always be ready to ship."**

---

## Technical Stack

### Approved
* **Languages & Runtimes:** Go (Wails, Fyne, Bubbletea), Python, Node.js, Bash / Coreutils.
* **Storage & Data Formats:** Plaintext, Markdown, CSV, XML, JSON, SVG, HTML, CSS, SQLite.
* **Development & Tooling:** Git, Gitea, Vim, VS Code, Linux (Debian-based; Mint preferred).
* **Local AI Infrastructure:** GGUF-based models via `llama.cpp` or `Koboldcpp`.

### Prohibited
* **Remote Network Access:** Strictly forbidden by default. Remote resources may only be accessed via local network bridges explicitly authorized by the Human Orchestrator.

---

## Project Isolation & Sandbox

1. **Local Scope:** All project resources, dependencies, and state MUST reside within the local project directory.
2. **Environment Isolation:** Runtimes MUST use project-scoped package managers and local environments (e.g., Python `.venv`, Node `./node_modules`, local Go modules). Global package installs are prohibited.
3. **Execution Context:** All operations run assuming a shared bare-metal environment with bounded storage, CPU, and RAM parameters. Dynamic GPU access SHOULD be utilized if available, but GPU presence MUST NOT be assumed.

---

## Role Definitions

* **ORCHESTRATOR:** Long-running system overseer. Manages task state, gates system permissions, and approves/denies requests requiring elevated human approval.
* **PLANNER:** Parses specs, decomposes requirements, and generates atomic, actionable task specifications.
* **BUILDER:** Implements source code, applies bug fixes, and resolves issues assigned by Planner, Reviewer, or Tester roles.
* **REVIEWER:** Inspects Builder outputs for code quality, adherence to specifications, and compliance with constraints.
* **TESTER:** Executes automated test suites and manual validation procedures against Reviewed outputs.
* **DOCUMENTER:** Generates user-facing guides, API references, and architecture documentation.

---

## Core Invariants (Hard Rules)

All agents and human operators MUST enforce the following constraints without exception:

1. **Human Oversight:** Any irreversible, destructive, or remote network operation MUST require explicit prior approval from the Human Orchestrator.
2. **Role Boundaries:** Agents MUST act exclusively within their assigned role responsibilities. Cross-role recommendations are permitted, but execution outside assigned roles is prohibited.
3. **Tooling Scopes:** Agents MAY only execute tools and skills explicitly approved for their active role.
4. **Deterministic Task Outcomes:** Every task execution MUST return exactly one terminal status:
   * `PASS`: Objective completed successfully. Triggers progression to the next workflow stage.
   * `FAIL`: Objective failed after exhausting valid alternatives. Triggers notification and investigation.
   * `BLOCKED`: Dependency or authorization missing. Triggers notification to Orchestrator or dependent agent.
5. **Loop Prevention & Retry Limits:** Infinite execution loops are prohibited. Tasks MUST NOT exceed **3 consecutive failed attempts**. If a task cannot resolve within 3 attempts, it MUST terminate with a `FAIL` or `BLOCKED` status.
6. **Auditability & Traceability:** All agent actions, subshell commands, state transitions, and environmental alterations MUST be logged to human-readable, auditable formats within the project directory.

---

## Execution Guidelines

1. **Output Standard:** Prioritize human-readable, human-verifiable, and machine-reproducible artifacts over dense black-box outputs.
2. **Alternative Exploration:** If an approach fails, agents SHOULD explore viable local alternatives before declaring a task `FAIL` or `BLOCKED`.
3. **State Management:** Current task states and process logs MUST remain accessible to both agents and human operators at all times.
4. **Context & Non-Technical Logging:** Licensing, copyright, accessibility considerations, and non-technical decision factors MUST be recorded alongside primary project artifacts.
5. **Adaptive Workflow Optimization:** Proven procedural optimizations SHOULD be captured and integrated into subsequent workflow iterations.
