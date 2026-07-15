#!/usr/bin/env python3
"""
generate.py — renders the Australian share transfer / officeholder change
precedent pack (Jinja/docxtpl-coded .docx template) from a single JSON
configuration file into ONE combined Word document.

Usage:
    python generate.py config.json [--outdir OUTPUT_DIR] [--templates TEMPLATES_DIR] [--output NAME]

The config JSON has a top-level "matters" list, each with a "doc_type" of
"share_transfer", "officeholder_change", or "waiver_of_preemption" — see
sample_data.json for a fully worked example. Every matter's data is pooled
into a single context and rendered against one combined template
(Share_Transfer_and_Officeholder_Change_Precedent_Pack.docx in --templates),
which contains the whole document set: Share Transfer(s), Director Resolution
(transfer), Share Certificate(s), Register Update Memorandum (members),
Compliance Checklist (transfer), Consent(s) to Act, Notice(s) of Resignation,
Directors Resolution (officeholder), Register Update Memorandum (officers),
Compliance Checklist (officeholder), and Waiver of Pre-emption.

Repeating sections (transfers, certificates, appointments, resignations,
waived items, waiving parties) are genuine Jinja loops inside that one file —
pass 2 or 20 entries and that section renders once per entry, each starting
on its own page. A section is omitted entirely if its list is empty (e.g. no
waiver section if you don't pass any waiving_parties).

Party object shape (used for transferor_party / transferee_party / each entry
in waiving_parties):
    Individual(s) signing personally:
        {"party_type": "individual",
         "signatories": [{"name": "...", "is_trustee": False, "trust_name": ""}]}
    Company executing under s127:
        {"party_type": "company", "company_name": "...", "acn": "...",
         "is_trustee": False, "trust_name": "",
         "executing_officers": [{"name": "...", "title": "Director/Secretary"}]}
"""
import argparse
import json
from pathlib import Path

from docxtpl import DocxTemplate

COMBINED_TEMPLATE_NAME = "Share_Transfer_and_Officeholder_Change_Precedent_Pack.docx"


def add_days(date_str, days):
    """Best-effort ASIC lodgement due-date calc (DD/MM/YYYY in, DD/MM/YYYY out)."""
    from datetime import datetime, timedelta
    try:
        d = datetime.strptime(date_str, "%d/%m/%Y")
        return (d + timedelta(days=days)).strftime("%d/%m/%Y")
    except Exception:
        return "28 days from change date"


def join_english(items):
    """['A', 'B', 'C'] -> 'A; B; and C' (semicolon-separated for readability
    when names themselves may contain commas, e.g. trust descriptions)."""
    items = [i for i in dict.fromkeys(items) if i]  # de-dupe, preserve order, drop blanks
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return "; ".join(items[:-1]) + "; and " + items[-1]


def build_combined_context(config):
    """Pool every matter in the config into one context for the combined template."""
    matters = config.get("matters", [])
    transfer_matter = next((m for m in matters if m.get("doc_type") == "share_transfer"), {})
    officeholder_matter = next((m for m in matters if m.get("doc_type") == "officeholder_change"), {})
    waiver_matter = next((m for m in matters if m.get("doc_type") == "waiver_of_preemption"), {})

    company_name = transfer_matter.get("company_name") or officeholder_matter.get("company_name") or waiver_matter.get("company_name", "")
    acn = transfer_matter.get("acn") or officeholder_matter.get("acn") or waiver_matter.get("acn", "")
    resolution_date = transfer_matter.get("resolution_date") or officeholder_matter.get("resolution_date", "")
    prepared_by = transfer_matter.get("prepared_by") or officeholder_matter.get("prepared_by", "")
    transfers = transfer_matter.get("transfers", [])

    return {
        "company_name": company_name,
        "acn": acn,
        "resolution_date": resolution_date,
        "prepared_by": prepared_by,
        "directors": transfer_matter.get("directors") or officeholder_matter.get("directors", []),
        "executing_officers": transfer_matter.get("executing_officers", []),
        "transfers": transfers,
        "transferor_names_joined": join_english([t["transferor_display"] for t in transfers]),
        "share_certificates": transfer_matter.get("share_certificates", []),
        "asic_lodgement_due_date": add_days(resolution_date, 28) if resolution_date else "",
        "appointments": officeholder_matter.get("appointments", []),
        "resignations": officeholder_matter.get("resignations", []),
        "waiver_date": waiver_matter.get("waiver_date", ""),
        "waived_items": waiver_matter.get("waived_items", []),
        "waiving_parties": waiver_matter.get("waiving_parties", []),
        "show_notes": config.get("show_notes", False),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Render the share transfer / officeholder change precedent pack into a single combined Word document."
    )
    parser.add_argument("config", help="Path to a JSON config file (see sample_data.json)")
    parser.add_argument("--outdir", default="output", help="Directory to write the rendered .docx to")
    parser.add_argument("--templates", default="templates", help="Directory containing the combined .docx template")
    parser.add_argument(
        "--output",
        default="Generated_Documents.docx",
        help="Output filename for the single combined document (default: Generated_Documents.docx)",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    templates_dir = Path(args.templates)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    with open(config_path, "r") as f:
        config = json.load(f)

    context = build_combined_context(config)

    tpl = DocxTemplate(str(templates_dir / COMBINED_TEMPLATE_NAME))
    tpl.render(context)
    out_path = outdir / args.output
    tpl.save(str(out_path))
    print(f"-> {out_path}")


if __name__ == "__main__":
    main()
