# Quad Poly Sphere Generator: User Guide

## Overview
The **Quad Poly Sphere Generator** is a tool for creating high-quality proxy spheres in Maya. It builds a sphere from a simple cube, applies subdivision smoothing, and handles UVs and naming automatically.

It is ideal for:
*   Creating collision proxies for characters.
*   Generating base meshes for sculpting or detailing.
*   Quick iteration on spherical geometry.

---

## The Workflow
When you click **Generate**, the tool performs the following steps in this specific order:

1.  **Creates a Cube:** Starts with a standard 1x1x1 cube.
2.  **Unwraps UVs:** Projects UVs onto the cube *before* it changes shape. This ensures clean UV layouts.
3.  **Subdivides:** Smooths the cube into a sphere shape based on your level preference.
4.  **Triangulates (Optional):** Converts quads to triangles if enabled.
5.  **Hardens Edges (Optional):** Makes all edges sharp if enabled.
6.  **Finalizes:** Scales to 2 units, freezes transforms, deletes history, and renames the object.

---

## Feature Breakdown

### 1. Geometry Settings
These controls determine the shape and density of the mesh.

*   **Subdivision Level (1–6):**
    *   Controls how "smooth" the sphere is.
    *   **Level 1–2:** Low poly. Good for distant collision or quick previews.
    *   **Level 3–4:** Medium poly. Good general-purpose proxy.
    *   **Level 5–6:** High poly. Very smooth, but heavier on your computer.
    *   *Best Practice:* Start with **Level 2 or 3**. You can always subdivide more later in the viewport if needed.

*   **Triangulate Mesh:**
    *   If checked, all quads (4-sided faces) are converted to triangles (3-sided faces).
    *   *When to use:* Useful if you are exporting to game engines that require triangles, or if you plan to boolean-cut the sphere.
    *   *Warning:* Triangulating *before* subdividing is not possible; this happens after the sphere shape is formed.

*   **Apply Hard Edge:**
    *   If checked, the mesh will look **faceted** (like a gemstone or low-poly art style) instead of smooth.
    *   *When to use:* For stylized 3D art where you want visible facets.
    *   *Warning:* Do **not** use this if you want a smooth, organic sphere. A subdivided cube with hard edges looks like a ball of triangles.

### 2. UV Settings
These controls determine how the texture mapping is laid out.

*   **Pack UV Shells:**
    *   **Checked (Default):** The UV islands are packed tightly into the 0-1 texture space. This is best for **baking textures** or using standard PBR workflows where you want to use as much texture resolution as possible.
    *   **Unchecked:** The UVs are left in their projected positions. They may overlap or stack on top of each other.
    *   *When to use:* Rarely needed for a sphere. Usually, you want packing ON. Only uncheck this if you are using a specific workflow that relies on stacked UVs (e.g., certain multi-material setups).

*   **UV Set Name:**
    *   The name of the UV channel created on the mesh (e.g., `uvSet1`).
    *   *Best Practice:* Keep the default `uvSet1` unless you have a specific reason to name it differently (e.g., `proxyUv` or `collisionUv`).

### 3. Naming
*   **Prefix:**
    *   The base name of the object.
    *   The tool automatically adds a number to ensure uniqueness.
    *   *Example:* If you name the prefix `qPolySphere` and you already have `qPolySphere1` in your scene, the new object will be named `qPolySphere2`.
    *   *Best Practice:* Use a consistent prefix like `qPolySphere`, `proxySphere`, or `colSphere` to keep your scene organized.

---

## Best Practices & Tips

### 1. The "Hard Edge" Trap
**This is the most common mistake.**
If you check **"Apply Hard Edge"**, your smooth sphere will immediately look like a faceted gem.
*   **Want a smooth sphere?** Leave Hard Edge **OFF**.
*   **Want a stylized low-poly look?** Turn Hard Edge **ON**, but consider using a lower subdivision level (1 or 2) for a cleaner faceted look.

### 2. Performance
*   **Subdivision Level 6** creates a mesh with over **200,000 faces**.
*   If your scene becomes slow, lower the subdivision level. You can always select the sphere in the viewport and press `1` (Object mode) to see the low-poly wireframe, or use `Ctrl+1` to switch to wireframe shading to improve viewport performance.

### 3. Scaling
The tool automatically scales the sphere so its largest dimension is **2 units**.
*   This means the sphere will fit inside a box that is 2x2x2 units.
*   If you need a different size, **do not scale the object manually** before using the tool. Let the tool scale it to 2, then scale it down or up as needed after generation.

### 4. UVs for Baking
*   Always ensure **Pack UV Shells** is **checked** if you plan to bake ambient occlusion, normal maps, or other maps onto this sphere.
*   If you uncheck packing, your UVs may overlap, causing "leaking" or corrupted bakes.

### 5. Triangulation for Games
*   If you are using this as a **collision proxy** for a game engine:
    1.  Set Subdivision to **1 or 2** (keep it lightweight).
    2.  Check **Triangulate Mesh** (most engines prefer triangles).
    3.  Leave **Hard Edge** OFF (collision proxies should be smooth).
    4.  Check **Pack UV Shells** (in case you need a texture later).

---

## Troubleshooting

| Problem | Likely Cause | Solution |
| :--- | :--- | :--- |
| **Sphere looks faceted/sharp** | "Apply Hard Edge" is checked. | Uncheck "Apply Hard Edge" and regenerate. |
| **Viewport is laggy** | Subdivision level is too high (5 or 6). | Reduce to level 2 or 3. Or press `W` to cycle shading to Wireframe. |
| **UVs look messy/overlapping** | "Pack UV Shells" is unchecked. | Check "Pack UV Shells" and regenerate. |
| **Object name is wrong** | You used a custom prefix. | Check the "Prefix" field. The tool appends a number automatically (e.g., `prefix1`). |
| **Nothing happens on click** | Check the Script Editor (Maya). | Look for red error messages in the Maya Script Editor window (Window > General Editors > Script Editor). |

---

## Quick Start Checklist

1.  Open the tool: **Window > Custom > Quad Poly Sphere Generator** (or however you loaded it).
2.  Set **Subdivision Level** to **2** (for a standard smooth sphere).
3.  Leave **Triangulate** and **Hard Edge** **OFF**.
4.  Leave **Pack UV Shells** **ON**.
5.  Set **Prefix** to your preferred name (e.g., `qPolySphere`).
6.  Click **Generate**.
7.  Your new sphere will appear in the scene, selected and ready to use.
