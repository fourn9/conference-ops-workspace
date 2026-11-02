# Conference Ops Workspace

**An event-level workspace for AI-assisted operations, with clear task ownership and decision history.**

Built by [Shinichi Kimura (@fourn9)](https://github.com/fourn9), with AI coding assistants. [日本語](README.ja.md)

I built a working environment for conference planning and operations: reusable task instructions, research artifacts, communication drafts, and records of decisions. I also built a session-journal prototype to address a recurring problem in agent-assisted work: an idea discussed in one session could be mistaken for an approved decision in the next.

This repository is a **public case study and newly written reference demo**. It describes earlier private work; the public Python implementation was created for this release and is not the original implementation.

## Try it in 30 seconds

Python 3.9 or newer; standard library only. No installation, account, API key, or network access required.

```bash
git clone https://github.com/fourn9/conference-ops-workspace.git
cd conference-ops-workspace
python3 demo/workspace.py
python3 -m unittest discover -s tests -v
```

The fictional event produces a handoff with **1 confirmed decision, 2 open items, 1 rejected option, and 3 unfinished tasks**. A record labeled `confirmed` without a human decision reference remains open, and tasks depending on it remain blocked. [Read the sample output](examples/operations-handoff.md).

```text
Event context + working records
               |
     Journal of decisions and open ideas
               |
      Explicit human decision records
               |
   Task queue + blockers + next-session handoff
```

## What I built in the private project

| Area | Implementation represented in the original project |
| --- | --- |
| Operational workspace | Shared instructions and task-specific skills for speaker, sponsor, communication, and reporting work |
| Planning artifacts | Research outputs, topic planning, and event-level working records |
| Decision memory | A session-journal prototype with transcript extraction, background summarization, an index, and recall scripts |
| State separation | Confirmed decisions, unresolved options, rejected options, and handoff notes represented separately |
| Improvement records | Lessons and architecture decisions stored separately from session history |

The companion [Conference Ops Engine](https://github.com/fourn9/conference-ops-engine) explains how common procedures were extracted into a reusable layer.

## What the public demo demonstrates

[`demo/workspace.py`](demo/workspace.py) converts synthetic decision and task records into a deterministic Markdown or JSON handoff. It checks whether a decision record includes an explicit approval flag, a named reviewer, a reference, and a non-future date. Open decisions block dependent tasks, and completed tasks leave the work queue.

These fields demonstrate provenance requirements; they are **not an authentication system**. The demo does not verify reviewer identity, summarize real transcripts, connect to business tools, or send messages. All names, tasks, approvals, and dates in the fixture are fictional.

```bash
python3 demo/workspace.py --json
python3 demo/workspace.py path/to/synthetic-fixture.json
```

## Read more

- [Case study: operations, memory, and trade-offs](docs/case-study.md)
- [Short project description for an application](docs/application-summary.md)
- [Publication scope](PUBLICATION.md)

The private journal design was recorded as a prototype proposal alongside implementation files. This case study does not claim proven organization-wide adoption, measured productivity gains, or guaranteed memory accuracy.

## License

[MIT](LICENSE) covers the new material in this repository. It grants no rights to the private projects or their data.
