import base64
import json
from dotenv import load_dotenv
from ria.instructions import load_instruction
from ria.utils import load_images, json_load, json_dump, load_text
import os
from enum import Enum
import questionary

# import from pydantic ai
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
import logfire

# import from pydantic
from pydantic import BaseModel, Field, ValidationError

load_dotenv(override=True)

# 01 -- DEFINE THE LLM MODEL AND OTHER CONSTANTS.
#__________________________________________________________________________________________

MODEL_NAME_DEFAULT = "gpt-5"

# INPUT_IMAGE_COUNT = 5

# def check_scores(scores: list[int] | None):
#     if scores:
#         if len(scores) != INPUT_IMAGE_COUNT:
#             raise ValidationError(f"Scores must be a list of {INPUT_IMAGE_COUNT} integers.")
#         for v in scores:
#             if v < 1 or v > 5:
#                 raise ValueError("Score must be between 1 and 5")
#     return scores

# 02 -- STATE ONE CLASS PER EACH METRIC YOU WANT TO EVALUATE. HERE IS A SAMPLE:
#__________________________________________________________________________________________

class ImprovementTarget(str, Enum):
    DESIGN_CONCEPT = "design_concept"
    DESIGN_MODELING = "design_modeling"
    DESIGN_GEOMETRY = "design_geometry"

class TectonicFramework(BaseModel):
    scores: int | None = Field(
        default=None,
        description="Does the design concept provide clear step-by-step instructions to generate procedural 3D facade geometries? Is it enough to inform a specific tectonic character to the resulting geometry? Ranging from 1 to 5. Low score=1: The design concept is bland, ambiguous and lacks tectonic specificity to become clear step-by-step instructions on how to model the intended facade. High score=5: The design task embodies material cues and expands them with relevant dimensions, formal and spatial implications, facade system and building components, clearly translating them into material-specific and concise modeling steps.",
    )
    explanation: str | None = Field(
        default=None,
        description="Explain your reasoning for the scores given above. Provide specific observations that support your evaluation of the design concept and its capability to direct the generation of an architectural facade geometry.",
    )
    
class FacadePotential(BaseModel):
    scores: int | None = Field(
        default=None,
        description="Does the image represent an elevation of a potential facade? Ranging from 1 to 5. Low score=1: The rendered image could be any geometry and does not resemble at all the elevation of a facade. High score=5: By observing the image, one can easily identify an elevation of a geometry that, even at a conceptual level, reads visible composition rules, credible proportions and/or relevant components that clearly communicate the potential to be developed into a real facade.",
    )
    explanation: str | None = Field(
        default=None,
        description="Explain your reasoning for the scores given above. Provide specific observations from the image and/or the .py function that support your evaluation of the facade potential.",
    )

class MaterialSpecificity(BaseModel):
    scores: int | None = Field(
        default=None,
        description="By observing the rendered image, and judging only by its geometrical cues, can you tell which material it is built of? Ranging from 1 to 5. Low score=1: The rendered image represents an ambiguous or highly generic geometry either with insufficient material cues or with cues that do not align at all with the material described in the design concept. High score=5: By observing the geometry rendered in the image, one can easily identify the material it is made of and, if the design concept describes a specific material, the generated facade geometry clearly embodies that material's inherent characteristics.",
    )
    explanation: str | None = Field(
        default=None,
        description="Explain your reasoning for the scores given above. Provide specific observations from the image, the .py function and the design task that support your evaluation of the material specificity.",
    )

# 03 -- OPTIONAL. DEFINE A CLASS TO SUGGEST IMPROVEMENTS BASED ON THE EVALUATIONS.
#__________________________________________________________________________________________
class ImprovementProposal(BaseModel):
    improvement_target: ImprovementTarget | None = Field(
        default=None,
        description="Based on your evaluations, which of the following 3 aspects would you prioritize for improvement? Choose only one: design concept, modeling function or overall geometry.",
    )
    improvement_proposal: str | None = Field(
        default=None,
        description="State a brief improvement proposal for the selected target, with concise language and 3 specific bulletpoints or actions to take.",
    )

