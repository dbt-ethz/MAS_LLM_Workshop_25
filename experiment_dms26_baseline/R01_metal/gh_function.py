""" Summary:
The script builds a façade on the XZ plane by iterating a grid of cells defined by column and row counts and cell dimensions. For each cell it creates an outer box at grid positions, then picks a random depth from a seeded range to vary relief. An inner smaller box offset by base_thickness forms a cavity; a boolean difference subtracts the inner from the outer box to produce a framed opening. Successful Breps are collected in a list. The code runs the function with different parameters, creating multiple façade variants and converting them into a Grasshopper DataTree for export."""

#! python 3
function_code = """def create_facade_geometry(x_count, y_count, cell_width, cell_height, random_seed):
    \"""
    Generate a 3D geometry for a facade on the XZ plane.

    The facade is comprised of a grid of rectangular openings resembling windows, defined by the number
    of columns and rows, along with the dimensions of each cell. Randomness is applied
    to vary the depth of the openings.

    Parameters:
    - x_count: The number of columns in the facade grid.
    - y_count: The number of rows in the facade grid.
    - cell_width: The width of each cell in the grid.
    - cell_height: The height of each cell in the grid.
    - random_seed: The seed for randomization to vary the depth uniformly.

    Returns:
    - A list of Breps representing the facade geometry, with varying depths.
    \"""

    import Rhino.Geometry as rg
    import random

    # Set the random seed for reproducibility
    random.seed(random_seed)
    
    # Define parameters
    facade_depth_min = 0.3
    facade_depth_max = 1.0
    base_thickness = 0.1

    # Initialize list to store geometry
    facade_geometries = []

    # Iterate over grid and create facade elements
    for i in range(x_count):
        for j in range(y_count):
            # Calculate cell origin
            origin = rg.Point3d(i * cell_width, 0, j * cell_height)
            
            # Create a box for each cell
            cell_depth = random.uniform(facade_depth_min, facade_depth_max)
            box = rg.Box(rg.Plane(origin, rg.Vector3d.XAxis, rg.Vector3d.ZAxis), rg.Interval(0, cell_width), rg.Interval(0, cell_depth), rg.Interval(0, cell_height))
            
            # Create opening by subtracting
            inner_box = rg.Box(rg.Plane(origin, rg.Vector3d.XAxis, rg.Vector3d.ZAxis), rg.Interval(base_thickness, cell_width - base_thickness), rg.Interval(0, cell_depth), rg.Interval(base_thickness, cell_height - base_thickness))
            boolean_difference = rg.Brep.CreateBooleanDifference([box.ToBrep()], [inner_box.ToBrep()], 0.01)

            # If boolean operation is successful, append result
            if boolean_difference:
                facade_geometries.append(boolean_difference[0])

    return facade_geometries"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = create_facade_geometry(10, 5, 1.2, 2.4, 42)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = create_facade_geometry(8, 6, 1.1, 2.5, 2026)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = create_facade_geometry(12, 7, 1.25, 2.0, 314159)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = create_facade_geometry(15, 4, 1.0, 2.8, 12345)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = create_facade_geometry(9, 8, 1.0, 2.2, 7777)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
