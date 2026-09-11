# Quad Poly Sphere Generator: User Guide & Best Practices

## What This Tool Does

The **Quad Poly Sphere Generator** is a Maya script tool that creates a clean, UV-mapped, quad-based sphere from a simple cube. It’s designed for artists who need a quick, predictable poly-sphere with proper UVs—without manually unwrapping, subdividing, and renaming every time.

Instead of the typical 10-step manual workflow (cube → auto-project → layout → smooth → freeze → delete history → rename…), this tool handles it all in one click with a simple UI.

---

## The Interface

When you run the tool, a small window appears with three sections:

### 1. Geometry
- **Subdivision Level**: How many times to smooth the cube into a sphere.  
  - `1` = 24 faces (a bit blocky)  
  - `2` = 96 faces (good for proxies)  
  - `3` = 384 faces (smoother)  
  - `4+` = Getting heavy (1,536+ faces)  
  - *Max is capped at 6 to avoid accidental memory explosions.*
- **Triangulate Mesh**: Converts all quads to triangles. Use this if your pipeline or renderer prefers tris, or if you’re exporting to a game engine.
- **Apply Hard Edge**: Makes all edges hard, giving the sphere a faceted, low-poly look. **Warning:** This will make a smooth-looking sphere look angular. Only use this if you actually want that aesthetic.

### 2. UV Settings
- **Pack UV Shells**:  
  - **Checked (default)**: UVs are packed neatly into the 0–1 UV space. This is what you want 95% of the time.
  - **Unchecked**: UVs are left as Maya’s auto-projection left them. Shells may overlap or fall outside the 0–1 space. Only disable this if you have a specific reason (e.g., you’re doing manual UV stacking later).
- **UV Set Name**: The name of the UV set to create. Default is `uvSet1`. You can change it if your project uses a different naming convention (e.g., `uv_main`, `uv_atlas`).

### 3. Naming
- **Prefix**: The base name for the object. Default is `qPolySphere`.  
  - The tool will automatically find the next available number.  
  - If `qPolySphere1` already exists, it will create `qPolySphere2`.  
  - Change this if you want a different naming convention (e.g., `sphere_`, `ball_`).

### The Button
- **Generate**: Click this to run the entire pipeline. You’ll see a confirmation in the Script Editor and viewport when it’s done.

---

## The Workflow (What Happens Under the Hood)

For transparency, here’s the exact order of operations:

1. **Create** a 1x1x1 poly cube.
2. **Auto-Project UVs** onto the cube (using the UV set you specified).
3. **Pack UVs** (if “Pack UV Shells” is checked).
4. **Subdivide** the cube the number of times you specified (UVs subdivide with the geometry).
5. **Triangulate** (if checked).
6. **Apply Hard Edges** (if checked, using a 0° smoothing angle).
7. **Scale** the result so its largest dimension is exactly 2.0 units.
8. **Freeze Transformations** (sets position/rotation/scale to 0/0/1).
9. **Delete Construction History** (bakes the mesh, removing all nodes).
10. **Rename** the transform and shape nodes with the appropriate numbering.
11. **Select** the result.

Everything is wrapped in a single undo chunk, so if you don’t like the result, **Ctrl+Z** will cleanly remove it.

---

## Best Practices

### Subdivision Level
- **Level 1–2**: Great for proxies, planning shots, or low-poly assets.
- **Level 3**: A good general-purpose sphere.
- **Level 4+**: Use with caution. Level 6 is ~100,000 faces. That’s fine for a single object, but generating 10 of them will slow your scene down.
- **Rule of thumb**: Start with 2. If it’s too blocky for your needs, bump it up. Don’t start at 6.

### Triangulate
- **Leave unchecked** if you’re staying in Maya and working with quads. Quads are easier to subdivide and edit.
- **Check it** if you’re exporting to a game engine, Unreal, Unity, or any DCC that handles tris better.
- **Note:** Triangulating after subdivision is fine. The UVs will remain valid.

