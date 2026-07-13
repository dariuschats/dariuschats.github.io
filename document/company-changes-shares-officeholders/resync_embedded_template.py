#!/usr/bin/env python3
"""
resync_embedded_template.py — refreshes the base64 fallback copy of the
combined template baked into document-generator.html.

You only need this for the FALLBACK path (used when the page is opened via
file:// or the .docx isn't hosted alongside the HTML). If you host the .docx
and the HTML together on a server, the page fetches the .docx live on every
load and this script is unnecessary.

Usage:
    python resync_embedded_template.py \\
        --docx templates/Share_Transfer_and_Officeholder_Change_Precedent_Pack.docx \\
        --html document-generator.html
"""
import argparse
import base64
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", default="templates/Share_Transfer_and_Officeholder_Change_Precedent_Pack.docx")
    parser.add_argument("--html", default="document-generator.html")
    args = parser.parse_args()

    docx_path = Path(args.docx)
    html_path = Path(args.html)

    b64 = base64.b64encode(docx_path.read_bytes()).decode()
    new_json = json.dumps({"combined": b64})

    html = html_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(<script id="templates-data" type="application/json">)(.*?)(</script>)', re.S
    )
    if not pattern.search(html):
        raise SystemExit("Couldn't find the <script id=\"templates-data\"> block in the HTML file.")

    html = pattern.sub(lambda m: m.group(1) + new_json + m.group(3), html, count=1)
    html_path.write_text(html, encoding="utf-8")
    print(f"Re-embedded {docx_path} ({len(b64)} base64 chars) into {html_path}.")


if __name__ == "__main__":
    main()
