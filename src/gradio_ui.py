"""Gradio UI for the Meta Prompt Generator."""

import os
import sys
import gradio as gr
import logging
from typing import Dict, Any, Tuple

# Add the parent directory to the path if needed
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.prompt_generator import MetaPromptGenerator
from src.llm_client import LLMClient
from src.config import OPENROUTER_MODEL, BACKUP_MODELS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the LLM client and Meta Prompt Generator
llm_client = LLMClient()
generator = MetaPromptGenerator(llm_client=llm_client)

# Example prompts for the UI
EXAMPLE_PROMPTS = [
    "Prompt that extracts total gross, total net, business name and a list of items including product name and price data as a JSON structure",
    "Create a prompt to extract sender information, recipient details, date, subject line, and the body text from email content",
    "Generate a prompt to extract all legal entities, contract dates, obligations, and key terms from legal documents",
    "Extract shipping information, order number, customer details, and payment method from order confirmations",
    "Pull out meeting details like participants, date, time, agenda items, and action items from meeting minutes"
]

def generate_prompt(query: str, temperature: float, model_selection: str) -> Tuple[str, Dict[str, Any]]:
    """Generate a prompt based on the user's query.
    
    Args:
        query: The user's query
        temperature: The temperature for generation (0.0-1.0)
        model_selection: The selected model
        
    Returns:
        Tuple containing the generated prompt and metadata
    """
    try:
        # Update the model if necessary
        if model_selection != llm_client.model:
            logger.info(f"Switching to model: {model_selection}")
            llm_client.model = model_selection
        
        # Generate the extraction prompt
        logger.info(f"Generating prompt for query: {query}")
        generated_prompt = generator.generate_extraction_prompt(query)
        
        # Post-process the prompt
        final_prompt = generator.post_process_prompt(generated_prompt)
        
        # Check if we got an error message
        if "Error generating prompt" in final_prompt:
            status = "warning"
            message = "Used fallback generation due to API issues. The prompt may be generic."
        else:
            status = "success"
            message = "Prompt generated successfully!"
        
        # Return the prompt and metadata
        metadata = {
            "query": query,
            "temperature": temperature,
            "model": llm_client.model,
            "status": status,
            "message": message
        }
        
        return final_prompt, metadata
    
    except Exception as e:
        logger.error(f"Error generating prompt: {str(e)}")
        # Generate a fallback prompt
        fallback_prompt = generator._generate_fallback_prompt(query)
        
        return fallback_prompt, {
            "status": "error", 
            "message": f"Error: {str(e)}. Used fallback template.",
            "query": query,
            "temperature": temperature,
            "model": llm_client.model
        }

def create_ui():
    """Create the Gradio UI for the Meta Prompt Generator."""
    
    # Combine the primary model with backup models
    all_models = [OPENROUTER_MODEL] + [m for m in BACKUP_MODELS if m != OPENROUTER_MODEL]
    
    # Create the UI
    with gr.Blocks(title="Meta Prompt Generator", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # Meta Prompt Generator
            
            Generate high-quality prompts for data extraction tasks. Simply describe what data you need to extract,
            and the system will generate a prompt that you can use with any LLM to extract structured data from your documents.
            """
        )
        
        with gr.Row():
            with gr.Column(scale=2):
                # Input components
                query_input = gr.Textbox(
                    label="Describe the data extraction task",
                    placeholder="E.g., Extract total gross, total net, business name and items from invoice",
                    lines=4
                )
                
                with gr.Row():
                    temperature_slider = gr.Slider(
                        label="Temperature",
                        minimum=0.0,
                        maximum=1.0,
                        value=0.5,
                        step=0.1,
                        info="Lower = more precise, higher = more creative"
                    )
                    
                    model_dropdown = gr.Dropdown(
                        label="Model",
                        choices=all_models,
                        value=all_models[0],
                        info="Select the model to use for prompt generation"
                    )
                
                # Generate button
                generate_button = gr.Button("Generate Prompt", variant="primary")
                
                # Status message
                status_message = gr.Markdown("")
                
                # Examples
                gr.Examples(
                    examples=EXAMPLE_PROMPTS,
                    inputs=query_input,
                    label="Example Tasks"
                )
            
            with gr.Column(scale=3):
                # Output components
                prompt_output = gr.Textbox(
                    label="Generated Prompt",
                    placeholder="Your generated prompt will appear here...",
                    lines=15,
                    show_copy_button=True
                )
                
                # Metadata output (hidden by default)
                with gr.Accordion("Request Details", open=False):
                    metadata_output = gr.JSON(label="Metadata")
                
                # Usage instructions
                with gr.Accordion("How to Use", open=True):
                    gr.Markdown(
                        """
                        ## How to use this prompt:
                        
                        1. Copy the generated prompt above
                        2. Replace `{file_content}` with your actual document text
                        3. Send the complete prompt to your preferred LLM
                        4. The LLM will extract the data in the requested format (typically JSON)
                        
                        ### Troubleshooting:
                        
                        If you encounter API errors:
                        - Try a different model from the dropdown
                        - Check your internet connection
                        - The system will automatically use templates if the API is unavailable
                        """
                    )
        
        # Set up the event handlers
        def update_status(metadata):
            if metadata and "status" in metadata and "message" in metadata:
                status = metadata["status"]
                message = metadata["message"]
                
                if status == "success":
                    return f"✅ {message}"
                elif status == "warning":
                    return f"⚠️ {message}"
                elif status == "error":
                    return f"❌ {message}"
            
            return ""
        
        generate_button.click(
            fn=generate_prompt,
            inputs=[query_input, temperature_slider, model_dropdown],
            outputs=[prompt_output, metadata_output]
        ).then(
            fn=update_status,
            inputs=[metadata_output],
            outputs=[status_message]
        )
        
        # Optional keyboard shortcut
        query_input.submit(
            fn=generate_prompt,
            inputs=[query_input, temperature_slider, model_dropdown],
            outputs=[prompt_output, metadata_output]
        ).then(
            fn=update_status,
            inputs=[metadata_output],
            outputs=[status_message]
        )
    
    return demo

if __name__ == "__main__":
    # Create and launch the UI
    demo = create_ui()
    demo.launch(share=True)
