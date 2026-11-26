# Architectural Render Quality Control (QC) Checklist

After `image-generator` produces a render, inspect the image using `read_file` and verify every item below before presenting or embedding it.

## Critical Checks (Any Failure Triggers 1 Auto-Fix Pass)

1. **Whole-Project Aerial Legibility**
   - Is the entire project and its overall massing idea clearly visible without awkward cropping of primary volumes?
   - Does the vantage point read as a real aerial architectural photograph (not a flat 2D satellite map and not a cropped eye-level shot unless requested)?
2. **True Architectural Scale (No Toy/Miniature Effect)**
   - Is the depth-of-field crisp and natural across the frame?
   - Fail if tilt-shift blur makes the buildings look like a miniature plastic/scale model.
3. **Reference Massing & Satellite Alignment** *(when visual references were provided)*
   - Does the render honor the overall massing idea, footprint organization, and relative height hierarchy of the input sketch/screenshot/plan/satellite crop?
   - Fail if the generator invented a completely unrelated building layout or ignored key massing moves.
4. **Editorial Photorealism & Lighting Discipline**
   - Does the lighting match the requested mode (default: soft diffused overcast daylight) with restrained editorial color grading?
   - Fail if the image looks like oversaturated HDR CGI, cartoon/painterly illustration, or has artificial neon/bloom artifacts.
5. **Tectonic & Artifact Cleanliness**
   - Are facades, roof edges, glazing grids, and ground connections structurally plausible?
   - Fail if there is visible gibberish signage/text, melted windows, floating architectural elements, or severely distorted vehicles/trees.
6. **Geographic, Topographic & Hydrological Fidelity (Anti-Hallucination Gate)**
   - Compare the render directly against `*_site_context.md` and the site's actual GIS/satellite map:
     - **Topography**: Does the terrain relief match reality? (**Fail** if hills, cliffs, mountains, or rolling parkland appear on a flat alluvial plain or flat desert site.)
     - **Hydrology**: Do water bodies match reality? (**Fail** if artificial turquoise ponds, lakes, lagoons, waterfalls, or perennial rivers appear on dry inland or ephemeral arid wadi sites, OR if a real bordering river like the Nile is missing or misplaced.)
     - **Surrounding Fabric**: Do neighboring edges match reality? (**Fail** if dense Egyptian urban fabric or flat agricultural fields were replaced by generic fantasy wilderness.)
     - **Vegetation Density**: Does planting match the true climate? (**Fail** if lush temperate/tropical lawns or dense green riverbanks appear in hyper-arid desert plots.)

## Auto-Fix Pass Rule

- **Maximum 1 automatic fix pass** per generation request.
- When a critical check fails:
  1. Identify the specific 1–2 concrete defects (e.g., *"hallucinated circular turquoise pond and rocky hills on flat Assiut alluvial plain; Nile River edge missing"* or *"shallow tilt-shift blur makes buildings look like a toy model"*).
  2. Re-invoke `image-generator` with a targeted correction explicitly removing the hallucinated landscape feature and restating the Site Reality Lock.
  3. Re-inspect the revised image with `read_file` before presenting or embedding.
- **If the fix pass or initial generation hits an image-generator usage/quota limit**, immediately trigger **Step 4B (Consolidated Multi-Prompt Fallback)** in `SKILL.md` so the user receives one complete copy-paste-ready prompt containing all required images.
- Never loop indefinitely—if minor imperfections remain after the 1 fix pass, present the best result clearly and note what can be refined next.
