""" Summary:
The script builds a parametric XZ-plane facade by tiling rectangular modules according to x_size, z_size and module_size. For each grid cell it creates a panel Brep from corner points using Rhino.Geometry. A random draw compared to window_ratio decides if the panel remains solid or becomes a void (windows are produced by omitting that panel). Random.seed(42) makes distributions reproducible. Multiple sample facades with different dimensions and window ratios are generated, collected into lists, and converted into a Grasshopper DataTree via ghpythonlib.treehelpers for downstream use. Parameters thus control scale, rhythm, and porosity of the architectural facade, allowing quick iteration and material exploration."""

#! python 3
function_code = """def create_facade_geometry(x_size, z_size, module_size, window_ratio):
    \"""
    Generate a parametrically designed facade geometry on the XZ plane.

    The facade is composed of modular panels, with a variable distribution of 
    solid and void (window) elements, controlled by a specified window ratio.

    Parameters:
    x_size (float): The total width of the facade in meters.
    z_size (float): The total height of the facade in meters.
    module_size (float): The size of each panel/module in meters.
    window_ratio (float): The ratio of window area to the total panel area (0 to 1).

    Returns:
    list: A list containing Rhino.Geometry.Brep objects that constitute 
          the facade geometry.
    \"""
    import Rhino.Geometry as rg
    import random

    # Set a seed for randomness
    random.seed(42)

    # Calculate number of modules in x and z directions
    num_modules_x = int(x_size // module_size)
    num_modules_z = int(z_size // module_size)

    # List to store facade geometry
    facade_geometry = []

    # Create modules
    for i in range(num_modules_x):
        for j in range(num_modules_z):
            # Create panel at position (i, j)
            x_origin = i * module_size
            z_origin = j * module_size
            panel_corners = [
                rg.Point3d(x_origin, 0, z_origin),
                rg.Point3d(x_origin + module_size, 0, z_origin),
                rg.Point3d(x_origin + module_size, 0, z_origin + module_size),
                rg.Point3d(x_origin, 0, z_origin + module_size)
            ]
            panel = rg.Brep.CreateFromCornerPoints(panel_corners[0], panel_corners[1],
                                                   panel_corners[2], panel_corners[3], 0.01)

            # Determine if this panel is a window based on window_ratio
            if random.random() > window_ratio:
                # Add solid panel to geometry
                facade_geometry.append(panel)
            else:
                # Create a window (void) by not adding to the facade_geometry
                pass

    return facade_geometry"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = create_facade_geometry(12.0, 6.0, 1.5, 0.4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = create_facade_geometry(20.0, 10.0, 1.25, 0.3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = create_facade_geometry(18.0, 9.0, 1.5, 0.45)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = create_facade_geometry(16.0, 8.0, 1.25, 0.5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = create_facade_geometry(24.0, 12.0, 2.0, 0.35)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
