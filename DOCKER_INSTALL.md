# Docker Installation Guide for Windows

## Step 1: Install Docker Desktop

### Download Docker Desktop

1. **Go to**: [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. **Click**: "Download for Windows"
3. **Choose**: Docker Desktop Installer.exe (downloads automatically)

### Install Docker Desktop

1. **Run the installer** (`Docker Desktop Installer.exe`)
2. **Follow the installation wizard**:
   - ✅ Check "Use WSL 2 instead of Hyper-V" (recommended)
   - ✅ Check "Add shortcut to desktop" (optional)
   - Click "OK" to install

3. **Restart your computer** when prompted (required)

4. **Launch Docker Desktop**:
   - After restart, Docker Desktop should start automatically
   - If not, find it in Start Menu → "Docker Desktop"

5. **Accept terms** and sign in (optional - you can skip sign-in)

6. **Wait for Docker to start**:
   - You'll see a whale icon in system tray
   - Wait until it says "Docker Desktop is running"

---

## Step 2: Verify Installation

Open PowerShell and run:

```powershell
docker --version
docker compose version
```

You should see version numbers. If you see errors, Docker isn't installed correctly.

---

## Step 3: Enable WSL 2 (If Needed)

If Docker asks for WSL 2, enable it:

**Option A: Automatic (Recommended)**
- Docker Desktop will prompt you
- Click "Install" when prompted
- Restart when done

**Option B: Manual**
1. Open PowerShell as Administrator:
   ```powershell
   # Right-click PowerShell → "Run as Administrator"
   ```

2. Enable WSL:
   ```powershell
   wsl --install
   ```

3. Restart computer

4. Set WSL 2 as default:
   ```powershell
   wsl --set-default-version 2
   ```

---

## Step 4: Test Docker

Run a test container:

```powershell
docker run hello-world
```

You should see "Hello from Docker!" message.

---

## Step 5: Run PharmaGuard

Now you can run PharmaGuard:

```powershell
cd C:\Pharma_Guard\Pharma_Guard

# Make sure you have .env file with GROQ_API_KEY
docker compose --env-file .env up --build
```

---

## Troubleshooting

### "Docker is not recognized"

**Problem**: Docker not in PATH or not installed.

**Solution**:
1. Make sure Docker Desktop is running (check system tray)
2. Restart PowerShell/terminal
3. Verify installation: Check if Docker Desktop is in Start Menu
4. Reinstall if needed

### "WSL 2 is required"

**Problem**: WSL 2 not enabled.

**Solution**:
1. Install WSL 2 (see Step 3 above)
2. Restart computer
3. Open Docker Desktop → Settings → General
4. Check "Use the WSL 2 based engine"

### "Docker Desktop won't start"

**Problem**: Docker Desktop fails to start.

**Solutions**:
1. **Check Windows version**: Need Windows 10 64-bit (Build 19041+) or Windows 11
2. **Enable virtualization**: 
   - Restart computer
   - Enter BIOS/UEFI (usually F2, F10, or Del during boot)
   - Enable "Virtualization Technology" or "VT-x"
   - Save and exit
3. **Check Hyper-V**: 
   - Windows Features → Enable "Hyper-V" and "Windows Subsystem for Linux"
   - Restart
4. **Reinstall Docker Desktop**: Uninstall → Restart → Reinstall

### "Port already in use"

**Problem**: Port 80 or 8000 already in use.

**Solution**:
1. Change ports in `docker-compose.yml`:
   ```yaml
   frontend:
     ports:
       - "3000:80"  # Changed from 80:80
   
   backend:
     ports:
       - "8001:8000"  # Changed from 8000:8000
   ```
2. Or stop the service using the port:
   ```powershell
   # Find what's using port 80
   netstat -ano | findstr :80
   # Kill the process (replace PID with actual process ID)
   taskkill /PID <PID> /F
   ```

---

## Alternative: Use Docker Without Desktop

If Docker Desktop doesn't work, you can use **Docker via WSL 2**:

1. Install WSL 2 (see Step 3)
2. Install Docker in WSL:
   ```bash
   # In WSL terminal
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```
3. Use WSL terminal for Docker commands

---

## System Requirements

- **Windows 10 64-bit**: Pro, Enterprise, or Education (Build 19041 or higher)
- **OR Windows 11 64-bit**
- **Virtualization enabled** in BIOS
- **4GB RAM minimum** (8GB recommended)
- **WSL 2** (Windows Subsystem for Linux 2)

---

## Quick Checklist

- [ ] Downloaded Docker Desktop
- [ ] Installed Docker Desktop
- [ ] Restarted computer
- [ ] Docker Desktop is running (whale icon in tray)
- [ ] `docker --version` works
- [ ] `docker compose version` works
- [ ] Tested with `docker run hello-world`

---

## Next Steps After Installation

1. ✅ Docker Desktop is running
2. ✅ Create `.env` file with `GROQ_API_KEY`
3. ✅ Run `docker compose --env-file .env up --build`
4. ✅ Visit http://localhost

For environment setup, see [ENV_SETUP.md](./ENV_SETUP.md).
