---
render_with_liquid: false
---
# Share Transfer & Officeholder Change Precedent Pack (Australia)

Word (.docx) templates coded for **docxtpl** (Jinja2). Styling matches the firm's
Deed of Variation precedent (Calibri, 11pt body, A4 margins, "[doc name] – Page X
of Y" footer). Wording and structure for the share transfer sections are matched
to the firm's real signed precedent (deed-style "signed"/"executed" execution
for individuals/trustees, s127 execution for the company, and support for joint
holders signing as trustee for a trust).

## What's included

The primary deliverable is **one file**:
`templates/Share_Transfer_and_Officeholder_Change_Precedent_Pack.docx`. Both
ways of generating documents from this pack — `generate.py` and
`document-generator.html` — always render this single template and always
produce a single combined `.docx`, never a set of separate files. It contains,
in order: Share Transfer(s) → Director Resolution (transfer) → Share
Certificate(s) → Register Update Memorandum (members) → Compliance Checklist
(transfer) → Consent(s) to Act → Notice(s) of Resignation → Directors
Resolution (officeholder) → Register Update Memorandum (officers) →
Compliance Checklist (officeholder) → Waiver of Pre-emption. Repeating
sections (transfers, certificates, appointments, resignations) are genuine
Jinja loops inside it, and a section is omitted entirely if you don't supply
any data for it — see "Rendering documents from data" below.

`templates/` also holds the **9 component templates** each section of the
combined document was originally assembled from:

| # | File | Purpose |
|---|------|---------|
| 1 | `01_instrument_of_transfer.docx` | Share Transfer (one per transfer; supports joint/trustee parties) |
| 2 | `02_directors_resolution_transfer.docx` | Director resolution tabling and approving one or more share transfers |
| 3 | `03_consent_to_act.docx` | Consent to act as director (s201D) or secretary (s204C) |
| 4 | `04_notice_of_resignation.docx` | Notice of resignation of a director/secretary |
| 5 | `05_directors_resolution_officeholder.docx` | Directors resolution approving appointment(s)/resignation(s) |
| 6 | `06_register_update_memo.docx` | Internal memo recording a register of members / register of officers entry |
| 7 | `07_compliance_checklist.docx` | Internal file cover sheet — ASIC lodgement deadlines, register updates, etc. |
| 8 | `08_share_certificate.docx` | Share certificate, executed by the company under s127 |
| 9 | `09_waiver_of_preemption.docx` | Waiver of rights of pre-emption over the transferred shares |

