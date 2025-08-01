# Makefile for Bot Factory Maker
# ملف Makefile لتبسيط العمليات الشائعة

.PHONY: help install run test clean setup

# Default target
help:
	@echo "Bot Factory Maker - Makefile"
	@echo "=========================="
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make setup      - Setup the project"
	@echo "  make run        - Run the bot"
	@echo "  make test       - Test the code"
	@echo "  make clean      - Clean cache files"
	@echo "  make help       - Show this help"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed successfully!"

# Setup the project
setup:
	@echo "Setting up the project..."
	python setup.py develop
	@echo "Project setup completed!"

# Run the bot
run:
	@echo "Starting Bot Factory..."
	python main.py

# Alternative run methods
run-bot:
	@echo "Starting Bot Factory (alternative method)..."
	python bot.py

run-start:
	@echo "Starting Bot Factory (simple method)..."
	python start.py

run-simple:
	@echo "Starting Bot Factory (ultra simple method)..."
	python run.py

# Test the code
test:
	@echo "Testing the code..."
	python -m py_compile main.py bot.py start.py run.py
	python -m py_compile utils/*.py
	python -m py_compile users/*.py
	python -m py_compile db/*.py
	python -m py_compile bots/*.py
	python -m py_compile broadcast/*.py
	python -m py_compile factory/*.py
	python -m py_compile handlers/*.py
	python -m py_compile Maker/*.py
	@echo "All files compiled successfully!"

# Clean cache files
clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".coverage" -delete
	find . -name "*.log" -delete
	@echo "Cache files cleaned!"

# Install as package
install-package:
	@echo "Installing as package..."
	pip install -e .
	@echo "Package installed successfully!"

# Uninstall package
uninstall-package:
	@echo "Uninstalling package..."
	pip uninstall bot-factory-maker -y
	@echo "Package uninstalled!"

# Show project info
info:
	@echo "Bot Factory Maker - Project Information"
	@echo "====================================="
	@echo "Version: 2.0.0"
	@echo "Python: $(shell python --version)"
	@echo "Pip: $(shell pip --version)"
	@echo ""

# Development setup
dev-setup: install setup
	@echo "Development environment setup completed!"

# Production setup
prod-setup: install install-package
	@echo "Production environment setup completed!"