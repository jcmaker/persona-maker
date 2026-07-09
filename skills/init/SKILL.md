---
name: init
description: Initialize a persona-maker project — create the personas/ structure and config.json. Run this first when the user wants to start persona research.
---

# init

Prepare the directory structure and config file for the persona-maker workflow
(research → generate → visualize → consult) in the current project.

## Language

Converse with the user in their language. When creating `config.json`, set
`language` to the language the user is speaking (fall back to `en` if unclear).
All generated artifacts (persona cards, journey maps, consultations) will be
written in `config.language`; this skill's instructions are in English but the
output follows the user.

## Instructions

1. In the current working directory, create the following directories (leave
   them if they already exist):
   - `personas/research`
   - `personas/cards`
   - `personas/journeys`
   - `personas/consultations`

2. Check whether `personas/config.json` already exists.
   - **If it does not exist**, create it with this content (set `language` to the
     user's language per the Language section above; `en` shown as the default):
     ```json
     {
       "model": "haiku",
       "persona_count": 5,
       "language": "en"
     }
     ```
   - **If it already exists, never overwrite it.** Instead, read the file and
     show the user the current settings as-is.

3. Whether you created it or showed existing values, explain each config key to
   the user:
   - `model`: the subagent model used when generating personas. Default `haiku`
     (low-cost bulk generation); changeable to `sonnet`, etc.
   - `persona_count`: total number of personas to generate (3–10, default 5).
     The default 5 is primary 1 + secondary 3 + anti-persona 1.
   - `language`: the language of the output artifacts (cards, journey maps,
     consultations, etc.).

4. If the user requests a settings change, explain how to edit
   `personas/config.json` directly (change the value of the desired key; it takes
   effect on the next run).

5. Finally, point to the next step: "Run `/persona-maker:research` to enter an
   idea or interview notes."
