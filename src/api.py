"""FastAPI server for the Meta Prompt Generator."""

import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.prompt_generator import MetaPromptGenerator
from src.llm_client import LLMClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the application
app = FastAPI(
    title="Meta Prompt Generator API",
    description="API for generating data extraction prompts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the LLM client and Meta Prompt Generator
llm_client = LLMClient()
generator = MetaPromptGenerator(llm_client=llm_client)

# Request model
class PromptRequest(BaseModel):
    """Request model for prompt generation."""
    
    query: str = Field(..., 
                      description="User query for data extraction prompt generation",
                      example="Prompt that extracts total gross, total net, business name and a list of items including product name and price data as a JSON structure")
    temperature: Optional[float] = Field(0.5, 
                                       description="Temperature for LLM generation (0.0-1.0)",
                                       ge=0.0, le=1.0)

# Response model
class PromptResponse(BaseModel):
    """Response model for prompt generation."""
    
    prompt: str = Field(..., description="Generated data extraction prompt")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the prompt generation")

@app.post("/generate-prompt", response_model=PromptResponse)
async def generate_prompt(request: PromptRequest):
    """Generate a data extraction prompt based on user request."""
    try:
        # Generate the extraction prompt
        generated_prompt = generator.generate_extraction_prompt(request.query)
        
        # Post-process the prompt
        final_prompt = generator.post_process_prompt(generated_prompt)
        
        # Prepare the response
        response = PromptResponse(
            prompt=final_prompt,
            metadata={
                "query": request.query,
                "temperature": request.temperature
            }
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error generating prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
