""" Summary:
The script defines a parametric function that reads section parameters (origin, facade length, floor heights, bay width, mullion/transom profiles, podium setback, fins, tolerances) and snaps facade length to a bay module. It computes bay lines and floor heights, then iterates floors to place horizontal transoms, vertical primary/secondary mullion boxes, and creates planar glass panels (vision and spandrel) sized between mullions and transoms. Spandrel shadow-boxes, corner returns and podium setbacks are handled. Vertical fins are added above the podium with configurable cadence and offsets. Geometry is built with Rhino Box/Polyline/Brep primitives, guarded by tolerance checks, and returns valid breps as output."""

#! python 3
function_code = """def generate_curtainwall_facade(
    origin=(0.0, 0.0, 0.0),
    facade_length=36.0,
    num_floors=8,
    elevation_name="east",
    # Core datums (meters)
    bay_width=1.5,
    structural_grid=6.0,
    floor_to_floor=3.6,
    sill_transom=0.9,
    head_transom=3.1,
    podium_floors=2,
    podium_setback=0.9,
    # Component profiles (width x depth in meters)
    primary_mullion=(0.120, 0.050),
    secondary_mullion=(0.065, 0.035),
    transom=(0.075, 0.035),
    glazing_inset=0.050,
    spandrel_shadow_depth=0.200,
    # Vertical fins (thickness along X, projection along Y)
    fin_size=(0.050, 0.250),
    fin_offset_from_mullion=0.150,
    fins_enabled=True,
    fin_cadence_override=None,
    # Constraints
    max_panel_width=1.65,
    expansion_joint_spacing=30.0,
    corner_return=0.150,
    module_tolerance=0.010
):
    \"""
    Generate a parametric curtain wall facade Brep/Surface assembly based on a construction section brief.
    \"""
    import Rhino
    from Rhino.Geometry import Point3d, Interval, Plane, Box, Brep, Polyline
    import System

    # Use a robust modeling tolerance (meters). Avoid overly small tolerances that can yield invalid breps.
    try:
        doc = Rhino.RhinoDoc.ActiveDoc
        doc_tol = doc.ModelAbsoluteTolerance if doc is not None else 0.001
    except:
        doc_tol = 0.001
    tol = max(0.0005, min(0.005, doc_tol))  # clamp between 0.5 mm and 5 mm
    eps = tol * 0.1  # geometric safety epsilon (smaller than tol)

    # Unpack origin
    ox, oy, oz = origin

    # Sanity: enforce module snapping and panel width constraint
    if bay_width <= 0:
        bay_width = 1.5
    if structural_grid <= 0:
        structural_grid = 6.0
    bays_per_grid = int(round(structural_grid / bay_width))  # expect 4
    bays_per_grid = max(1, bays_per_grid)

    # Snap facade length to bay module
    n_bays = max(1, int(round(facade_length / bay_width)))
    snapped_length = n_bays * bay_width

    # Keep continuity across setbacks within tolerance; otherwise enforce module
    if abs(snapped_length - facade_length) > module_tolerance:
        facade_length_eff = snapped_length
    else:
        facade_length_eff = snapped_length  # same in either case to preserve module

    # Panel width constraint safeguard
    if bay_width > max_panel_width:
        bay_width = max_panel_width
        n_bays = max(1, int(round(facade_length_eff / bay_width)))
        facade_length_eff = n_bays * bay_width

    # Determine fin cadence based on elevation
    if fin_cadence_override is not None and isinstance(fin_cadence_override, int) and fin_cadence_override > 0:
        fin_cadence = fin_cadence_override
    else:
        name = (elevation_name or "").lower()
        if name == "east":
            fin_cadence = 2
        elif name == "west":
            fin_cadence = 4
        else:
            fin_cadence = 3

    # Helper creators
    def box_from_bounds(x0, x1, y0, y1, z0, z1):
        # Ensure positive extents above epsilon to avoid degenerate/invalid boxes
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        dz = abs(z1 - z0)
        if dx <= eps or dy <= eps or dz <= eps:
            return None
        ix = Interval(min(x0, x1), max(x0, x1))
        iy = Interval(min(y0, y1), max(y0, y1))
        iz = Interval(min(z0, z1), max(z0, z1))
        b = Box(Plane.WorldXY, ix, iy, iz)
        brep = b.ToBrep()
        if brep is None or not brep.IsValid:
            return None
        return brep

    def panel_from_corners_xy(xmin, xmax, y, zmin, zmax):
        # Guard against degenerate panels
        if xmax - xmin <= eps or zmax - zmin <= eps:
            return None
        # Build a planar brep from a closed polyline to improve validity at doc tolerances
        pts = [
            Point3d(xmin, y, zmin),
            Point3d(xmax, y, zmin),
            Point3d(xmax, y, zmax),
            Point3d(xmin, y, zmax),
            Point3d(xmin, y, zmin)
        ]
        plc = Polyline(pts)
        crv = plc.ToNurbsCurve()
        breps = Brep.CreatePlanarBreps(crv, tol)
        if breps and len(breps) > 0 and breps[0] is not None and breps[0].IsValid:
            return breps[0]
        return None

    geom = []

    # Precompute bay lines (centerlines for vertical members)
    x0 = ox
    x_positions = [x0 + i * bay_width for i in range(n_bays + 1)]
    x_end = x0 + facade_length_eff

    # Profiles
    prim_w, prim_d = primary_mullion
    sec_w, sec_d = secondary_mullion
    tr_h, tr_d = transom
    glass_gap = max(0.002, tol)  # gasket/edge clearance, at least tolerance

    # Heights
    total_height = num_floors * floor_to_floor
    z_building_top = oz + total_height
    z_podium_top = oz + podium_floors * floor_to_floor

    # For fins
    fin_thk_x, fin_proj_y = fin_size

    # Iterate floors
    for f in range(num_floors):
        z_floor_base = oz + f * floor_to_floor
        z_floor_top = z_floor_base + floor_to_floor

        if z_floor_top - z_floor_base <= eps:
            continue

        # Facade datum for this floor (podium setback applied)
        is_podium = (f < podium_floors)
        face_y = oy - (podium_setback if is_podium else 0.0)
        glass_y = face_y - glazing_inset

        # Transom elevations
        z_sill = z_floor_base + sill_transom
        z_head = z_floor_base + head_transom

        # 1) Horizontal transoms (full run)
        if tr_d > eps and tr_h > eps:
            b1 = box_from_bounds(
                x0, x_end,
                face_y - tr_d, face_y,
                z_sill - tr_h * 0.5, z_sill + tr_h * 0.5
            )
            if b1: geom.append(b1)

            b2 = box_from_bounds(
                x0, x_end,
                face_y - tr_d, face_y,
                z_head - tr_h * 0.5, z_head + tr_h * 0.5
            )
            if b2: geom.append(b2)

        # 2) Vertical mullions at each bay line (per floor segments to respect podium setback)
        for i, xi in enumerate(x_positions):
            is_primary = (i % bays_per_grid == 0)
            mw = prim_w if is_primary else sec_w
            md = prim_d if is_primary else sec_d
            if mw <= eps or md <= eps:
                continue
            bm = box_from_bounds(
                xi - mw * 0.5, xi + mw * 0.5,
                face_y - md, face_y,
                z_floor_base, z_floor_top
            )
            if bm: geom.append(bm)

        # 3) Panels (vision and spandrel) per bay
        for i in range(n_bays):
            xl = x_positions[i]
            xr = x_positions[i + 1]

            # Determine mullion widths at bay edges
            left_primary = (i % bays_per_grid == 0)
            right_primary = ((i + 1) % bays_per_grid == 0)
            wL = prim_w if left_primary else sec_w
            wR = prim_w if right_primary else sec_w

            # Clear opening in X between inside faces of mullions
            x_min = xl + wL * 0.5 + glass_gap
            x_max = xr - wR * 0.5 - glass_gap
            if x_max <= x_min + module_tolerance:
                continue  # degenerate opening; skip

            # Vision glass (between sill and head, leaving transom depths/gaps)
            z_vmin = z_sill + tr_h * 0.5 + glass_gap
            z_vmax = z_head - tr_h * 0.5 - glass_gap
            if z_vmax > z_vmin + module_tolerance:
                pg = panel_from_corners_xy(x_min, x_max, glass_y, z_vmin, z_vmax)
                if pg and pg.IsValid:
                    geom.append(pg)

            # Spandrel glass (from slab to sill minus half transom height and gap)
            z_smin = z_floor_base + glass_gap
            z_smax = z_sill - tr_h * 0.5 - glass_gap
            if z_smax > z_smin + module_tolerance:
                ps = panel_from_corners_xy(x_min, x_max, glass_y, z_smin, z_smax)
                if ps and ps.IsValid:
                    geom.append(ps)
                # Shadow-box behind spandrel
                if spandrel_shadow_depth > eps:
                    sb = box_from_bounds(
                        x_min, x_max,
                        glass_y - spandrel_shadow_depth, glass_y,
                        z_smin, z_smax
                    )
                    if sb: geom.append(sb)

        # 4) Corner returns (glass) for this floor
        return_thk_y = 0.010
        if corner_return > eps and return_thk_y > eps:
            bl = box_from_bounds(
                x0 - corner_return, x0,
                glass_y, glass_y + return_thk_y,
                z_floor_base + glass_gap, z_floor_top - glass_gap
            )
            if bl: geom.append(bl)
            br = box_from_bounds(
                x_end, x_end + corner_return,
                glass_y, glass_y + return_thk_y,
                z_floor_base + glass_gap, z_floor_top - glass_gap
            )
            if br: geom.append(br)

    # 5) Vertical fins (above podium only)
    if fins_enabled and num_floors > podium_floors and fin_cadence > 0:
        z_fin_base = z_podium_top
        if z_building_top > z_fin_base + module_tolerance and fin_thk_x > eps and fin_proj_y > eps:
            # Place fins near the left mullion of each selected bay, offset into the bay
            for i in range(n_bays):
                if i % fin_cadence != 0:
                    continue
                xl = x_positions[i]
                xr = x_positions[i + 1]
                # Fin near left mullion, offset into the bay by fin_offset_from_mullion (keep within bay)
                x_fin_center = xl + fin_offset_from_mullion
                # prevent collision with bay edge
                x_fin_center = max(xl + fin_thk_x * 0.5 + glass_gap, min(x_fin_center, xr - fin_thk_x * 0.5 - glass_gap))
                # Fin sits on upper facade plane (no podium setback)
                face_y_upper = oy  # upper facade datum
                bf = box_from_bounds(
                    x_fin_center - fin_thk_x * 0.5,
                    x_fin_center + fin_thk_x * 0.5,
                    face_y_upper,
                    face_y_upper + fin_proj_y,
                    z_fin_base,
                    z_building_top
                )
                if bf: geom.append(bf)

    # Only return valid breps
    geom_valid = [g for g in geom if g is not None and getattr(g, "IsValid", True)]
    return geom_valid"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/3
    geometry = generate_curtainwall_facade(origin=(0.0, 0.0, 0.0), facade_length=48.0, num_floors=12, elevation_name="west", bay_width=1.5, structural_grid=6.0, floor_to_floor=3.6, sill_transom=0.9, head_transom=3.1, podium_floors=2, podium_setback=0.9, primary_mullion=(0.12, 0.05), secondary_mullion=(0.065, 0.035), transom=(0.075, 0.035), glazing_inset=0.05, spandrel_shadow_depth=0.2, fin_size=(0.05, 0.25), fin_offset_from_mullion=0.15, fins_enabled=True, fin_cadence_override=None, max_panel_width=1.65, expansion_joint_spacing=30.0, corner_return=0.15, module_tolerance=0.01)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/3
    geometry = generate_curtainwall_facade(origin=(5.0, 2.0, 0.0), facade_length=30.0, num_floors=10, elevation_name="north", bay_width=1.25, structural_grid=5.0, floor_to_floor=3.2, sill_transom=0.8, head_transom=3.0, podium_floors=1, podium_setback=0.5, primary_mullion=(0.14, 0.06), secondary_mullion=(0.06, 0.03), transom=(0.08, 0.04), glazing_inset=0.04, spandrel_shadow_depth=0.15, fin_size=(0.06, 0.30), fin_offset_from_mullion=0.1, fins_enabled=True, fin_cadence_override=3, max_panel_width=1.6, expansion_joint_spacing=25.0, corner_return=0.12, module_tolerance=0.005)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/3
    geometry = generate_curtainwall_facade(origin=(2.0, -1.0, 0.0), facade_length=24.0, num_floors=6, elevation_name="east", bay_width=1.2, structural_grid=4.8, floor_to_floor=3.3, sill_transom=0.85, head_transom=3.05, podium_floors=0, podium_setback=0.0, primary_mullion=(0.11, 0.045), secondary_mullion=(0.055, 0.03), transom=(0.07, 0.035), glazing_inset=0.03, spandrel_shadow_depth=0.18, fin_size=(0.04, 0.20), fin_offset_from_mullion=0.12, fins_enabled=False, fin_cadence_override=None, max_panel_width=1.7, expansion_joint_spacing=20.0, corner_return=0.1, module_tolerance=0.01)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
