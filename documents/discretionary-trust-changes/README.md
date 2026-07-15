# Discretionary Trust Changes — Precedent Pack (Australia)

A browser-based document generator for 8 types of discretionary trust changes,
built from your Actionstep-exported precedent templates. Fill in a form,
click Generate, and get a ready-to-execute Word document set — entirely
client-side, nothing uploaded anywhere.

## What's included

- **`document-generator.html`** — the tool. Open it directly in a browser, or
  host it on a server/intranet alongside `templates/` (see "Keeping templates
  in sync" below).
- **`templates/`** — the 17 source `.docx` templates, renamed to short, clean
  names for easy hosting (e.g. `COT_Deed.docx` instead of the original
  `COT_Deed_of_change_of_trustee-__trust_name__.docx`). Also includes the
  original `discretionary-trust-changes_variables.docx` reference document.
- **`resync_embedded_templates.py`** — refreshes the tool's built-in fallback
  copies of the 17 templates after you edit any of them.

## The 8 change types

| Selector value | Documents generated | Namespace |
|---|---|---|
| Deed of Variation (general) | Deed + Resolution | `dov` |
| Deed of Variation (exclude foreign persons) | Deed + Resolution | `fe` |
| Change of Trustee | Deed + Resolution + Statutory Declaration | `cot` |
| Change of Beneficiary | Deed + Resolution | `cob` |
| Change of Controller / Appointor | Deed + Resolution | `coc` |
| Appointment of Successor Controller / Appointor | Deed + Resolution | `soc` |
| Appointment of Successor Trustee | Deed + Resolution | `sot` |
| Winding Up & Vesting | Deed + Resolution | `dow` |

Only one change type is generated per run (unlike the share transfer pack,
these are standalone legal instruments, not sections of one combined
document) — the tool downloads the relevant 2–3 files together as a zip.

## Data model

**Always collected** (Section 1–3 of the form):
- `trust`: name, date, settlor, settlor_address, settlement_sum,
  trust_jurisdiction, original_trustee, controller (bool), controller_name
- `trustee[]`: current trustees — name, address, type (Individual/Company),
  directorone, directortwo (director fields only meaningful for companies)
- `controller[]`: current controllers/appointors — same shape, only
  collected if `trust.controller` is checked

**Per change type**, one of `dov` / `fe` / `cot` / `cob` / `coc` / `soc` /
`sot` / `dow` is populated — see `discretionary-trust-changes_variables.docx`
for the full field-by-field description of each, or read the form itself
(the labels match the variables document's questions closely).

**Additional entity lists**, populated only for their relevant change type:
`newtrustee[]` (Change of Trustee), `beneficiarys[]` (Change of Beneficiary —
note the different shape: name, type, power, change [Add/Remove]),
`newcontroller[]` (Change of Controller), `successorcontroller[]`
(Successor Controller), `successortrustee[]` (Successor Trustee).

## How the templating works — Actionstep merge syntax, not Jinja

These templates use **Actionstep's own merge-field syntax**, not
Jinja/docxtpl (worth flagging since a previous project's templates *did* use
Jinja — these do not):

- `[[var]]` — plain field substitution
- `[[var|rn=*]]` — field scoped to the current repeat row
- `[[*REPEAT|data_source=X|*]] ... [[*REPEAT|END*]]` — loop over `context[X]`
- `[[*IF {var} == "value" *]] ... [[*ENDIF*]]` — conditional (booleans are
  compared as the literal strings `"true"`/`"false"`)
- `[[X_nameList]]` — derived: an English-joined list of `context[X][].name`
  (e.g. "Jane Smith and John Smith")

The browser tool implements this syntax from scratch in JavaScript
(`document-generator.html`'s inline `<script>`), including the same
run-defragmentation handling used in the share transfer pack — Word often
splits a `[[ ... ]]` field across multiple XML runs (spell-check, re-saving,
formatting changes), and the engine reconstructs the original contiguous
text before parsing, regardless of how it's fragmented.

**A source-template typo was found and fixed during testing:** the Change of
Beneficiary deed's "Add" condition read `{beneficiarys_chang|rn=*}` (missing
the final "e"), which would have silently prevented that paragraph from ever
rendering. Corrected to `{beneficiarys_change|rn=*}` in `templates/COB_Deed.docx`
and re-embedded in the tool.

## Keeping templates in sync

Same two-tier loading as the share transfer pack's tool:

1. **Live fetch** — on load, the tool tries to fetch each template from a
   `templates/` folder next to the HTML file. Host the two together and
   editing a `.docx` is picked up immediately, no rebuild step.
2. **Embedded fallback** — if that fails (opened via `file://`, or no server),
   it falls back to the base64 copies baked into the page. The banner at the
   top of the page tells you which source is active.

After editing any `.docx` in `templates/`, refresh the fallback copies with:

```bash
python resync_embedded_templates.py --templates templates --html document-generator.html
```

This is only needed for the fallback path — unnecessary if you always host
`document-generator.html` and `templates/` together on a server.

## A note on scope

This pack was built and tested against all 8 change types (rendered and
visually verified: Change of Trustee, Deed of Variation general, and Change
of Beneficiary in full; the remaining 5 confirmed to render without error
using representative data). As with any precedent, review the generated
documents before use — particularly the Winding Up & Vesting deed, which the
source template itself flags as needing manual review regardless.
