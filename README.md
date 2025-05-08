# AgenticIntegrate AI

![AgenticIntegrate AI Logo](assets/images/AgenticAI.png)

**AgenticIntegrate AI** is an intelligent agentic integration platform that connects your business applications with natural language interfaces. Built by Jinvaanii AI in collaboration with Global AI Jaipur, this open-source project enables seamless interaction with various business tools through conversational AI.

## 🌟 Features

- **Natural Language Interface**: Query your business data using plain English
- **Multiple Integrations**: Currently supports HubSpot with more integrations coming soon
- **AI-Powered**: Leverages Azure OpenAI and LangChain for intelligent processing
- **Modern UI**: Responsive React frontend with light/dark mode
- **Extensible**: Easily add new integrations and capabilities

## 🏗️ Architecture

IntegrateAI consists of two main components:

### Backend (Python)
- FastAPI server for high-performance API endpoints
- Integration with Azure OpenAI for natural language processing
- Direct API connections to business platforms
- Mock data support for development without API keys

### Frontend (React)
- Modern UI built with React and NextUI components
- Responsive design for all devices
- Markdown rendering for rich responses
- Data visualization capabilities

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ (Note: Some dependencies may have issues with Python 3.13)
- Node.js 14+
- API keys for integrations you wish to use

### Backend Setup

1. Navigate to the server directory:
```bash
cd server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the template:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your API keys and configuration.

5. Start the server:
```bash
python simple_server.py
```

The server will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at http://localhost:3000

## 🔌 Available Integrations

### HubSpot
- Query contacts, companies, and deals using natural language
- Search and filter data based on various properties
- Generate conversational responses about your HubSpot data

### Coming Soon
- Salesforce
- Microsoft Dynamics
- Google Workspace
- Slack
- And more!

## 🛠️ Development

### Adding New Integrations

To add a new integration:

1. Create a new tool class in the server directory
2. Implement the required API endpoints
3. Add the integration to the frontend UI
4. Update documentation

See our [Contributing Guide](CONTRIBUTING.md) for more details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👥 Credits

Developed by [Jinvaanii AI](https://jinvaanii.com) in collaboration with [Global AI Jaipur](https://globalai.community/chapters/jaipur/).

## 📧 Contact

For questions or support, please open an issue or contact us at [devashish@jinvaanii.com](mailto:devashish@jinvaanii.com).
