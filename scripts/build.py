#!/usr/bin/env python3
"""Generate the same accessible academic homepage for Jekyll and static hosting."""
from collections import Counter
from html import escape
from pathlib import Path
import json
import re
import shutil
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DIST = ROOT / "dist"

CATEGORIES = {
    "li2026bdcc": ("review", "Manuscript"),
    "li2026eswa": ("review", "Manuscript"),
    "li2025jbi": ("journal", "Journal article"),
    "li2023semanticsearch": ("journal", "Journal article"),
    "li2026lncs16786": ("conference", "Conference paper"),
    "li2026rolecond": ("conference", "Conference paper"),
    "li2026icaart": ("conference", "Conference paper"),
    "li2025lncs15908": ("conference", "Conference paper"),
    "li2024lncs14835": ("conference", "Conference paper"),
    "kovalchuk2024wiiat": ("conference", "Conference paper"),
    "kovalchuk2026rl": ("teaching", "Study guide"),
    "li2026cogsci": ("abstract", "Conference abstract"),
    "tarasov2026roles": ("abstract", "Conference abstract / talk"),
    "li2025apsara": ("abstract", "Conference talk"),
    "li2024congress": ("abstract", "Conference abstract"),
    "li2024itmoconf": ("abstract", "Conference abstract / talk"),
    "li2024cane": ("abstract", "Conference abstract / talk"),
}


def plain(value):
    value = re.sub(r"\\(?:textbf|emph|textit|texttt)\{([^{}]*)\}", r"\1", value)
    value = value.replace(r"\&", "&").replace(r"\_", "_")
    value = value.replace("{", "").replace("}", "")
    value = value.replace("---", "—").replace("--", "–")
    return re.sub(r"\s+", " ", value).strip()


def parse_bib(text):
    entries = []
    for match in re.finditer(r"^@(\w+)\{([^,]+),", text, re.M):
        cursor, depth = match.end(), 1
        while depth:
            if cursor >= len(text):
                raise ValueError("Unclosed bibliography entry")
            char = text[cursor]
            if cursor == 0 or text[cursor - 1] != "\\":
                depth += (char == "{") - (char == "}")
            cursor += 1
        raw = text[match.start():cursor]
        body = text[match.end():cursor - 1]
        fields, pos = {}, 0
        while pos < len(body):
            field_match = re.search(r"(\w+)\s*=\s*\{", body[pos:])
            if not field_match:
                break
            start = pos + field_match.end()
            end, inner = start, 1
            while inner:
                if end >= len(body):
                    raise ValueError("Unclosed bibliography field")
                if end == 0 or body[end - 1] != "\\":
                    inner += (body[end] == "{") - (body[end] == "}")
                end += 1
            fields[field_match.group(1).lower()] = body[start:end - 1]
            pos = end
        key = match.group(2)
        if key not in CATEGORIES:
            if "under review" in fields.get("note", "").lower() or "submitted" in fields.get("keywords", "").lower():
                CATEGORIES[key] = ("review", "Manuscript")
            elif "abstract" in fields.get("keywords", "").lower():
                CATEGORIES[key] = ("abstract", "Conference abstract / talk")
            else:
                default = {"article": ("journal", "Journal article"), "inproceedings": ("conference", "Conference paper"),
                           "book": ("teaching", "Study guide"), "misc": ("abstract", "Conference contribution")}
                if match.group(1) not in default:
                    raise ValueError(f"Add a category for new bibliography entry: {key}")
                CATEGORIES[key] = default[match.group(1)]
        entries.append({"id": key, "type": match.group(1), "raw": raw,
                        "fields": {name: plain(value) for name, value in fields.items()}})
    if len(entries) != len({item["id"] for item in entries}):
        raise ValueError("Duplicate bibliography keys")
    category_order = {"journal": 0, "conference": 1, "abstract": 2, "teaching": 3, "review": 4}
    return sorted(entries, key=lambda item: (-int(item["fields"]["year"]),
                                            category_order[CATEGORIES[item["id"]][0]],
                                            item["fields"].get("author", "").casefold(),
                                            item["fields"]["title"].casefold()))


def authors(value):
    names = []
    for name in re.split(r"\s+and\s+", value):
        if "," in name:
            family, given = name.split(",", 1)
            name = given.strip() + " " + family.strip()
        name_html = escape(name)
        if name == "Chao Li":
            name_html = f"<strong>{name_html}</strong>"
        names.append(name_html)
    return ", ".join(names)


