""" Summary:
The script defines generate_facade_geometry, which builds a regular XZ grid of box modules using Rhino.Geometry. For each grid cell it computes a base_point at (i*module_size, 0, j*module_size), seeds randomness for reproducibility, and generates a per-module random_factor that scales the box extents. The Box constructor uses intervals to vary the module width and depth (module_size*(1-random_factor)) while keeping vertical size constant. Each box is converted to a Brep and collected. The outer script invokes the function with five parameter sets, collects results into a Grasshopper DataTree, and prints status. Note: the provided code does not apply a reference image or material either."""

#! python 3
function_code = """def generate_facade_geometry(grid_size=10, module_size=1, randomness=0.2):
    \"""
    Generates a 3D geometry representing a facade on the XZ plane.
    
    Parameters:
    grid_size (int): The number of modules in each direction of the grid.
    module_size (float): The size of each grid module.
    randomness (float): A value between 0 and 1 indicating the randomness of the facade pattern.
    
    Returns:
    List of Breps: A list of Brep objects representing the facade geometry.
    \"""
    import Rhino.Geometry as rg
    from random import seed, random
    
    seed(42)  # Ensures that the randomness is replicable
    
    geometries = []
    
    # Iterate through the grid
    for i in range(grid_size):
        for j in range(grid_size):
            # Calculate the base point of the current module
            base_point = rg.Point3d(i * module_size, 0, j * module_size)
            
            # Random factor for creating variance
            random_factor = random() * randomness
            
            # Create a module geometry
            box = rg.Box(rg.Plane(base_point, rg.Vector3d.ZAxis), rg.Interval(0, module_size * (1 - random_factor)), rg.Interval(0, module_size), rg.Interval(0, module_size * (1 - random_factor)))
            
            # Convert to Brep and add to the list
            geometries.append(box.ToBrep())
    
    return geometries"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(grid_size=12, module_size=0.5, randomness=0.3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(grid_size=8, module_size=1.2, randomness=0.45)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(grid_size=16, module_size=0.75, randomness=0.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(grid_size=20, module_size=0.4, randomness=0.15)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(grid_size=6, module_size=2.0, randomness=0.6)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
