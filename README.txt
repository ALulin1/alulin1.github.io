Chao Li academic homepage
Updated: 2026-10-08

This is a complete single-page English academic homepage. All 17 research outputs,
all 5 projects, the scientific supervisor, education, appointments and contact
information appear on the homepage. A separate printable CV is also included.

The visual design follows the restrained typography, light background and blue
links of Sergey V. Kovalchuk's homepage, with a custom layout for a single-page
research profile. The source supports Jekyll and GitHub Pages; minima is the
configured theme, while index.html and cv.html use their own page layout.

Preview locally
1. Run: python3 scripts/build.py
2. Run: python3 -m http.server 8000 --directory dist --bind 127.0.0.1
3. Open http://127.0.0.1:8000
   Ctrl+C stops the local preview server.

Publish with GitHub Pages
1. Create a personal repository named alulin1.github.io.
2. Upload the contents of this source package to its main branch. Include the
   .github/workflows/pages.yml file; it is a hidden folder on some computers.
3. In Settings > Pages, select GitHub Actions as the build/deployment source.
4. The included workflow regenerates the pages, builds with Jekyll and deploys
   the site. Check the Actions run for success before using the live URL.
5. The public address is https://alulin1.github.io/.
   Source repository: https://github.com/ALulin1/alulin1.github.io

Maintain the website
- Edit data/profile.json for the biography, supervisor, projects and background.
- Edit data/publications.bib for publications. Existing entries retain their
  explicit category; new entries are categorised by their BibTeX type and
  keywords (abstract/submitted) or Under review note. Do not invent missing
  venue, DOI or publication status information.
- Run python3 scripts/build.py after edits, or let the GitHub workflow regenerate
  the pages when changes are pushed to main.
- Change assets/portrait.jpeg to replace the photograph.
- Edit assets/styles.css for visual styling and assets/site.js for interactions.
- Update the updated field in data/profile.json when revising the content.

CV and citations
- assets/chao-li-cv.pdf is the downloadable CV, updated 8 October 2026.
- cv.html also provides a printable web CV. Its Print / save as PDF button opens
  the browser's print dialog.
- assets/chao-li-cv-source.zip contains the updated LaTeX CV source, including
  the Senior Researcher title, the two manuscript updates, and all three
  supervisor appointments confirmed by the owner.
- assets/publications.bib contains 17 research outputs, including a Mathematics
  manuscript after its first-round revision and an Expert Systems with
  Applications submission currently with the editor. These are not marked as
  accepted or published.
- Publications are present in the initial HTML. Search and type filters are
  optional enhancements; they do not hide outputs by default.
- There are no analytics, tracking cookies, third-party fonts or databases.

Reference URLs
https://iterater.github.io/
https://github.com/actions/starter-workflows/blob/main/pages/jekyll-gh-pages.yml
https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