# 04 -- BUILD THE EVALUATION AGENT.
#__________________________________________________________________________________________
class EvaluationAgent:
    def __init__(self, model_name=MODEL_NAME_DEFAULT, logfire_debug=True):
        # Initialize logfire for logging
        if logfire_debug:
            logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
            logfire.instrument_openai()
            
        # Initialize the OpenAI model with the specified model name
        model = OpenAIChatModel(
            model_name=model_name,
            provider=OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
            )

        self.agent = Agent(model=model, deps_type=str)

        @self.agent.instructions
        def concept_instructions(ctx: RunContext[str]) -> str:
            prompt = load_instruction(ctx.deps, ext="md")
            return prompt

# 05 -- DEFINE HOW TO RUN THE EVALUATIONS AND WHAT DATA TO LOOK AT IN EACH STEP.  
#__________________________________________________________________________________________

    def evaluate_design(self, path: str) -> None:
        print (f"validating files integrity in {path}...")

        # load design driver
        file = os.path.join(path, "design_driver.json")
        if not os.path.exists(file):
            raise FileNotFoundError(f"design_driver.json not found")
        design_driver = json_load(file)

        # load user task
        design_concept = design_driver.get("task")
        material = design_driver.get("material")

         # load reference images
        ref_img_data = load_images(design_driver.get("reference_images"))

        # load render images
        render_data = load_images([os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.png', '.jpeg', '.gif', '.webp'))])

        # load generated script 
        file = os.path.join(path, "gh_function.py")
        if not os.path.exists(file):
            raise FileNotFoundError(f"gh_function.py not found")
        gh_python_script = load_text(file)
        
        print ("files validated. running evaluation...")

        framework_score = self.agent.run_sync(
            user_prompt=[
                f"Evaluate the overall strength of the driver {design_driver}, using also the reference image if provided.",
                f"Evaluate the overall strength of the design task {design_concept}, and its capability to integrate a specific material {material} and its tectonic consequences to generate modeling instructions. To do so, you can also check the python code that is generated after the design task instructions.",
                f"code: {gh_python_script}", 
                *ref_img_data
            ],
            deps='evaluation_01_framework_system',
            output_type=TectonicFramework
        ).output

        facadeness_score = self.agent.run_sync(
            user_prompt=[
                f"Evaluate how well does the rendered image represent an elevation of a potential facade.",
                f"To do so, look at the render data and the python code that generates the model: {gh_python_script}. You can also check the design concept {design_concept} to see the original intentions and instructions for the design and complement your assessment.", 
                *render_data,
            ],
            deps='evaluation_02_facadeness_system',
            output_type=FacadePotential
        ).output

        materiality_score = self.agent.run_sync(
            user_prompt=[
                f"Evaluate if a specific construction material can be depicted from the rendered image, judging only by the geometrical cues represented in the rendered image.",
                f"To complement your assessment, you can also check the python code that generates the model: {gh_python_script} and the specific material {material} that was specified in the design driver.", 
                *render_data,
            ],
            deps='evaluation_03_materiality_system',
            output_type=MaterialSpecificity
        ).output

        # Extract scores as floats
        scores = [
            float(framework_score.scores) if framework_score.scores else None,
            float(facadeness_score.scores) if facadeness_score.scores else None,
            float(materiality_score.scores) if materiality_score.scores else None,
        ]
        # Filter out None values
        valid_scores = [s for s in scores if s]
        average_score = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else None

        # Generate improvement proposal
        improvement = self.agent.run_sync(
            user_prompt=[
                "Based on the previous evaluations and scores, choose the weakest segment in the pipeline OR the segment whose improvement would have the most significant impact, and provide an improvement proposal",
                f"Tectonic framework: {framework_score}",
                f"Facade potential: {facadeness_score}",
                f"Material specificity: {materiality_score}",
            ],
            deps='evaluation_04_improvement_system',
            output_type=ImprovementProposal
        ).output

        # Return all scores and improvement proposal as a dictionary
        json_dump(
            dict(
                tectonic_framework=framework_score.model_dump(),
                facade_potential=facadeness_score.model_dump(),
                material_specificity=materiality_score.model_dump(),
                average_score=average_score,
                improvement_proposal=improvement.model_dump()
            ),
            os.path.join(path, "evaluation_report.json")
        )

        print ("Evaluation completed. Report saved to evaluation_report.json")