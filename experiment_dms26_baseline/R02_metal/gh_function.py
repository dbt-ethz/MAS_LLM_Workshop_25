""" Summary:
The script defines generate_facade(...) that tiles a rectangular facade area with modular box elements aligned to the XZ plane. It computes module counts from width/height and iterates a grid; each cell has an 80% chance to place a module, creating a Rhino.Box whose intervals map X (horizontal), Y (negative depth) and Z (vertical) so boxes extrude into the facade. Random seed ensures repeatable variation. The function returns Brep boxes. The top-level code calls generate_facade with different parameters to produce five sample states, collects them into lists, and converts them into a Grasshopper DataTree for downstream use in Rhino/Grasshopper and visualization."""

#! python 3
function_code = """def generate_facade(width, height, depth, module_size, random_seed=42):
    \"""
    Generates a 3D facade geometry on the XZ plane based on a modular design concept.
    
    Args:
        width (float): Total width of the facade.
        height (float): Total height of the facade.
        depth (float): Depth of the facade elements.
        module_size (float): Size of the modular units that make up the facade.
        random_seed (int, optional): Seed for randomization. Default is 42.
    
    Returns:
        list: A list of Brep geometry objects representing the facade.
    \"""
    import Rhino.Geometry as rg
    import random
    
    random.seed(random_seed)
    facade_geometry = []

    num_modules_x = int(width // module_size)
    num_modules_z = int(height // module_size)

    for i in range(num_modules_x):
        for j in range(num_modules_z):
            # Randomly decide to place a module or leave a void
            if random.random() > 0.2:  # 80% chance to place a module
                x = i * module_size
                z = j * module_size
                box = rg.Box(rg.Plane.WorldXY, 
                             rg.Interval(x, x + module_size), 
                             rg.Interval(-depth, 0), 
                             rg.Interval(z, z + module_size))
                facade_geometry.append(box.ToBrep())
    
    return facade_geometry"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade(12.0, 6.0, 0.3, 0.6, random_seed=101)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade(15.0, 7.5, 0.25, 0.5, random_seed=2024)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade(10.0, 4.0, 0.4, 0.5, random_seed=7)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade(20.0, 8.0, 0.35, 0.8, random_seed=12345)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade(18.0, 9.0, 0.2, 0.75, random_seed=314)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
