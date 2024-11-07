#!/bin/bash

# Run tests with coverage and generate HTML report
echo "Running tests with coverage..."
pytest --cov=pywork --cov-report=html
echo "Tests completed. Coverage report available at ./htmlcov/index.html"
