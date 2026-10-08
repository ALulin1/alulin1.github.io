# Chao Li — Academic homepage

Live website: https://alulin1.github.io/

An academic profile built with GitHub Pages, Jekyll and Minima, with a custom single-page layout. The homepage includes all 17 research outputs, 5 projects, supervisor information, academic background and contact links.

## Update content

- Edit `data/profile.json` for biography, projects, supervisor and appointments.
- Edit `data/publications.bib` for research outputs and manuscript status.
- Replace `assets/portrait.jpeg` to update the photograph.
- Replace `assets/chao-li-cv.pdf` to update the downloadable CV.
- Run `python3 scripts/build.py` to regenerate `index.html` and `cv.html`.
- Push changes to `main`; the included GitHub Actions workflow builds with Jekyll and deploys GitHub Pages.

## Local preview

```sh
python3 scripts/build.py
python3 -m http.server 8000 --directory dist --bind 127.0.0.1
```

Open http://127.0.0.1:8000/ and press Ctrl+C to stop the preview.

The manuscripts listed on the site retain their actual submission status; they are not marked as accepted or published.
