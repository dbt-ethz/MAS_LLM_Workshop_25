""" Summary:
The script lays out a grid across the XZ plane using width, height and grid_density to define module size. For each cell it creates a closed polyline, converts it to a planar Brep, then offsets/extrudes the face to produce panel thickness. Material and the provided reference image inform stochastic decisions (seeded for reproducibility): transparent materials or random choices produce reduced thickness or voids, while others keep full depth. Panels that fail validation are skipped. Multiple parameterized facade variants are generated, collected as Brep lists, and exported for visualization and fabrication. Seeded randomness ensures repeatable variations while allowing rapid design exploration."""

#! python 3
function_code = """def generate_facade(reference_image, material, width=10.0, height=10.0, depth=0.5, grid_density=4):
    \"""
    Generate a 3D facade geometry on the XZ plane inspired by a reference image
    and specified material characteristics.

    Parameters:
    - reference_image: str, Path to a reference image influencing the facade design.
    - material: str, Material description influencing the facade characteristics.
    - width: float, Width of the facade in meters.
    - height: float, Height of the facade in meters.
    - depth: float, Depth of the facade (thickness) in meters.
    - grid_density: int, Number of grid divisions to create different modules.

    Returns:
    - List of Brep objects representing the facade geometry.
    \"""
    import Rhino.Geometry as rg
    import random

    # Set seed for reproducibility
    random.seed(42)

    # Create a list to store facade panels (breps)
    facade_panels = []

    # Calculate grid size based on width and height
    x_spacing = width / grid_density
    z_spacing = height / grid_density

    # Iterate over grid positions to create panels
    for i in range(grid_density):
        for j in range(grid_density):
            x_start = i * x_spacing
            z_start = j * z_spacing

            # Create a base rectangle for each panel
            base_corners = [
                rg.Point3d(x_start, 0, z_start),
                rg.Point3d(x_start + x_spacing, 0, z_start),
                rg.Point3d(x_start + x_spacing, 0, z_start + z_spacing),
                rg.Point3d(x_start, 0, z_start + z_spacing),
                rg.Point3d(x_start, 0, z_start) # Ensure closed loop with this point
            ]
            base_polyline = rg.Polyline(base_corners)
            base_curve = base_polyline.ToNurbsCurve()

            # Correctly create surface for each panel
            base_surface = rg.Brep.CreatePlanarBreps(base_curve)
            if not base_surface or not base_surface[0].IsValid:
                continue

            # Simulate some randomness inspired by material (voids)
            if 'transparent' in material.lower() or random.choice([True, False]):
                # Create a void by skipping the panel or reducing thickness
                panel_thickness = depth * 0.5
            else:
                panel_thickness = depth

            # Offset the surface to create a panel thickness
            if panel_thickness > 0:
                extrusion_vector = rg.Vector3d(0, panel_thickness, 0)
                offset_brep = rg.Brep.CreateFromOffsetFace(
                    base_surface[0].Faces[0], 
                    extrusion_vector.Y, 
                    0.01, 
                    True, 
                    True
                )
                if offset_brep and offset_brep.IsValid:
                    facade_panels.append(offset_brep)

    return facade_panels"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade("C:/images/facade_reference.jpg", "transparent glass", width=15.0, height=12.0, depth=0.4, grid_density=5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade("C:/projects/textures/brick_pattern.jpg", "weathered brick", width=20.0, height=8.0, depth=0.3, grid_density=6)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade("assets/images/stone_mosaic.png", "perforated metal", width=18.0, height=9.0, depth=0.45, grid_density=7)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade("assets/photos/vertical_garden.jpg", "natural timber slats", width=14.0, height=11.0, depth=0.25, grid_density=6)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade("assets/textures/patterned_ceramics.png", "glazed ceramic tiles", width=12.5, height=9.0, depth=0.35, grid_density=8)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
