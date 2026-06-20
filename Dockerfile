# Use the official Playwright Python image containing pre-installed browser binaries and system libraries
FROM mcr.microsoft.com/playwright/python:v1.45.0-noble

# Set environment variables to optimize Python performance
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
COPY . .

# Create directory structures for screenshots and logs and set permissions
RUN mkdir -p logs screenshots && chmod -R 777 logs screenshots

# Default command runs the test suite (can be overridden during execution)
CMD ["python", "-m", "pytest", "tests/"]
