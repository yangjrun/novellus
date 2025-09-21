# Novellus

A comprehensive AI-powered storytelling and worldbuilding platform designed for novelists, writers, and creative professionals. Novellus combines advanced conflict analysis, cultural framework modeling, and intelligent story generation to help creators develop rich, multi-dimensional fictional worlds.

## 🌟 Overview

Novellus is an innovative platform that leverages artificial intelligence to enhance the creative writing process. It provides sophisticated tools for analyzing narrative conflicts, managing cultural frameworks, and generating compelling story elements across multiple domains of human experience.

### Key Features

- **🔍 Advanced Conflict Analysis**: Multi-dimensional conflict detection and analysis across cultural, emotional, and narrative domains
- **🌍 Comprehensive Worldbuilding**: Cultural framework modeling with support for complex societal structures
- **🤖 AI-Powered Generation**: Claude API integration for intelligent content creation and story development
- **📊 Cross-Domain Analytics**: Sophisticated analysis tools for understanding story dynamics and cultural patterns
- **🔗 RESTful API**: Full-featured FastAPI service for programmatic access to all platform capabilities
- **📚 Project Management**: Organize multiple writing projects with hierarchical structure support
- **🔄 Collaborative Workflows**: Multi-user support with role-based access and collaborative editing

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ with pgvector extension
- UV package manager (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd novellus
   ```

2. **Set up the environment**
   ```bash
   # Using UV (recommended)
   uv sync

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Configure the database**
   ```bash
   # Initialize the database
   python init_database.py

   # Import cultural frameworks
   python import_large_cultural_data.py
   ```

4. **Start the API server**
   ```bash
   # Development mode
   python run_api.py --dev

   # Production mode
   python run_api.py --prod
   ```

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.api.yml up --build
```

## 📁 Project Structure

```
novellus/
├── src/                    # Core application source code
│   ├── analysis/          # Conflict analysis and processing modules
│   └── etl/              # Data extraction, transformation, and loading
├── docs/                  # Comprehensive documentation
│   ├── architecture/     # System architecture and design documents
│   ├── api/             # API documentation and guides
│   ├── development/     # Development guides and implementation notes
│   └── reports/         # Analysis reports and system assessments
├── tests/                # Test suites and validation scripts
├── config/               # Configuration files and templates
├── scripts/              # Utility and maintenance scripts
├── examples/             # Usage examples and demos
└── docker/              # Docker configuration and deployment files
```

## 🛠️ Core Components

### Conflict Analysis Engine
Advanced multi-dimensional conflict detection system that analyzes narrative tensions across:
- **Emotional Conflicts**: Personal, interpersonal, and psychological tensions
- **Cultural Conflicts**: Societal norms, traditions, and value system clashes
- **Structural Conflicts**: Power dynamics, institutional pressures, and systemic issues

### Cultural Framework Processor
Sophisticated modeling system for cultural elements including:
- **Social Structures**: Hierarchies, roles, and relationship patterns
- **Belief Systems**: Religious, philosophical, and ideological frameworks
- **Economic Models**: Trade, resource distribution, and economic relationships
- **Governance**: Political systems, law structures, and authority models

### Story Generation System
AI-powered content creation tools featuring:
- **Character Development**: Multi-dimensional character creation with psychological depth
- **Plot Generation**: Intelligent story arc development with conflict integration
- **World Building**: Automated generation of consistent fictional environments
- **Dialogue Systems**: Context-aware conversation generation

## 📖 Documentation

- **[API Documentation](docs/api/)** - Complete API reference and integration guides
- **[Architecture Guide](docs/architecture/)** - System design and technical architecture
- **[Development Guide](docs/development/)** - Setup, configuration, and development workflows
- **[User Guide](docs/)** - End-user documentation and tutorials

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
make test

# Run specific test categories
make test-unit
make test-integration
make test-api

# Generate coverage report
make coverage
```

## 🔧 Configuration

The platform supports multiple configuration methods:

- **Environment Variables**: Configure via `.env` file (see `.env.api.example`)
- **Configuration Files**: YAML and JSON configuration in `config/`
- **Command Line**: Runtime configuration via CLI arguments

Key configuration areas:
- Database connections and credentials
- AI service API keys and endpoints
- Logging levels and output formats
- Performance and caching settings

## 🤝 Contributing

We welcome contributions! Please see our development documentation for guidelines on:

- Code style and standards
- Testing requirements
- Pull request process
- Development environment setup

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🆘 Support

For support, questions, or feature requests:

- Check the [documentation](docs/)
- Review existing [issues](../../issues)
- Create a new issue for bugs or feature requests

## 🔮 Roadmap

- **Enhanced AI Integration**: Expanded Claude API capabilities and custom model support
- **Advanced Visualization**: Interactive conflict maps and cultural relationship diagrams
- **Multi-language Support**: Internationalization and localization features
- **Plugin Architecture**: Extensible plugin system for custom analysis tools
- **Collaborative Features**: Real-time collaboration and shared workspace functionality