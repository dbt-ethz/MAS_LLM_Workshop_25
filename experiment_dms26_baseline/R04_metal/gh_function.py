""" Summary:
The script builds a facade on the XZ plane by tiling a grid of modules sized by module_size across width and height. For each grid cell it uses a seeded random test against pattern_density to decide whether to place a solid module or leave a void. Solid modules are created as Rhino Boxes using intervals for X, Y (depth) and Z extents, converted to Breps and collected. The function returns a list of Breps representing the facade. The wrapper runs the generator with varied parameters to create multiple facade states, then converts them into a Grasshopper DataTree for downstream visualization."""

#! python 3
function_code = """def generate_facade_geometry(width, height, depth, module_size, pattern_density):
    \"""
    Generates a 3D facade geometry on the XZ plane.

    The facade is composed of a series of repeating modules with voids, arranged
    according to a specified pattern density. The geometry resembles a facade 
    system built with a selected material.

    Parameters:
    - width (float): Total width of the facade in meters.
    - height (float): Total height of the facade in meters.
    - depth (float): Depth of the facade elements in meters.
    - module_size (float): Size of each repeating module.
    - pattern_density (float): Density of voids in the facade pattern (0 to 1).

    Returns:
    - List[Rhino.Geometry.Brep]: List of 3D geometry objects representing the facade.
    \"""
    import Rhino
    import random
    random.seed(42)

    breps = []
    num_x = int(width / module_size)
    num_z = int(height / module_size)

    for i in range(num_x):
        for j in range(num_z):
            # Calculate 3D point coordinates
            x = i * module_size
            z = j * module_size
            # Determine whether to create a void or solid
            if random.random() > pattern_density:
                # Define base point and vector
                base_point = Rhino.Geometry.Point3d(x, 0, z)
                x_interval = Rhino.Geometry.Interval(x, x + module_size)
                y_interval = Rhino.Geometry.Interval(0, depth)
                z_interval = Rhino.Geometry.Interval(z, z + module_size)

                # Create box using intervals
                box = Rhino.Geometry.Box(Rhino.Geometry.Plane.WorldXY, x_interval, y_interval, z_interval)
                brep = box.ToBrep()
                breps.append(brep)

    return breps"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(12.0, 6.0, 0.25, 0.5, 0.35)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(15.0, 8.0, 0.2, 0.5, 0.45)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(18.0, 7.2, 0.25, 0.6, 0.3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(9.0, 3.6, 0.2, 0.3, 0.4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(24.0, 12.0, 0.18, 0.6, 0.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
