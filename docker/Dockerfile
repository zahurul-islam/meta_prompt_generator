FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/
COPY templates/ ./templates/

# Expose port for Gradio UI
EXPOSE 7860

# Run the application
CMD ["python", "-m", "src.gradio_ui"]
