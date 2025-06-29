#!/bin/bash

# Women's Euro 2025 Game Setup Script

echo "🏆 Setting up Women's Euro 2025 Game..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "📦 Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add Poetry to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"
    
    # Check if installation was successful
    if ! command -v poetry &> /dev/null; then
        echo "❌ Poetry installation failed. Please install Poetry manually:"
        echo "   curl -sSL https://install.python-poetry.org | python3 -"
        echo "   Then restart your terminal and run this script again."
        exit 1
    fi
fi

echo "✅ Poetry found"

# Install dependencies
echo "📚 Installing dependencies with Poetry..."
poetry install

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your settings before continuing"
fi

# Create database migrations
echo "🗄️ Creating database migrations..."
poetry run python manage.py makemigrations

# Apply migrations
echo "🔄 Applying database migrations..."
poetry run python manage.py migrate

# Create superuser prompt
echo "👤 Would you like to create a superuser account? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    poetry run python manage.py createsuperuser
fi

# Create sample data prompt
echo "🎯 Would you like to create sample data for testing? (y/n)"
read -r create_sample
if [ "$create_sample" = "y" ] || [ "$create_sample" = "Y" ]; then
    poetry run python manage.py create_sample_data
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the development server:"
echo "1. Configure your .env file with database and API settings"
echo "2. Run: poetry run python manage.py runserver"
echo "3. Visit: http://localhost:8000/weuro2025_game/"
echo ""
echo "Other useful Poetry commands:"
echo "- poetry shell                    # Activate virtual environment"
echo "- poetry add <package>            # Add new dependency"
echo "- poetry add --group dev <package> # Add development dependency"
echo "- poetry update                   # Update dependencies"
echo ""
echo "For production deployment, see DEPLOYMENT.md for detailed instructions."
