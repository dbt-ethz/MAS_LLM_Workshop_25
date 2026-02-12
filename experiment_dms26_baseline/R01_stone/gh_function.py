""" Summary:
The script defines generate_facade_geometry(...) that builds an array of rectangular panels parametrically. For each panel grid cell it computes a sinusoidal vertical offset using wave_amplitude and wave_frequency across the X index, then creates four corner Point3d coordinates where the top edge is lifted by that offset. It makes a NURBS surface from the corners, converts it to a Brep if valid, and appends it to a list. Multiple sample parameter sets produce varied facade iterations, which are collected and turned into a Grasshopper DataTree. The code relies on Rhino.Geometry for geometry creation and ghpythonlib for Grasshopper integration and export utilities."""

#! python 3
function_code = """def generate_facade_geometry(panel_count_x=10, panel_count_y=5, panel_width=1.0, panel_height=2.0, wave_amplitude=0.5, wave_frequency=2):
    \"""
    Generates a 3D facade geometry using undulating panels.

    Args:
    - panel_count_x (int): Number of panels along the X-axis (width direction).
    - panel_count_y (int): Number of panels along the Y-axis (height direction).
    - panel_width (float): Width of each panel in meters.
    - panel_height (float): Height of each panel in meters.
    - wave_amplitude (float): Amplitude of the wave pattern in meters.
    - wave_frequency (int): Frequency of the wave across the panels.

    Returns:
    - List of Breps: A list of 3D Brep geometry representing the facade panels.
    \"""
    import Rhino.Geometry as rg
    from math import sin, pi

    breps = []
    for i in range(panel_count_x):
        x_start = i * panel_width
        for j in range(panel_count_y):
            y_start = j * panel_height
            # Calculate wave offset
            wave_offset = wave_amplitude * sin(wave_frequency * pi * i / panel_count_x)
            
            # Define the corners of the panel
            pt0 = rg.Point3d(x_start, y_start, 0)
            pt1 = rg.Point3d(x_start + panel_width, y_start, 0)
            pt2 = rg.Point3d(x_start + panel_width, y_start + panel_height, wave_offset)
            pt3 = rg.Point3d(x_start, y_start + panel_height, wave_offset)
            
            # Correcting: Creating a valid surface from corner points
            corners = [pt0, pt1, pt2, pt3]
            surface = rg.NurbsSurface.CreateFromCorners(*corners)
            
            # Add to the list
            if surface and surface.IsValid:
                breps.append(rg.Brep.CreateFromSurface(surface))

    return breps"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/5
    geometry = generate_facade_geometry(panel_count_x=20, panel_count_y=8, panel_width=1.2, panel_height=2.8, wave_amplitude=0.6, wave_frequency=4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/5
    geometry = generate_facade_geometry(panel_count_x=12, panel_count_y=6, panel_width=0.9, panel_height=2.5, wave_amplitude=0.8, wave_frequency=3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/5
    geometry = generate_facade_geometry(panel_count_x=15, panel_count_y=10, panel_width=1.5, panel_height=3.0, wave_amplitude=0.4, wave_frequency=5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 4/5
    geometry = generate_facade_geometry(panel_count_x=8, panel_count_y=12, panel_width=0.8, panel_height=2.4, wave_amplitude=0.9, wave_frequency=6)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 5/5
    geometry = generate_facade_geometry(panel_count_x=30, panel_count_y=5, panel_width=1.1, panel_height=2.2, wave_amplitude=0.3, wave_frequency=7)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
