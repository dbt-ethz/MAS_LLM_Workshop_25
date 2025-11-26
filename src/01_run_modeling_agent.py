import os
from ria.agents.modeling_agent import ParametricModelingAgent
import pathlib

OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
PREV_ITERATION_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "21_demo")
IMAGE_PATH = os.path.join(OUTPUT_FOLDER, '00_reference_images')

def get_output_padding(dir):
    pad = 0
    for folder in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, folder)):
            pad += 1
    return str(pad).zfill(2)

if __name__ == "__main__":
    id = get_output_padding(OUTPUT_FOLDER)
    label = 'demo'

    output_dir = os.path.join(OUTPUT_FOLDER, f"{id}_{label}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    reference_images=[]
    for img_file in os.listdir(IMAGE_PATH):
        suffix=pathlib.Path(img_file).suffix.lower()
        if suffix in ['.png', '.jpeg', '.gif', '.webp']:
            reference_images.append(os.path.join(IMAGE_PATH, img_file))
    
    previous_renders=[]
    for img_file in os.listdir(PREV_ITERATION_FOLDER):
        suffix=pathlib.Path(img_file).suffix.lower()
        if suffix in ['.png', '.jpeg', '.gif', '.webp']:
            previous_renders.append(os.path.join(PREV_ITERATION_FOLDER, img_file))

    # USER PROMPT: This is where you define the task for the modeling agent.
    task = "You will receive an image representing the axonometric view of a facade. Generate another 3D model of that facade, improving the previous design according to the improvement proposal stated below. If there is no image, imagine the section of the facade represents a cladding with tilted tiles"
    improvement = "- Establish explicit grid and vertical datums: bay_width=1.5 m; structural_grid=6.0 m (4 bays); floor_to_floor=3.6 m; sill_transom=0.9 m; head_transom=3.1 m; spandrel zone from finished slab to 0.5 m below slab above; podium = first 2 floors with 0.9 m facade setback.\n- Define component profiles and offsets for character: primary mullion 120\u00d750 at structural grid; secondary mullion 65\u00d735 at each bay; transoms 75\u00d735 at sill/head; glazing inset 50 mm from facade datum; shadow-box spandrel depth 200 mm; vertical fins 250\u00d750 every 3rd bay, 150 mm off mullion centerline; fins off within podium zone.\n- Encode variation and constraints: max panel width 1.65 m with snap to 1.5 m module; align primary mullions to expansion joints every 30 m; at corners, wrap with 150 mm return; per-elevation overrides (east fin cadence=2, west=4); all dimensions parametric with \u00b110 mm tolerance to preserve module continuity across setbacks."

    # OPTIONAL: Add reference_images=IMAGE_FOLDER if any.
    modeling_agent = ParametricModelingAgent()
    modeling_agent.generate_code(user_task=task, output_dir=output_dir, reference_images=previous_renders, improvement_proposal=improvement)