def venue(entry):
    fields = entry["fields"]
    source = fields.get("journal") or fields.get("booktitle") or fields.get("howpublished") or fields.get("publisher", "")
    if entry["type"] == "article" and CATEGORIES[entry["id"]][0] == "review" and fields.get("publisher"):
        source += " (" + fields["publisher"] + ")"
    parts = [source] if source else []
    if fields.get("volume"):
        parts.append("vol. " + fields["volume"])
    if fields.get("number"):
        parts.append("no. " + fields["number"])
    if fields.get("pages"):
        parts.append(("pp. " if "–" in fields["pages"] else "") + fields["pages"])
    if entry["type"] == "inproceedings" and fields.get("publisher"):
        parts.append(fields["publisher"])
    parts.append(fields["year"])
    if entry["id"] == "li2026cogsci":
        parts.append("Nizhny Novgorod, 24–28 August 2026")
    return escape(", ".join(parts))


def head(profile, cv=False):
    title = profile["name"] + (" | Curriculum Vitae" if cv else " | Norm Dynamics & Multi-Agent Systems")
    description = "Research in multi-agent norm dynamics, hybrid cognitive systems, human–AI interaction and intelligent decision support."
    person = {"@context": "https://schema.org", "@type": "Person", "name": profile["name"],
              "jobTitle": profile["appointments"][0]["title"], "email": "mailto:" + profile["email"],
              "affiliation": [{"@type": "Organization", "name": "Sirius University of Science and Technology"},
                              {"@type": "Organization", "name": "ITMO University"}],
              "sameAs": [profile["scholar_url"]]}
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description)}">
  <meta name="theme-color" content="#fdfdfd">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <title>{escape(title)}</title>
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="assets/styles.css">
  <script type="application/ld+json">{json.dumps(person, ensure_ascii=False)}</script>
  <script src="assets/site.js" defer></script>
</head>
<body class="{'cv-page' if cv else 'home-page'}">
<a class="skip-link" href="#main-content">Skip to content</a>'''


def header(profile, cv=False):
    prefix = "index.html" if cv else ""
    navigation = "".join(f'<a href="{prefix}#{anchor}">{label}</a>' for anchor, label in
                         [("about", "About"), ("research", "Research"), ("publications", "Publications"),
                          ("projects", "Projects"), ("supervisor", "Supervisor"), ("contact", "Contact")])
    return f'''<header class="site-header">
  <div class="wrapper header-inner">
    <a class="brand" href="{prefix or '#about'}">{escape(profile['name'])}</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="main-nav" aria-label="Toggle navigation">Menu <span aria-hidden="true">☰</span></button>
    <nav id="main-nav" class="main-nav" aria-label="Main navigation">{navigation}</nav>
  </div>
