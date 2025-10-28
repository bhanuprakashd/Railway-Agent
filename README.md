# Indian Railway Agent Engine Deployment

This repository contains the deployment configuration for the Indian Railway Assistant Agent Engine on Google Cloud Vertex AI.

## 🚀 Quick Deployment

### Prerequisites

1. **Google Cloud Project** with Vertex AI enabled
2. **Python 3.13+** environment
3. **Google Cloud SDK** installed and authenticated
4. **Required Python packages** (see requirements below)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/bhanuprakashd/Railway-Agent.git
cd Railway-Agent
git checkout agent_engine_deploy
```

2. **Create and activate conda environment**
```bash
conda create -n agent-engine python=3.13
conda activate agent-engine
```

3. **Install dependencies**
```bash
pip install google-cloud-aiplatform[agent_engines,adk]>=1.101.0
pip install python-dotenv>=1.0.0
pip install mcp>=1.0.0
```

4. **Configure environment variables**
```bash
# Create .env file with your configuration
cp .env.example .env
# Edit .env with your Google Cloud project details
```

### Environment Configuration

Create a `.env` file with the following variables:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# MCP Configuration
MCP_ENDPOINT=https://railway-mcp.amithv.xyz/mcp
MCP_TIMEOUT=360

# Logging
LOG_LEVEL=INFO
```

### 🚀 Deploy Agent Engine

**Deploy the Indian Railway Assistant to Vertex AI:**

```bash
python agent_engine.py
```

This command will:
- ✅ Initialize Vertex AI with your project configuration
- ✅ Create the agent engine with MCP tools integration
- ✅ Deploy to Google Cloud Vertex AI Agent Engine
- ✅ Provide resource name for testing

### 📊 Deployment Output

After successful deployment, you'll see:
```
AgentEngine created. Resource name: projects/YOUR_PROJECT/locations/us-central1/reasoningEngines/RESOURCE_ID
To use this AgentEngine in another session:
agent_engine = vertexai.agent_engines.get('projects/YOUR_PROJECT/locations/us-central1/reasoningEngines/RESOURCE_ID')
```

### 🧪 Testing the Deployed Agent

Test your deployed agent engine:

```bash
python test_agent.py
```

Update the resource ID in `test_agent.py` with your deployed agent engine resource name.

## 📁 Project Structure

```
Agent_Engine_MCP_Deploy/
├── root_agent.py              # Main agent definition with MCP tools
├── agent_engine.py           # Vertex AI deployment configuration
├── config.py                 # Environment configuration
├── test_agent.py             # Testing script for deployed agent
├── .env                      # Environment variables
└── installation_scripts/
    └── install_mcp.sh        # Node.js and MCP installation script
```

## 🔌 Features

### ✅ **Native Gemini Integration**
- Uses Google's native Gemini model for optimal performance
- No external dependencies like LiteLlm
- Better reliability and faster responses

### ✅ **MCP Tools Integration**
- Real-time Indian Railway data access
- Train schedules, seat availability, PNR status
- Live train tracking and station information
- Powered by [Indian Railway MCP Server](https://railway-mcp.amithv.xyz/mcp)

### ✅ **Container-Ready Deployment**
- Optimized for Google Cloud container environment
- Automatic Node.js and MCP installation
- Proper error handling and logging

## 🛠️ Configuration Details

### Agent Engine Configuration

The agent engine is configured with:

- **Display Name**: `indian_railway_assistant`
- **Model**: Native Gemini 2.5 Flash
- **Tools**: Greeting function + MCP toolset
- **Session Management**: Vertex AI session service
- **Artifact Storage**: Google Cloud Storage bucket

### MCP Integration

The agent connects to the Indian Railway MCP server providing:

- `Get-trains-between-stations` - Search trains between stations
- `Get-live-train-status` - Real-time train location and delays
- `Get-pnr-status` - PNR booking status checking
- `Get-seat-availability` - Seat availability by class
- `Get-station-code` - Station codes and information
- `Get-train-schedule` - Complete train schedule and route

## 🔧 Troubleshooting

### Common Issues

**1. Authentication Error**
```bash
# Ensure you're authenticated with Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

**2. Permission Denied**
```bash
# Ensure Vertex AI API is enabled
gcloud services enable aiplatform.googleapis.com
```

**3. Container Startup Failure**
- Check Google Cloud Console logs for detailed error messages
- Verify Node.js installation in container logs
- Ensure MCP endpoint is accessible

**4. MCP Connection Issues**
```bash
# Test MCP endpoint manually
npx -y mcp-remote https://railway-mcp.amithv.xyz/mcp
```

## 📊 Performance

- **Deployment Time**: ~3-5 minutes
- **Response Time**: 2-5 seconds (typical)
- **Memory Usage**: ~500MB per session
- **Concurrent Users**: Depends on Google Cloud quotas

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Bhanu Prakash D**
- GitHub: @bhanuprakashd
- Repository: [Railway-Agent](https://github.com/bhanuprakashd/Railway-Agent)

## 🙏 Acknowledgments

- **Google ADK Team** - For the excellent Agent Development Kit
- **@amith-vp** - For creating the Indian Railway MCP Server
- **Google Cloud Team** - For Vertex AI Agent Engine platform
- **MCP Community** - For the Model Context Protocol standard

---

**Made with ❤️ for Indian Railway travelers**

_Last Updated: October 28, 2025_
