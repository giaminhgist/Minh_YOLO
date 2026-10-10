# Third-Party Notices

minh-agent is MIT-licensed work by its maintainer (Minh) plus curated content from
five upstream skill repositories. Every shipped component carries provenance in
`registry/components.json` (source path, revision, license, mode: verbatim/adapted,
and the changes made when adapted). This file is the human-readable summary.

## Direct upstream sources (exactly five)

| ID | Repository | Revision | License |
|---|---|---|---|
| aris | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | `26b95cfa0d8747078e9e43b42e20952709e561b8` | MIT |
| superpowers | [obra/superpowers](https://github.com/obra/superpowers) | `8ca22dba9a94f28898bbce59f2537ff4d87c747d` | MIT |
| orchestra | [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | `773a52944ba4747a18bd4ae9ade53fff041adcbc` | MIT |
| claude_skills | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | `19392f7a08264ed00486a251f5b2098321771f94` | MIT |
| context_engineering | [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | `58b55a8921758d13453b440704fb1b5b208c0b0e` | MIT |

Full license texts of these five repositories are shipped verbatim in
[`licenses/`](licenses/).

## Component-level notes

- Each adapted resource file ends with a provenance line naming its source
  repository, revision, and path.
- Where an upstream file itself incorporates third-party material (for example
  Apache-2.0-licensed patterns from Anthropic's Claude Science compute-env setup,
  or LaTeX class files under LPPL), that fact is recorded in the component's
  `local_changes` field in `registry/components.json`. LPPL-licensed LaTeX class
  files (e.g. IEEEtran) are **not** shipped; obtain them from TeX Live/CTAN or the
  venue author kit.
- The maintainer's cache used to fetch and inspect the upstream trees
  (`.cache/upstreams/`, git-ignored) is never part of the installed plugin.
