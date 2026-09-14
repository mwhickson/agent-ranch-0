# Notes

- Gemini's context and reasoning skills seem much improved over my last encounter
- LLM workflow isn't particularly special, it's actually very organic and similar to managing people (when using roles)
- "LLM agents as people" is fairly loose here though, pertaining mostly to the ability to direct in plain, natural language -- albeit sometimes needing to resort to blunt legalese-style DOs and DON'Ts and CAPS-based emphasis
- role-based LLM workflow can be implemented as a straightforward serial state machine
- prompts do (or can do) a lot of the heavy lifting when dealing with code generation
- establishing strong communication protocols (often via JSON structures - our `action schema` in this case) makes communicating with LLMs less prone to error
- LLMs on a low temperature seem less prone to hallucination, when prompted with programming/software development tasks -- however, LLMs still make typo style mistakes
- LLM role-based agents are lazy, or highly-efficient depending on your view
- LLM role-based agents often try to one-shot solutions
- LLM role-based agents are prone to "game" requirements fulfillment by following the shortest path which can result in previously "completed" tasks being rubber-stamped in subsequent runs, unless explicit instructions to review are given
- keeping roles to short, well-defined activities with additional roles being used to evaluate the efforts of previous tasks by precursor roles seems to work well -- BUT, results in more opportunity for delays as the roles pass task ownership back and forth
- having roles agents write code, then write tests with an intermediate review stage to determine if code is doing the correct thing helps insulate from the variability that occurs in LLM task completion -- TDD, at macro or micro scale, seems too volatile for predictable, reliable, quality results (maybe not for bigger LLMs?)
- context is precious, and things can be bumped unexpectedly which results in potentially revisiting the same issues -- worth watching out for
- patience and perserverance are important (on the part of the human at keyboard), and it helps that your AI counterpart isn't usually subject to the
frustration, disappointment, and confusion that can result from AI-assisted development -- leverage that!
- let your frustration guide features and optimizations!
- apparently, according to Gemini, code capture via `cat` is common, and fairly effective when dealing with local LLMs (who occassionally try to use things like `sed` cleverly -- don't let that happen)
- having the agent express/log thoughts helps when determining why certain code/actions/etc. came to pass
- LLMs are fallible, (even moreso than humans?), but also so much better at maintaining focus and awareness, and dealing with complexity when provided with a fresh context of the task at hand (I asked Gemini to summarize all the work we did, and it summarized the last handful of interactions, and got the project name wrong... on the other hand, it regularly digested and correctly assessed issues when presented with logs, source code, screen captures and my own thoughts -- almost instantly!)
