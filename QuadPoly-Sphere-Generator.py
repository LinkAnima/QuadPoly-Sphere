import maya.cmds as cmds
import maya.mel as mel

class QuadPolySphereGenerator:
    def __init__(self):
        self.window_name = "QuadPolySphereGeneratorWindow"

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def build_ui(self):
        """Build the Quad Poly Sphere Generator UI."""

        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)

        self.window = cmds.window(
            self.window_name,
            title="Quad Poly Sphere Generator",
            widthHeight=(380, 430),
            sizeable=True
        )

        # Main Scroll Area
        scroll = cmds.scrollLayout(
            horizontalScrollBarThickness=0,
            verticalScrollBarThickness=12,
            childResizable=True
        )

        main = cmds.columnLayout(
            adjustableColumn=True,
            rowSpacing=8,
            columnOffset=("both", 10)
        )

        # --- Geometry Settings ---
        cmds.frameLayout(
            label="Geometry",
            labelAlign="left",
            collapsable=False,
            marginWidth=8,
            marginHeight=8
        )

        cmds.columnLayout(
            adjustableColumn=True,
            rowSpacing=6
        )

        cmds.text(label="Subdivision Level:", align="left")

        self.subdiv_input = cmds.intSliderGrp(
            field=True,
            minValue=1,
            maxValue=6,
            fieldMinValue=1,
            fieldMaxValue=6,
            value=2,
            step=1,
            label="",
            columnWidth=[(1, 1), (2, 100), (3, 180)],
            annotation="Number of subdivision iterations"
        )

        self.triangulate_check = cmds.checkBox(
            label="Triangulate Mesh",
            value=False,
            annotation="Convert all quads to triangles."
        )

        self.hard_edge_check = cmds.checkBox(
            label="Apply Hard Edge",
            value=False,
            annotation="Apply a hard edge to all edges (makes mesh faceted)."
        )

        cmds.setParent("..") # Close Geometry Column
        cmds.setParent("..") # Close Geometry Frame

        # --- UV Settings ---
        cmds.separator(height=6, style="in")

        cmds.frameLayout(
            label="UV Settings",
            labelAlign="left",
            collapsable=False,
            marginWidth=8,
            marginHeight=8
        )

        cmds.columnLayout(
            adjustableColumn=True,
            rowSpacing=6
        )

        # Checkbox controls "Packing". 
        # If checked: UVs are packed into 0-1. 
        # If unchecked: UVs are left as projected (shells may overlap/stack).
        self.pack_check = cmds.checkBox(
            label="Pack UV Shells",
            value=True,
            annotation="If checked, packs UVs into 0-1 space. If unchecked, skips packing."
        )

        cmds.text(label="UV Set Name:", align="left")

        self.uv_set_input = cmds.textField(
            text="uvSet1",
            annotation="Name of the UV set to create/use."
        )

        cmds.setParent("..") # Close UV Column
        cmds.setParent("..") # Close UV Frame

        # --- Naming Settings ---
        cmds.separator(height=6, style="in")

        cmds.frameLayout(
            label="Naming",
            labelAlign="left",
            collapsable=False,
            marginWidth=8,
            marginHeight=8
        )

        cmds.columnLayout(
            adjustableColumn=True,
            rowSpacing=6
        )

        cmds.text(label="Prefix:", align="left")

        self.prefix_input = cmds.textField(
            text="qPolySphere",
            annotation="Prefix for the generated object."
        )

        cmds.setParent("..") # Close Naming Column
        cmds.setParent("..") # Close Naming Frame

        # --- Action ---
        cmds.separator(height=10, style="in")

        cmds.button(
            label="Generate",
            height=45,
            command=self.execute,
            annotation="Generate the quad poly sphere."
        )

        # --- Finish ---
        cmds.setParent("..") # Close Main Column
        cmds.setParent("..") # Close Scroll Layout

        cmds.showWindow(self.window)

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def _get_next_index(self, prefix):
        """Return the next available numeric suffix."""
        index = 1
        while True:
            name = f"{prefix}{index}"
            if not cmds.objExists(name):
                return index
            index += 1

    def _show_error(self, message):
        """Display an error in the Script Editor."""
        cmds.warning(message)

    # ---------------------------------------------------------
    # UVs
    # ---------------------------------------------------------

    def _ensure_uv_set(self, shape, uv_set_name):
        """Ensure the requested UV set exists and make it current."""
        if not uv_set_name:
            uv_set_name = "uvSet1"

        existing_sets = cmds.polyUVSet(
            shape,
            query=True,
            allUVSets=True
        ) or []

        if uv_set_name not in existing_sets:
            cmds.polyUVSet(
                shape,
                create=True,
                uvSet=uv_set_name
            )
            print(f"Created UV set: {uv_set_name}")

        # Make the requested set the current UV set
        try:
            cmds.polyUVSet(
                shape,
                currentUVSet=True,
                uvSet=uv_set_name
            )
        except Exception:
            # Fallback for older versions: rely on selection
            pass

    def _unwrap_uvs(self, shape, uv_set_name):
        """
        Create UVs using Maya's automatic projection.
        Must run BEFORE subdivision.
        """
        self._ensure_uv_set(shape, uv_set_name)
        cmds.select(shape, replace=True)

        try:
            cmds.polyAutoProjection(
                lm=0,           # layoutMethod: None
                pb=0,           # projectedBounds: None
                ibd=1,          # interiorBoundaryDivisions
                cm=0,           # cornerMode: None
                l=0,            # length: None
                sc=1,           # scaleCorrection: Yes
                o=1,            # overlap: Yes
                p=6,            # projection: Auto
                ps=0.2,         # projectionSize
                ws=0            # wrapSize
            )
            print(f"UVs projected onto: {uv_set_name}")
        except Exception as exc:
            raise RuntimeError(f"Automatic UV projection failed: {exc}")

    def _layout_uvs(self, shape, do_pack, uv_set_name):
        """
        Layout UV shells.
        Must run BEFORE subdivision.
        """
        if not do_pack:
            print("Pack UV Shells disabled: Skipping UV layout.")
            return

        self._ensure_uv_set(shape, uv_set_name)
        cmds.select(shape, replace=True)

        try:
            cmds.polyLayoutUV(
                layout=2, # Pack
                scale=1.0
            )
            print(f"UVs packed in set: {uv_set_name}")
        except Exception as exc:
            cmds.warning(f"UV layout failed: {exc}. Continuing.")

    # ---------------------------------------------------------
    # Geometry
    # ---------------------------------------------------------

    def _subdivide(self, transform, levels):
        """Apply subdivision/smoothing."""
        if levels <= 0:
            return

        for level in range(levels):
            shapes = cmds.listRelatives(transform, shapes=True, noIntermediate=True, type="mesh")
            if not shapes:
                raise RuntimeError("Could not find mesh shape during subdivision.")
            
            shape = shapes[0]
            cmds.polySmooth(shape, dv=1)
            print(f"Subdivision level {level + 1}/{levels} applied.")

    def _triangulate(self, transform):
        """Triangulate the mesh."""
        shapes = cmds.listRelatives(transform, shapes=True, noIntermediate=True, type="mesh")
        if not shapes:
            raise RuntimeError("Could not find mesh shape during triangulation.")
        
        shape = shapes[0]
        cmds.polyTriangulate(shape)
        print("Mesh triangulated.")

    def _apply_hard_edge(self, transform):
        """
        Make all mesh edges hard using polySoftEdge with angle=0.
        """
        shapes = cmds.listRelatives(
            transform,
            shapes=True,
            noIntermediate=True,
            type="mesh"
        )

        if not shapes:
            raise RuntimeError("Could not find mesh shape for hard edge.")

        shape = shapes[0]

        edges = cmds.ls(f"{shape}.e[*]", flatten=True)

        if not edges:
            print("No edges found to harden.")
            return

        try:
            # angle=0 makes all selected edges hard
            cmds.polySoftEdge(edges, angle=0)
            print(f"Hard edges applied to {len(edges)} edges.")
        except Exception as exc:
            raise RuntimeError(f"Failed to apply hard edges: {exc}")

    def _scale_to_bbox(self, transform, size=2.0):
        """Scales the object uniformly so its largest dimension equals 'size'."""
        bbox = cmds.exactWorldBoundingBox(transform)
        width = bbox[3] - bbox[0]
        height = bbox[4] - bbox[1]
        depth = bbox[5] - bbox[2]

        max_dim = max(width, height, depth)

        if max_dim == 0:
            raise RuntimeError("Object has zero dimensions.")

        scale_factor = size / max_dim

        cmds.scale(
            scale_factor, scale_factor, scale_factor, 
            transform, 
            relative=True
        )
        print(f"Uniformly scaled by {scale_factor:.4f}")

    # ---------------------------------------------------------
    # Main Execution
    # ---------------------------------------------------------

    def execute(self, *args):
        """
        Generate the quad poly sphere proxy mesh.
        Order: Cube -> UV -> Layout -> Subdiv -> Triang -> HardEdge -> Scale -> Freeze -> DelHistory -> Rename
        """
        subdiv_level = cmds.intSliderGrp(self.subdiv_input, query=True, value=True)
        do_pack = cmds.checkBox(self.pack_check, query=True, value=True)
        do_triangulate = cmds.checkBox(self.triangulate_check, query=True, value=True)
        do_hard_edge = cmds.checkBox(self.hard_edge_check, query=True, value=True)
        
        uv_set_name = cmds.textField(self.uv_set_input, query=True, text=True).strip()
        prefix = cmds.textField(self.prefix_input, query=True, text=True).strip()

        if not uv_set_name:
            self._show_error("UV Set Name cannot be empty.")
            return
        if not prefix:
            self._show_error("Naming Prefix cannot be empty.")
            return

        chunk_opened = False
        cube_transform = None
        
        try:
            cmds.undoInfo(openChunk=True, chunkName="Quad Poly Sphere Generate")
            chunk_opened = True

            # 1. Create Base Cube
            cube_transform = cmds.polyCube(
                width=1.0,
                height=1.0,
                depth=1.0,
                subdivisionsX=1,
                subdivisionsY=1,
                subdivisionsZ=1
            )[0]

            shapes = cmds.listRelatives(cube_transform, shapes=True, noIntermediate=True, type="mesh")
            if not shapes:
                raise RuntimeError("Created cube has no mesh shape.")
            
            cube_shape = shapes[0]
            print(f"Created base cube: {cube_transform}")

            # 2. UV Unwrap (On Base Cube)
            self._unwrap_uvs(cube_shape, uv_set_name)

            # 3. UV Layout (On Base Cube)
            self._layout_uvs(cube_shape, do_pack, uv_set_name)

            # 4. Apply Subdivision
            self._subdivide(cube_transform, subdiv_level)

            # 5. Triangulate (Optional)
            if do_triangulate:
                self._triangulate(cube_transform)

            # 6. Hard Edge (Optional)
            if do_hard_edge:
                self._apply_hard_edge(cube_transform)

            # 7. Scale to Bounding Box
            self._scale_to_bbox(cube_transform, size=2.0)

            # 8. Freeze Transformations
            cmds.makeIdentity(cube_transform, apply=True, t=True, r=True, s=True)

            # 9. Delete Construction History
            cmds.delete(cube_transform, constructionHistory=True)

            # 10. Rename
            next_num = self._get_next_index(prefix)
            transform_name = f"{prefix}{next_num}"
            shape_name = f"{prefix}Shape{next_num}"

            transform_name = cmds.rename(cube_transform, transform_name)
            
            final_shapes = cmds.listRelatives(transform_name, shapes=True, noIntermediate=True, type="mesh")
            if not final_shapes:
                raise RuntimeError("Could not find mesh shape after rename.")
            
            shape_name = cmds.rename(final_shapes[0], shape_name)

            # 11. Select Result
            cmds.select(transform_name)

            print("--------------------------------")
            print(f"Success: {transform_name}")
            print(f"Shape:   {shape_name}")
            print(f"UV Set:  {uv_set_name}")
            print(f"Subdiv:  {subdiv_level}")
            print(f"Triang:  {do_triangulate}")
            print(f"PackUV:  {do_pack}")
            print(f"HardE:   {do_hard_edge}")
            print("--------------------------------")

        except Exception as exc:
            import traceback
            error_msg = f"Generation Failed: {exc}"
            print(error_msg)
            traceback.print_exc()
            self._show_error(error_msg)

            if cube_transform and cmds.objExists(cube_transform):
                try:
                    cmds.delete(cube_transform)
                except Exception:
                    pass

        finally:
            if chunk_opened:
                cmds.undoInfo(closeChunk=True)

# -------------------------------------------------------------
# Launch
# -------------------------------------------------------------

if __name__ == "__main__":
    try:
        tool = QuadPolySphereGenerator()
        tool.build_ui()
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"Failed to launch UI: {exc}")
