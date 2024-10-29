# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the victim app will run on
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_APP=app.py

# Run the victim app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
