# Environment Variables Setup Guide

This guide shows you how to set the `GROQ_API_KEY` environment variable for PharmaGuard.

---

## Option 1: Using .env File (Recommended for Docker)

### Step 1: Create .env File

Navigate to the `Pharma_Guard` directory and create a `.env` file:

**Windows (PowerShell)**:
```powershell
cd C:\Pharma_Guard\Pharma_Guard
Copy-Item .env.example .env
notepad .env
```

**Windows (CMD)**:
```cmd
cd C:\Pharma_Guard\Pharma_Guard
copy .env.example .env
notepad .env
```

**Linux/Mac**:
```bash
cd Pharma_Guard
cp .env.example .env
nano .env  # or use your preferred editor
```

### Step 2: Edit .env File

Open `.env` and add your Groq API key:

```env
GROQ_API_KEY=gsk_your_actual_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

**Important**: Replace `gsk_your_actual_api_key_here` with your actual Groq API key from [console.groq.com/keys](https://console.groq.com/keys)

### Step 3: Run Docker Compose

```bash
docker compose --env-file .env up --build
```

The `--env-file .env` flag tells Docker Compose to load variables from `.env` file.

---

## Option 2: Set Environment Variables Directly (Windows)

### PowerShell (Recommended)

**Temporary (current session only)**:
```powershell
$env:GROQ_API_KEY="gsk_your_actual_api_key_here"
$env:GROQ_MODEL="llama-3.1-8b-instant"
```

**Permanent (for current user)**:
```powershell
[System.Environment]::SetEnvironmentVariable("GROQ_API_KEY", "gsk_your_actual_api_key_here", "User")
[System.Environment]::SetEnvironmentVariable("GROQ_MODEL", "llama-3.1-8b-instant", "User")
```

After setting permanent variables, **restart your terminal** or run:
```powershell
refreshenv  # If you have Chocolatey
# OR restart PowerShell
```

**Verify it's set**:
```powershell
echo $env:GROQ_API_KEY
```

### Command Prompt (CMD)

**Temporary (current session only)**:
```cmd
set GROQ_API_KEY=gsk_your_actual_api_key_here
set GROQ_MODEL=llama-3.1-8b-instant
```

**Permanent (for current user)**:
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to "Advanced" tab → "Environment Variables"
3. Under "User variables", click "New"
4. Variable name: `GROQ_API_KEY`
5. Variable value: `gsk_your_actual_api_key_here`
6. Click OK
7. Repeat for `GROQ_MODEL` if needed
8. **Restart your terminal/IDE** for changes to take effect

**Verify it's set**:
```cmd
echo %GROQ_API_KEY%
```

---

## Option 3: Set Environment Variables (Linux/Mac)

### Temporary (current session only)

**Bash/Zsh**:
```bash
export GROQ_API_KEY="gsk_your_actual_api_key_here"
export GROQ_MODEL="llama-3.1-8b-instant"
```

**Verify**:
```bash
echo $GROQ_API_KEY
```

### Permanent (add to shell profile)

**Bash** (add to `~/.bashrc` or `~/.bash_profile`):
```bash
echo 'export GROQ_API_KEY="gsk_your_actual_api_key_here"' >> ~/.bashrc
echo 'export GROQ_MODEL="llama-3.1-8b-instant"' >> ~/.bashrc
source ~/.bashrc
```

**Zsh** (add to `~/.zshrc`):
```bash
echo 'export GROQ_API_KEY="gsk_your_actual_api_key_here"' >> ~/.zshrc
echo 'export GROQ_MODEL="llama-3.1-8b-instant"' >> ~/.zshrc
source ~/.zshrc
```

---

## Option 4: Docker Compose with Inline Variables

You can also set variables directly in the command:

**Windows (PowerShell)**:
```powershell
$env:GROQ_API_KEY="gsk_your_key"; docker compose up --build
```

**Windows (CMD)**:
```cmd
set GROQ_API_KEY=gsk_your_key && docker compose up --build
```

**Linux/Mac**:
```bash
GROQ_API_KEY="gsk_your_key" docker compose up --build
```

---

## Option 5: Modify docker-compose.yml Directly

Edit `docker-compose.yml` and replace `${GROQ_API_KEY:-}` with your actual key:

```yaml
backend:
  environment:
    GROQ_API_KEY: gsk_your_actual_api_key_here  # ⚠️ Not recommended for production
    GROQ_MODEL: llama-3.1-8b-instant
