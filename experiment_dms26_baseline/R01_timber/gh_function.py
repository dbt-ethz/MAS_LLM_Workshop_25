""" Summary:
The script defines a parametric function create_facade_geometry(module_width=1.0, module_height=2.5, rows=4, columns=6) that generates a facade on the XZ plane (y=0) by tiling rectangular modules. For each row and column it computes module corner points, builds a polyline perimeter, converts it to a planar Brep via Rhino.Geometry, and appends it to a list. The script then instantiates five sample facades with varied module sizes and grid counts, collects them, and converts the results into a Grasshopper DataTree for downstream use. Note: the code produces geometry only; neither the reference image nor material selection is interpreted. Material assignment and image-driven modulation are absent."""

#! python 3
function_code = """def create_facade_geometry(module_width=1.0, module_height=2.5, rows=4, columns=6):
    \"""
    Generates a parametric 3D facade geometry on the XZ plane using modular design.

    The facade consists of repeated modules represented as rectangular Breps. The size
    of each module and the number of rows and columns are defined by the input parameters.

    Parameters:
    - module_width: float, width of each module in meters.
    - module_height: float, height of each module in meters.
    - rows: int, number of vertical modules.
    - columns: int, number of horizontal modules.

    Returns:
    - List of Breps: A list of Brep objects representing the facade geometry.
    \"""
    import Rhino.Geometry as rg

    facade = []
    # Loop through each row and column to create the facade grid
    for row in range(rows):
        for col in range(columns):
            # Calculate the corner point for each module
            x = col * module_width
            z = row * module_height
            # Create a rectangular plane for each module
            pt1 = rg.Point3d(x, 0, z)
            pt2 = rg.Point3d(x + module_width, 0, z)
            pt3 = rg.Point3d(x + module_width, 0, z + module_height)
            pt4 = rg.Point3d(x, 0, z + module_height)
            # Create edges and brep
            edge1 = rg.Line(pt1, pt2)
            edge2 = rg.Line(pt2, pt3)
            edge3 = rg.Line(pt3, pt4)
            edge4 = rg.Line(pt4, pt1)
            polyline = rg.Polyline([edge1.From, edge2.From, edge3.From, edge4.From, edge1.To])
            perimeter_curve = polyline.ToNurbsCurve()
            brep = rg.Brep.CreatePlanarBreps(perimeter_curve)[0]
            facade.append(brep)
            
    return facade"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = create_facade_geometry(module_width=1.5, module_height=3.0, rows=4, columns=8)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = create_facade_geometry(module_width=1.2, module_height=2.8, rows=5, columns=7)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = create_facade_geometry(module_width=0.9, module_height=2.4, rows=6, columns=5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = create_facade_geometry(module_width=1.8, module_height=2.6, rows=8, columns=4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = create_facade_geometry(module_width=2.0, module_height=3.5, rows=3, columns=10)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
