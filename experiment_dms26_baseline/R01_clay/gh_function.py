""" Summary:
The script builds a modular facade by tiling a grid of rectangular modules across the XZ plane using width, height and module_size to compute columns and rows. For each cell it creates a solid box (block) extruded in depth, then constructs a smaller centered box (window) sized by window_ratio. It subtracts the window from the block with a Boolean difference to produce a facade piece. Resulting Breps are collected and returned. Sample facades with different parameters are generated and packaged into a Grasshopper DataTree for output. Rhino.Geometry is used for geometry; a fixed random seed exists though randomness is unused."""

#! python 3
function_code = """def generate_facade(width, height, depth, module_size, window_ratio):
    \"""
    Generate a 3D geometry representing a facade on the XZ plane.

    The function creates a modular facade with voids and solids based on a given module size
    and window to wall ratio. The facade resembles a pattern with repetitive elements.

    Parameters:
    - width (float): Total width of the facade.
    - height (float): Total height of the facade.
    - depth (float): Depth of the solid elements.
    - module_size (float): Size of each modular unit.
    - window_ratio (float): Ratio to determine the size of the windows.

    Returns:
    - List of Rhino.Geometry.Brep: A list of 3D breps representing the facade.
    \"""
    import Rhino
    import Rhino.Geometry as rg
    import random
    
    random.seed(42)
    
    breps = []
    columns = int(width / module_size)
    rows = int(height / module_size)
    
    for i in range(columns):
        for j in range(rows):
            
            x = i * module_size
            z = j * module_size
            
            # Determine the size of the window
            window_width = module_size * window_ratio
            window_height = module_size * window_ratio
            
            # Create a solid block
            block_corners = [
                rg.Point3d(x, 0, z),
                rg.Point3d(x + module_size, 0, z),
                rg.Point3d(x + module_size, depth, z),
                rg.Point3d(x, depth, z),
                rg.Point3d(x, 0, z + module_size),
                rg.Point3d(x + module_size, 0, z + module_size),
                rg.Point3d(x + module_size, depth, z + module_size),
                rg.Point3d(x, depth, z + module_size)
            ]
            block = rg.Brep.CreateFromBox(block_corners)
            
            # Create a window (void) in the block
            window_corners = [
                rg.Point3d(x + (module_size - window_width) / 2, 0, z + (module_size - window_height) / 2),
                rg.Point3d(x + (module_size + window_width) / 2, 0, z + (module_size - window_height) / 2),
                rg.Point3d(x + (module_size + window_width) / 2, depth, z + (module_size - window_height) / 2),
                rg.Point3d(x + (module_size - window_width) / 2, depth, z + (module_size - window_height) / 2),
                rg.Point3d(x + (module_size - window_width) / 2, 0, z + (module_size + window_height) / 2),
                rg.Point3d(x + (module_size + window_width) / 2, 0, z + (module_size + window_height) / 2),
                rg.Point3d(x + (module_size + window_width) / 2, depth, z + (module_size + window_height) / 2),
                rg.Point3d(x + (module_size - window_width) / 2, depth, z + (module_size + window_height) / 2)
            ]
            window = rg.Brep.CreateFromBox(window_corners)
            
            # Subtract the window from the block
            facade_piece = rg.Brep.CreateBooleanDifference(block, window, 0.01)
            if facade_piece:
                breps.extend(facade_piece)
                
    return breps"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade(10, 6, 0.5, 1, 0.6)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade(12, 8, 0.4, 1.5, 0.5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade(15, 9, 0.3, 1.25, 0.55)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade(16, 8, 0.4, 1.6, 0.65)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade(20, 10, 0.6, 0.8, 0.45)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
