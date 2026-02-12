""" Summary:
The script defines generate_facade_geometry(pattern_scale, window_width, window_height) to produce Brep-based facade geometry. It computes facade width, height and thickness scaled by pattern_scale, creates an initial solid box aligned to the XZ plane (thickness along Y), then tessellates window void boxes in a regular grid using the provided window dimensions. Each window box is subtracted from the solid with a Boolean difference to create voids. Example calls produce several parameter variations; results are collected, converted to a Grasshopper DataTree, and returned. Random seeding is set but not used in the current grid generation. The function returns a list of Brep facade geometries."""

#! python 3
function_code = """def generate_facade_geometry(pattern_scale=1.0, window_width=1.0, window_height=2.0):
    \"""
    Generate a 3D facade geometry with window voids on the XZ plane.
    
    Parameters:
    - pattern_scale: float, scales the entire pattern size. Default is 1.0.
    - window_width: float, the width of each window void. Default is 1.0.
    - window_height: float, the height of each window void. Default is 2.0.
    
    Returns:
    - List of Brep: A list of RhinoCommon Brep objects representing the facade geometry.
    \"""
    import Rhino.Geometry as rg
    import random

    # Seed for randomness
    random.seed(42)

    # Define facade dimensions
    facade_width = 10 * pattern_scale
    facade_height = 10 * pattern_scale
    facade_thickness = 0.3 * pattern_scale
    
    # Initial solid facade
    solid = rg.Box(
        rg.Plane.WorldXY,
        rg.Interval(0, facade_width),
        rg.Interval(-facade_thickness / 2, facade_thickness / 2),
        rg.Interval(0, facade_height)
    ).ToBrep()

    # Create window voids
    windows = []
    for i in range(int(facade_width // (window_width * 2))):
        for j in range(int(facade_height // (window_height * 2))):
            x = i * 2 * window_width + window_width / 2
            z = j * 2 * window_height + window_height / 2
            window = rg.Box(
                rg.Plane.WorldXY,
                rg.Interval(x - window_width / 2, x + window_width / 2),
                rg.Interval(-facade_thickness, facade_thickness),
                rg.Interval(z - window_height / 2, z + window_height / 2)
            ).ToBrep()
            windows.append(window)

    # Subtract windows from the solid facade
    facade_with_voids = rg.Brep.CreateBooleanDifference([solid], windows, 0.01)

    return facade_with_voids

# Example usage:
# facade_geometries = generate_facade_geometry(1.0, 1.0, 2.0)"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(1.5, 0.8, 1.8)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(2.0, 1.2, 2.5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(0.75, 0.6, 1.5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(1.25, 0.7, 2.0)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(1.0, 0.9, 2.2)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
