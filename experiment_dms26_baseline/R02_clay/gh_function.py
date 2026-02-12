""" Summary:
The script defines generate_facade(width, height, depth, module_count, void_ratio) which tiles the XZ plane into a module_count×module_count grid by computing module_width = width/module_count and module_height = height/module_count. For each grid cell it seeds the RNG and uses a random test against void_ratio to decide whether to create a solid module or leave a void. Solid modules are created as Rhino.Geometry.Box instances positioned at (x_start, depth/2, z_start) with their thickness along Y equal to depth, then converted to Breps. The main section produces five sample facades with varying parameters and packs the resulting Brep lists into a Grasshopper DataTree for output structure."""

#! python 3
function_code = """def generate_facade(width, height, depth, module_count, void_ratio):
    \"""
    Generates a 3D geometry representing a facade on the XZ plane.

    Parameters:
    width (float): The total width of the facade.
    height (float): The total height of the facade.
    depth (float): The depth of the facade elements.
    module_count (int): The number of modules along the width.
    void_ratio (float): The ratio of voids to solids within the facade modules.

    Returns:
    list: A list of Brep geometries representing the facade.
    \"""
    import Rhino.Geometry as rg
    import random
    
    random.seed(42)
    
    breps = []
    module_width = width / module_count
    module_height = height / module_count
    
    for i in range(module_count):
        for j in range(module_count):
            x_start = i * module_width
            z_start = j * module_height
            if random.random() > void_ratio:
                # Create a solid module
                solid = rg.Box(
                    rg.Plane(rg.Point3d(x_start, depth / 2, z_start), rg.Vector3d.YAxis),
                    rg.Interval(0, module_width),
                    rg.Interval(0, depth),
                    rg.Interval(0, module_height)
                )
                breps.append(solid.ToBrep())
            else:
                # Create a void module (skip adding the geometry to the list)
                pass
                
    return breps"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade(12.0, 6.0, 0.5, 12, 0.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade(18.0, 9.0, 0.6, 9, 0.35)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade(20.0, 10.0, 0.8, 10, 0.15)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade(16.0, 8.0, 0.3, 8, 0.4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade(24.0, 12.0, 0.4, 6, 0.2)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
