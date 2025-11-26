""" Summary:
The script creates a parametric facade by mapping design inputs (bay_width, structural_grid, floor_to_floor, sill/head transoms, podium_floors/offset, glazing_inset, spandrel_depth, fin dimensions, max_panel_width, expansion_joint, fin cadences) to geometry. It computes number of bays and floors, then loops floors and bays to place components: primary/secondary mullions, transoms, glazing panels sized to max_panel_width, and conditional fins (respecting podium and cadence). Geometry uses RhinoCommon boxes and plane surfaces converted to Breps. The function returns a list of Breps; the script produces three sample variants, packs them into a Grasshopper DataTree, and prints success."""

#! python 3
function_code = """def generate_facade(bay_width=1.5, structural_grid=6.0, floor_to_floor=3.6, 
                    sill_transom=0.9, head_transom=3.1, podium_floors=2, 
                    podium_offset=0.9, glazing_inset=0.05, spandrel_depth=0.2, 
                    fin_width=0.25, fin_height=0.05, fin_offset=0.15, 
                    max_panel_width=1.65, expansion_joint=30, fin_cadence_east=2, 
                    fin_cadence_west=4):
    \"""
    Generate a facade design with parametric control over grid, datum, and component profiles.

    Parameters:
    - bay_width: Width of each bay in meters.
    - structural_grid: Structural grid span in meters.
    - floor_to_floor: Floor-to-floor height in meters.
    - sill_transom: Sill transom height in meters.
    - head_transom: Head transom height in meters.
    - podium_floors: Number of floors making up the podium.
    - podium_offset: Facade setback at podium in meters.
    - glazing_inset: Inset distance of glazing from facade datum in meters.
    - spandrel_depth: Depth of shadow-box spandrel in meters.
    - fin_width: Width of the vertical fins in meters.
    - fin_height: Height of the vertical fins in meters.
    - fin_offset: Offset distance of fins from mullion centerline in meters.
    - max_panel_width: Maximum panel width in meters.
    - expansion_joint: Distance for expansion joints to appear in meters.
    - fin_cadence_east/west: Cadence of fins on the east and west facades.

    Returns:
    - List of RhinoCommon Breps representing the facade geometries.
    \"""
    import Rhino.Geometry as rg
    import random
    
    random.seed(42)
    geometries = []

    num_bays = int(structural_grid / bay_width)
    num_floors = int(expansion_joint / floor_to_floor)
    
    for floor in range(num_floors):
        for bay in range(num_bays):
            base_x = bay * bay_width
            base_y = 0
            base_z = floor * floor_to_floor

            if floor < podium_floors:
                base_y += podium_offset
            
            # Create primary mullions
            if bay % (structural_grid / bay_width) == 0:
                mullion = rg.Box(
                    rg.Plane(rg.Point3d(base_x, base_y, base_z), rg.Vector3d.ZAxis),
                    rg.Interval(-0.06, 0.06),
                    rg.Interval(0, 0.05),
                    rg.Interval(0, floor_to_floor)
                )
                geometries.append(mullion.ToBrep())
            
            # Create secondary mullions
            mullion = rg.Box(
                rg.Plane(rg.Point3d(base_x, base_y, base_z), rg.Vector3d.ZAxis),
                rg.Interval(-0.0325, 0.0325),
                rg.Interval(0, 0.05),
                rg.Interval(0, floor_to_floor)
            )
            geometries.append(mullion.ToBrep())

            # Create transoms
            for transom_height in [sill_transom, head_transom]:
                transom = rg.Box(
                    rg.Plane(rg.Point3d(base_x, base_y, base_z + transom_height), rg.Vector3d.ZAxis),
                    rg.Interval(-0.0375, 0.0375),
                    rg.Interval(0, bay_width),
                    rg.Interval(0, 0.03)
                )
                geometries.append(transom.ToBrep())

            # Create glazing panel
            panel_width = min(max_panel_width, bay_width - 0.05)
            glazing_panel = rg.PlaneSurface(
                rg.Plane(rg.Point3d(base_x + glazing_inset, base_y, base_z + sill_transom), rg.Vector3d.ZAxis),
                rg.Interval(0, panel_width),
                rg.Interval(0, head_transom - sill_transom)
            )
            geometries.append(glazing_panel.ToBrep())

            # Create fins
            if floor >= podium_floors:
                if bay % fin_cadence_east == 0:
                    fin = rg.Box(
                        rg.Plane(rg.Point3d(base_x + fin_offset, base_y, base_z), rg.Vector3d.XAxis),
                        rg.Interval(0, fin_height),
                        rg.Interval(0, floor_to_floor),
                        rg.Interval(0, fin_width)
                    )
                    geometries.append(fin.ToBrep())

    return geometries"""

try:
    exec(function_code)
    import ghpythonlib.treehelpers as th
    from Grasshopper.Kernel.Data import GH_Path
    geometry_states = []
    # Generate sample geometry 1/3
    geometry = generate_facade(bay_width=1.2, structural_grid=12.0, floor_to_floor=3.3, sill_transom=0.85, head_transom=3.05, podium_floors=3, podium_offset=1.2, glazing_inset=0.06, spandrel_depth=0.25, fin_width=0.2, fin_height=0.06, fin_offset=0.1, max_panel_width=1.5, expansion_joint=36, fin_cadence_east=3, fin_cadence_west=5)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 2/3
    geometry = generate_facade(bay_width=1.5, structural_grid=15.0, floor_to_floor=3.6, sill_transom=0.9, head_transom=3.2, podium_floors=2, podium_offset=0.8, glazing_inset=0.04, spandrel_depth=0.18, fin_width=0.25, fin_height=0.06, fin_offset=0.12, max_panel_width=1.6, expansion_joint=36, fin_cadence_east=4, fin_cadence_west=2)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Generate sample geometry 3/3
    geometry = generate_facade(bay_width=1.25, structural_grid=10.0, floor_to_floor=3.2, sill_transom=0.8, head_transom=3.0, podium_floors=1, podium_offset=0.6, glazing_inset=0.03, spandrel_depth=0.22, fin_width=0.18, fin_height=0.055, fin_offset=0.2, max_panel_width=1.4, expansion_joint=30, fin_cadence_east=3, fin_cadence_west=6)
    geometry = list(geometry) if not isinstance(geometry, list) else geometry
    geometry_states.append(geometry)

    # Convert the list of geometries to a Grasshopper DataTree
    geometry_states = th.list_to_tree(geometry_states)

    print("success")
except Exception as e:
    print("Error: ", e)
