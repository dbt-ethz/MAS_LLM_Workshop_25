""" Summary:
The script defines generate_facade_geometry to produce a row of rectangular panels on the XZ plane by iterating panel_count times and placing each panel at increasing X positions. Each panel is built from four corner points forming a closed polyline and converted to a Brep. A seeded random y_offset shifts panels in depth for controlled variation. Parameters (panel_count, panel_height, panel_width, offset) let you tune scale and rhythm. The top-level code creates five sample variations, collects their Breps, and converts them into a Grasshopper DataTree for downstream use. Rhino.Geometry is used for geometry creation and validity checks, ensuring reproducible, consistent outcomes overall."""

#! python 3
function_code = """def generate_facade_geometry(panel_count=10, panel_height=3.0, panel_width=1.0, offset=0.2):
    \"""
    Creates a facade geometry using a series of panels on the XZ plane.

    Parameters:
    - panel_count (int): The number of panels in the facade.
    - panel_height (float): The height of each panel.
    - panel_width (float): The width of each panel.
    - offset (float): The offset distance between each panel to create depth.

    Returns:
    - geometries (list): A list of Brep geometries representing the facade panels.
    \"""
    import Rhino.Geometry as rg
    import random

    # Seed for replicable randomness
    random.seed(42)

    geometries = []
    
    for i in range(panel_count):
        x_location = i * panel_width
        y_offset = random.uniform(-offset, offset)
        
        panel_corners = [
            rg.Point3d(x_location, y_offset, 0),
            rg.Point3d(x_location + panel_width, y_offset, 0),
            rg.Point3d(x_location + panel_width, y_offset, panel_height),
            rg.Point3d(x_location, y_offset, panel_height),
            rg.Point3d(x_location, y_offset, 0)  # Close the polyline
        ]

        polyline = rg.Polyline(panel_corners)
        if polyline.IsClosed:
            panel = rg.Brep.CreateFromCornerPoints(panel_corners[0], panel_corners[1], panel_corners[2], panel_corners[3], 0.01)
            if panel is not None and panel.IsValid:
                geometries.append(panel)

    return geometries"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(panel_count=12, panel_height=3.0, panel_width=1.5, offset=0.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(panel_count=8, panel_height=4.5, panel_width=0.8, offset=0.4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(panel_count=20, panel_height=3.5, panel_width=0.9, offset=0.15)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(panel_count=6, panel_height=5.0, panel_width=2.0, offset=0.5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(panel_count=15, panel_height=2.8, panel_width=1.2, offset=0.3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
