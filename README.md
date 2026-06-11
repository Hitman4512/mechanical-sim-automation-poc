# Animation & Rendering Automation POC

Proof-of-concept framework that converts CAD 3D models + procedural PDFs into 4K mechanical simulation videos.

## How It Works

```
CAD Model + Procedure PDF 
    ↓
n8n (orchestrator)
    ↓
Claude API (document understanding)
    ↓
Blender (simulation & rendering)
    ↓
4K MP4 Video Output
```

## Stack

- **n8n** - Workflow orchestration
- **Claude API** (Anthropic) - AI document processing
- **Blender** (headless) - 3D simulation & rendering  
- **AWS S3** - File storage
- **AWS EC2** - GPU compute

## Quick Start

### Prerequisites

- n8n instance running
- Claude API key from Anthropic
- AWS S3 bucket + EC2 access (for production)
- Blender installed
- Python 3.8+

### Setup

1. Clone and install
```bash
git clone <repo>
cd animation_and_rendering_automation-n8n
pip install -r requirements.txt
```

2. Configure credentials
```bash
cp config/example.env config/.env
# Edit with your Claude API key, AWS credentials, etc.
```

3. Import n8n workflow
- Open n8n dashboard
- Import workflow from `n8n-workflows/`
- Configure Claude API + AWS credentials

## Workflow Phases

1. **Input** - Upload CAD model + PDF to S3
2. **Parse** - Extract PDF text with n8n
3. **Understand** - Claude converts text → structured JSON
4. **Preprocess** - Blender imports CAD model
5. **Map** - Claude maps procedural objects → mesh names
6. **Simulate** - Blender executes simulation with constraints
7. **Render** - Generate image sequence → MP4
8. **Deliver** - Upload output to S3

## Project Structure

```
.
├── README.md              # This file
├── .gitignore            # Git ignore (secrets, temp files)
├── requirements.txt      # Python dependencies
│
├── config/
│   └── example.env       # Environment variables template
│
├── n8n-workflows/        # n8n workflow exports
│   └── main-pipeline.json
│
├── scripts/              # Helper scripts
│   ├── blender/         # Blender automation scripts
│   └── lambda/          # Optional AWS Lambda functions
│
└── logs/                # Execution logs
```

## Configuration

Copy `config/example.env` to `config/.env` and set:

```
CLAUDE_API_KEY=your_key
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1
S3_BUCKET=your-bucket
N8N_URL=http://localhost:5678
N8N_API_KEY=xxx
BLENDER_PATH=/usr/bin/blender
```

## Development

- Add n8n workflows to `n8n-workflows/`
- Add Python scripts to `scripts/`
- Update configuration in `config/`

## License

Open source. Use and modify freely.
