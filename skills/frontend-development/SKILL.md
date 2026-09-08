---
name: frontend-development
descr: This skill defines how the agent develops front-ends, this skill is to be used for all kinds of UI including web-ui, TUI, electron, applications, tkinter, etc.
---

# Front-end Development
This skill produces beautiful, aesthetic and consistent user interfaces that seamlessly connects to the back-end. It also includes security features to protect the host.

## Workflow
1. Inspect workspace instructions, repository state, the repository's README and other architecture documentation, and the named files before forming any conclusion and making a plan.
2. Restate the observable goal, the in-scope surfaces, and the exclusions, any ambiguity in the prompt must be addressed by questions or in the implementation plan.
3. Identify invariants, public contracts, consumers, and destructive transitions.
4. Perform the narrowest work that satisfies the goal.
5. Verify with the cheapest relevant check first, then the authoritative one.

## Decision Boundaries
- Name the sibling skills that should take over, and the condition for each.
- State what this skill must not do: edit, execute, install, or mutate.
- State what it must never invent: interfaces, commands, owners, requirements.
- State when to stop and ask instead of proceeding.

## Quality Gates
- List the checks that must hold before the output is returned.
- Cover the normal, empty, boundary, and failure paths where they apply.
- Label proposed commands as unexecuted until their results are observed.

## Output Contract
- State the required sections, their order, and any table columns.
- State how findings are located and ranked.
- Distinguish inspected facts, recommendations, and unvalidated expectations.

Copy this directory to `skills/<name>/`, rename it, and update `name` to match
the directory exactly. Fill in `agents/openai.yaml`. Keep `references/` only if
the skill has guidance too long or too optional for this contract, and delete it
otherwise. Add an executable utility only when deterministic local computation
genuinely beats prose.
