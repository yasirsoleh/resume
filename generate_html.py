#!/usr/bin/env python3
"""Generate index.html from resume.tex (the single source of truth).

Uses pandoc to convert the LaTeX source to HTML, then post-processes the
output into the resume's HTML layout. Pandoc is run via the pandoc/latex
Docker image (as in README.md), falling back to a local pandoc binary if
available.

Usage:
    python3 generate_html.py
"""

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "index.html"

TITLE = "Mohammad Alif Yasir bin Soleh — Resume"

CSS = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: "Segoe UI", Arial, Helvetica, sans-serif;
      font-size: 13px;
      line-height: 1.4;
      color: #222;
      max-width: 820px;
      margin: 40px auto;
      padding: 0 48px;
    }
    header { text-align: center; margin-bottom: 16px; }
    h1 { font-size: 24px; margin-bottom: 4px; }
    .contact { font-size: 12px; color: #444; }
    .contact a { color: #444; text-decoration: none; }
    .contact a:hover { text-decoration: underline; }
    .contact p { margin: 1px 0; }
    h2 {
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 1px;
      border-bottom: 1px solid #ccc;
      padding-bottom: 2px;
      margin: 18px 0 8px 0;
    }
    .entry { margin-bottom: 14px; }
    .entry-header { margin-bottom: 3px; }
    .entry-org { font-weight: 700; }
    .entry-role-date {
      display: flex;
      justify-content: space-between;
      font-style: italic;
    }
    .subproject { font-weight: 700; margin: 8px 0 3px 0; }
    ul { margin: 4px 0 4px 18px; }
    li { margin-bottom: 2px; }
    .stack { font-style: italic; font-size: 12px; color: #555; margin-top: 4px; }
    .summary { margin-bottom: 4px; }
    @media print {
      body { max-width: 100%; margin: 0; padding: 0 36px; }
    }
"""

ORG_ROLE = re.compile(
    r"^<p><strong>(.*?)</strong>\s*<br />\s*<em>(.*?)</em>\s*(.*?)\s*</p>$"
)
SUBPROJECT = re.compile(r"^<p><strong>(.*?)</strong></p>$")
STACK = re.compile(r"^<p><em>Stack:</em>\s*(.*?)</p>$")


def run_pandoc() -> str:
    if shutil.which("pandoc"):
        cmd = ["pandoc", "-f", "latex", "-t", "html", str(ROOT / "resume.tex")]
    else:
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{ROOT}:/data",
            "pandoc/latex:latest",
            "-f", "latex", "-t", "html",
            "resume.tex",
        ]
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def split_blocks(html: str) -> list[str]:
    blocks = []
    cur_lines = []
    depth = 0
    for line in html.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        depth_delta = (
            stripped.count("<ul>") + stripped.count("<div")
            + stripped.count("<p>") + stripped.count("<h1")
            - stripped.count("</ul>") - stripped.count("</div>")
            - stripped.count("</p>") - stripped.count("</h1")
        )
        if cur_lines and depth == 0 and stripped.startswith(("<ul>", "<h1", "<p>", "<div")):
            blocks.append(" ".join(cur_lines))
            cur_lines = []
        cur_lines.append(stripped)
        depth += depth_delta
    if cur_lines:
        blocks.append(" ".join(cur_lines))
    return blocks


def render_header(block: str) -> list[str]:
    name = re.search(r"<strong>(.*?)</strong>", block).group(1)
    links = re.findall(r'<a href="([^"]+)">(.*?)</a>', block)
    fields_text = re.sub(r"<.*?>", "", block.split("</strong>", 1)[1]).strip()
    fields = [f.strip() for f in fields_text.split("\u2022") if f.strip()]
    contact_line = " \u2022 ".join(fields)
    links_line = " \u2022 ".join(
        f'<a href="{href}">{label}</a>' for href, label in links
    )
    return [
        "<header>",
        f'  <h1>{name}</h1>',
        '  <div class="contact">',
        f"    <p>{contact_line}</p>",
        f"    <p>{links_line}</p>",
        "  </div>",
        "</header>",
    ]


def render_list(block: str) -> str:
    block = re.sub(r'<li>\s*<p>(.*?)</p>\s*</li>', r"<li>\1</li>", block)
    return block


def classify(block: str) -> tuple[str, str]:
    """Return (kind, payload) for a non-header, non-heading block."""
    m = ORG_ROLE.match(block)
    if m:
        return "orgrole", (m.group(1), m.group(2), m.group(3))
    m = SUBPROJECT.match(block)
    if m:
        return "subproject", m.group(1)
    m = STACK.match(block)
    if m:
        return "stack", m.group(1)
    if block.startswith("<ul>"):
        return "list", block
    return "paragraph", block


def main() -> None:
    blocks = split_blocks(run_pandoc())
    lines: list[str] = []
    entry_open = False
    section_open = False
    section = None

    def close_entry() -> None:
        nonlocal entry_open
        if entry_open:
            lines.append("  </div>")
            entry_open = False

    def close_section() -> None:
        nonlocal section_open
        if section_open:
            lines.append("</section>")
            section_open = False

    def open_entry(org: str, role: str, date: str) -> None:
        nonlocal entry_open
        close_entry()
        lines.append('  <div class="entry">')
        lines.append('    <div class="entry-header">')
        lines.append(f'      <span class="entry-org">{org}</span>')
        lines.append("    </div>")
        lines.append('    <div class="entry-role-date">')
        lines.append(f"      <span>{role}</span>")
        lines.append(f"      <span>{date}</span>")
        lines.append("    </div>")
        entry_open = True

    for block in blocks:
        if block.startswith('<div class="center">'):
            lines.extend(render_header(block))
            continue
        if block.startswith("<h1"):
            close_entry()
            close_section()
            match = re.match(r'<h1 id="(\w+)">(.*?)</h1>', block)
            section = match.group(1)
            lines.append("<section>")
            section_open = True
            lines.append(f"  <h2>{match.group(2)}</h2>")
            continue

        kind, payload = classify(block)
        if kind == "orgrole":
            open_entry(*payload)
        elif kind == "subproject":
            lines.append(f'    <div class="subproject">{payload}</div>')
        elif kind == "stack":
            lines.append(f'    <div class="stack">Stack: {payload}</div>')
        elif kind == "list":
            items = re.findall(r"<li>(.*?)</li>", payload, flags=re.S)
            if items and all(ORG_ROLE.match(it) for it in items):
                for it in items:
                    open_entry(*ORG_ROLE.match(it).groups())
            else:
                lines.append("    " + render_list(payload))
        else:
            if section == "summary":
                payload = payload.replace("<p>", '<p class="summary">', 1)
            lines.append("    " + payload)
    close_entry()
    close_section()

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{TITLE}</title>
  <style>
{CSS}
  </style>
</head>
<body>

{chr(10).join(lines)}

</body>
</html>
"""
    OUTPUT.write_text(document)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