</header>'''


def section_start(anchor, title, lede=""):
    return f'<section id="{anchor}" class="section" aria-labelledby="{anchor}-heading"><div class="section-heading"><h2 id="{anchor}-heading">{title}</h2>{f"<p class=\"section-lede\">{lede}</p>" if lede else ""}</div>'


def publication_section(entries, interactive=True):
    html = section_start("publications", "Publications &amp; talks", "Research papers, conference contributions and teaching material.")
    if interactive:
        counts = Counter(CATEGORIES[item["id"]][0] for item in entries)
        buttons = []
        for key, label in [("all", "All"), ("journal", "Journal articles"), ("conference", "Conference papers"),
                           ("abstract", "Abstracts & talks"), ("teaching", "Teaching material"), ("review", "Manuscripts")]:
            count = len(entries) if key == "all" else counts[key]
            buttons.append(f'<button type="button" class="filter-button{ " is-active" if key == "all" else ""}" data-filter="{key}" aria-pressed="{str(key == "all").lower()}">{escape(label)} <span>{count}</span></button>')
        html += f'''<div class="publications-controls" hidden>
          <div class="search-wrap"><label class="visually-hidden" for="publication-search">Search publications by title, author, venue or year</label><input id="publication-search" type="search" placeholder="Search by title, author or year" autocomplete="off"></div>
          <div class="filter-group" role="group" aria-label="Filter research outputs by type">{''.join(buttons)}</div>
        </div><p class="results-count" role="status" aria-live="polite">All {len(entries)} research outputs</p>'''
    years = sorted({entry["fields"]["year"] for entry in entries}, reverse=True)
    for year in years:
        html += f'<div class="publication-year"><h3 class="year-label">{year}</h3><ul class="publication-list">'
        for entry in entries:
            if entry["fields"]["year"] != year:
                continue
            category, label = CATEGORIES[entry["id"]]
            fields = entry["fields"]
            status_class = "status-label" if category == "review" else "type-label"
            status_note = f'<p class="pub-status-note">{escape(fields["note"])}</p>' if category == "review" and fields.get("note") else ""
            button = f'<button hidden type="button" class="citation-button" data-citation="{entry["id"]}" aria-label="View BibTeX for {escape(fields["title"], quote=True)}">BibTeX</button>' if interactive else ""
            html += f'''<li id="pub-{entry['id']}" class="publication-item" data-category="{category}">
              <div class="pub-meta"><span class="{status_class}">{escape(label)}</span></div>
              <h4 class="pub-title">{escape(fields['title'])}</h4>
              <p class="pub-authors">{authors(fields['author'])}</p>
              <p class="pub-venue">{venue(entry)}</p>
              {status_note}
              {f'<div class="pub-actions">{button}</div>' if button else ''}
            </li>'''
        html += "</ul></div>"
    if interactive:
        html += '<p class="empty-state" hidden>No matching publications. Try another search or choose All.</p>'
        html += '<p class="bibliography-link"><a href="assets/publications.bib" download>Download complete bibliography <span aria-hidden="true">↓</span></a></p>'
    return html + "</section>"


def project_section(profile):
    html = section_start("projects", "Research projects", "From collective behaviour to intelligent decision support.") + '<div class="project-list">'
    for project in profile["projects"]:
        announcement = ""
        if project.get("announcement_url"):
            label = project.get("announcement_label", "Official project approval announcement")
            announcement = f'<p class="project-link"><a href="{escape(project["announcement_url"])}" target="_blank" rel="noopener noreferrer">{escape(label)} <span aria-hidden="true">↗</span></a></p>'
        details = ""
        if project["funding"] or project["reference"]:
            details = f'''<details class="project-details"><summary>Funding &amp; project details</summary>
              <p>{escape(project['funding'])}</p><p>{escape(project['reference'])}</p></details>'''
        html += f'''<article id="project-{project['id']}" class="project-item">
          <p class="project-date">{escape(project['dates'])}</p>
          <div class="project-content"><h3>{escape(project['title'])}</h3>
          <p class="project-meta">{escape(project['institution'])}</p>
          <p>{escape(project['description'])}</p>
          <p class="project-role"><strong>My role</strong> · {escape(project['role'])}</p>
          {announcement}{details}</div></article>'''
    return html + "</div></section>"


def supervisor_section(profile):
    person = profile["supervisor"]
    html = section_start("supervisor", "Scientific supervisor")
    return html + f'''<div class="supervisor-panel">
      <p class="supervisor-name"><a href="{escape(person['url'])}" target="_blank" rel="noopener noreferrer">{escape(person['name'])}, {escape(person['degree'])} <span aria-hidden="true">↗</span></a></p>
      <ul class="supervisor-affiliations">{''.join(f'<li>{escape(item)}</li>' for item in person['affiliations'])}</ul>
      <p><a href="{escape(person['url'])}" target="_blank" rel="noopener noreferrer">Personal website <span aria-hidden="true">↗</span></a></p>
    </div></section>'''


def timeline(items, heading_level=3):
    return '<ol class="timeline">' + "".join(f'''<li class="timeline-item"><p class="timeline-date">{escape(item['dates'])}</p>
      <div class="timeline-info"><h{heading_level}>{escape(item['title'])}</h{heading_level}><p>{escape(item.get('institution', item.get('description', '')))}</p></div></li>''' for item in items) + "</ol>"


def footer(profile):
    updated = date.fromisoformat(profile["updated"])
    display_date = f"{updated.day} {updated.strftime('%B %Y')}"
    return f'''<footer class="site-footer"><div class="wrapper footer-inner"><p>{escape(profile['name'])} · Academic homepage</p><p>Updated <time datetime="{profile['updated']}">{display_date}</time></p></div></footer>
<button class="back-to-top" hidden type="button" aria-label="Back to top">↑</button>
</body></html>'''


def dialog_markup(entries):
    citations = json.dumps({entry["id"]: entry["raw"] for entry in entries}, ensure_ascii=False).replace("<", "\\u003c")
    return f'''<script type="application/json" id="citation-data">{citations}</script>
<dialog class="citation-dialog" aria-labelledby="citation-heading">
  <div class="dialog-head"><h2 id="citation-heading">BibTeX citation</h2><button id="close-citation" type="button" aria-label="Close citation">×</button></div>
  <pre id="citation-text" tabindex="0"></pre>
  <div class="dialog-actions"><button class="button" id="copy-citation" type="button">Copy BibTeX</button><p id="copy-status" role="status" aria-live="polite"></p></div>
