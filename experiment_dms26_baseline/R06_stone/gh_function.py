""" Summary:
The script defines generate_facade_geometry which produces a repeating panel system on the XZ plane. For each panel it computes x_position using panel_width and gap, defines four corner Point3d with Y=0 (placing geometry on XZ), builds a closed polyline, and converts it to a planar Brep via Rhino.Geometry. Parameters (panel_count, panel_width, panel_height, gap) control layout and proportions. The top-level code runs five sample configurations, collects their Breps into lists, and converts them to a Grasshopper DataTree for downstream use. The script does not apply material or use the reference image directly; material assignment would be handled separately."""

#! python 3
function_code = """def generate_facade_geometry(panel_count=5, panel_width=2, panel_height=3, gap=0.2):
    \"""
    Generate a facade geometry on the XZ plane with a repeating panel system.
    
    Parameters:
    - panel_count (int): The number of panels in the facade.
    - panel_width (float): The width of each panel.
    - panel_height (float): The height of each panel.
    - gap (float): The gap between adjacent panels.

    Returns:
    - List[Rhino.Geometry.Brep]: A list of Brep objects representing the facade panels.
    \"""
    import Rhino.Geometry as rg
    
    geometries = []
    
    for i in range(panel_count):
        # Calculate the x position of the panel
        x_position = i * (panel_width + gap)
        
        # Create the corner points of the panel
        p0 = rg.Point3d(x_position, 0, 0)
        p1 = rg.Point3d(x_position + panel_width, 0, 0)
        p2 = rg.Point3d(x_position + panel_width, 0, panel_height)
        p3 = rg.Point3d(x_position, 0, panel_height)
        
        # Create the panel surface
        polyline = rg.Polyline([p0, p1, p2, p3, p0])
        panel_surface = rg.Brep.CreatePlanarBreps(polyline.ToNurbsCurve())[0]
        
        geometries.append(panel_surface)
    
    return geometries"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(panel_count=10, panel_width=1.8, panel_height=3.5, gap=0.15)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(panel_count=8, panel_width=2.5, panel_height=4.0, gap=0.1)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(panel_count=6, panel_width=3.0, panel_height=2.5, gap=0.05)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(panel_count=12, panel_width=1.2, panel_height=2.8, gap=0.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(panel_count=15, panel_width=1.5, panel_height=3.2, gap=0.12)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
