#!/usr/bin/env python3
"""
resync_embedded_templates.py — refreshes the base64 fallback copies of the
17 trust-change templates baked into document-generator.html.

You only need this for the FALLBACK path (used when the page is opened via
file:// or the templates/ folder isn't hosted alongside the HTML). If you
host document-generator.html and templates/ together on a server, the page
fetches each .docx live on every load and this script is unnecessary.

Usage:
    python resync_embedded_templates.py --templates templates --html document-generator.html
"""
import argparse
import base64
import json
import re
from pathlib import Path

TEMPLATE_KEYS = [
    "VARIATION_Deed", "VARIATION_Resolution",
    "FOREIGN_Deed", "FOREIGN_Resolution",
    "COT_Deed", "COT_Resolution", "COT_StatDec",
    "COB_Deed", "COB_Resolution",
    "COA_Deed", "COA_Resolution",
    "ASA_Deed", "ASA_Resolution",
    "AST_Deed", "AST_Resolution",
    "WINDING_Deed", "WINDING_Resolution",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--templates", default="templates", help="Directory containing the 17 named .docx templates")
    parser.add_argument("--html", default="document-generator.html")
    args = parser.parse_args()

    templates_dir = Path(args.templates)
    html_path = Path(args.html)

    obj = {}
    for key in TEMPLATE_KEYS:
        path = templates_dir / f"{key}.docx"
        if not path.exists():
            raise SystemExit(f"Missing template file: {path}")
        obj[key] = base64.b64encode(path.read_bytes()).decode()

    new_json = json.dumps(obj)
    html = html_path.read_text(encoding="utf-8")
    pattern = re.compile(r'(<script id="templates-data" type="application/json">)(.*?)(</script>)', re.S)
    if not pattern.search(html):
        raise SystemExit("Couldn't find the <script id=\"templates-data\"> block in the HTML file.")

    html = pattern.sub(lambda m: m.group(1) + new_json + m.group(3), html, count=1)
    html_path.write_text(html, encoding="utf-8")
    print(f"Re-embedded {len(obj)} templates ({len(new_json)} base64 chars total) into {html_path}.")


if __name__ == "__main__":
    main()
