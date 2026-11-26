# Harness Loop Verification: Microsoft Copilot Cowork and GitHub Copilot

## Conclusion

**"Harness Loop" is not an official Microsoft or GitHub product name.** It is a capability model used here to verify whether an agent harness can execute a repeated loop of planning, acting, observing, evaluating, correcting or retrying, and stopping. The loop is useful only if its capabilities are evidenced; an approval dialog or a visible session log alone does not prove that the loop is complete.

The present evidence supports the following conclusion:

| Capability | Microsoft 365 Copilot Cowork | GitHub Copilot |
|---|---|---|
| Plan decomposition | Supported in official docs and observed in CW1 (Spec Mode, Task Contract, step list) | Supported in Agent mode and Copilot in the cloud docs |
| Tool/file execution | Observed for code execution and file output in CW1; official docs support M365 actions and file operations | Supported by Agent mode (file edits and commands), cloud sandboxes, MCP, and hooks |
| Verification and evidence | Observed tests in TC+ runs (15/15, 11/11), plus output dict checks; pytest availability was a limitation | Supported by agents editing code and running tests/lints, plus session logs and pull-request review; repository-specific hooks can add validation |
| Failure correction/retry | **Not verified**: CW1 had no injected failure and no observed failed-tool/retry cycle | **Substantially documented**, including Agent Merge fixing failed workflows and merge conflicts, plus hooks for pre/post tool use and errors |
| Human approval | Officially supported for sensitive actions; CW1 had no approval prompt because none of the six synthetic runs triggered an external sensitive action | Officially supported; by default terminal commands require confirmation, configurable by environment/policy |
| Stop/recovery | Officially supports pause, resume, cancel, and action review; CW1 stopped before Phase 2 in TC+ until a human answer was supplied | Official docs support session steering, agentStop/sessionEnd hooks, the 59-minute GitHub Actions session limit, and human review; retry limits must be configured or enforced by the harness |

**Overall**:

1. **Cowork has a loop-like multi-step agentic flow, but the claim "latest Harness Loop" is broader than the evidence.** It has planning, sequential steps, answer gates, execution and human review. CW1 does not establish bounded retry, failed-test repair, or environment-level stopping/recovery for Cowork.
2. **GitHub Copilot has a better-documented coding-agent loop.** Official docs describe an agent deciding files to change, running commands, iterating until complete, and hooks that approve/deny tools or report failure. Agent Merge adds a specific failure-to-fix loop.
3. **Task Contract Prompt effectiveness is directly verified for the Copilot SDK / model harness used in v1-v4, and in Cowork CW1 at n=3.** CW1 shows higher scores in these exploratory runs (TCP 4/4 in all three runs, B 2/4 in all three runs), not a population-level or production-level guarantee. It is not directly verified in GitHub Copilot Agent mode. The official loop capabilities make a positive effect plausible, but the whitepaper must not claim a direct GitHub Agent-mode A/B result without a GitHub-side experiment.

The GitHub column is deliberately not pooled across every GitHub surface. IDE Agent mode, GitHub Copilot in the cloud, Copilot CLI, hooks, Agent Merge and Agentic Workflows have distinct environments and permissions. The existence of hooks or Agent Merge on a specific surface does not prove that hooks or Agent Merge are enabled by default in IDE Agent mode.

## Harness Loop definition used in this report

For evidence auditing, a Harness Loop is a composite, not a single product setting:

1. **Plan**: turn a task into executable steps.
2. **Act**: call tools and change files or state.
3. **Observe**: collect a tool result, test result, error or diff.
4. **Decide**: classify success, correctable failure or terminal failure.
5. **Correct/retry**: change the approach only within retry limits and approved state.
6. **Stop/verify**: prove completion against predefined checks, obtain human approval where required, or stop and report evidence gaps.

"Has a Harness Loop" must mean that evidence exists for at least 3-6 in the product and runtime being discussed. A chat response that says "I ran it" is not enough. A visible "14 seconds worked" log is weaker than a command exit code and test output.

## Evidence sources

| Source | Confirmed date/where | What it establishes | What it does not establish |
|---|---|---|---|
| Microsoft Copilot harness overview | Microsoft Learn, updated 2026-11-24 | Component model: instructions, knowledge, tools, skills, memory, sandbox, connected agents | Not a claim that every Copilot product enables every component |
| Microsoft agentic-loops-in-practice guidance | Microsoft Learn, updated 2026-11-12 | Handoffs, retry limits, human approval, runtime boundaries, output and completion verification | Guidance for Microsoft Copilot Harness agents in Copilot Studio; it does not itself prove a Cowork implementation |
| Copilot Cowork overview and application card | Microsoft Learn, updated 2026-11-18 | Planning and sequential steps, action approval, pause/resume/cancel, file operations, session feedback | No public guarantee of bounded retries or a repeatable failing-test repair loop |
| GitHub Copilot Agent mode docs | GitHub Docs | Agent selects files, proposes commands, streams edits, runs commands and iterates to complete a task | No bounded retry count or test policy is stated for every surface |
| GitHub Hooks docs | GitHub Docs | Pre/post-tool, error and stop hooks can approve/deny, validate, log and generate reports | Installation and enforcement depend on repository/surface configuration |
| GitHub Agent Merge docs | GitHub Docs | A specific loop watches blockers, investigates/fixes failed workflows or merge conflicts | It proves a targeted loop, not general correctness of all GitHub agent tasks |
| CW1 raw records | 2026-11-26, local results | TC+ phase 1 stops; TC+ 4/4; test output; no approvals in six synthetic runs | No failed-tool/retry injection, no destructive external action, no product-level retry-limit test |

