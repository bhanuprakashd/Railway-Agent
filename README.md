# 🚂 Railway Agent - Indian Railway Information Assistant

An intelligent AI-powered chatbot that provides real-time Indian Railway information through a ChatGPT-style conversational interface.

![Python](https://img.shields.io/badge/python-3.13-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.50.0-red)
![Google ADK](https://img.shields.io/badge/google--adk-1.16.0-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

## 🌟 Overview

Railway Agent is a conversational AI assistant built using Google's Agent Development Kit (ADK) that provides comprehensive Indian Railway information. It connects to real-time railway data through the Model Context Protocol (MCP) and delivers responses in natural, human-friendly language.

## ✨ Features

### Core Capabilities
- **🔍 Train Search** - Find trains between any two stations
- **📍 Live Train Status** - Real-time tracking and delay information
- **🎫 PNR Status Checking** - Verify booking status and seat confirmation
- **💺 Seat Availability** - Check available seats across all classes and quotas
- **🏢 Station Information** - Get station codes, facilities, and details
- **🗺️ Route Planning** - Comprehensive journey information with schedules

### User Experience
- Clean, minimal ChatGPT-inspired interface
- Conversational multi-turn dialogue support
- Context-aware responses with conversation memory
- Beautiful train animations during loading
- Structured output formatting (tables, bullet points)
- Mobile-responsive design

### Technical Features
- Persistent session management across conversations
- Async/await for non-blocking operations
- Real-time data from official railway systems via [Indian Railway MCP](https://github.com/amith-vp/indian-railway-mcp)
- Error handling with user-friendly fallback messages
- Comprehensive logging for debugging and monitoring

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│          Streamlit Web Interface                │
│       (ChatGPT-style UI with Custom CSS)        │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│           Agent Orchestration                    │
│  • Google ADK Runner                            │
│  • In-Memory Session Service                   │
│  • Conversation History Management              │
└─────────────────┬───────────────────────────────┘
                  │
                  ├──────────► LiteLLM Interface
                  │             └─► Ollama GLM-4.6
                  │
                  └──────────► MCP Toolset
                                └─► Indian Railway MCP Server
                                    (https://github.com/amith-vp/indian-railway-mcp)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Conda (recommended) or pip
- Ollama with GLM-4.6 model
- Node.js & npx (for MCP server)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/bhanuprakashd/Railway-Agent.git
cd Railway-Agent
```

2. **Create and activate conda environment**
```bash
conda create -n adk python=3.13
conda activate adk
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install and start Ollama with GLM-4.6**
```bash
# Install Ollama from https://ollama.ai
ollama pull glm-4.6:cloud
ollama serve
```

5. **Verify MCP server access**
```bash
npx -y mcp-remote https://railway-mcp.amithv.xyz/mcp
```

> **Note:** This project uses the [Indian Railway MCP Server](https://github.com/amith-vp/indian-railway-mcp) 
> by [@amith-vp](https://github.com/amith-vp) for accessing real-time Indian Railway data.

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 💬 Usage Examples

### Train Search
```
User: "Show me trains from Hyderabad to Bangalore tomorrow"
Agent: Lists all trains with departure/arrival times, duration, and classes
```

### Seat Availability
```
User: "Check seat availability for train 12760 from LPI to GNT on 20-10-2025"
Agent: Shows availability across all classes (SL, 3A, 2A, etc.)
```

### Live Train Status
```
User: "Where is train 12806 right now?"
Agent: Provides current location, delays, and upcoming stations
```

### PNR Status
```
User: "Check PNR 1234567890"
Agent: Shows booking status, seat details, and coach information
```

### Station Information
```
User: "What's the station code for Guntur?"
Agent: Provides station code, full name, and additional details
```

## 📁 Project Structure

```
Railway-Agent/
│
├── app.py                      # Streamlit web interface
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── train_agent/
│   ├── __init__.py            # Package initialization
│   └── agent.py               # Core agent logic & MCP integration
│
└── logs/                       # Application logs (auto-generated)
    └── chat_YYYYMMDD.log
```

## 🔌 MCP Server Integration

This project uses the **[Indian Railway MCP Server](https://github.com/amith-vp/indian-railway-mcp)** to access real-time railway data.

### About the MCP Server

The Indian Railway MCP Server is an open-source Model Context Protocol server that provides:
- Real-time train schedules and information
- Live train running status
- PNR status checking
- Seat availability queries
- Station details and codes

### Available MCP Tools

The server exposes several tools that our agent uses:
- `Get-trains-between-stations` - Search trains between two stations
- `Get-live-train-status` - Get real-time train location and delays
- `Get-pnr-status` - Check PNR booking status
- `Get-seat-availability` - Check seat availability by class
- `Get-station-code` - Get station codes and information
- `Get-train-schedule` - Get complete train schedule and route

### Credits

**MCP Server Repository:** https://github.com/amith-vp/indian-railway-mcp  
**Author:** [@amith-vp](https://github.com/amith-vp)  
**Endpoint:** https://railway-mcp.amithv.xyz/mcp

Special thanks to Amith VP for creating and maintaining this excellent MCP server!

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional):

```bash
# LLM Configuration
OLLAMA_API_BASE=http://localhost:11434
MODEL_NAME=ollama/glm-4.6:cloud
TEMPERATURE=0.1

# MCP Configuration
MCP_ENDPOINT=https://railway-mcp.amithv.xyz/mcp
MCP_TIMEOUT=360

# Logging
LOG_LEVEL=INFO
```

### Agent Configuration

Edit `train_agent/agent.py` to customize:
- Model temperature and parameters
- Agent instructions and behavior
- Tool configurations
- Session management settings

## 🛠️ Development

### Key Components

#### 1. **app.py** - Web Interface
- Streamlit-based UI with custom CSS
- Session state management
- Async event loop handling
- Chat history persistence

#### 2. **train_agent/agent.py** - Agent Logic
- `root_agent`: Main agent with MCP tools
- `greeting()`: Custom greeting function
- `workflow()`: Query processing pipeline
- `initialize_session()`: Session setup

#### 3. **MCP Integration**
- Real-time connection to railway API
- Tool discovery and invocation
- Response parsing and formatting

### Adding New Features

**To add a new tool:**

1. Define the tool function in `agent.py`:
```python
def my_new_tool(param: str) -> str:
    """Tool description"""
    # Implementation
    return result
```

2. Add to agent's tools list:
```python
root_agent = Agent(
    tools=[greeting, mcp_toolset, my_new_tool],
    ...
)
```

**To modify UI:**

Edit CSS in `app.py` under the `st.markdown()` section (lines 42-121)

## 📊 Performance

- **Response Time**: 2-5 seconds (typical)
- **Concurrent Users**: Depends on hardware
- **Memory Usage**: ~500MB per session
- **MCP Timeout**: 6 minutes (configurable)

## 🔍 Troubleshooting

### Common Issues

**1. "Could not connect to Ollama"**
```bash
# Ensure Ollama is running
ollama serve

# Check if model is installed
ollama list
```

**2. "MCP connection timeout"**
```bash
# Test MCP endpoint manually
npx -y mcp-remote https://railway-mcp.amithv.xyz/mcp

# Increase timeout in agent.py
timeout=600  # 10 minutes
```

**3. "Module not found" errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**4. Streamlit crashes on async operations**
```bash
# Check Python version (requires 3.13+)
python --version

# Verify event loop configuration in app.py
```

## 📝 Logging

Logs are automatically created in the `logs/` directory:
- Format: `chat_YYYYMMDD.log`
- Level: INFO
- Contents: Query processing, errors, agent responses

View logs:
```bash
tail -f logs/chat_$(date +%Y%m%d).log
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update README for significant changes
- Use meaningful commit messages

## 🐛 Known Issues

- [ ] Streamlit `st.rerun()` may cause performance issues with very long conversations
- [ ] MCP connection doesn't auto-reconnect on timeout (requires session reset)
- [ ] CSS typo: `#ffff` should be `#ffffff` (lines 46, 69 in app.py)

## 🗺️ Roadmap

### Version 1.1
- [ ] Add authentication/user management
- [ ] Implement rate limiting
- [ ] Add response caching for common queries
- [ ] Export conversation history

### Version 1.2
- [ ] Multi-language support (Hindi, Tamil, Telugu)
- [ ] Voice input/output capabilities
- [ ] Mobile app (React Native)
- [ ] Fare calculator integration

### Version 2.0
- [ ] Train booking integration
- [ ] Payment gateway
- [ ] User preferences and favorites
- [ ] Push notifications for train status

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Bhanu Prakash D**
- GitHub: [@bhanuprakashd](https://github.com/bhanuprakashd)
- Repository: [Railway-Agent](https://github.com/bhanuprakashd/Railway-Agent)

## 🙏 Acknowledgments

- **Google ADK Team** - For the excellent Agent Development Kit
- **[@amith-vp](https://github.com/amith-vp)** - For creating and maintaining the [Indian Railway MCP Server](https://github.com/amith-vp/indian-railway-mcp)
- **Streamlit Team** - For the amazing web framework
- **Ollama Team** - For enabling local LLM capabilities
- **Indian Railways** - For providing the data and infrastructure
- **MCP Community** - For the Model Context Protocol standard

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review logs for error details

---

**Made with ❤️ for Indian Railway travelers**

*Last Updated: October 18, 2025*

