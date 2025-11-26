""" Summary:
The script builds a vertical tower by stacking cube modules along a base plane Z-axis. For each level it places a cube centered at incremental heights, computes a lateral offset on a circle (offset_radius) and rotates the cube around the vertical axis (twist_per_level_deg plus start_angle). Optional jitter randomizes angle and radius for an assembled look, and skip_every removes periodic levels to create vertical voids. Module size and inter-level gap set proportions. Each cube is created as a RhinoCommon Box converted to a Brep and collected into a list, enabling parametric control over geometry and reproducible variations via seed for fabrication."""

#! python 3
function_code = """def generate_cube_tower(levels=18, module=4.0, gap=0.2, twist_per_level_deg=8.0, offset_radius=1.2, start_angle_deg=0.0, jitter=0.0, skip_every=0, seed=1, base_plane=None):
    \"""
    Generate a vertical tower composed of stacked cubic modules (Breps), suitable for Grasshopper (Rhino 8, Python 3.9).

    Purpose
    - Creates a parametric tower made of cubes that can twist and laterally shift as they rise.
    - Designed to approximate a variety of "stacked cube tower" references by tuning parameters.

    What it does
    - Stacks equal-size cubic Breps along the base plane Z-axis.
    - Applies a controlled per-level twist and circular lateral offset of each cube around the tower's central axis.
    - Optionally skips periodic levels to introduce vertical voids.
    - Optionally adds reproducible jitter to angle and radius for a less uniform, more "assembled" look.

    Inputs
    - levels (int): Number of cubes (levels) to create. Must be >= 1.
    - module (float): Edge length of each cube in meters. Must be > 0.
    - gap (float): Vertical gap between cubes in meters (0 for touching).
    - twist_per_level_deg (float): Rotation applied per level in degrees around the vertical axis.
    - offset_radius (float): Lateral offset radius in meters; 0 for a straight, aligned stack.
    - start_angle_deg (float): Starting rotation angle at the first level, in degrees.
    - jitter (float): 0..1 factor controlling randomness; 0 is none. Affects both angle and radius slightly.
    - skip_every (int): If > 0, skips every Nth level (e.g., 5 skips levels 5, 10, 15...) to create vertical voids.
    - seed (int): Random seed for reproducibility when jitter > 0.
    - base_plane (Rhino.Geometry.Plane or None): Base plane for the tower; if None, uses WorldXY.

    Outputs
    - List[Rhino.Geometry.Brep]: A list of cube Breps forming the tower.

    Notes
    - Units are meters. Z-axis is height; X is width; Y is depth.
    - Uses RhinoCommon only; no rhinoscriptsyntax.
    \"""
    import math
    import random
    import Rhino.Geometry as RG

    # Validate inputs
    if levels < 1 or module <= 0:
        return []

    rnd = random.Random(seed)
    plane = base_plane if base_plane is not None else RG.Plane.WorldXY

    # Precompute intervals for a cube centered at the local plane origin
    half = module * 0.5
    xint = RG.Interval(-half, half)
    yint = RG.Interval(-half, half)
    zint = RG.Interval(-half, half)

    # Jitter magnitudes
    # Angle jitter: fraction of twist per level; Radius jitter: fraction of offset radius
    angle_jit_deg = abs(jitter) * abs(twist_per_level_deg)
    radius_jit = abs(jitter) * 0.5 * abs(offset_radius)

    geos = []
    vertical_step = module + max(0.0, gap)

    for i in range(levels):
        # Optional skipping to form voids
        if skip_every and skip_every > 0 and ((i + 1) % skip_every == 0):
            continue

        # Base angle accumulation
        angle_deg = start_angle_deg + i * twist_per_level_deg

        # Jittered rotation and radius
        if jitter > 0.0:
            angle_deg += rnd.uniform(-angle_jit_deg, angle_jit_deg)
            radius_i = max(0.0, offset_radius + rnd.uniform(-radius_jit, radius_jit))
        else:
            radius_i = max(0.0, offset_radius)

        angle_rad = math.radians(angle_deg)

        # Compute lateral offset in the base plane XY frame
        # offset = XAxis * (r*cos(theta)) + YAxis * (r*sin(theta))
        ox = radius_i * math.cos(angle_rad)
        oy = radius_i * math.sin(angle_rad)
        offset_vec = plane.XAxis * ox + plane.YAxis * oy

        # Vertical position: center of the cube at this level
        center_height = i * vertical_step + half
        center_pt = plane.Origin + offset_vec + (plane.ZAxis * center_height)

        # Local plane for the cube centered at center_pt, oriented with base plane
        local_plane = RG.Plane(plane)
        local_plane.Origin = center_pt

        # Apply twist by rotating the local plane around its Z axis through the cube center
        if twist_per_level_deg != 0.0 or start_angle_deg != 0.0 or jitter > 0.0:
            rot = RG.Transform.Rotation(angle_rad, local_plane.ZAxis, local_plane.Origin)
            local_plane.Transform(rot)

        # Create cube as a Brep
        box = RG.Box(local_plane, xint, yint, zint)
        brep = box.ToBrep()
        if brep is not None:
            geos.append(brep)

    return geos"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/3
    geometry = generate_cube_tower(levels=18, module=1.2, gap=0.05, twist_per_level_deg=8.0, offset_radius=0.6, start_angle_deg=15.0, jitter=0.15, skip_every=6, seed=123)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/3
    geometry = generate_cube_tower(levels=30, module=0.8, gap=0.02, twist_per_level_deg=12.0, offset_radius=0.9, start_angle_deg=0.0, jitter=0.05, skip_every=5, seed=42)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/3
    geometry = generate_cube_tower(levels=24, module=0.6, gap=0.03, twist_per_level_deg=6.5, offset_radius=0.5, start_angle_deg=10.0, jitter=0.12, skip_every=4, seed=7)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
