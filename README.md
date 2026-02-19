🤖 Autonomous CI/CD Healing Agent
AI-Powered DevOps Automation with Sandboxed Execution
📌 Problem Statement
Modern CI/CD pipelines detect failures but do not fix them. Developers must manually inspect logs, debug code, and rerun pipelines—wasting time and slowing releases.
This project builds an Autonomous CI/CD Healing Agent that:
- Detects test failures automatically
- Uses AI to generate targeted code fixes
- Commits fixes to a new branch
- Ensures all execution is safely sandboxed
- Provides visibility through a simple dashboard
  
💡 Solution Overview
Our system acts as an AI-powered DevOps agent that closes the CI/CD feedback loop.
The agent focuses on automation, safety, and explainability, making CI/CD recovery faster and more reliable.
✨ Key Features

🔗 Accepts a GitHub repository URL
🐳 Executes untrusted code inside Docker (sandboxed)
🧪 Automatically discovers and runs tests (Python + pytest)
🧠 Uses a Large Language Model (LLM) to generate fixes
🌱 Commits fixes to a new branch with [AI-AGENT] prefix
📊 Displays execution status via a lightweight dashboard
🔁 Designed for closed-loop CI/CD healing (extensible)
