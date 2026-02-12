""" Summary:
The script defines generate_facade_geometry(width, height, depth, module_count, offset, seed) which builds a modular grid across the XZ plane by dividing width and height into module_count cells. For each cell it randomly chooses a solid module or a punched (void) module using the seeded RNG for reproducibility. Solids are created by extruding the module rectangle in the Y direction by depth to form a Brep box. Voids are produced by creating an inset inner box and performing a Boolean difference from the outer box, yielding frame-like modules. The wrapper calls this function with parameter sets and converts Breps into a Grasshopper DataTree."""

#! python 3
function_code = """def generate_facade_geometry(width, height, depth, module_count, offset, seed):
    \"""
    Generate a 3D facade geometry on the XZ plane.

    The function creates a modular facade with defined voids and solids that can represent windows
    or structural elements based on a repetitive grid pattern. The modules are determined by a grid 
    structure with specified dimensions and randomness applied to module variations.

    Parameters:
        width (float): Total width of the facade in meters.
        height (float): Total height of the facade in meters.
        depth (float): Depth of each module in meters.
        module_count (int): Number of modules along the width.
        offset (float): Offset distance for voids in modules.
        seed (int): Random seed for replicable variations.

    Returns:
        list: A list of Brep objects representing the facade geometry.
    \"""
    import Rhino.Geometry as rg
    import random
    
    random.seed(seed)
    facade_geometry = []

    module_width = width / module_count
    module_height = height / module_count

    for i in range(module_count):
        for j in range(module_count):
            x = i * module_width
            z = j * module_height
            solid = random.choice([True, False])

            base_point = rg.Point3d(x, 0, z)
            module_corners = [
                base_point,
                rg.Point3d(x + module_width, 0, z),
                rg.Point3d(x + module_width, 0, z + module_height),
                rg.Point3d(x, 0, z + module_height)
            ]

            if solid:
                corners = [rg.Point3d(c.X, c.Y + depth, c.Z) for c in module_corners]
                box_corners = module_corners + corners
                module_brep = rg.Brep.CreateFromBox(rg.Box(rg.Plane.WorldXY, box_corners))
            else:
                inset_x = min(offset, module_width / 2)
                inset_z = min(offset, module_height / 2)
                inner_base_point = rg.Point3d(x + inset_x, 0, z + inset_z)
                inner_corners = [
                    inner_base_point,
                    rg.Point3d(x + module_width - inset_x, 0, z + inset_z),
                    rg.Point3d(x + module_width - inset_x, 0, z + module_height - inset_z),
                    rg.Point3d(x + inset_x, 0, z + module_height - inset_z)
                ]
                inner_corners.extend([rg.Point3d(c.X, c.Y + depth, c.Z) for c in inner_corners])
                
                outer_corners = module_corners + [rg.Point3d(c.X, c.Y + depth, c.Z) for c in module_corners]
                outer_brep = rg.Brep.CreateFromBox(rg.Box(rg.Plane.WorldXY, outer_corners))
                
                inner_brep = rg.Brep.CreateFromBox(rg.Box(rg.Plane.WorldXY, inner_corners))
                boolean_diff = rg.Brep.CreateBooleanDifference([outer_brep], [inner_brep], 0.001)
                if boolean_diff:
                    module_brep = boolean_diff[0]
                else:
                    module_brep = outer_brep

            facade_geometry.append(module_brep)

    return facade_geometry"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(20.0, 10.0, 0.3, 10, 0.2, 123)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(30.5, 12.0, 0.45, 12, 0.1, 42)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(18.0, 9.0, 0.25, 6, 0.2, 2024)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(25.0, 8.5, 0.35, 8, 0.15, 7)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(40.0, 15.0, 0.5, 16, 0.1, 999)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
