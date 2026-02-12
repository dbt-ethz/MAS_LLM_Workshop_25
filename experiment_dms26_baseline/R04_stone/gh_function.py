""" Summary:
The script builds a facade on the XZ plane by tiling rectangular modules across width and height using module_size to compute rows and columns. For each module it places corner points, makes a polyline, and converts that loop into a planar Brep panel. A random seed and window_ratio control which modules become voids: panels are added only when random.random() exceeds the window_ratio, producing randomized window placement. The function returns a list of panel Breps. The wrapper runs the generator with five parameter sets, collecting results into a Grasshopper DataTree for visualization; material and reference image mapping are not implemented here."""

#! python 3
function_code = """def generate_facade_geom(width, height, module_size, window_ratio):
    \"""
    Generate a facade geometry on the XZ plane.

    This function designs a facade by creating a grid of modular panels on the XZ plane,
    where a specified ratio of these panels are removed to simulate windows.

    Parameters:
    width (float): Total width of the facade in meters.
    height (float): Total height of the facade in meters.
    module_size (float): Size of each module in meters.
    window_ratio (float): Ratio of modules to remove for windows (0 to 1).

    Returns:
    List[Rhino.Geometry.Brep]: A list of Breps representing the facade panels.
    \"""
    import Rhino
    import random
    random.seed(42)

    # Create a list to store panel geometries
    panels = []

    # Calculate grid dimensions
    num_cols = int(width / module_size)
    num_rows = int(height / module_size)

    # Create the grid
    for row in range(num_rows):
        for col in range(num_cols):
            # Determine the base point for each module
            base_x = col * module_size
            base_z = row * module_size

            # Define the corners of each panel
            corners = [
                Rhino.Geometry.Point3d(base_x, 0, base_z),
                Rhino.Geometry.Point3d(base_x + module_size, 0, base_z),
                Rhino.Geometry.Point3d(base_x + module_size, 0, base_z + module_size),
                Rhino.Geometry.Point3d(base_x, 0, base_z + module_size),
                Rhino.Geometry.Point3d(base_x, 0, base_z)  # Closing the loop
            ]

            # Create a polyline from corner points
            polyline = Rhino.Geometry.Polyline(corners)

            # Create a planar surface from the polyline
            surface = Rhino.Geometry.Brep.CreatePlanarBreps(polyline.ToNurbsCurve())

            # Check if surface creation was successful
            if surface:
                # Randomly determine if this panel is a window (void)
                if random.random() > window_ratio:
                    # Add the surface to the panel list (if not a window)
                    panels.append(surface[0])

    return panels"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geom(20.0, 10.0, 1.0, 0.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geom(30.0, 12.0, 0.75, 0.3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geom(18.0, 9.0, 0.9, 0.2)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geom(25.0, 8.0, 0.5, 0.15)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geom(16.0, 11.2, 0.8, 0.35)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