```

**⚠️ Warning**: Don't commit this to Git! Add `docker-compose.yml` to `.gitignore` or use `.env` file instead.

---

## Option 6: Cloud Platform Deployment

### Railway

1. Go to your Railway project
2. Click on the `backend` service
3. Go to "Variables" tab
4. Click "New Variable"
5. Name: `GROQ_API_KEY`
6. Value: `gsk_your_actual_api_key_here`
7. Click "Add"

### Render

1. Go to your Render dashboard
2. Select your backend service
3. Go to "Environment" tab
4. Click "Add Environment Variable"
5. Key: `GROQ_API_KEY`
6. Value: `gsk_your_actual_api_key_here`
7. Click "Save Changes"

### Fly.io

```bash
fly secrets set GROQ_API_KEY=gsk_your_actual_api_key_here
```

### DigitalOcean App Platform

1. Go to your app in DigitalOcean
2. Settings → Environment Variables
3. Add:
   - Key: `GROQ_API_KEY`
   - Value: `gsk_your_actual_api_key_here`
4. Save

### Vercel (if deploying backend)

1. Go to your Vercel project
2. Settings → Environment Variables
3. Add:
   - Key: `GROQ_API_KEY`
   - Value: `gsk_your_actual_api_key_here`
   - Environment: Production, Preview, Development (select all)
4. Save

---

## Verify Environment Variable is Set

### Check in Docker Container

```bash
# Check if backend container sees the variable
docker compose exec backend env | grep GROQ
```

### Check in Backend Logs

Start the app and check logs:
```bash
docker compose logs backend
```

Look for any errors about missing API key.

### Test API Key

You can test if your API key works:

**Python**:
```python
import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("✅ API key works!")
    print(response.choices[0].message.content)
else:
    print("❌ GROQ_API_KEY not set")
```

**cURL**:
```bash
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

---

## Troubleshooting

### "llm_not_configured_placeholder" in Results

**Problem**: Environment variable not set or not loaded.

**Solutions**:
1. Check if variable is set: `echo $GROQ_API_KEY` (Linux/Mac) or `echo %GROQ_API_KEY%` (Windows)
2. Verify `.env` file exists and has correct key
3. Restart Docker containers: `docker compose restart backend`
4. Check backend logs: `docker compose logs backend`

### Variable Not Loading in Docker

**Problem**: Docker Compose not reading `.env` file.

**Solutions**:
1. Make sure `.env` file is in same directory as `docker-compose.yml`
2. Use explicit flag: `docker compose --env-file .env up`
3. Check `.env` file syntax (no spaces around `=`)
4. Verify file is not `.env.txt` (Windows sometimes hides extensions)

### Variable Set But Not Working

**Problem**: Wrong format or invalid key.

**Solutions**:
1. Verify key starts with `gsk_`
2. Check for extra spaces or quotes
3. Get a new key from [console.groq.com/keys](https://console.groq.com/keys)
4. Test key with cURL (see above)

---

## Security Best Practices

1. ✅ **Never commit `.env` file to Git**
   - Add `.env` to `.gitignore`
   - Use `.env.example` as template

2. ✅ **Use environment variables, not hardcoded keys**
   - Don't put API keys in code
   - Use `.env` file or platform environment variables

3. ✅ **Rotate keys regularly**
   - Generate new keys in Groq console
   - Update environment variables
   - Revoke old keys

4. ✅ **Use different keys for dev/prod**
   - Development: Use free tier key
   - Production: Use separate key with monitoring

---

## Quick Reference

| Platform | Method | Command |
|----------|--------|---------|
| **Docker (Recommended)** | `.env` file | `docker compose --env-file .env up` |
| **Windows PowerShell** | `$env:VAR="value"` | Temporary |
| **Windows CMD** | `set VAR=value` | Temporary |
| **Linux/Mac** | `export VAR="value"` | Temporary |
| **Railway** | Dashboard → Variables | Permanent |
| **Render** | Dashboard → Environment | Permanent |
| **Fly.io** | `fly secrets set` | Permanent |

---

## Next Steps

1. ✅ Get Groq API key from [console.groq.com/keys](https://console.groq.com/keys)
2. ✅ Set environment variable using one of the methods above
3. ✅ Run `docker compose --env-file .env up --build`
4. ✅ Test at http://localhost

For more help, see [GROQ_SETUP.md](./GROQ_SETUP.md).
