# Contributing to AgenticIntegrate AI

Thank you for your interest in contributing to AgenticIntegrate AI! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Environment details (OS, browser, etc.)

### Suggesting Features

We welcome feature suggestions! Please create an issue with:
- A clear, descriptive title
- Detailed description of the proposed feature
- Any relevant examples or mockups
- Explanation of why this feature would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests if applicable
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Open a Pull Request

### Pull Request Guidelines

- Follow the coding style of the project
- Include tests for new features
- Update documentation as needed
- Keep pull requests focused on a single change
- Link any relevant issues

## Adding New Integrations

AgenticIntegrate AI is designed to be extensible. To add a new integration:

### Backend Integration

1. Create a new file in the server directory for your integration
2. Implement the necessary API client and tools
3. Add appropriate error handling and mock data support
4. Update the main server file to include your integration

Example structure for a new integration:

```python
class NewServiceTool:
    name: str = "get_new_service_data"
    description: str = "Get data from New Service. Useful for finding specific information."
    
    def _run(self, limit: int = 25, query: str = None, properties: List[str] = None):
        # Implementation here
        pass
```

### Frontend Integration

1. Add a new component in the frontend for your integration
2. Update the UI to include your integration
3. Add appropriate documentation

## Development Setup

See the README.md file for instructions on setting up the development environment.

## License

By contributing to AgenticIntegrate AI, you agree that your contributions will be licensed under the project's MIT License.

## Questions?

If you have any questions about contributing, please open an issue or contact us at [devashish@jinvaanii.com](mailto:devashish@jinvaanii.com).
