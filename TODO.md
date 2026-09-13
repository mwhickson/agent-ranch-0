# TODO

- split (or at least reorganize) `run.py` into something more human-friendly (though Gemini has done pretty good so far)
- update init script to allow for named folder setup, including stubs for PROJECT_SPEC.md, etc.
- add a second project in another language (e.g. Go) to mirror the Python example to ensure the basic functionality holds up across languages
- allow agents greater autonomy (i.e. no need to check in with the human orchestrator for every task)
- allow "second opinion" agents - effectively the ability for an agent to generate a twin (in the same role/context) for pairing (programming, testing, reviewing, etc.) to produce highest/higher quality results
- allow splitting of roles internally into specific domains of concern - allow for security, accessibility, optimization, etc.
    - NOTE: roles like REVIEWER may become custom splits instead of their own unique role
- allow orchestrator intervention within the scope of `run.py` where sign-off is requested (e.g. "No, but what about if you tried this...")
- allow generation of the PROJECT_SPEC.md to be an in interative, interactive process with the PLANNER/DOCUMENTER (or new role for this purpose)
- add source control (Git) support
- add Model Context Protocol (MCP) skills support (or equivalent) - use this to get communication between agents out of the LLM context, and to permit establishing longer term, queryable context (e.g. wiki or other knowledge base/management system)
- add more integration with all the goals laid out in MISSION.md
- introduce increasingly complex projects to "test the waters" with the limits of the architecture, but also to devise new approaches to breaking down more complex projects into projects that can be handled by Agent-Ranch-0
- as much as this is a learning project, find out what already exists that operates in a similar manner at a wider rate of adoption to determine if Agent-Ranch-0 is the best solution for my personal projects
