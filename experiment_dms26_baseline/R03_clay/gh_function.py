""" Summary:
The script creates an XZ-plane façade by stacking interpolated transverse curves along the height and lofting them into 3D panels. For each height section it samples points across the width with coordinates (x, depth + amplitude*sin(frequency*x), z), so the sine function sculpts relief in the Y direction. Consecutive interpolated curves are lofted into Breps, producing a wavy surface whose scale, frequency, depth and overall dimensions are controllable by parameters. The wrapper runs five sample configurations, collects Breps, and converts them into a Grasshopper DataTree. Material or texture is not assigned here but can be applied later in the GH pipeline."""

#! python 3
function_code = """def generate_facade_wave(height, width, depth, wave_amplitude, wave_frequency):
    \"""
    Generate a facade geometry with a wavy texture, inspired by a specific organic style.

    Parameters:
    height (float): The total height of the facade.
    width (float): The total width of the facade.
    depth (float): The depth of the facade elements.
    wave_amplitude (float): The amplitude of the sine wave texture.
    wave_frequency (float): The frequency of the sine wave texture.

    Returns:
    List[Rhino.Geometry.Brep]: A list containing the façade's 3D geometries.
    \"""
    import Rhino.Geometry as rg
    import math

    # Create a list to store the resulting breps
    breps = []

    # Define number of sections along the height for contouring the wave
    num_sections_height = int(height / 3.0)
    
    # Loop through each section to create a wavy surface
    for i in range(num_sections_height + 1):
        z = i * (height / num_sections_height)
        
        # Create points along the width with sinusoidal variation
        points = []
        for j in range(int(width) + 1):
            x = j
            y = depth + wave_amplitude * math.sin(wave_frequency * j)
            points.append(rg.Point3d(x, y, z))
        
        # Create an interpolated curve from these points
        curve = rg.Curve.CreateInterpolatedCurve(points, 3)
        
        # Create a surface by lofting these curves together
        if i > 0:
            loft = rg.Brep.CreateFromLoft([prev_curve, curve], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)
            breps.extend(loft)

        prev_curve = curve
    
    return breps"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_wave(12.0, 30.0, 1.0, 2.5, 0.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_wave(18.0, 40.0, 0.8, 1.5, 0.4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_wave(9.0, 25.0, 0.6, 1.2, 0.18)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_wave(15.0, 50.0, 1.2, 3.0, 0.15)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_wave(20.0, 60.0, 1.5, 2.0, 0.3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
