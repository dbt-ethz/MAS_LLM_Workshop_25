""" Summary:
The script defines generate_facade_geometry(module_width=2.0, module_height=3.0, rows=5, columns=3) which builds a modular grid on the XZ plane. For each row and column it computes four corner Point3d with Y=0, alternates solid versus void using (r+c)%2, and constructs rectangular Breps via Rhino.Geometry.Brep.CreateFromCornerPoints. Solid modules are appended to facade_geometry and returned as a list of Breps. The script seeds random for reproducibility, then calls the function five times with different module sizes and grid counts, collecting results into geometry_states. Finally it converts the list to a Grasshopper DataTree and exported for visualization or fabrication purposes."""

#! python 3
function_code = """def generate_facade_geometry(module_width=2.0, module_height=3.0, rows=5, columns=3):
    \"""
    Generates a facade geometry on the XZ plane, based on a modular grid system.

    Parameters:
    - module_width (float): The width of each module in meters.
    - module_height (float): The height of each module in meters.
    - rows (int): The number of rows of modules.
    - columns (int): The number of columns of modules.

    Returns:
    - List[Rhino.Geometry.Brep]: A list of breps representing the facade.

    The function creates a grid of modules with specified width and height,
    forming a facade on the XZ plane. Each module can represent a facade panel
    or a void, achieving a facade pattern using modularity.
    \"""
    import Rhino
    import random
    random.seed(42)  # Ensures replicability

    facade_geometry = []
    for r in range(rows):
        for c in range(columns):
            # Alternate between solid and void based on position
            if (r + c) % 2 == 0:
                # Create a rectangular surface for solid parts
                pt1 = Rhino.Geometry.Point3d(c * module_width, 0, r * module_height)
                pt2 = Rhino.Geometry.Point3d((c + 1) * module_width, 0, r * module_height)
                pt3 = Rhino.Geometry.Point3d((c + 1) * module_width, 0, (r + 1) * module_height)
                pt4 = Rhino.Geometry.Point3d(c * module_width, 0, (r + 1) * module_height)

                # Create a polyline and a surface
                polyline = Rhino.Geometry.Polyline([pt1, pt2, pt3, pt4, pt1])
                surface = Rhino.Geometry.Brep.CreateFromCornerPoints(pt1, pt2, pt3, pt4, 0.01)
                if surface:
                    facade_geometry.append(surface)

    return facade_geometry"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(module_width=1.5, module_height=2.7, rows=4, columns=6)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(module_width=2.5, module_height=3.2, rows=6, columns=8)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(module_width=1.8, module_height=2.4, rows=8, columns=5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(module_width=2.2, module_height=3.5, rows=7, columns=4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(module_width=3.0, module_height=1.8, rows=9, columns=3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
