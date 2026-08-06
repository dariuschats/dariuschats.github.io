#!/usr/bin/env python3
"""
resync_embedded_templates.py — refreshes the base64 fallback copies baked
into BOTH document-generator.html (deeds/resolutions/statutory declaration)
and letters.html (cover letters), in one run.

You only need this for the FALLBACK path (used when a page is opened via
file:// or the templates/ folder isn't hosted alongside it). If you host
the HTML files and templates/ together on a server, each page fetches its
.docx files live on every load and this script is unnecessary.

Usage:
    python resync_embedded_templates.py --templates templates
    # or, to point at differently-named/located files:
    python resync_embedded_templates.py --templates templates \\
        --deed-html document-generator.html --letter-html letters.html
"""
import argparse
import base64
import json
import re
from pathlib import Path

# document-generator.html: deeds, resolutions, and the one statutory declaration.
DEED_RESOLUTION_KEYS = [
    "VARIATION_Deed", "VARIATION_Resolution",
    "FOREIGN_Deed", "FOREIGN_Resolution",
    "COT_Deed", "COT_Resolution", "COT_StatDec",
    "COB_Deed", "COB_Resolution",
    "COA_Deed", "COA_Resolution",
    "ASA_Deed", "ASA_Resolution",
    "AST_Deed", "AST_Resolution",
    "WINDING_Deed", "WINDING_Resolution",
]

# letters.html: the 8 cover letters, one per change type.
LETTER_KEYS = [
    "VARIATION_Letter", "FOREIGN_Letter", "COT_Letter", "COB_Letter",
    "COA_Letter", "ASA_Letter", "AST_Letter", "WINDING_Letter",
]


def resync_file(html_path, templates_dir, keys):
    if not html_path.exists():
        print(f"Skipping {html_path} (file not found).")
        return

    obj = {}
    for key in keys:
        path = templates_dir / f"{key}.docx"
        if not path.exists():
            raise SystemExit(f"Missing template file: {path}")
        obj[key] = base64.b64encode(path.read_bytes()).decode()

    new_json = json.dumps(obj)
    html = html_path.read_text(encoding="utf-8")
    pattern = re.compile(r'(<script id="templates-data" type="application/json">)(.*?)(</script>)', re.S)
    if not pattern.search(html):
        raise SystemExit(f"Couldn't find the <script id=\"templates-data\"> block in {html_path}.")

    html = pattern.sub(lambda m: m.group(1) + new_json + m.group(3), html, count=1)
    html_path.write_text(html, encoding="utf-8")
    print(f"Re-embedded {len(obj)} templates into {html_path}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--templates", default="templates", help="Directory containing the 25 named .docx templates")
    parser.add_argument("--deed-html", default="document-generator.html", help="Deed/Resolution tool HTML file")
    parser.add_argument("--letter-html", default="letters.html", help="Cover letter tool HTML file")
    args = parser.parse_args()

    templates_dir = Path(args.templates)

    resync_file(Path(args.deed_html), templates_dir, DEED_RESOLUTION_KEYS)
    resync_file(Path(args.letter_html), templates_dir, LETTER_KEYS)


if __name__ == "__main__":
    main()
