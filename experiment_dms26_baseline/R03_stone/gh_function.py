""" Summary:
The script defines generate_facade_geometry which builds an XZ‑plane facade from wave parameters. It seeds randomness, computes control points across the panel width (x) and height bands (z), displacing each point in y by a sine wave (wave_frequency, wave_amplitude) plus small random offset (wave_height, variation_seed). It assembles these points into NURBS curves and extrudes every other horizontal band into Brep surfaces, collecting them as the facade panels. The main block runs five sample parameter sets, converts results into a Grasshopper DataTree using ghpythonlib.treehelpers, and prints success. Rhino.Geometry and Grasshopper libraries provide the geometry and data tree plumbing for procedural facade generation."""

#! python 3
function_code = """def generate_facade_geometry(wave_height, wave_frequency, wave_amplitude, panel_width, panel_height, variation_seed):
    \"""
    Generate a facade geometry inspired by organic, wave-like forms.

    Parameters:
    wave_height (float): The height of the waves in the facade.
    wave_frequency (int): The number of waves across the facade width.
    wave_amplitude (float): The amplitude of the waves.
    panel_width (float): The total width of the facade.
    panel_height (float): The total height of the facade.
    variation_seed (int): A seed for random variation in the facade's surface.

    Returns:
    List[Rhino.Geometry.Brep]: A list of Brep surfaces representing the facade geometry.
    \"""
    import Rhino.Geometry as rg
    import math
    import random

    random.seed(variation_seed)
    geometries = []
    
    points = []
    wave_step = panel_width / wave_frequency

    # Create control points for wave effect
    for i in range(wave_frequency + 1):
        for j in range(2):
            x = i * wave_step
            y = 0
            z = j * panel_height
            y += math.sin(i * 2 * math.pi / wave_frequency) * wave_amplitude
            y += random.uniform(-wave_height, wave_height) * 0.1
            points.append(rg.Point3d(x, y, z))
    
    # Loop through each facade "band"
    for z in range(int(panel_height)):
        if z % 2 == 0:
            # Create one band of the facade
            curve = rg.NurbsCurve.Create(False, 3, points)
            loft = rg.Brep.CreateFromSurface(rg.Surface.CreateExtrusion(curve, rg.Vector3d(0, 0, 1)))
            geometries.append(loft)
    
    return geometries"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(0.5, 10, 0.8, 20.0, 5.0, 42)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(0.8, 20, 1.5, 40.0, 10.0, 7)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(1.0, 12, 1.2, 25.0, 6.0, 99)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(0.6, 15, 1.0, 30.0, 8.0, 123)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(0.3, 8, 0.6, 15.0, 4.0, 256)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
