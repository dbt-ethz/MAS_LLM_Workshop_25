""" Summary:
The script defines create_facade_geometry(height, width, depth, window_size, brick_size) to produce a parametric facade on the XZ plane. It computes how many modular bricks fit across width and height, then iterates to place Box geometries (Rhino.Geometry.Box) for each brick using X and Z coordinates. For every third brick position ((i+j)%3==0) a window Box is created and positioned centered horizontally with a random vertical offset, acting as a void. Geometries are converted to Breps and returned. A fixed random seed ensures repeatability, and sample facades are generated and assembled into a Grasshopper DataTree for material assignment and downstream use and quick parameter studies."""

#! python 3
function_code = """def create_facade_geometry(height, width, depth, window_size, brick_size):
    \"""
    Generates a parametric 3D facade geometry on the XZ plane.

    This function creates a facade design based on an input height and width, using modular bricks with windows included as voids. 
    The facade is composed of bricks represented as boxes, and regularly spaced windows.

    Parameters:
    - height (float): The total height of the facade in meters.
    - width (float): The total width of the facade in meters.
    - depth (float): The depth/thickness of the facade in meters.
    - window_size (tuple): The size of the windows (width, height) as a tuple.
    - brick_size (tuple): The size of the bricks (width, height, depth) as a tuple.

    Returns:
    - list: A list of 3D Brep geometries representing the facade, including bricks and voids for windows.
    \"""
    
    import Rhino.Geometry as rg
    import random
    
    random.seed(0)  # Ensuring replicability

    facade_geometries = []
    
    brick_w, brick_h, brick_d = brick_size
    window_w, window_h = window_size

    # Calculate number of bricks across width and height
    num_bricks_x = int(width // brick_w)
    num_bricks_z = int(height // brick_h)
    
    # Create bricks
    for i in range(num_bricks_x):
        for j in range(num_bricks_z):
            # Determine position of each brick
            brick_x = i * brick_w
            brick_z = j * brick_h

            # Create brick geometry
            brick = rg.Box(
                rg.Plane(rg.Point3d(brick_x, 0, brick_z), rg.Vector3d.XAxis, rg.Vector3d.ZAxis),
                rg.Interval(0, brick_w), rg.Interval(0, depth), rg.Interval(0, brick_h)
            )
            facade_geometries.append(brick.ToBrep())

            # Create window voids at random intervals
            if (i + j) % 3 == 0:
                window_height_position = random.uniform(0, brick_h - window_h)
                window = rg.Box(
                    rg.Plane(rg.Point3d(brick_x + (brick_w - window_w) / 2, 0, brick_z + window_height_position), rg.Vector3d.XAxis, rg.Vector3d.ZAxis),
                    rg.Interval(0, window_w), rg.Interval(0, depth), rg.Interval(0, window_h)
                )
                facade_geometries.append(window.ToBrep())

    return facade_geometries"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = create_facade_geometry(8.0, 12.0, 0.25, (1.0, 1.2), (0.6, 0.3, 0.25))
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = create_facade_geometry(5.0, 9.0, 0.18, (0.9, 1.1), (0.45, 0.3, 0.18))
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = create_facade_geometry(6.0, 10.0, 0.2, (0.4, 0.25), (0.6, 0.4, 0.2))
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = create_facade_geometry(3.6, 7.2, 0.2, (0.8, 0.5), (0.6, 0.3, 0.2))
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = create_facade_geometry(12.0, 20.0, 0.25, (0.4, 1.0), (0.5, 1.2, 0.25))
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