These aren't part of the normal generation flow any more — neither
`generate.py` nor the browser tool touches them. They're kept purely as a
reference/fallback for rendering a single section on its own (see "Rendering
by hand" below), and as the historical source of each section of the combined
template. If you edit the combined `.docx` directly (the normal way to make
changes now — see "Regenerating the source templates" at the bottom), these
9 files won't pick up that edit automatically; only touch them if you actually
use the standalone-rendering path below, otherwise feel free to ignore or
delete them to keep the pack lean.

### When to use the waiver of pre-emption

Include this whenever the company's constitution or a shareholders agreement
gives existing members a right of first refusal over shares being transferred.
Every shareholder who could have exercised that right needs to sign it (or the
transfer is technically in breach of the constitution/agreement), so prepare and
execute it alongside the share transfer and director resolution — not as an
afterthought.

## Rendering documents from data — always produces one file

`generate.py` renders every matter in a JSON config into **one combined Word
document**. There's no separate-files mode — running the script always gives
you a single .docx containing the whole set, in this order: Share Transfer(s)
→ Director Resolution (transfer) → Share Certificate(s) → Register Update
Memorandum (members) → Compliance Checklist (transfer) → Consent(s) to Act →
Notice(s) of Resignation → Directors Resolution (officeholder) → Register
Update Memorandum (officers) → Compliance Checklist (officeholder) → Waiver of
Pre-emption.

Repeating sections are genuine Jinja loops inside that one file: pass 2 (or
20) entries in `transfers`, `share_certificates`, `appointments`, or
`resignations` and that section renders once per entry, each starting on its
own page — you don't need to copy/paste sections by hand for multiple
transfers. A section is **omitted entirely** if its underlying list is empty
(e.g. no waiver section appears if you don't pass `waiving_parties`).

```bash
pip install docxtpl --break-system-packages   # one-off
python generate.py sample_data.json --outdir output --templates templates
# -> output/Generated_Documents.docx  (one file, everything inside it)
```

Use `--output some_name.docx` to change the output filename.

See `sample_data.json` for a fully worked example — a share transfer with a
trust-holding party, its waiver of pre-emption, and a separate officeholder
change, all for the same company. Each matter in the `matters` list needs a
`doc_type` of:

- **`share_transfer`** — one Share Transfer section per transfer, a director
  resolution covering all of them, one share certificate section per entry in
  `share_certificates`, a register-of-members entry per transfer, and a
  compliance checklist.

  Each transfer needs `transferor_display` / `transferee_display` (the
  plain-English combined party name, e.g. `"A and B as trustee for the C Family
  Trust"`) plus `transferor_party` / `transferee_party` — see the party object
  shape at the top of `generate.py`.

  `share_certificates` is a **separate, explicit list** rather than one-per-transfer
  — real matters often consolidate several transfers into a single certificate
  for the buyer, and separately reissue a certificate to a seller for their
  remaining balance, so this can't be reliably auto-derived. `executing_officers`
  (list of `{name, title}`, e.g. `title: "Director/Secretary"`) drives the s127
  execution block on each certificate.

- **`officeholder_change`** — one Consent to Act section per appointment, one
  Notice of Resignation section per resignation, a directors' resolution
  covering all changes, a register-of-officers entry per change, and a
  compliance checklist.

- **`waiver_of_preemption`** — `waived_items` is a list of
  `{number_of_shares, class_of_shares, transferor_display, transferee_display}`
  rendered as a lettered list; `waiving_parties` is a list of party objects
  (same shape as transferor_party/transferee_party), one execution block per
  waiving shareholder.

See `sample_data.json` for the exact shape, or read the docstring at the top of
`generate.py`.

If you only want the raw, unrendered template to browse or hand-edit in Word
(the `{{ placeholders }}` and Jinja tags are visible), that's
`Share_Transfer_and_Officeholder_Change_Precedent_Pack.docx` in `templates/` —
no rendering required.

## Browser-based generator (no install, no server)

`document-generator.html` is a single self-contained web page that renders the
whole document set directly in the browser — fill in a form, click Generate,
and download **one combined .docx**. Nothing is uploaded anywhere; everything
runs client-side using JSZip and nunjucks (a Jinja2-compatible template
engine), loaded from a CDN.

**To use it:** open the file directly in a browser, or host it as a normal page
on your firm's site/intranet (it's one HTML file — no build step, no backend).

It covers the same ground as `generate.py`: company/director details, one or
more share transfers (each transferor/transferee can be individuals or a
company, optionally as trustee), share certificates, officeholder appointments
and resignations, and a waiver of pre-emption. The party sub-form (individual
vs company, trustee toggle) is reused everywhere a signing party appears.

### Keeping it in sync with the template — automatically

The page loads the template two ways, in order:

1. **Live fetch** — on every load it first tries to fetch
   `Share_Transfer_and_Officeholder_Change_Precedent_Pack.docx` from the same
   folder/URL it's served from. If you host `document-generator.html` and the
   `.docx` together (e.g. both in `templates/` on your intranet, or both
   committed to the same repo folder), **editing the `.docx` is all you ever
   need to do** — the page always renders whatever is currently on disk, no
   re-embedding, no rebuild step.
2. **Embedded fallback** — if that fetch fails (most commonly because the
   page was opened directly from disk via `file://`, which browsers block from
   fetching sibling files for security reasons, or the `.docx` isn't present
   next to it), it falls back to a base64 copy baked into the page itself. The
   status message after generating tells you which one was actually used, so
   you're never left wondering.

Practical upshot: if you always host the two files together on a server, you
can ignore the rest of this section — just edit the `.docx` and you're done.
The embedded fallback exists purely so the page still works as a single
portable file when there's no server involved (e.g. emailed as one
attachment, or opened by double-click).

A couple of things worth knowing:
- It's a form-first tool, not a legal-review tool — it doesn't check that the
  numbers add up (e.g. that certificate totals reconcile against transfers).
- The generated document is identical in substance to what `generate.py`
  produces, since both render the same combined docxtpl template.
