---
name: c13-doctor
description: "C13: doctor reports installable vs runtime-ready and missing optional tools honestly"
runs: 1
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---
Invoke the minh-agent:doctor skill and report this plugin's health: the
installable verdict, the runtime-ready verdict, which optional tools are
missing, and which capabilities degrade as a result. If you cannot execute
the doctor script in this environment, read
${CLAUDE_PLUGIN_ROOT}/scripts/doctor.py and the registry instead and state
clearly that the script could not be executed here. Do not install anything
and do not call any paid service.