### Hard Edges
- **Leave unchecked** for 99% of use cases. A smooth sphere should have soft edges.
- **Check it** only if you want a deliberate low-poly, faceted aesthetic (think: retro game style, certain stylized looks).
- **Warning:** Hard edges on a high-subdivision sphere will make it look like a geodesic dome. Make sure that’s what you want.

### UV Packing
- **Keep it checked** unless you have a specific reason not to.
- Unpacked UVs (from auto-projection only) will have shells scattered across the UV space, possibly overlapping or extending beyond 0–1. This is rarely what you want.
- If you’re using this sphere as a source for procedural texturing or baking, packed UVs are almost always preferable.

### Naming
- Use a consistent prefix that matches your project’s naming conventions.
- The tool is smart about numbering, so you can safely run it multiple times without worrying about name conflicts.
- If you’re generating many spheres in a batch, consider using a prefix that includes a scene or asset code (e.g., `scene1_sphere`, `asset_ball`).

---

## Troubleshooting

### “Generation Failed” Error
- Check the Script Editor (Window → General Editors → Script Editor). The error message will tell you exactly which step failed and why.
- Most common causes:
  - The scene is locked or read-only.
  - You’re trying to create a UV set that doesn’t meet Maya’s naming requirements (no spaces, no special characters).
  - You don’t have enough memory for the subdivision level you chose.

### The Sphere Looks Faceted
- You likely checked **Apply Hard Edge**. Uncheck it and regenerate.

### The UVs Look Messy or Overlapping
- You likely unchecked **Pack UV Shells**. Re-check it and regenerate.
- If you *want* overlapping shells, that’s intentional. But for most workflows, you want packed UVs.

### The Object Is Too Big or Too Small
- The tool always scales the result to a 2.0 unit bounding box. If that’s not what you want, manually scale the object after generation. This is by design—consistent sizing makes it easier to work with in a scene.

### I Want to Undo
- **Ctrl+Z** will undo the entire generation in one step. This is reliable because the tool uses a single undo chunk.

---

## Where to Place This in Your Scene

The generated sphere is a **quads-based poly mesh** with:
- Clean, predictable UVs (packed into 0–1).
- No construction history (it’s a “baked” mesh).
- Frozen transformations (origin at 0,0,0).

This makes it ideal for:
- **Proxies** in animation or layout.
- **Base meshes** for sculpts or further modeling.
- **Export targets** for game pipelines (if triangulated).
- **Procedural source** for texturing or baking.

It’s **not** ideal for:
- High-end production renders where you need perfect topology (a true sphere has better UVs and edge flow).
- Situations where you need NURBS-based spherical geometry.

---

## Installation

1. Save the script as `quad_poly_sphere_generator.py` in your Maya `scripts` folder (e.g., `C:\Users\<you>\maya\<version>\scripts\` on Windows, or `~/maya/<version>/scripts/` on Mac/Linux).
2. Restart Maya.
3. To run:
   - Open the **Script Editor** (Window → General Editors → Script Editor).
   - Paste the following and hit **Run**:
     ```python
     import quad_poly_sphere_generator
     tool = quad_poly_sphere_generator.QuadPolySphereGenerator()
     tool.build_ui()
     ```
4. Or, add a button to your shelf that calls the same code.

---

## A Note on Design Decisions

- **Why start from a cube?** It gives you perfectly even quad topology and predictable UV shells. A native poly sphere in Maya has poles and uneven topology, which is harder to UV.
- **Why UV before subdivision?** UVs need to be on a simple topology to project cleanly. Once you subdivide, the UVs follow the geometry, so you get a full set of UVs on the high-poly result.
- **Why scale to 2.0?** It’s a consistent, scene-friendly size. You can always scale it later, but starting with a known size makes composition easier.

This tool is a **starting point**, not a replacement for proper UV unwrapping or modeling. If you need a specific UV layout or edge flow, model it manually. But for quick spheres with clean UVs, it’s a huge time-saver.
