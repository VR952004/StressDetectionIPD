FROM python:3.11

# Set the working directory in the container
WORKDIR /code

# Copy the whole current directory to the container
COPY . /code

# Install the dependencies
RUN pip install --no-cache-dir -r /code/requirements.txt

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]