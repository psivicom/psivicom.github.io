# teamai.md — Elected AI Council — PSIVI.COM
 
> NASA Open Science Timestamp Standard: Excellence Edition
> All timestamps MUST be RFC3339 UTC Zulu.

## Timestamp Standard

- Format: `YYYY-MM-DDTHH:MM:SSZ` (RFC3339 UTC)
- Logs: `YYYY-MM-DDTHH:MM:SS.sssZ`
- Rule: Always Z. Never local. Never ambiguous.
- Example: `2026-09-01T19:24:11Z`
- Compliance: Satisfies NASA SPD-41a, CSA, ESA Open Science.

## FORTH Governance

This is a FORTH system. Discipline is architecture.

- **BASE FROZEN:** `base.f` / core dictionary is immutable. No redefinition in place.
- **RAM NURSERY:** All new WORDs start in RAM nursery (`ram/` or `:NONAME`). Test in volatile.
- **FLASH PROMOTION:** Only after TEST + 2 reviews, promote to FLASH. `FORGET` is forbidden on FLASH.
- Stack effect is law. Document: `( -- avg )` or `( n1 n2 -- n3 )`.
- No hidden state. No magic.

## Elected AI List Format

From README.md — elected AIs must include heart emoji.

Format:
```
### 2026-09-01T19:24:11Z - elected - model-identifier
- Agent: @model-name ❤️
- Role: FORTH wordsmith / reviewer / tester
- Word: `WORDNAME`
- Status: elected
```

Requirement: Heart emoji ❤️ MANDATORY. No heart = not elected. See README.md line 1.

## Contribution Rules

1. All commits: `YYYY-MM-DDTHH:MM:SSZ - type - message`
   Example: `2026-09-01T19:24:11Z - feat - Added AVG10`
2. Every file with frontmatter:
   ```yaml
   ---
   created: 2026-05-11T00:00:00.000Z
   updated: 2026-09-01T19:24:11.000Z
   author: lpaudette / teamai-elected
   ---
   ```
3. Last updated: `2026-05-11T00:00:00Z` — Never `2026-05-11`. Always Zulu.
4. CHANGELOG.md entry required for every WORD.
5. No non-ISO dates in repo. Action will block.

Maintained for Louis-Philippe Audette — Langford BC — psivi.com

- Code Apache-2.0, Docs CC-BY-4.0