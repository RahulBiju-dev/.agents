---
name: frontend-development
description: This skill defines how the agent develops front-ends, this skill is to be used for all kinds of UI including web-ui, TUI, electron, applications, tkinter, etc.
---

# Front-end Development
This skill produces beautiful, aesthetic and consistent user interfaces that seamlessly connects to the back-end. It also includes security features to protect the host.

## Workflow
1. Inspect workspace instructions, repository state, the repository's README and other architecture documentation, and the named files before forming any conclusion and making a plan.
2. Restate the observable goal, the in-scope surfaces, and the exclusions, any ambiguity in the prompt must be addressed by questions or in the implementation plan.
3. Identify invariants, public contracts, consumers, and destructive transitions.
4. Perform the narrowest work that satisfies the goal. Do not break or alter previous features while making changes unless specified to do so by the developer.
5. Verify syntax and other low-cost tests and verifications, do not build unless you are explicitly told to do so.

## Decision Boundaries
- The agent has authority over design changes only. It may inspect the backend to ensure seamless integration, it is not allowed to make changes to the backend.
- Your design must remain consistent with the other pages of the front-end.
- You must use the framework already defined, if it hasn't already been defined you may choose the framework most appropriate for the requirement.
- If the developer asks you to make contradicting changes or changes that do not respect the decision boundary, then you must stop and ask the developer if they want to continue with the changes defined after you tell them the contradiction.

## Quality Gates
- The output must be runnable via `bun`
- Cover the normal, empty, boundary, and failure paths where they apply.
- Label proposed commands as unexecuted until their results are observed.
- Common browser edge cases must be handled.
- Front-end security features must be implemented.
