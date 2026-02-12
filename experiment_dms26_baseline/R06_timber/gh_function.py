""" Summary:
The script builds a parametric facade on the XZ plane by tiling rectangular modules in a grid. For each module the loops compute X and Z offsets from module_width, module_height and grid_spacing, place a Plane at (x,0,z) oriented by X and Z axes, then create an rg.Box with width, depth (material-driven thickness) and height. Material selection sets the box thickness (concrete, wood, default), and a fixed random seed is set for reproducibility. Boxes are converted to Breps and collected. Sample calls produce multiple facade variants that are packed into a Grasshopper DataTree for downstream use and exported to modeling environment."""

#! python 3
function_code = """def generate_facade_geometry(material, module_width=1.0, module_height=2.5, grid_spacing=0.5):
    \"""
    Generates a parametric 3D facade geometry on the XZ plane.

    The function creates a facade system based on a grid of modules
    that can be customized according to the chosen material's attributes.

    Parameters:
        material (str): The type of material which affects the facade's thickness.
        module_width (float): The width of each module in the facade.
        module_height (float): The height of each module in the facade.
        grid_spacing (float): The spacing between the modules.

    Returns:
        List[Rhino.Geometry.Brep]: A list of Brep geometries representing the facade.

    Note:
        The dimensions in the modeling space are in meters. ZAxis represents height, 
        XAxis represents width, and YAxis represents depth.
    \"""
    import Rhino.Geometry as rg
    import random

    random.seed(42)  # Ensures replicable randomness

    # Assign thickness based on material
    if material == "concrete":
        thickness = 0.2
    elif material == "wood":
        thickness = 0.1
    else:
        thickness = 0.15  # Default for other materials

    num_modules_x = 10  # Number of modules in the X direction
    num_modules_z = 4   # Number of modules in the Z direction

    geometries = []

    # Create modules in a grid pattern
    for i in range(num_modules_x):
        for j in range(num_modules_z):
            x = i * (module_width + grid_spacing)
            z = j * (module_height + grid_spacing)
            
            # Create a basic box for each module
            base_point = rg.Point3d(x, 0, z)
            box = rg.Box(rg.Plane(base_point, rg.Vector3d.XAxis, rg.Vector3d.ZAxis),
                         rg.Interval(0, module_width),
                         rg.Interval(0, thickness),
                         rg.Interval(0, module_height))
            
            brep = box.ToBrep()
            geometries.append(brep)
    
    return geometries"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry("wood", module_width=1.2, module_height=2.8, grid_spacing=0.3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry("steel", module_width=1.5, module_height=2.2, grid_spacing=0.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry("concrete", module_width=0.9, module_height=3.0, grid_spacing=0.4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry("aluminum", module_width=0.8, module_height=2.4, grid_spacing=0.2)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry("glass", module_width=1.1, module_height=2.6, grid_spacing=0.15)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
