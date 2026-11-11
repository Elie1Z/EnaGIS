# Publish EnaGIS Live with Netlify Drop

From the repository root, run:

```sh
python -m scripts.package_netlify
```

The script uses only Python's standard library and writes:

- `outputs/netlify-drop/EnaGIS-Netlify-Drop.zip`: ready to upload, with `index.html` at the ZIP root.
- `outputs/netlify-drop/site/`: the equivalent folder, also ready to drop.
- `outputs/netlify-drop/package-audit.json`: file hashes and archive integrity information.
- `outputs/netlify-drop/DEPLOY.md`: brief publishing instructions.

Open [Netlify Drop](https://app.netlify.com/drop) and drop the ZIP or the `site` folder.
Upload the actual `site` folder, not `outputs/netlify-drop` or the whole repository.
Netlify supplies the hosted URL. No build command, Python server, secret or environment variable
is needed to run the deployed site. Official steps: [Netlify Drop quickstart](https://docs.netlify.com/start/quickstarts/netlify-drop-quickstart/).

The package contains the current `live/` app, local fonts and libraries, the saved Nyabihu
analysis, and licence notices. Runtime files are copied unchanged; research scripts, Python
environments, raw datasets and private verification folders are excluded.

Fresh place searches and online basemaps need internet and depend on external public services.
The bundled Nyabihu analysis can be replayed without those services once the app's files load.
Publishing does not complete field verification or change the interpretation of scientific results.
