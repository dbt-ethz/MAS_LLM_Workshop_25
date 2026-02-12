""" Summary:
The script defines generate_facade_geometry to create a row of panels along the X axis on the XZ plane. For each panel it computes corner Point3d coordinates, builds a rectangular polyline converted to a NURBS curve, and—unless randomized as an opening—creates a NURBS surface converted to a Brep. Random.opening decisions use opening_frequency with a fixed seed for reproducibility. The function returns a list of Breps representing solid panels. The outer code calls this function five times with different parameters, collects the resulting geometry states and converts them into a Grasshopper DataTree for downstream use in Rhino/Grasshopper and visualization or fabrication workflows."""

#! python 3
function_code = """def generate_facade_geometry(panel_count=5, panel_width=1.0, panel_height=3.0, opening_frequency=0.5):
    \"""
    Generate facade geometry on the XZ plane.

    This function creates a series of panels representing a facade.
    The facade consists of solid and open panels, simulating windows or voids.

    Parameters:
    panel_count (int): The number of panels in the facade.
    panel_width (float): The width of each panel.
    panel_height (float): The height of each panel.
    opening_frequency (float): The probability of a panel being a window (0 to 1).

    Returns:
    List[Brep]: List of Breps representing the facade panels.
    \"""
    import Rhino
    import random
    random.seed(42)

    facade_panels = []
    for i in range(panel_count):
        x_start = i * panel_width
        opening = random.random() < opening_frequency
        
        # Define corner points of the panel
        panel_pts = [
            Rhino.Geometry.Point3d(x_start, 0, 0),
            Rhino.Geometry.Point3d(x_start + panel_width, 0, 0),
            Rhino.Geometry.Point3d(x_start + panel_width, 0, panel_height),
            Rhino.Geometry.Point3d(x_start, 0, panel_height)
        ]
        
        # Create a rectangle for the panel
        panel_curve = Rhino.Geometry.Polyline(panel_pts + [panel_pts[0]]).ToNurbsCurve()
        
        # Only create a solid panel if not an opening
        if not opening:
            panel_brep = Rhino.Geometry.Brep.CreateFromSurface(Rhino.Geometry.NurbsSurface.CreateFromCorners(*panel_pts))
            facade_panels.append(panel_brep)
    
    return facade_panels"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(panel_count=12, panel_width=1.5, panel_height=3.0, opening_frequency=0.4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(panel_count=10, panel_width=1.2, panel_height=2.8, opening_frequency=0.6)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(panel_count=8, panel_width=2.0, panel_height=4.0, opening_frequency=0.3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(panel_count=15, panel_width=0.9, panel_height=2.5, opening_frequency=0.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(panel_count=20, panel_width=0.85, panel_height=3.2, opening_frequency=0.45)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
