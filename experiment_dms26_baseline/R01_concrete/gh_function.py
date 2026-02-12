""" Summary:
The script defines generate_facade_geometry(width, height, depth, module_size, void_ratio, material_property), which builds a grid of box modules on the XZ plane using Rhino.Geometry. Rows and columns derive from facade dimensions divided by module_size. A seeded random generator decides per module whether to place a solid box or leave a void according to void_ratio. Boxes are created as Breps spanning module_size in X and Z and depth in Y. The function returns a list of Breps. The wrapper calls it five times with different parameters and material_property keywords, collects results into geometry_states, and converts them into a Grasshopper DataTree for output successfully."""

#! python 3
function_code = """def generate_facade_geometry(width, height, depth, module_size, void_ratio, material_property):
    \"""
    Generate a 3D facade geometry on the XZ plane based on given parameters.

    Args:
    - width (float): Total width of the facade.
    - height (float): Total height of the facade.
    - depth (float): Depth of facade elements.
    - module_size (float): Size of each repeating module.
    - void_ratio (float): Ratio of void spaces to solid spaces in the facade (0 to 1).
    - material_property (str): String representing the type of material characteristic to emphasize (e.g., 'transparency').

    Returns:
    - List[Rhino.Geometry.Brep]: List of Brep geometries representing the facade structure.
    \"""
    import Rhino.Geometry as rg
    import random

    random.seed(42)  # Ensure replicability

    rows = int(height // module_size)
    cols = int(width // module_size)

    geometries = []

    for i in range(rows):
        for j in range(cols):
            # Determine if a void or solid module based on void ratio
            if random.random() > void_ratio:
                # Create a box representing a module
                base = rg.Point3d(j * module_size, 0, i * module_size)
                box = rg.Brep.CreateFromBox(rg.BoundingBox(base, rg.Point3d((j + 1) * module_size, depth, (i + 1) * module_size)))
                geometries.append(box)

    # Additional logic based on material property can be added here

    return geometries"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(12.0, 6.0, 0.3, 0.5, 0.4, 'transparency')
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(18.0, 9.0, 0.25, 0.75, 0.35, 'thermal_performance')
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(24.0, 8.0, 0.35, 0.6, 0.3, 'daylighting')
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(30.0, 12.0, 0.4, 0.6, 0.45, 'solar_shading')
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(10.0, 5.0, 0.2, 0.5, 0.25, 'acoustic_insulation')
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
