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
    # Get list of available reference images
    available_images = []
    for img_file in os.listdir(IMAGE_PATH):
        suffix = pathlib.Path(img_file).suffix.lower()
        if suffix in ['.png', '.jpeg', '.gif', '.webp', '.jpg']:
            available_images.append(img_file)
    
    # Let user select a reference image
    if not available_images:
        print("No reference images found in _reference_images folder!")
        exit(1)
    
    print("\nAvailable reference images:")
    for i, img in enumerate(available_images, 1):
        print(f"{i}. {img}")
    
    selection = int(input("\nSelect image number: ")) - 1
    selected_image = available_images[selection]
    selected_image_path = os.path.join(IMAGE_PATH, selected_image)
    
    # Extract image name without extension
    image_name = pathlib.Path(selected_image).stem
    
    ########################################################################## 
    # USER PROMPT: This is where you define the material for the modeling agent.
    material = "timber"  
    task = "Generate a script for a 3D geometry that represents a facade on the XZ plane, based on the reference image and the selected material"
    improvement = None
    ##########################################################################  
 
    # Create output folder name: {image_name}_{material}
    label = f"{image_name}_{material}"
    output_dir = os.path.join(OUTPUT_FOLDER, label)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    previous_renders = []
    if os.path.exists(PREV_ITERATION_FOLDER):
        for img_file in os.listdir(PREV_ITERATION_FOLDER):
            suffix = pathlib.Path(img_file).suffix.lower()
            if suffix in ['.png', '.jpeg', '.gif', '.webp', '.jpg']:
                previous_renders.append(os.path.join(PREV_ITERATION_FOLDER, img_file))
    

    # OPTIONAL: Add reference_images=IMAGE_FOLDER if any.
    modeling_agent = ParametricModelingAgent()
    #modeling_agent.generate_code(user_task=task, output_dir=output_dir, reference_images=previous_renders, improvement_proposal=improvement)
    modeling_agent.generate_code(
        user_task=task, 
        output_dir=output_dir, 
        reference_images=[selected_image_path],
        material=material
    )