- If you extend the template with a genuinely new field (a `{{ variable }}`
  the form doesn't already collect), you'll need to add a matching input to
  the form's HTML/JS as well — re-syncing the template file alone only covers
  wording/formatting/structure changes to fields that already exist.
- To refresh the embedded fallback copy after editing the `.docx` (so the
  page still behaves sensibly even when opened via `file://`), see
  "Regenerating the source templates" below.

### Rendering by hand (no script)

The individual component templates (`01_instrument_of_transfer.docx`,
`08_share_certificate.docx`, `09_waiver_of_preemption.docx`, etc. in
`templates/`) are also valid standalone docxtpl templates, if you ever want
just one section rendered on its own rather than the full combined document:

```python
from docxtpl import DocxTemplate
tpl = DocxTemplate("templates/09_waiver_of_preemption.docx")
tpl.render({
    "company_name": "Acme Widgets Pty Ltd",
    "acn": "123 456 789",
    "waiver_date": "10/07/2026",
    "waived_items": [{
        "number_of_shares": "1,000",
        "class_of_shares": "ordinary",
        "transferor_display": "Sarah Chen and Michael Ostrowski as trustee for the Chen Ostrowski Family Trust",
        "transferee_display": "David Ostrowski",
    }],
    "waiving_parties": [{
        "party_type": "individual",
        "signatories": [{"name": "Michael Ostrowski", "is_trustee": False, "trust_name": ""}],
    }],
})
tpl.save("output/waiver.docx")
```

## How the Jinja/docxtpl coding works

- Plain variables use standard Jinja syntax: `{{ company_name }}`.
- Lists that need to repeat (multiple transfers, multiple directors signing,
  multiple joint signatories, multiple waived items) use standard Jinja
  `{% for %} ... {% endfor %}` loops written directly as paragraphs — including
  around a whole table, where a transfer's mini label:value table repeats once
  per transfer inside the director resolution. A one-item list still renders
  correctly for a sole transferor/transferee/director.
- Table **rows** that need to repeat (e.g. the director resolution's execution
  table) use docxtpl's row-loop syntax instead: a hidden row containing
  `{%tr for x in list %}`, the templated data row, then a hidden row containing
  `{%tr endfor %}`.
- The waiver's lettered list (a, b, c...) is generated inside the loop with
  `{{ "abcdefghijklmnopqrstuvwxyz"[loop.index0] }}` so the letters advance
  correctly regardless of how many items are passed.
- Optional sections (e.g. "Appointments" / "Resignations", or "members" vs
  "officers" in the register memo) are wrapped in ordinary Jinja block tags:
  `{% if appointments %} ... {% endif %}`.
- Each template also carries **editorial drafting notes** (grey italics) explaining
  the expected shape of the data. These are wrapped in `{% if show_notes %} ...
  {% endif %}` and are **hidden by default** — they will not appear in documents
  you render for a client. Pass `"show_notes": true` in the context if you want an
  annotated copy for training or template maintenance.

## Statutory references used (Corporations Act 2001 (Cth))

- s127 — company execution (by two directors, or a director and secretary, or —
  for a sole director/secretary company — that one person alone)
- s201D — consent to act as director
- s204C — consent to act as secretary
- s203A / s205A — director resignation and ASIC notification
- s205B — ASIC notification of officeholder changes (28 days)
- s178A — ASIC notification of changes to top 20 members / shareholding structure (28 days)
- s206A / s206B / Part 2D.6 — director eligibility declarations

**This pack is a starting precedent, not legal advice.** Confirm current ASIC
lodgement requirements, stamp duty treatment (which varies by State/Territory),
and the company's own constitution and any shareholders agreement (particularly
pre-emption/first-refusal provisions) before relying on any of these documents in
a live matter.

## Regenerating the source templates

The templates are built from small Node.js scripts (using the `docx` npm
package) rather than edited as raw XML — see `build/`. If you want to adjust
styling globally (fonts, sizes, margins, footer format, the plain field-table
header), edit `build/helpers.js` and re-run each script in `build/` to
regenerate the `.docx` files in `templates/`.

If you hand-edit `Share_Transfer_and_Officeholder_Change_Precedent_Pack.docx`
directly in Word instead (formatting, wording, adding/removing non-variable
text), that's fine — just be careful around the small grey `{{ }}` / `{% %}`
tags scattered through the document; they're structural, not decorative, and
deleting one without its matching pair (e.g. an `{% if %}` without its
`{% endif %}`) will break generation. After editing, refresh the browser
tool's embedded fallback copy with:

```bash
python resync_embedded_template.py --docx templates/Share_Transfer_and_Officeholder_Change_Precedent_Pack.docx --html document-generator.html
```

This is only needed for the fallback path — see "Keeping it in sync with the
template — automatically" above. If you host the `.docx` and the HTML
together on a server, the page fetches the current `.docx` on every load and
this step is unnecessary. `generate.py` never needs any equivalent step — it
always reads the `.docx` fresh from `--templates` at run time.
