import os
import json
import pandas as pd
import glob

TEST_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "_reference_images")
OUTPUT_DIR = os.path.dirname(__file__)  # experiment_dms26_baseline directory itself

def parse_results(base_dir) -> pd.DataFrame:
    """
    Parse results from project folders (e.g., R01_clay, R02_concrete) 
    within the experiment_dms26_baseline directory.
    Each folder contains design_driver.json, evaluation_report.json, and render images.
    """
    test_images = os.listdir(TEST_IMAGES_DIR)
    columns = [
        "project_folder",
        "run_number",
        "material",
        "reference_image_path",
        "render_image_path",
        "tectonic_framework",
        "facade_potential",
        "material_specificity",
        "average_score",
        "improvement_target",
        "improvement_proposal",
        "total_iterations",
    ]

    df = pd.DataFrame(columns=columns)

    # Get all subdirectories in base_dir that match the pattern R##_material
    project_folders = [d for d in os.listdir(base_dir) 
                      if os.path.isdir(os.path.join(base_dir, d)) 
                      and d.startswith('R')]
    
    for folder_name in sorted(project_folders):
        folder_path = os.path.join(base_dir, folder_name)
        
        # Check for required files
        design_driver_path = os.path.join(folder_path, "design_driver.json")
        evaluation_report_path = os.path.join(folder_path, "evaluation_report.json")
        
        if not os.path.exists(design_driver_path):
            print(f"Warning: design_driver.json not found in {folder_name}, skipping...")
            continue
        
        if not os.path.exists(evaluation_report_path):
            print(f"Warning: evaluation_report.json not found in {folder_name}, skipping...")
            continue
        
        # Read design_driver.json
        with open(design_driver_path, "r") as f:
            design_driver = json.load(f)
        
        # Read evaluation_report.json
        with open(evaluation_report_path, "r") as f:
            evaluation_report = json.load(f)
        
        # Find all render images in the folder (e.g., 00_render.png, 01_render.png, etc.)
        render_images = sorted(glob.glob(os.path.join(folder_path, "*_render.png")))
        
        if not render_images:
            print(f"Warning: No render images found in {folder_name}, skipping...")
            continue
        
        # Get reference image
        reference_number = folder_name.split("_")[0]  # e.g., "R01"
        reference_image_path = None
        for img in test_images:
            if reference_number in img:
                reference_image_path = os.path.join(TEST_IMAGES_DIR, img)
                break
        
        if reference_image_path is None:
            print(f"Warning: Reference image not found for {folder_name}")
        
        # Get material from design_driver
        material = design_driver.get("material", "unknown")
        
        # Get progress log if available
        progress_log_path = os.path.join(folder_path, "progress_log.json")
        total_iterations = None
        if os.path.exists(progress_log_path):
            with open(progress_log_path, "r") as f:
                progress_log = json.load(f)
                if progress_log:
                    total_iterations = len(progress_log)
        
        # Create a row for each render image
        for render_image_path in render_images:
            row_data = {}
            
            # Extract run number from filename (e.g., "00_render.png" -> 0)
            run_number = os.path.basename(render_image_path).split("_")[0]
            
            row_data["project_folder"] = folder_name
            row_data["run_number"] = int(run_number)
            row_data["material"] = material
            row_data["reference_image_path"] = reference_image_path
            row_data["render_image_path"] = render_image_path
            
            # Get evaluation scores
            row_data["tectonic_framework"] = evaluation_report.get("tectonic_framework", {}).get("scores")
            row_data["facade_potential"] = evaluation_report.get("facade_potential", {}).get("scores")
            row_data["material_specificity"] = evaluation_report.get("material_specificity", {}).get("scores")
            row_data["average_score"] = evaluation_report.get("average_score")
            
            # Get improvement proposal
            improvement = evaluation_report.get("improvement_proposal", {})
            row_data["improvement_target"] = improvement.get("improvement_target")
            row_data["improvement_proposal"] = improvement.get("improvement_proposal")
            
            row_data["total_iterations"] = total_iterations
            
            df.loc[len(df)] = row_data
    
    return df

if __name__ == "__main__":
    df = parse_results(base_dir=OUTPUT_DIR)
    
    # Save to CSV in the experiment_dms26_baseline directory
    output_csv_path = os.path.join(OUTPUT_DIR, "parsed_results.csv")
    df.to_csv(output_csv_path, index=False)
    
    print(f"\nParsing complete!")
    print(f"Total rows: {len(df)}")
    print(f"Output saved to: {output_csv_path}")
    print(f"\nSummary by material:")
    print(df.groupby('material').size())