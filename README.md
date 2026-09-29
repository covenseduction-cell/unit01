# Settlers III Wiki

The player wiki for the Settlers III Minecraft server, served at https://unit01.xyz by GitHub Pages.

## Editing

Pages live in `pages/` as HTML fragments. The first line of each is its metadata:

```html
<!-- title: Ships & sailing | group: Travel | order: 20 | status: live | summary: One-line description. -->
```

- `group` is the sidebar section: Start here, The World, Survival, Building, Travel, Trade, Reference.
- `order` sorts pages within a group.
- `status` is `live`, `partial` or `planned` (shown as a badge), or left out.
- `pages/home.html` becomes `index.html`.

After editing, rebuild and commit:

```sh
python3 build.py
git add -A && git commit -m "Update wiki" && git push
```

`build.py` needs only Python 3. It writes one `.html` per page into the root and a `search-index.json` for the search box. Styling is in `assets/style.css`, behaviour in `assets/wiki.js`.
