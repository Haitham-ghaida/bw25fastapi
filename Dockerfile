# Use an official Python runtime
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Create the Brightway3 directory in the container to ensure it exists
RUN mkdir -p /.local/share/Brightway3

# Optionally, ensure the directory is writable by the non-root user
# This step depends on whether you run the container as a non-root user
# RUN chmod -R 777 /root/.local/share/Brightway3

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
