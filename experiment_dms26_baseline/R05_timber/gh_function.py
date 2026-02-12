""" Summary:
The script defines create_facade_geometry(module_size, num_modules, pattern_variation) which builds a grid of modular boxes on the XZ plane. It iterates i,j over num_modules, computes module centers on X (center_x) and Z (center_z), sets a base plane with that origin, and uses Rhino.Geometry.Box with intervals sized by module_size to create Brep modules that extrude in Y, forming solid panels. A fixed Random(42) seed and pattern_variation control probabilistic voids: if random.NextDouble() > pattern_variation a box is created, otherwise the cell is left empty, producing porosity. Multiple parameter sets generate alternative facade states returned as Breps and packed into a Grasshopper DataTree for visualization purposes."""

#! python 3
function_code = """def create_facade_geometry(module_size=1.0, num_modules=5, pattern_variation=0.2):
    \"""
    Generates a 3D facade geometry on the XZ plane, representing a facade system
    based on modular elements and specified material characteristics.

    Parameters:
    - module_size (float): The size of each module side in meters.
    - num_modules (int): The number of modules horizontally.
    - pattern_variation (float): A factor for varying the pattern density.

    Returns:
    - List of Breps: A list of Brep geometries representing the facade.
    \"""
    import Rhino.Geometry as rg
    from System import Random

    # Initialize random generator
    random = Random(42)
    
    facade_breps = []

    for i in range(num_modules):
        # Vary the pattern of the facade
        for j in range(num_modules):
            # Calculate the center of each module
            center_x = i * module_size
            center_z = j * module_size
            
            # Create a base plane for each module
            base_plane = rg.Plane.WorldXY
            base_plane.Origin = rg.Point3d(center_x, 0, center_z)

            # Randomly decide whether to create a void or a solid
            if random.NextDouble() > pattern_variation:
                # Create a solid module
                module = rg.Box(base_plane,
                                rg.Interval(0, module_size),
                                rg.Interval(-module_size, 0),
                                rg.Interval(0, module_size)).ToBrep()
                facade_breps.append(module)
            else:
                # Potential space for a void (no module added)
                continue

    return facade_breps"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = create_facade_geometry(module_size=1.0, num_modules=6, pattern_variation=0.15)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = create_facade_geometry(module_size=0.75, num_modules=12, pattern_variation=0.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = create_facade_geometry(module_size=1.25, num_modules=8, pattern_variation=0.18)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = create_facade_geometry(module_size=0.5, num_modules=10, pattern_variation=0.3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = create_facade_geometry(module_size=1.8, num_modules=9, pattern_variation=0.12)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
