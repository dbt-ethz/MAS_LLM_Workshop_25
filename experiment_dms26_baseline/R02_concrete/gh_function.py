""" Summary:
The script defines generate_facade_geometry to create a modular facade on the XZ plane by tiling rectangular panels. Given panel_width, panel_height, num_columns and num_rows it loops across columns and rows, computing corner Point3d coordinates for each panel and building planar Breps via rg.Brep.CreateFromCornerPoints. Each Brep is appended to a list returned as the facade geometry. The outer code executes multiple sample calls with different dimensions to produce five design variations, collects them in geometry_states, converts that list into a Grasshopper DataTree using ghpythonlib.treehelpers, and prints success or an error message. Materials and opacity are implied by solid panels but not assigned."""

#! python 3
function_code = """def generate_facade_geometry(panel_width, panel_height, num_columns, num_rows):
    \"""
    Generate a 3D facade geometry on the XZ plane.

    This function creates a facade system based on grid-like panels,
    simulating a modular pattern. The facade is composed of rectangular panels 
    repeated along the X and Z axes, forming a grid. Each panel can be a solid,
    representing an opaque material.

    Parameters:
    - panel_width (float): The width of each panel on the X-axis.
    - panel_height (float): The height of each panel on the Z-axis.
    - num_columns (int): The number of panels along the X-axis.
    - num_rows (int): The number of panels along the Z-axis.
    
    Returns:
    - List[Rhino.Geometry.Brep]: A list of breps representing the facade panels.
    \"""
    import Rhino.Geometry as rg

    facade_panels = []
    
    for i in range(num_columns):
        for j in range(num_rows):
            origin = rg.Point3d(i * panel_width, 0, j * panel_height)
            panel_corners = [
                origin,
                rg.Point3d(origin.X + panel_width, origin.Y, origin.Z),
                rg.Point3d(origin.X + panel_width, origin.Y, origin.Z + panel_height),
                rg.Point3d(origin.X, origin.Y, origin.Z + panel_height)
            ]
            panel_surface = rg.Brep.CreateFromCornerPoints(panel_corners[0], panel_corners[1], panel_corners[2], panel_corners[3], 0.001)
            facade_panels.append(panel_surface)
    
    return facade_panels"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(1.2, 2.4, 8, 5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(0.75, 2.2, 10, 6)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(1.5, 2.8, 9, 7)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(0.9, 2.6, 12, 4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(1.1, 2.5, 7, 10)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
