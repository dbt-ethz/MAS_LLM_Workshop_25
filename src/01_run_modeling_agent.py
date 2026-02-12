import os
from ria.agents.modeling_agent import ParametricModelingAgent
import pathlib

OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "experiment_dms26_baseline")
PREV_ITERATION_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "experiment_dms26_baseline", "baseline_01")
IMAGE_PATH = os.path.join(OUTPUT_FOLDER, '_reference_images')

def get_output_padding(dir):
    pad = 0
    for folder in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, folder)):
            pad += 1
    return str(pad).zfill(2)

if __name__ == "__main__":
    id = get_output_padding(OUTPUT_FOLDER)
    label = 'baseline'

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
    task = "Generate a parametric model of a facade for a building of 6 meters width and 12 meters height. If a reference image is provided, use it as a guide. If not, use your own internal logic as a driver concept."
    improvement = None

    # OPTIONAL: Add reference_images=IMAGE_FOLDER if any.
    modeling_agent = ParametricModelingAgent()
    #modeling_agent.generate_code(user_task=task, output_dir=output_dir, reference_images=previous_renders, improvement_proposal=improvement)
    modeling_agent.generate_code(user_task=task, output_dir=output_dir, reference_images=None, improvement_proposal=improvement)