""" Summary:
The script maps a 2D construction‑section intent into a 3D facade system by building box solids and subtracting voids. User parameters (stories, bays, bay width, depth, wall/slab thickness, openings, roof type, pitch, overhang, etc.) define dimensions. It creates an outer and inner wall box then boolean-differences to form a shell. Regular bay-based windows and a door are cut as box voids per story (with clamping for valid sizes). It adds a foundation ring, four strip footings, interior floor slabs, and a flat roof slab with parapet or a gable extrusion. Outputs are Rhino Breps directly ready for visualization and modelling."""

#! python 3
function_code = """def generate_building_from_section(
    stories=2,
    num_bays=4,
    bay_width=4.0,
    building_depth=8.0,
    wall_thickness=0.3,
    slab_thickness=0.25,
    foundation_depth=1.0,
    footing_width=0.8,
    roof_type="gable",
    roof_pitch_deg=25.0,
    roof_overhang=0.5,
    parapet_height=0.6,
    window_width=1.5,
    window_height=1.2,
    window_sill=1.0,
    door_width=1.0,
    door_height=2.2,
    door_bay_index=0,
    openings_on_back=True
):
    \"""
    Generate a 3D architectural model from a typical construction section intent.

    Purpose:
        Builds a parametric 3D model that translates a 2D construction section concept into solids
        representing: perimeter walls (with optional parapet), windows, a main entrance door,
        floor slabs, a foundation ring with strip footings, and either a flat or gable roof.
        The model is aligned to World axes: X = width, Y = depth, Z = height. Units are meters.

    What it does:
        - Constructs a perimeter wall shell by subtracting an inner volume from an outer one.
        - Cuts window and door openings as boolean voids in the wall shell.
        - Adds a ring foundation below grade and four exterior strip footings.
        - Adds slabs at ground and intermediate story levels.
        - Adds a flat roof slab with parapet or a gable roof solid with configurable pitch and overhangs.

    Inputs:
        stories (int): Number of stories above grade (>=1).
        num_bays (int): Number of structural/facade bays along X (>=1).
        bay_width (float): Width of each bay along X (m).
        building_depth (float): Overall building depth along Y (m).
        wall_thickness (float): Exterior wall thickness (m).
        slab_thickness (float): Slab thickness for floors/flat roof (m).
        foundation_depth (float): Depth of foundation below grade (m, positive).
        footing_width (float): Width of strip footings extending outwards from walls (m).
        roof_type (str): "flat" or "gable".
        roof_pitch_deg (float): Gable roof pitch in degrees (angle of each slope from horizontal).
        roof_overhang (float): Overhang for roof beyond walls along X and Y (m).
        parapet_height (float): Parapet height for flat roof (m).
        window_width (float): Window clear width (m).
        window_height (float): Window clear height (m).
        window_sill (float): Window sill height above floor (m).
        door_width (float): Entry door clear width (m).
        door_height (float): Entry door height (m).
        door_bay_index (int): Bay index along X where the main entry door is placed on the front facade (0-based).
        openings_on_back (bool): If True, mirrors windows on the back facade.

    Outputs:
        list[Rhino.Geometry.Brep]: A list of closed Breps representing:
            - Exterior wall shell (with openings)
            - Foundation ring
            - Four strip footings
            - Floor slabs and (if flat roof) roof slab
            - Gable roof solid (if roof_type == "gable")
        All returned objects are Breps suitable for further boolean operations or visualization.

    Notes:
        - The function focuses on robust, box-based operations for stability.
        - Openings are subtracted as voids; their placement assumes regular bay spacing.
        - If an opening would exceed bounds (e.g., clash with story height), it is clamped to remain valid.
        - The model is created at origin; outer footprint starts at (0,0,0).
    \"""
    import math
    import Rhino
    import Rhino.Geometry as rg

    # Tolerance from active doc or fallback
    tol = 1e-5
    try:
        doc = Rhino.RhinoDoc.ActiveDoc
        if doc:
            tol = doc.ModelAbsoluteTolerance
    except:
        pass

    # Guard/clamp inputs
    stories = max(1, int(stories))
    num_bays = max(1, int(num_bays))
    bay_width = max(0.5, float(bay_width))
    building_depth = max(1.0, float(building_depth))
    wall_thickness = max(0.05, float(wall_thickness))
    slab_thickness = max(0.05, float(slab_thickness))
    foundation_depth = max(0.2, float(foundation_depth))
    footing_width = max(0.1, float(footing_width))
    roof_overhang = max(0.0, float(roof_overhang))
    parapet_height = max(0.0, float(parapet_height))
    roof_pitch_deg = float(roof_pitch_deg)

    # Derived dimensions
    width = num_bays * bay_width
    story_height = 3.2  # typical default for generic section if not provided explicitly
    eave_elevation = stories * story_height

    # Clamp opening sizes to bay/story constraints
    max_window_width = max(0.1, bay_width - 2 * 0.25)  # keep ~25cm jambs by default
    window_width = min(max_window_width, max(0.3, float(window_width)))
    window_height = max(0.3, float(window_height))
    window_sill = max(0.2, float(window_sill))

    door_width = min(bay_width - 0.2, max(0.6, float(door_width)))
    door_height = max(1.9, float(door_height))
    door_bay_index = max(0, min(num_bays - 1, int(door_bay_index)))

    # Helper to make a Box Brep from intervals
    def make_box_brep(x0, x1, y0, y1, z0, z1):
        bx = rg.Box(rg.Plane.WorldXY, rg.Interval(x0, x1), rg.Interval(y0, y1), rg.Interval(z0, z1))
        return bx.ToBrep()

    geometry = []

    # 1) WALL SHELL (outer - inner)
    if roof_type.lower() == "flat":
        outer_top = eave_elevation + parapet_height
        inner_top = eave_elevation
    else:
        outer_top = eave_elevation
        inner_top = eave_elevation

    outer_walls = make_box_brep(0.0, width, 0.0, building_depth, 0.0, outer_top)
    inner_walls = make_box_brep(
        wall_thickness, width - wall_thickness,
        wall_thickness, building_depth - wall_thickness,
        0.0, inner_top
    )
    walls_shell = rg.Brep.CreateBooleanDifference([outer_walls], [inner_walls], tol)
    if not walls_shell or len(walls_shell) == 0:
        walls_shell = [outer_walls]  # fallback, no shell

    # 2) OPENINGS: Windows and Door
    openings = []

    # Window placement per story and per bay
    eps = wall_thickness * 1.2  # extend through wall
    for s in range(stories):
        z0 = s * story_height + window_sill
        z1 = z0 + window_height
        # clamp top below ceiling
        max_head = min(eave_elevation - 0.2, (s + 1) * story_height - 0.2)
        if z1 > max_head:
            z1 = max_head
            z0 = z1 - window_height
            if z0 < s * story_height + 0.2:
                z0 = s * story_height + 0.2  # ensure some headroom
        if z1 <= z0:
            continue  # invalid after clamping

        for b in range(num_bays):
            # Skip door bay at ground floor to avoid clashes
            if s == 0 and b == door_bay_index:
                continue
            cx = (b + 0.5) * bay_width
            x0 = max(0.05, cx - window_width * 0.5)
            x1 = min(width - 0.05, cx + window_width * 0.5)

            # Front facade window
            w_front = make_box_brep(x0, x1, -eps, wall_thickness + eps, z0, z1)
            openings.append(w_front)
            # Back facade window (optional)
            if openings_on_back:
                w_back = make_box_brep(x0, x1, building_depth - wall_thickness - eps, building_depth + eps, z0, z1)
                openings.append(w_back)

    # Door on front facade at ground floor
    d_cx = (door_bay_index + 0.5) * bay_width
    dx0 = max(0.05, d_cx - door_width * 0.5)
    dx1 = min(width - 0.05, d_cx + door_width * 0.5)
    dz0, dz1 = 0.0, min(door_height, story_height - 0.1)
    door_front = make_box_brep(dx0, dx1, -eps, wall_thickness + eps, dz0, dz1)
    openings.append(door_front)

    # Subtract all openings from wall shell
    if openings and walls_shell:
        cut = rg.Brep.CreateBooleanDifference(walls_shell, openings, tol)
        if cut and len(cut) > 0:
            walls_shell = cut

    # Collect walls
    geometry.extend(walls_shell)

    # 3) FOUNDATION RING (below grade)
    outer_found = make_box_brep(0.0, width, 0.0, building_depth, -foundation_depth, 0.0)
    inner_found = make_box_brep(
        wall_thickness, width - wall_thickness,
        wall_thickness, building_depth - wall_thickness,
        -foundation_depth, 0.0
    )
    foundation_ring = rg.Brep.CreateBooleanDifference([outer_found], [inner_found], tol)
    if not foundation_ring or len(foundation_ring) == 0:
        foundation_ring = [outer_found]
    geometry.extend(foundation_ring)

    # 4) STRIP FOOTINGS around perimeter (outside the walls)
    # Front strip footing
    footing_front = make_box_brep(0.0, width, -footing_width, 0.0, -foundation_depth, 0.0)
    # Back strip footing
    footing_back = make_box_brep(0.0, width, building_depth, building_depth + footing_width, -foundation_depth, 0.0)
    # Left strip footing
    footing_left = make_box_brep(-footing_width, 0.0, 0.0, building_depth, -foundation_depth, 0.0)
    # Right strip footing
    footing_right = make_box_brep(width, width + footing_width, 0.0, building_depth, -foundation_depth, 0.0)

    geometry.extend([footing_front, footing_back, footing_left, footing_right])

    # 5) FLOOR SLABS (inside inner footprint)
    x_in0, x_in1 = wall_thickness, width - wall_thickness
    y_in0, y_in1 = wall_thickness, building_depth - wall_thickness
    for s in range(stories):
        z0 = s * story_height
        z1 = z0 + slab_thickness
        slab = make_box_brep(x_in0, x_in1, y_in0, y_in1, z0, z1)
        geometry.append(slab)

    # 6) ROOF
    if roof_type.lower() == "flat":
        # Roof slab at eave elevation, parapet already part of wall shell
        roof_slab = make_box_brep(x_in0, x_in1, y_in0, y_in1, eave_elevation, eave_elevation + slab_thickness)
        geometry.append(roof_slab)
    else:
        # Gable roof solid (triangular prism) with overhangs on X and Y
        # Cross-section in XZ plane: eave at eave_elevation, ridge height from pitch
        half_span = 0.5 * width
        pitch_rad = math.radians(roof_pitch_deg)
        ridge_z = eave_elevation + math.tan(pitch_rad) * half_span

        p0 = rg.Point3d(-roof_overhang, 0.0, eave_elevation)
        p1 = rg.Point3d(width + roof_overhang, 0.0, eave_elevation)
        p2 = rg.Point3d(0.5 * width, 0.0, ridge_z)

        pl = rg.Polyline([p0, p1, p2, p0])
        crv = rg.PolylineCurve(pl)

        extr_len = building_depth + 2.0 * roof_overhang
        extrusion = rg.Extrusion.Create(crv, extr_len, True)
        if extrusion:
            roof_brep = extrusion.ToBrep()
            # Shift to center over building depth (start from -overhang along Y)
            xform = rg.Transform.Translation(rg.Vector3d(0.0, -roof_overhang, 0.0))
            roof_brep.Transform(xform)
            geometry.append(roof_brep)

    return geometry"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/3
    geometry = generate_building_from_section(stories=3, num_bays=6, bay_width=3.5, building_depth=12.0, wall_thickness=0.25, slab_thickness=0.3, foundation_depth=1.2, footing_width=1.0, roof_type="gable", roof_pitch_deg=30.0, roof_overhang=0.5, parapet_height=0.6, window_width=1.4, window_height=1.2, window_sill=1.0, door_width=1.0, door_height=2.1, door_bay_index=2, openings_on_back=True)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/3
    geometry = generate_building_from_section(stories=2, num_bays=5, bay_width=4.0, building_depth=10.0, wall_thickness=0.3, slab_thickness=0.2, foundation_depth=0.8, footing_width=0.7, roof_type="flat", roof_pitch_deg=20.0, roof_overhang=0.4, parapet_height=0.8, window_width=1.2, window_height=1.0, window_sill=1.1, door_width=0.9, door_height=2.0, door_bay_index=1, openings_on_back=False)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/3
    geometry = generate_building_from_section(stories=1, num_bays=3, bay_width=5.0, building_depth=9.0, wall_thickness=0.25, slab_thickness=0.2, foundation_depth=0.5, footing_width=0.6, roof_type="gable", roof_pitch_deg=35.0, roof_overhang=0.6, parapet_height=0.4, window_width=1.6, window_height=1.4, window_sill=0.9, door_width=1.2, door_height=2.2, door_bay_index=1, openings_on_back=True)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
