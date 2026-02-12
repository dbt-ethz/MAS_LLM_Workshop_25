""" Summary:
The script defines generate_facade_geometry(...), which builds a grid of rectangular panels on the XZ plane. For each panel cell it computes base x and z positions from panel dimensions and indices, applies small random scale offsets (controlled by random_seed) to width and height, and constructs four Rhino.Geometry.Point3d corner points. Each panel becomes a planar Brep via Rhino.Geometry.Brep.CreateFromCornerPoints and is appended to geometries. The main block calls the function with five different parameter sets, collecting results into geometry_states, converts them to a Grasshopper DataTree with ghpythonlib.treehelpers for output, and prints success. Random seed ensures repeatable variation and supports quick facade iterations."""

#! python 3
function_code = """def generate_facade_geometry(panel_width, panel_height, num_panels_x, num_panels_z, random_seed):
    \"""
    Generates a 3D facade geometry on the XZ plane, consisting of rectangular panels.

    The facade consists of a grid of rectangular panels, with customizable dimensions and
    the ability to introduce randomness in panel arrangement or scaling.

    Parameters:
    - panel_width (float): The width of each panel in meters.
    - panel_height (float): The height of each panel in meters.
    - num_panels_x (int): The number of panels in the horizontal direction (X-axis).
    - num_panels_z (int): The number of panels in the vertical direction (Z-axis).
    - random_seed (int): A seed for randomness to ensure replicability of variations.

    Returns:
    - list: A list of Rhino.Geometry.Brep objects representing the facade geometry.
    \"""
    import Rhino
    import random
    random.seed(random_seed)

    geometries = []
    
    # Random factor to introduce slight variations
    scale_variation = 0.1

    for i in range(num_panels_x):
        for j in range(num_panels_z):
            x = i * panel_width
            z = j * panel_height

            # Introduce minor random scaling to panels for variation
            scale_x = 1 + random.uniform(-scale_variation, scale_variation)
            scale_z = 1 + random.uniform(-scale_variation, scale_variation)

            corners = [
                Rhino.Geometry.Point3d(x, 0, z),
                Rhino.Geometry.Point3d(x + panel_width * scale_x, 0, z),
                Rhino.Geometry.Point3d(x + panel_width * scale_x, 0, z + panel_height * scale_z),
                Rhino.Geometry.Point3d(x, 0, z + panel_height * scale_z)
            ]

            # Create a planar surface for each panel
            panel_brep = Rhino.Geometry.Brep.CreateFromCornerPoints(corners[0], corners[1], corners[2], corners[3], 0.01)
            
            if panel_brep:
                geometries.append(panel_brep)

    return geometries"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(1.2, 2.4, 10, 6, 42)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(0.9, 2.2, 12, 5, 2021)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(1.0, 2.5, 8, 7, 12345)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(1.5, 3.0, 15, 4, 777)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(1.25, 2.7, 18, 9, 31415)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
