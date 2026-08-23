# Use an official lightweight Python runtime
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /workspace

# Copy only requirements first to leverage Docker's caching mechanism
COPY requirements.txt .

# Install requirements without storing cache files to keep image size small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining frontend code
COPY . .

# Expose Streamlit's default port to allow host access
EXPOSE 8501

# Execute Streamlit listening on all network interfaces
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]