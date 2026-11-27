# Sculptural Form References (`style_refs/`)

Drop curated architectural form reference images (`.jpg`, `.png`, `.webp`) here to guide bold, non-boxy silhouettes in `build_render_pack.py` and `render_jobs.json`:

- `courtyard/` — sculptural monolithic walls, thin-shell oculus roofs, deep light-slots
- `terrace/` — stepped monolithic earth/stone strata & carved light-canyons
- `cantilever/` — cantilevered trusses, floating solar blades, suspended decks
- `clustered_compound/` — faceted crystalline/monolithic clusters with deep apertures
- `bridge/` — long-span structural diagrids & parabolic arches

When `build_render_pack.py` runs, it automatically copies matching references into each `site_<N>/refs/` folder and attaches them alongside `satellite_lock.png` in `render_jobs.json` (`attach_images`), strictly locking **Image 1** to site/scale/terrain and **Image 2+** to sculptural building form.
