# xkazuka.github.io — LLM Compendium web frontend

Static site that renders articles from [xkazuka/llm-compendium](https://github.com/xkazuka/llm-compendium).

## Build

```sh
python3 -m venv .venv && .venv/bin/pip install markdown   # one-time setup
cp <article.md> content/<section>/                        # add content
.venv/bin/python tools/build.py                           # renders to index.html + articles/
```

## Deploy

`index.html` and `articles/` are committed to `main`; GitHub Pages serves them at https://xkazuka.github.io.
Preview locally with `python3 -m http.server` from the repo root.