</dialog>'''


def homepage(profile, entries):
    html = head(profile) + header(profile) + '<main id="main-content" class="wrapper">'
    html += f'''<section id="about" class="intro" aria-labelledby="name-heading">
      <div class="intro-copy"><p class="eyebrow">Multi-agent systems · Norm dynamics · Hybrid cognition</p>
        <h1 id="name-heading">{escape(profile['name'])}</h1>
        <ul class="intro-affiliations">{''.join(f'<li>{escape(item)}</li>' for item in profile['affiliations'])}</ul>
        <p class="intro-description">{escape(profile['intro'])}</p>
        <div class="intro-links"><a href="mailto:{profile['email']}">Email <span aria-hidden="true">↗</span></a><a href="{escape(profile['scholar_url'])}" target="_blank" rel="noopener noreferrer">Google Scholar <span aria-hidden="true">↗</span></a><a href="cv.html">Curriculum vitae <span aria-hidden="true">↗</span></a></div>
      </div><div class="portrait-wrap"><img class="portrait" src="assets/portrait.jpeg" width="180" height="180" alt="Portrait of Chao Li" fetchpriority="high"></div>
    </section>'''
    html += section_start("research", "Research interests") + '<div class="research-grid">'
    html += "".join(f'<article class="research-topic"><h3>{escape(topic["title"])}</h3><p>{escape(topic["description"])}</p></article>' for topic in profile["research"])
    html += "</div></section>"
    html += publication_section(entries)
    html += project_section(profile)
    html += supervisor_section(profile)
    html += section_start("background", "Academic background") + '<div class="profile-grid">'
    html += '<div><h3 class="section-label">Education</h3>' + timeline(profile["education"], 4) + '</div>'
    html += '<div><h3 class="section-label">Appointments &amp; experience</h3>' + timeline(profile["appointments"], 4) + '</div></div></section>'
    html += section_start("exchange", "Academic exchange") + timeline(profile["exchange"]) + '</section>'
    html += section_start("contact", "Contact") + f'''<div class="contact-panel"><p>For research enquiries and collaboration:</p>
      <p><a href="mailto:{profile['email']}">{profile['email']}</a></p><p><a href="{escape(profile['scholar_url'])}" target="_blank" rel="noopener noreferrer">Google Scholar <span aria-hidden="true">↗</span></a> <span aria-hidden="true">·</span> <a href="cv.html">Curriculum vitae</a></p></div></section>'''
    html += "</main>" + dialog_markup(entries) + footer(profile)
    return html


def curriculum_vitae(profile, entries):
    html = head(profile, cv=True) + header(profile, cv=True) + '<main id="main-content" class="wrapper">'
    html += f'''<section class="intro"><div class="intro-copy"><p class="eyebrow">Curriculum vitae</p><h1>{escape(profile['name'])}</h1>
      <p><a href="mailto:{profile['email']}">{profile['email']}</a> · <a href="{escape(profile['scholar_url'])}">Google Scholar</a></p>
      <div class="intro-links"><a href="assets/chao-li-cv.pdf" download>Download CV PDF ↓</a><button id="print-cv" class="button" type="button">Print / save as PDF</button><a href="assets/chao-li-cv-source.zip" download>LaTeX source ↓</a><a href="index.html">Back to homepage</a></div></div></section>'''
    for anchor, title, key in [("employment", "Employment history", "appointments"), ("education", "Education", "education")]:
        html += section_start(anchor, title) + timeline(profile[key]) + '</section>'
    html += supervisor_section(profile)
    html += publication_section(entries, interactive=False)
    html += project_section(profile)
    html += section_start("exchange", "Academic exchange") + timeline(profile["exchange"]) + '</section>'
    return html + "</main>" + footer(profile)


def main():
    profile = json.loads((DATA / "profile.json").read_text(encoding="utf-8"))
    bibliography = (DATA / "publications.bib").read_text(encoding="utf-8")
    entries = parse_bib(bibliography)
    assert entries, "Bibliography must not be empty."
    DIST.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "assets", DIST / "assets", dirs_exist_ok=True)
    for dest in [ROOT / "assets/publications.bib", DIST / "assets/publications.bib"]:
        dest.write_text(bibliography, encoding="utf-8")
    for filename, content in [("index.html", homepage(profile, entries)), ("cv.html", curriculum_vitae(profile, entries))]:
        (DIST / filename).write_text(content, encoding="utf-8")
        # Raw protects BibTeX's double braces from Liquid. Jekyll emits the same static page.
        (ROOT / filename).write_text("---\nlayout: null\n---\n{% raw %}\n" + content + "\n{% endraw %}\n", encoding="utf-8")
    print(f"Built homepage and printable CV: {len(entries)} outputs, {len(profile['projects'])} projects.")
    print("Static preview directory:", DIST)


if __name__ == "__main__":
    main()
