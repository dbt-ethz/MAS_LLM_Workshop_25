""" Summary:
The script defines generate_organic_facade which creates an XZ-plane facade by sampling points across the X axis and modulating their Z positions with a sinusoidal wave (frequency and amplitude parameters). Pairs of points form polyline curves along the height, which are lofted into continuous surfaces. Each lofted surface is converted to a curve and extruded along the Y-axis to produce volumetric Breps with specified depth. The main block calls this function five times with different parameters, collecting results and converting them to a Grasshopper DataTree for downstream use. Note: material selection and reference-image analysis are not implemented in this code currently."""

#! python 3
function_code = """def generate_organic_facade(x_width, z_height, depth, wave_frequency, wave_amplitude):
    \"""
    Generate a 3D geometry that represents an organic facade on the XZ plane.

    The facade resembles an organic wave-like structure, inspired by natural forms.

    Parameters:
    - x_width: float - The overall width of the facade on the X-axis.
    - z_height: float - The overall height of the facade on the Z-axis.
    - depth: float - The depth of the facade volume on the Y-axis.
    - wave_frequency: int - The number of wave undulations along the X-axis.
    - wave_amplitude: float - The amplitude of the wave undulations.

    Returns:
    - List of Rhino.Geometry.Brep: A list of Breps representing the facade geometry.
    \"""
    import Rhino.Geometry as rg
    import math

    # Create a base surface in the XZ plane using a network surface
    points = []
    for i in range(11):  # Create 11 sections along the X-axis
        x = x_width * i / 10.0
        z_wave = lambda z: z + wave_amplitude * math.sin(2 * math.pi * wave_frequency * (x / x_width) + z)
        points.append([rg.Point3d(x, 0, z_wave(0)), rg.Point3d(x, 0, z_wave(z_height))])
    
    curves = []
    for pt_pair in zip(*points):
        curve = rg.PolylineCurve(pt_pair)
        curves.append(curve)

    loft_type = rg.LoftType.Normal
    breps = rg.Brep.CreateFromLoft(curves, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False)

    if not breps or breps[0] is None:
        return []

    # Extrude the surfaces to create volume
    brep_facades = []
    for brep in breps:
        surface = brep.Faces[0].ToNurbsSurface()
        if surface:
            extrusion_curve = surface.ToBrep().Edges[0].DuplicateCurve()
            if extrusion_curve:
                extrusion = rg.Extrusion.Create(extrusion_curve, depth, True)
                brep_facade = extrusion.ToBrep()
                if brep_facade:
                    brep_facades.append(brep_facade)

    return brep_facades"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_organic_facade(10.0, 5.0, 0.5, 3, 0.8)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_organic_facade(15.0, 6.0, 0.8, 4, 1.2)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_organic_facade(12.5, 4.0, 0.6, 5, 1.0)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_organic_facade(20.0, 8.0, 1.0, 6, 1.5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_organic_facade(8.0, 3.5, 0.4, 2, 0.6)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
