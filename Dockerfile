# Use the official Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /web

# Install system dependencies for Django, Tailwind, and npm
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libpq-dev \
    npm \
    && apt-get clean

# Install pipenv or pip for managing dependencies (if you use pipenv)
RUN pip install --upgrade pip

# Copy the requirements.txt (if using pip) or Pipfile (if using pipenv) and install dependencies
COPY requirements.txt .

RUN pip install -r requirements.txt

# If you're using pipenv, uncomment the next lines
# COPY Pipfile* ./
# RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

# Copy the Django project files into the container
COPY . .

# Install Tailwind CSS and DaisyUI
# Must install datatables manually
#WORKDIR /web/app/static/js
# RUN npm install tailwindcss daisyui htmx flatpickr
# RUN npm run tailwind-watch
# RUN npm run tailwind-build

# Return to app root directory
WORKDIR /web

# Collect static files (if needed)
RUN python manage.py collectstatic --noinput

# Expose port 8000 (Django default)
EXPOSE 8000

ENV VIRTUAL_ENV /web/.env
# ENV PATH /env/bin:$PATH

# Run migrations and start Django server
CMD ["python", "manage.py", "migrate" , "&&", "python", "manage.py", "makemigrations"]