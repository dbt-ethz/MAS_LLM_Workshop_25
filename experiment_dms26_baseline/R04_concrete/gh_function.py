""" Summary:
This script defines generate_facade_geometry(...) to create a modular facade on the XZ plane by instancing rectangular modules across a grid. Using module_width, module_height, module_depth and module counts along X and Z, it iterates i and j to compute module positions. With a fixed random seed (42) each grid cell has a 70% chance to become a solid; solids are built as Rhino Boxes from two corner Point3d coordinates (y used for depth) and converted to Breps. The main block calls the function with five parameter sets, collects resulting Breps into lists, and converts samples into a Grasshopper DataTree for workflows."""

#! python 3
function_code = """def generate_facade_geometry(module_width, module_height, module_depth, num_modules_x, num_modules_z):
    \"""
    Generates a 3D facade geometry based on a modular system.

    This function creates a facade on the XZ plane using modules made of the specified material,
    translating the design concept into a pattern of solid modules and voids.

    Parameters:
    - module_width: float, width of a single module in meters.
    - module_height: float, height of a single module in meters.
    - module_depth: float, depth of a single module in meters.
    - num_modules_x: int, number of modules along the X-axis.
    - num_modules_z: int, number of modules along the Z-axis.
    
    Returns:
    - A list of Rhino.Geometry.Brep objects representing the facade.

    \"""

    import Rhino.Geometry as rg
    import random
    
    random.seed(42)
    modules = []
    
    for i in range(num_modules_x):
        for j in range(num_modules_z):
            x = i * module_width
            z = j * module_height
            
            # Randomly decide if this module is a solid or a void
            if random.random() < 0.7:  # 70% chance of a solid
                corner1 = rg.Point3d(x, 0, z)
                corner2 = rg.Point3d(x + module_width, module_depth, z + module_height)
                box = rg.Box(rg.BoundingBox(corner1, corner2))
                brep = box.ToBrep()
                modules.append(brep)

    return modules"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(1.0, 1.5, 0.2, 10, 5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(0.8, 1.8, 0.25, 12, 6)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(1.2, 2.4, 0.15, 15, 8)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(0.6, 1.2, 0.18, 18, 7)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(0.9, 2.0, 0.22, 14, 10)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
