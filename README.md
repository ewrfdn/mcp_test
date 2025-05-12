# MCP_ICM Project Documentation

## Project Overview | 项目概述
mcp demo

### Prerequisite

- Python (3.12 or newer recommended)

### Installation 

1. **Clone the repository**

```
git clone [repository-url]
cd project-folder
```

2. **Create a virtual environment**

On Windows:
```
create_venv.bat
```

On Linux/Mac:
```
chmod +x create_venv.sh
./create_venv.sh
```

3. **Activate the virtual environment**

On Windows:
```
./activate_venv.bat
```

On Linux/Mac:
```
source ./activate_venv.sh
```

4. **Install dependencies**

```
pip install -r requirements.txt
```

The project uses environment variables for configuration. Create a `.env` file in the client directory with the following variables:

```
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_ID=your-deployment-id
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_ENDPOINT=https://openai-deployname.openai.azure.com
```

## Basic Usage 

start mcp client
```
python ./client/client.py
```

