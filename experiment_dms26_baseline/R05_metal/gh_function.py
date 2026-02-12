""" Summary:
The script builds a modular facade by tiling rectangular panel Breps along the X axis and stacking their height on Z. Parameters (panel_width, panel_height, panel_depth, num_panels, offset) control panel size, thickness and spacing. For each panel it computes four corner points, uses a fixed random seed to toggle a vertical offset for a porous staggered effect, and creates a Brep from those corners. It repeats this to produce multiple sample variations, collects them in a list, and converts the results into a Grasshopper DataTree for downstream use. Material and image-driven styling are not applied here but could be mapped onto the Breps in Rhino/Grasshopper."""

#! python 3
function_code = """def create_facade_geometry(panel_width=1.0, panel_height=2.5, panel_depth=0.1, num_panels=10, offset=0.2):
    \"""
    Generates a facade geometry on the XZ plane using a modular panel system.

    The geometry consists of panels structured in a grid pattern, with voids created between the panels to mimic
    a porous structure.

    Args:
    - panel_width (float): The width of each panel in meters.
    - panel_height (float): The height of each panel in meters.
    - panel_depth (float): The depth (thickness) of each panel in meters.
    - num_panels (int): The number of panels across the width of the facade.
    - offset (float): The horizontal space between panels in meters.

    Returns:
    - List[Rhino.Geometry.Brep]: A list of Breps representing the facade geometry.

    Note:
    - This function uses RhinoCommon and is intended for use within Grasshopper for Rhino 8.
    \"""
    import Rhino.Geometry as rg
    import random

    random.seed(42)  # Ensure repeatability

    facade = []

    for i in range(num_panels):
        # Calculate the X position of this panel
        x_pos = i * (panel_width + offset)

        # Randomly decide if this panel should be offset vertically to create a porous effect
        y_offset = random.choice([0, offset])

        # Create a corner point for the panel
        pt1 = rg.Point3d(x_pos, 0, y_offset)
        pt2 = rg.Point3d(x_pos + panel_width, 0, y_offset)
        pt3 = rg.Point3d(x_pos + panel_width, panel_depth, y_offset + panel_height)
        pt4 = rg.Point3d(x_pos, panel_depth, y_offset + panel_height)

        # Create a rectangular Brep for this panel
        panel_brep = rg.Brep.CreateFromCornerPoints(pt1, pt2, pt3, pt4, 0.01)
        
        if panel_brep:
            facade.append(panel_brep)

    return facade"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = create_facade_geometry(panel_width=1.2, panel_height=3.0, panel_depth=0.15, num_panels=12, offset=0.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = create_facade_geometry(panel_width=0.8, panel_height=2.2, panel_depth=0.12, num_panels=20, offset=0.15)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = create_facade_geometry(panel_width=1.5, panel_height=2.8, panel_depth=0.2, num_panels=8, offset=0.3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = create_facade_geometry(panel_width=0.6, panel_height=2.0, panel_depth=0.08, num_panels=15, offset=0.1)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = create_facade_geometry(panel_width=0.4, panel_height=2.5, panel_depth=0.05, num_panels=30, offset=0.08)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