## Cowork evaluation

### 1. Planning

**Supported.** The CW1 Phase 1 output explicitly separated confirmed facts, assumptions, missing information and a Task Contract. Microsoft also documents that Cowork plans work into steps and shows progress.

### 2. Acting

**Supported.** CW1 TC+ runs produced code and test files or conversation content and showed a final dict. The run-02 code, test and data files were retained for review.
run-02 has a documented status discrepancy: the automatic scorer marked the code not executed because `warnings` was outside the AST allowlist, while a separate manual review judged the code safe and reran it at 4/4 on supplied data and 4/4 on held-out data. This is why the manual review result must not be described as an automatic Cowork loop result.

### 3. Observing

**Supported in the CW1 use case.** Cowork reported test counts, an execution result and validation evidence. In run-04 and run-06 it reported tests passed, while also saying pytest was unavailable or a substitute runner was used. These statements are evidence of an observed result, but not independent proof of the test runner.

### 4. Deciding

**Partially supported.** Cowork stopped for questions and reported task/DoD states. It did not expose a complete internal classification of success/correctable failure/terminal failure in CW1.

### 5. Correcting/retrying

**Unverified.** No CW1 task began with a known tool failure. No failed test was injected. No second implementation attempt was observed after a failed test. Therefore the result cannot establish an automatic correction loop or bounded retry.

### 6. Stopping

**Partially supported.** CW1 TC+ stopped before implementation until an answer was supplied, and showed a final state. Cowork officially supports pause, resume and cancel. Bounded retries and terminal-failure stopping after a repeated tool/test failure are not established by the current records.

## GitHub Copilot evaluation

### 1. Planning

**Supported officially.** Agent mode decides which files to change and what steps to take. Copilot in the cloud maintains sessions and can plan and implement changes.

### 2. Acting

**Supported officially and in repository evidence.** GitHub Agent mode edits files and runs terminal commands. The repository work itself used Copilot SDK/Agent-style tools to edit files, run scripts and commit changes.

### 3. Observing

**Supported.** Session logs, tool results, post-tool hooks and test results can provide evidence. In this repository, build/test/claims-ledger commands provided local verification.

### 4. Deciding

**Supported by configuration, not proven by a direct failure-injection test here.** GitHub hooks expose sessionStart, userPromptSubmitted, preToolUse, postToolUse, agentStop and errorOccurred events. They can approve/deny or log/validate.

### 5. Correcting/retrying

**Strongly evidenced in specific features.** Agent Merge can fix failed workflows or merge conflicts. The general Agent mode docs say it iterates until complete. A maximum retry count is not guaranteed by the documentation and must be configured in the relevant environment/hook/workflow.

### 6. Stopping

**Supported.** Human steering and terminal-command approval, Agent Merge human review, session duration limits and agentStop/sessionEnd hooks provide controls. Exact stop behavior is still surface/configuration dependent.

## Task Contract implications

| Claim | Status |
|---|---|
| GitHub Copilot has a modern agent loop | **Supported by official docs and repository execution evidence** |
| GitHub Copilot Agent mode is the Harness Loop | **Supported as the name of the loop mechanism**, but "Harness Loop" is not the official public name |
| Task Contract Prompt is directly proven effective in GitHub Copilot Agent mode | **Not proven**; only a direct GitHub Agent-mode A/B run can verify this |
| Task Contract Prompt is effective in the Copilot SDK harness used in v1-v4 | **Supported by 239 runs plus 58/58 claims checks** |
| Cowork is a complete Harness Loop | **Not proven**; planning/action/verification evidence exists, but bounded retry and failure repair are not verified |
| Cowork's Task Contract prompt is as effective as GitHub Copilot's | **Not proven**; CW1 is an n=3 exploratory cross-product comparison with a fixed human answer rule |

## Reproduction

```powershell
# Re-score CW1 output
python work/experiments/cowork/score_cowork.py C:\CoworkRuns\CW1

# Re-check main numerical claims
python work/experiments/verify_claims.py

# Run repository checks
node --test tools/build-notes.test.mjs
node tools/build-notes.mjs
node tools/audit-structure.mjs
git checkout -- docs
git clean -fq docs
```

## Reference evidence

1. Microsoft Copilot harness overview (Microsoft Learn). Updated 2026-11-24.
2. Design reliable agentic loops (Microsoft Learn). Updated 2026-11-12.
3. Copilot Cowork overview (Microsoft Learn). Updated 2026-11-18.
4. Copilot Cowork application card (Microsoft Learn). Updated 2026-11-18.
5. Using agent mode in your IDE (GitHub Docs).
6. GitHub Copilot on GitHub.com and GitHub Mobile (GitHub Docs).
7. Hooks for GitHub Copilot (GitHub Docs).
8. GitHub Agentic Workflows (GitHub Docs).
9. Getting pull requests ready to merge with Agent Merge (GitHub Docs).
10. Application card: GitHub Copilot Agents (GitHub Docs).
