import os
from ria.agents.evaluation import EvaluationAgent

OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "experiment_dms26_baseline")

if __name__ == "__main__":
    # Get all folders except _reference_images
    all_folders = [d for d in os.listdir(OUTPUT_FOLDER) 
                   if os.path.isdir(os.path.join(OUTPUT_FOLDER, d)) 
                   and d != "_reference_images"]

    if not all_folders:
        print("No design folders found in the experiment directory.")
        exit(0)
    
    print(f"Found {len(all_folders)} folders to evaluate.")
    
    # Process each folder
    eval_agent = EvaluationAgent()
    
    for idx, design_folder in enumerate(sorted(all_folders), 1):
        design_path = os.path.join(OUTPUT_FOLDER, design_folder)
        report_path = os.path.join(design_path, 'evaluation_report.json')
        
        print(f"\n[{idx}/{len(all_folders)}] Processing: {design_folder}")
        
        # Skip if evaluation report already exists
        if os.path.exists(report_path):
            print(f"  Skipping - evaluation report already exists")
            continue
        
        # Run evaluation
        try:
            eval_agent.evaluate_design(design_path)
            print(f"  ✓ Completed evaluation for {design_folder}")
        except Exception as e:
            print(f"  ✗ Error evaluating {design_folder}: {str(e)}")
    
    print(f"\n✓ Batch evaluation complete!")