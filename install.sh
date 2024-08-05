#!/bin/bash

# Constants
VENV_DIR="venv"
ENV_TEMPLATE=".env-template"
ENV_FILE=".env"
REQUIREMENTS_FILE="requirements.txt"

# Function to print colored messages
print_message() {
    local COLOR=$1
    local MESSAGE=$2
    echo -e "${COLOR}${MESSAGE}\033[0m"
}

# Colors
RED="\033[0;31m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
YELLOW="\033[0;33m"

# Create a virtual environment
print_message $CYAN "### Creating virtual environment..."
python3 -m venv $VENV_DIR

# Set settings .env variables
print_message $CYAN "### Setting up .env variables..."
if [ -f "$ENV_TEMPLATE" ]; then
    cp $ENV_TEMPLATE $ENV_FILE
    print_message $GREEN "Environment variables file created. Please edit $ENV_FILE with appropriate values."
else
    print_message $RED "Error: $ENV_TEMPLATE not found!"
    exit 1
fi

# Bootstrap the project
print_message $CYAN "### Bootstrapping the project..."
source ./$VENV_DIR/bin/activate

if [ -f "$REQUIREMENTS_FILE" ]; then
    print_message $CYAN "Installing dependencies..."
    pip install -r $REQUIREMENTS_FILE
else
    print_message $RED "Error: $REQUIREMENTS_FILE not found!"
    exit 1
fi

print_message $CYAN "Running migrations..."
python3 manage.py migrate

print_message $CYAN "Creating superuser..."
python3 manage.py createsuperuser

# Start the server
DEFAULT_IP=$(hostname -I | awk '{print $1}')
print_message $CYAN "Starting the server at $DEFAULT_IP:8080..."
python3 manage.py runserver $DEFAULT_IP:8080

print_message $GREEN "Setup complete! The server is running at http://$DEFAULT_IP:8080"

