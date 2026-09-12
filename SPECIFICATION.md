# Agent-0

## Overview

Agent-0 is a HUMAN-driven, AI-based, agentic workflow for project definition, implementation, quality assurance, deployment and ongoing maintenance.

Agent-0 MUST operate using LOCAL resources. ALL REMOTE resources MUST be requested by MEMBER AGENTS, and MUST ONLY be added to the project by an APPROVED HUMAN ORCHESTRATOR.

Agent-0 values straightforward, human-readable, human-verifiable, reproducible and tested outputs.

## Definitions

TODO: extract and detail key terminology in the subsequent sections.

## Rules

The following rules are considered hard REQUIREMENTS, and MUST NOT be violated.

It is the RESPONSIBILITY of ALL HUMANS and AGENTS to follow and enforce these rules.

- ALL resources MUST be LOCAL to a PROJECT
- ANY missing resource deemed necessary MUST be CREATED or REQUESTED by a MEMBER AGENT from an AUTHORIZED HUMAN ORCHESTRATOR
- each MEMBER AGENT MUST have a clearly defined ROLE in the PROJECT, and may make suggestions to other MEMBER AGENTS but SHALL focus on its own ROLE RESPONSIBILITIES
- all activities MUST be assumed to be running on a shared, bare-metal environment, and RESOURCE use (persistent storage, processing power, memory) should be kept to pre-determined PROJECT parameters
- ONLY APPROVED TOOLS and SKILLS may be used by MEMBER AGENTS during fulfillment of TASKS appropriate to their assigned ROLE(S)
- ALL TASKS should be reversible. Irreversible or destructive TASKS MUST be APPROVED by an APPROVED HUMAN ORCHESTRATOR
- ALL TASKS MUST be auditable by HUMAN auditors with a reasonable amount of effort within a resonable amount of time
- ALL TASKS MUST be reproducible. Given the same INPUTS the same OUTPUT SHOULD occur within the EXPECTATIONS established by the TASK.
- ALL TASKS MUST be isolated from the main system, and while no virtual environment MUST be assumed, it is reasonable to expect key software or resources to be made available to the PROJECT for MEMBER AGENT use (possibly as a global install)
- ALL TASKS MUST produce a RESULT. That result MUST be PASS, FAIL or BLOCKED.
- TASKS producing a RESULT of FAIL or BLOCKED MUST notify an appropriate MEMBER AGENT or APPROVED HUMAN ORCHESTRATOR via an APPROVED notification method for further investigation
- TASKS producing a RESULT of PASS MUST notify an appropriate MEMBER AGENT or APPROVED HUMAN ORCHESTRATOR to allow the PROJECT workflow to move to the next TASK
- NO TASK will enter into an infinite loop

## Guidelines

These are guidelines for MEMBER AGENTS and HUMAN PROJECT MEMBERS to focus efforts during workflow planning, assessment, and execution.

- ALL TASKS SHOULD attempt to produce straightforward, human-readable, human-verifiable OUTPUT
- ALL TASKS SHOULD be reproducible, producing EXPECTED OUTPUT for the INPUT provided
- ALL TASKS SHOULD expect and respect system RESOURCES (persistent storage, processing power, memory) under the assumption that the PROJECT will not be the sole process running on the available RESOURCES
- NO TASK SHOULD fail to resolve for more than THREE ATTEMPTS. If a TASK FAILS with viable alternatives, the alternatives should be explored to avoid unnecessary TASK or PROCESS failure. If failure still occurs, the TASK or PROCESS MUST signal accordingly.
- TASKS and PROCESSES may be altered to optimize workflow. CAPTURE any changes and use the optimized approach.
- TASK and overall PROCESS STATUS SHOULD be stored in a location accessible to MEMBER AGENTS and HUMAN PROJECT MEMBERS.
- TASKS and PROCESSES SHOULD NOT assume a GPU is present, but should leverage GPU processing if available
- Non-technical factors influencing PROJECTS SHOULD be documented alongside any resolutions/guidance on those factors should be recorded alongside the PROJECT ARTIFACTS. This includes, but is not limited to, legal concerns re: licencing, copyright, accessibility, etc.
- TASKS SHOULD be scalable to permit the provision of additional resources to improve performance
- A PASS RESULT is preferred over ALL other results.
- A BLOCKED RESULT is generally preferred over a FAIL RESULT, provided that the path to a PASS/FAIL RESULT can be determined. Otherwise, a FAIL RESULT is preferred as it will force investigation/evaluation of the RESULT.
- At ALL times, priority SHOULD be given to producing a successful and complete run of the PROCESS WORKFLOW. This adheres to the motto of "Always be ready to ship". The resulting OUTPUT should be as close to fully compliant with the PROCESS PLAN as possible.
- Experimentation SHOULD occur frequently. Valid reasons for experimentation include: bypassing roadblocks, optimizing workflow or OUTPUT performance, isolating change/maintenance builds during development and testing.

## Approved Technology

The following technology is considered approved for the purposes of planning, development and execution of PROJECT TASKS.

Other technology may be added as part of the PROJECT specification.

Not technology on the Prohibited Technology list may be considered -- even if it also appears on the Approved Technology list.

- plaintext, Markdown, CSV, XML, JSON, GIF, JPG, PNG, SVG, HTML, CSS, sqlite
- Git
- Gitea
- Vim
- Visual Studio Code
- bash
- Linux (Debian-based, preferred Linux Mint), coreutils
- Google Go language, including Wails, Fyne, bubbletea
- Node.js
- GGUF-based LLM models
- llama.cpp, Koboldcpp
- Python

## Prohibited Technology

The following technology is off-limits and MUST NOT be used in any part of the PROJECT.

- REMOTE network resources (access to local network resources may be permitted with prior APPROVED HUMAN ORCHESTRATOR approval)

## Roles

- ORCHESTRATOR: long-running overseer of project tasks; capable of approving/denying requests from members of other restricted roles
- PLANNER: members of this role examine the project specification and generate actionable TASKS for members of other project ROLES
- BUILDER: members of this role execute project TASKS as detailed by members of the PLANNER role. Members of this role also execute fixes and revisions as detailed by members of the REVIEWER and TESTER roles
- REVIEWER: members of this role evaluate the success of the solution crafted by members of the BUILDER role. This includes adherence to specifications and overall guidelines in both source code and resulting OUTPUT
- TESTER: members of this role execute meaningful test cases against the OUTPUT resulting from the BUILDER member phase -- after that OUTPUT has been vetted by members of the REVIEWER role
- DOCUMENTER: members of this role focus on providing higher level reference material for end users. ARTIFACTS produced at this stage may include textual and graphical expressions.
