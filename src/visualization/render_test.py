import bpy
from pathlib import Path
from mathutils import Vector
from enum import StrEnum
import math
import bpy
import os

def create_collection(name: str, hidden=False):
    if name in bpy.data.collections:
        collection = bpy.data.collections.get(name)
        remove_obj_and_collection(collection=collection)
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    if hidden:
        collection.hide_viewport = True
    return collection

def remove_obj_and_collection(collection):
    for obj in collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    for child in collection.children:
        remove_obj_and_collection(child)
    bpy.data.collections.remove(collection, do_unlink=True)

def get_bounding_box_corners(objs):
    bps = []
    for obj in objs:
        bps.extend([obj.matrix_world @ Vector(corner) for corner in obj.bound_box])
    min_vec = Vector((min(p.x for p in bps), min(p.y for p in bps), min(p.z for p in bps)))
    max_vec = Vector((max(p.x for p in bps), max(p.y for p in bps), max(p.z for p in bps)))
    domain = [max_vec.x - min_vec.x, max_vec.y - min_vec.y, max_vec.z - min_vec.z]
    print (f"Bounding box min: {min_vec}, max: {max_vec}, domain: {domain}")
    return bps, min_vec, max_vec, domain

def set_scene(dir: str, collection_name: str, fit_margin=0.5, res_x=512, res_y=512):
    """
    Moves the camera to fit all objects in the specific collection.
    
    :param camera_obj: The camera object (bpy.types.Object)
    :param collection_name: Name of the target collection (str)
    :param fit_margin: Multiplier to add padding around the objects (default 1.1)
    """
    # clear origin points
    bpy.ops.object.origin_clear()

    # # Remove existing objects in the scene (except cameras and lights)
    for collection in bpy.data.collections:
        remove_obj_and_collection(collection)
    
    # Add collection
    collection = create_collection(collection_name)

    # remove existing cameras and lights
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    # bpy.context.collection = collection
    bpy.ops.wm.obj_import(filepath=dir, up_axis='Z')
    for obj in bpy.context.selected_objects:
        collection.objects.link(obj)
        bpy.context.collection.objects.unlink(obj)

    # Create and assign material with RGB (201, 226, 255)
    obj_mat = bpy.data.materials.new(name="ImportedObjMat")
    obj_mat.use_nodes = True
    bsdf = obj_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (201 / 255, 226 / 255, 255 / 255, 1.0)
    for obj in collection.objects:
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(obj_mat)

    # set render resolution
    scene = bpy.context.scene
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y

    # create camera
    cam_data = bpy.data.cameras.new(name="Camera")
    cam_data.lens = 50 # Focal length
    cam_obj = bpy.data.objects.new(name='Camera', object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Get the collection
    # collection = bpy.data.collections.get(collection_name)
    # if not collection:
    #     print(f"Collection '{collection_name}' not found.")
    #     return

    # Filter for visible types that have geometry
    valid_types = {'MESH', 'CURVE', 'SURFACE', 'VOLUME'}
    geometries = []
    
    for obj in collection.objects:
        if obj.type not in valid_types or obj.hide_viewport:
            continue
        geometries.append(obj)
    
    if not geometries:
        print("No valid geometry objects found in the collection.")
        return
    
    # 2. Calculate the center of the bounding box
    _, min_vec, max_vec, domain = get_bounding_box_corners(geometries)
    
    if min_vec != Vector((0,0,0)):
        for obj in geometries:
            obj.location -= min_vec # Move objects so the minimum corner is at the origin
        print (f"Moved objects by {-min_vec} to set minimum corner at the origin.")
        bpy.context.view_layer.update()  # Flush depsgraph so matrix_world reflects the new location

    _, min_vec, max_vec, domain = get_bounding_box_corners(geometries)
    if domain[-1] == min(domain):
        print ("Warning: Z is the shortest axis.")
        for obj in geometries:
            print (f"Rotating object {obj.name} to make Z the up axis.")
            obj.rotation_euler[0] = math.radians(90) # Rotate 90 degrees around X to make Z the "up" axis
        bpy.context.view_layer.update()  # Flush depsgraph so matrix_world reflects the new location
    
    _, min_vec, max_vec, domain = get_bounding_box_corners(geometries)

    if min_vec != Vector((0,0,0)):
        for obj in geometries:
            obj.location -= min_vec # Move objects so the minimum corner is at the origin
        bpy.context.view_layer.update()  # Flush depsgraph so matrix_world reflects the new location
    
    bps, min_vec, max_vec, domain = get_bounding_box_corners(geometries)
    
    x_dir = True
    if domain[1] < domain[0]:
        x_dir = False

    center = Vector((0,0,0))
    for p in bps:
        center += p/len(bps)

    # 3. Calculate the radius (size) of the bounding sphere
    radius = 0
    for p in bps:
        dist = (p - center).length
        if dist > radius:
            radius = dist
    
    # Get camera data for FOV
    cam_data = cam_obj.data
    fov = cam_data.angle # Horizontal FOV in radians
    
    # Adjust FOV for aspect ratio if necessary (simplified for standard horizontal fit)
    aspect_ratio = res_x/res_y
    
    # If the render is portrait (taller than wide), the vertical FOV is the limiting factor
    if aspect_ratio < 1.0:
        fov = 2 * math.atan(math.tan(fov / 2) * (1 / aspect_ratio))

    # Trigonometry: Distance = Radius / sin(FOV / 2) 
    # Using sin ensures the whole sphere fits. using tan fits the plane. 
    # sin is safer for arbitrary rotations.
    distance = (radius * fit_margin) / math.sin(fov / 2)
    print (distance)

    # Calculate new camera position
    # Direction vector (camera looking down its local -Z)
    # We rotate the vector (0,0,1) by the camera's rotation to find "backward"
    if x_dir:
        direction_back = cam_obj.matrix_world.to_quaternion() @ Vector((1, 0, 0))
    else:
        direction_back = cam_obj.matrix_world.to_quaternion() @ Vector((0, 1, 0))
    
    # Set location: Center of object + (Backwards direction * Distance)
    cam_obj.location = center + (direction_back * distance)
    
    # Set camera tracking
    target_name = "camera_target"
    target = bpy.data.objects.get(target_name)
    
    if not target:
        target = bpy.data.objects.new(target_name, None) # None = Empty
        bpy.context.collection.objects.link(target)
        target.location = (center.x, center.y, center.z)
        target.empty_display_size = 0.5  # Make it small and unobtrusive
    
    constraint = cam_obj.constraints.new(type='TRACK_TO')
    constraint.target = target

    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    print (x_dir)
    # Add light
    light_data = bpy.data.lights.new(name="Light", type='SUN')
    light_data.angle = math.radians(150) # Soft shadows
    light_data.energy = 10
    light_obj = bpy.data.objects.new(name="Light", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    if x_dir:
        light_obj.location = (cam_obj.location.x/4, min_vec.y, max_vec.z)
    else:
        pass
    
    constraint = light_obj.constraints.new(type='TRACK_TO')
    constraint.target = target

    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    # Add a ground plane
    bpy.ops.mesh.primitive_plane_add(size=500, location=(0, 0, min_vec.z), calc_uvs=True )
    for obj in bpy.context.selected_objects:
        obj.name = "Ground"

    # Add back plane material
    bp_mat = bpy.data.materials.new(name="ImportedObjMat")
    bp_mat.use_nodes = True
    bsdf = bp_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (.196, .196, .196, 1.0)

    # Add a back plane
    if x_dir:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(min(min_vec.x-domain[0]/50, min_vec.x-.01), center.y, center.z), rotation=(0,math.radians(90), 0), calc_uvs =True)
        for obj in bpy.context.selected_objects:
            obj.name = "BackPlane"
            obj.scale = (domain[2], domain[1], 1)
            obj.data.materials.clear()
            obj.data.materials.append(bp_mat)
            collection.objects.link(obj)
            bpy.context.collection.objects.unlink(obj)
    else:
        pass
    bpy.context.view_layer.update()  # Flush depsgraph so matrix_world reflects the new location

    # Add grease pencil line art
    gp_data = bpy.data.grease_pencils_v3.new("LineArt")
    gp_obj = bpy.data.objects.new("LineArt", gp_data)
    bpy.context.collection.objects.link(gp_obj)  # must be linked before assigning material to modifier

    # Create a black stroke material and add to the object BEFORE referencing it in the modifier
    mat = bpy.data.materials.new("LineArtMat")
    mat.diffuse_color = (0, 0, 0, 1)
    bpy.data.materials.create_gpencil_data(mat)
    gp_obj.data.materials.append(mat)

    # Add a drawing layer
    layer = gp_data.layers.new("Lines", set_active=True)

    # Add Line Art modifier targeting the geometry collection
    la_mod = gp_obj.modifiers.new(name="LineArt", type='LINEART')
    la_mod.target_layer = layer.name
    la_mod.target_material = mat
    la_mod.thickness = int(distance)
    la_mod.source_type = 'COLLECTION'
    la_mod.source_collection = collection
    la_mod.stroke_depth_offset = 0.05

    # Set up world background gradient based on camera ray direction
    set_world_background()

def set_world_background():
    """
    Sets the world background to a gradient that mixes between a horizon colour
    and a zenith colour based on the Z component of the incoming camera ray.
    """
    world = bpy.data.worlds.get("World")
    if not world:
        world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True

    nt = world.node_tree
    nt.nodes.clear()

    # --- nodes ---
    output_node   = nt.nodes.new('ShaderNodeOutputWorld')
    bg_node       = nt.nodes.new('ShaderNodeBackground')
    mix_node      = nt.nodes.new('ShaderNodeMixRGB')
    light_path_node = nt.nodes.new('ShaderNodeLightPath')

    mix_node.inputs['Color1'].default_value = (0, 0, 0, 1) # Horizon colour
    mix_node.inputs['Color2'].default_value = (1, 1, 1, 1)
    bg_node.inputs['Strength'].default_value = 2.0

    # # --- links ---
    nt.links.new(light_path_node.outputs['Is Camera Ray'], mix_node.inputs[0])  
    nt.links.new(mix_node.outputs['Color'], bg_node.inputs['Color'])
    nt.links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])

def render_scene(output_path: str):
    """
    Renders the current scene to the specified output path.
    
    :param output_path: File path to save the rendered image (str)
    """
    scene = bpy.context.scene
    # scene.render.resolution_x = 512
    # scene.render.resolution_y = 512
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

input_dir = Path.cwd() / 'experiment_dms26_baseline'

if __name__ == "__main__":
    for dir in input_dir.iterdir():
        if dir.is_dir() and 'R' in dir.name:
            print (f"Processing directory: {dir}")
            for file in dir.iterdir():
                if file.suffix.lower() == '.obj':
                    print (f"Processing file: {file.name}")
                    set_scene(dir=str(file), collection_name="Collection", fit_margin=1.0)
                    render_scene(output_path=str(file.parent / f"{file.stem.split('_')[0]}_render.png"))
    # file = r"C:\Users\chewei\Documents\github\MAS_LLM_Workshop_25\experiment_dms26_baseline\R04_clay\00_render.obj"
    # set_scene(dir=str(file), collection_name="Collection", fit_margin=1.0)