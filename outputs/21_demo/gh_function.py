""" Summary:
The script takes section-driven parameters (floors, floor-to-floor, bay count/width, sill/head, mullion/transom dimensions, setbacks, glazing inset, spandrel/slab thickness, fins) and builds a parametric bay grid. It lays out vertical mullion positions and extrudes continuous mullions, splitting runs where podium setbacks change front offsets and deepening corner mullions. For each floor it computes sill/head elevations (enforcing 2.10 m clear head and avoiding soffit conflict), places transoms, then fills each bay with inset vision-glass prisms and spandrel solids from head to slab soffit. Slab edge bands span the width and optional fins are added on a cadence. All elements return as closed Breps."""

#! python 3
function_code = """def build_facade(floors=10,
                  floor_to_floor=3.6,
                  bay_count=8,
                  bay_width=1.6,
                  sill=0.9,
                  head=2.6,
                  mullion_width=0.065,
                  mullion_depth=0.15,
                  transom_depth=0.12,
                  glazing_setback=0.075,
                  spandrel_thickness=0.2,
                  slab_thickness=0.3,
                  glass_thickness=0.032,
                  fin_enabled=True,
                  fin_depth=0.3,
                  fin_every_n=3,
                  podium_levels=(1, 2),
                  podium_setback=0.3,
                  corner_mullion_depth_factor=1.25,
                  tolerance=0.005):
    \"""
    Generate a parametric curtain wall facade as 3D Breps from a building section concept.
    
    Purpose:
        Constructs a 3D facade model consistent with a typical section-driven curtain wall system.
        The function builds primary facade elements as separate solids (Breps) with clean, parametric
        dependencies:
        - Continuous vertical mullions at bay grid
        - Horizontal transoms at sill/head per floor
        - Vision glass between sill/head
        - Spandrel zone aligned from head transom to slab soffit above (top floor spandrel +150 mm)
        - Slab edge bands
        - Optional vertical fins every N mullions
        - Podium setback for lower levels (L1–L2) by +300 mm (inboard)
        - Corner mullions deepened to 1.25× typical
        - Glazing inset equals glazing_setback
        - Maintain minimum 2.10 m clear head by lifting head transoms if needed
        
    What it does:
        - Lays out a bay grid along X (width), extrudes elements along Y (depth), and stacks floors along Z (height).
        - Places mullions continuously but segments them where podium setbacks occur.
        - Inserts transoms at sill/head elevations per floor; trims head to avoid soffit conflicts and enforces 2.10 m min clear head.
        - Populates each bay/floor with vision glass (between transoms) and spandrel panels (head-to-soffit).
        - Adds slab edge bands for each floor slab.
        - Optionally adds architectural fins centered on every_n mullions.
        
    Units and axes:
        - All inputs are in meters.
        - X = facade width (bays), Y = depth (positive = outward, negative = inward), Z = height.
        - Facade datum/front face is at Y=0; podium-setback floors are at Y=-podium_setback.
        - Glazing front face is inset by glazing_setback from the local facade front at each floor.
    
    Inputs:
        floors (int): Number of floors (>= 1).
        floor_to_floor (float): Floor-to-floor height in meters (default 3.6).
        bay_count (int): Number of bays (6–12 typical).
        bay_width (float): Bay module width in meters (1.5–1.8, default 1.6).
        sill (float): Sill elevation above finished floor in meters (default 0.90).
        head (float): Head elevation above finished floor in meters (default 2.60). Will be raised to min 2.10 if needed.
        mullion_width (float): Mullion face width along X (default 0.065 m).
        mullion_depth (float): Mullion depth along Y (default 0.15 m, measured inward from facade datum).
        transom_depth (float): Transom depth along Y (default 0.12 m).
        glazing_setback (float): Inset of glass from facade front (default 0.075 m).
        spandrel_thickness (float): Opaque spandrel build-up thickness along Y inward (default 0.20 m).
        slab_thickness (float): Slab thickness (default 0.30 m).
        glass_thickness (float): Vision glass thickness (0.028–0.036 m typical, default 0.032 m).
        fin_enabled (bool): If True, adds vertical fins on a cadence (default True).
        fin_depth (float): Fin projection outward (0.25–0.40 m typical, default 0.30 m).
        fin_every_n (int): Place a fin centered on every Nth mullion (default 3).
        podium_levels (tuple[int]|list[int]): Floor indices (1-based) that are set back (default (1,2)).
        podium_setback (float): Inboard offset for podium levels (default 0.30 m).
        corner_mullion_depth_factor (float): Depth multiplier for corner mullions (default 1.25).
        tolerance (float): Modeling tolerance for small overlaps/gaps (default 0.005 m).
    
    Outputs:
        list[Rhino.Geometry.Brep]: A list of closed Breps representing:
            - Vertical mullions (incl. deeper corner mullions)
            - Horizontal transoms at sill and head per floor
            - Vision glass panels (solid prisms for downstream operations)
            - Spandrel panels (solid)
            - Slab edge bands (solid)
            - Optional vertical fins (solid)
        Note: Elements are distinct solids; no booleans are performed.
    
    Primary elements modeled:
        - Vertical mullions
        - Horizontal transoms
        - Vision glass
        - Spandrel
        - Slab edge
        - Optional fins
    
    Key parametric dependencies enforced:
        - Continuous vertical mullions at bay grid; segmented at podium setback runs.
        - Sill/head transoms per floor; head transom min at 2.10 m clear head.
        - Spandrel zone aligns head-to-soffit; top floor spandrel +0.15 m.
        - Glazing inset equals glazing_setback from local floor facade datum (0.0 or -podium_setback).
        - Fins centered on every_n mullions; corner mullions are 1.25× depth.
        - Podium (L1–L2) facade set back by podium_setback.
    
    Example JSON config matching inputs:
        {
          "floors": 10,
          "floor_to_floor": 3.6,
          "bay_count": 8,
          "bay_width": 1.6,
          "sill": 0.9,
          "head": 2.6,
          "mullion": {"width": 0.065, "depth": 0.15},
          "transom": {"depth": 0.12},
          "spandrel": {"thickness": 0.2},
          "slab": {"thickness": 0.3},
          "glazing_setback": 0.075,
          "fin": {"enabled": true, "depth": 0.3, "every_n": 3},
          "setbacks": {"podium_levels": [1, 2], "offset": 0.3}
        }
    \"""
    import Rhino.Geometry as rg

    # Clamp selected parameters to suggested ranges for robustness
    bay_width = max(1.5, min(1.8, float(bay_width)))
    fin_depth = max(0.25, min(0.40, float(fin_depth)))
    glass_thickness = max(0.028, min(0.036, float(glass_thickness)))
    fin_every_n = max(1, int(fin_every_n))
    floors = max(1, int(floors))
    bay_count = max(1, int(bay_count))

    # Helper: make a box brep aligned to WorldXY given min/max along axes
    def _box(x0, x1, y0, y1, z0, z1):
        a, b = (x0, x1) if x0 <= x1 else (x1, x0)
        c, d = (y0, y1) if y0 <= y1 else (y1, y0)
        e, f = (z0, z1) if z0 <= z1 else (z1, z0)
        if (abs(b - a) < tolerance) or (abs(d - c) < tolerance) or (abs(f - e) < tolerance):
            return None
        box = rg.Box(rg.Plane.WorldXY, rg.Interval(a, b), rg.Interval(c, d), rg.Interval(e, f))
        return box.ToBrep()

    geoms = []

    total_width = bay_count * bay_width
    total_height = floors * floor_to_floor

    # Determine floor-by-floor facade datum offset (podium setback floors move inboard)
    podium_set = set(int(i) for i in podium_levels) if podium_levels else set()
    floor_front_y = []
    for f in range(floors):
        level_index = f + 1  # 1-based
        front_y = -podium_setback if level_index in podium_set else 0.0
        floor_front_y.append(front_y)

    # Vertical mullions (continuous by run, segmented where setback changes)
    mullion_xs = [i * bay_width for i in range(bay_count + 1)]
    for k, x in enumerate(mullion_xs):
        is_corner = (k == 0 or k == bay_count)
        depth_k = mullion_depth * (corner_mullion_depth_factor if is_corner else 1.0)

        # Build continuous vertical runs with constant front_y
        run_start = 0
        cur_front = floor_front_y[0]
        for f in range(1, floors + 1):
            next_front = floor_front_y[f] if f < floors else None  # sentinel on last step
            if next_front != cur_front:
                z0 = run_start * floor_to_floor
                z1 = f * floor_to_floor
                brep = _box(x - mullion_width * 0.5, x + mullion_width * 0.5,
                            cur_front - depth_k, cur_front,
                            z0, z1)
                if brep: geoms.append(brep)
                run_start = f
                cur_front = next_front

    # Horizontal transoms, spandrels, glass per floor and bay
    transom_thickness_z = mullion_width  # use mullion face width as transom "height" along Z

    for f in range(floors):
        base_z = f * floor_to_floor
        soffit_z = (f + 1) * floor_to_floor - slab_thickness
        front_y = floor_front_y[f]

        # Enforce clear head >= 2.10 m and avoid conflict with soffit
        head_elev = max(base_z + head, base_z + 2.10)
        # Keep some clearance below soffit for build-up/tolerance
        max_head_elev = soffit_z - (0.05 + tolerance)
        if head_elev > max_head_elev:
            head_elev = max_head_elev

        sill_elev = base_z + sill

        # Transoms at sill/head (span full width)
        # Sill
        tz0 = sill_elev - 0.5 * transom_thickness_z
        tz1 = sill_elev + 0.5 * transom_thickness_z
        brep = _box(0.0, total_width, front_y - transom_depth, front_y, tz0, tz1)
        if brep: geoms.append(brep)
        # Head
        tz0 = head_elev - 0.5 * transom_thickness_z
        tz1 = head_elev + 0.5 * transom_thickness_z
        brep = _box(0.0, total_width, front_y - transom_depth, front_y, tz0, tz1)
        if brep: geoms.append(brep)

        # Per-bay vision glass and spandrel
        for i in range(bay_count):
            x0 = i * bay_width + 0.5 * mullion_width
            x1 = (i + 1) * bay_width - 0.5 * mullion_width

            # Vision glass between transoms
            gz0 = sill_elev + 0.5 * transom_thickness_z
            gz1 = head_elev - 0.5 * transom_thickness_z
            if gz1 > gz0 + tolerance:
                gy1 = front_y - glazing_setback  # front face of glass
                gy0 = gy1 - glass_thickness      # back face of glass inward
                brep = _box(x0, x1, gy0, gy1, gz0, gz1)
                if brep: geoms.append(brep)

            # Spandrel from top of head transom to soffit (top floor +150 mm)
            sz0 = head_elev + 0.5 * transom_thickness_z
            extra_top = 0.15 if (f == floors - 1) else 0.0
            sz1 = soffit_z + extra_top
            if sz1 > sz0 + tolerance:
                sy1 = front_y - glazing_setback
                sy0 = sy1 - spandrel_thickness
                brep = _box(x0, x1, sy0, sy1, sz0, sz1)
                if brep: geoms.append(brep)

    # Slab edges (bands) for each floor slab (span full width, extend inward)
    slab_backset = max(spandrel_thickness, mullion_depth) + 1.0  # generic interior extent
    for f in range(floors):
        z_top = (f + 1) * floor_to_floor
        z_bot = z_top - slab_thickness
        brep = _box(0.0, total_width, -slab_backset, 0.0, z_bot, z_top)
        if brep: geoms.append(brep)

    # Optional fins on every_n mullions (skip corners)
    if fin_enabled and fin_every_n > 0 and fin_depth > tolerance:
        fin_thickness = 0.02  # nominal fin thickness along X
        for k, x in enumerate(mullion_xs):
            if k == 0 or k == bay_count:
                continue
            if (k % fin_every_n) == 0:
                # Place fins projecting outward from main datum (Y=0)
                brep = _box(x - 0.5 * fin_thickness, x + 0.5 * fin_thickness,
                            0.0, fin_depth,
                            0.0, total_height)
                if brep: geoms.append(brep)

    return geoms"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/3
    geometry = build_facade(floors=12, floor_to_floor=3.3, bay_count=10, bay_width=1.6, sill=0.9, head=2.7, mullion_width=0.06, mullion_depth=0.18, transom_depth=0.12, glazing_setback=0.08, spandrel_thickness=0.25, slab_thickness=0.32, glass_thickness=0.032, fin_enabled=True, fin_depth=0.35, fin_every_n=4, podium_levels=(1,2), podium_setback=0.4, corner_mullion_depth_factor=1.25)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/3
    geometry = build_facade(floors=8, floor_to_floor=3.5, bay_count=6, bay_width=1.7, sill=0.85, head=2.5, mullion_width=0.065, mullion_depth=0.14, transom_depth=0.10, glazing_setback=0.06, spandrel_thickness=0.18, slab_thickness=0.28, glass_thickness=0.034, fin_enabled=False, fin_depth=0.3, fin_every_n=3, podium_levels=(1,), podium_setback=0.25, corner_mullion_depth_factor=1.3)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/3
    geometry = build_facade(floors=14, floor_to_floor=3.0, bay_count=7, bay_width=1.5, sill=0.95, head=2.65, mullion_width=0.07, mullion_depth=0.16, transom_depth=0.12, glazing_setback=0.05, spandrel_thickness=0.22, slab_thickness=0.28, glass_thickness=0.03, fin_enabled=True, fin_depth=0.28, fin_every_n=2, podium_levels=(1,2,3), podium_setback=0.35, corner_mullion_depth_factor=1.4)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
