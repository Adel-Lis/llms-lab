# Docker Setup Guide for Code Porter

Complete installation and configuration guide for Docker across all platforms.

---

## Table of Contents

- [Docker for Code Porter](#docker-for-code-porter)
- [Installation Instructions](#installation-instructions)
  - [Windows Installation](#windows-installation)
  - [macOS Installation](#macos-installation)
  - [Linux Installation](#linux-installation)
- [Docker Image Specifications](#docker-image-specifications)

---

### Why Docker for Code Porter?

Code Porter uses Docker so you do not have to install or manage compilers yourself. Python, C++, Rust, and Java are already available inside the container, and the environment is the same on Windows, macOS, and Linux. This avoids system conflicts and removes setup friction.

All code runs in an isolated sandbox. It cannot access your files or the network, and each run is cleaned up automatically. This keeps execution safe and prevents leftover processes or data.

Docker also makes execution predictable. Code always runs in the same environment, which avoids “works on my machine” issues and keeps results consistent.

Finally, resource limits are enforced. Each container is restricted to 1 GB of memory and one CPU core, so runaway or misbehaving code cannot impact your system.

---

## Docker for Code Porter

### Container Specifications

The Code Porter Docker image contains:

**Base System:**

- **Operating System**: `Ubuntu 22.04 LTS (64-bit)`
- **Architecture**: `x86_64 (AMD64)`
- **Size**: `Approximately 1.5 GB`

**Installed Compilers:**

- **Python**: `3.10.12`
- **GCC (C++)**: `11.4.0` with optimization flags (-O3, -march=native)
- **Rust**: `1.70+` via rustup (optimized builds)
- **OpenJDK**: `17` (Java compiler and runtime)

**Resource Limits:**

- **Memory**: `1 GB` maximum
- **CPU**: `1 core` (100% of one CPU)
- **Network**: `Disabled` (no internet access)
- **Disk**: Uses `host temporary directory` (auto-cleaned)

**Compilation Commands:**

```bash
# C++ (GCC with optimizations)
g++ -O3 -std=c++17 -march=native code.cpp -o cpp_program

# Rust (Maximum optimizations)
rustc -C opt-level=3 -C target-cpu=native code.rs -o rust_program

# Java (Standard compilation)
javac Main.java
java Main
```

---

## Installation Instructions <p style="font-size: 12px; font-weight: 500">✨ AI Generated</p>

### Windows Installation

<u>_Docker Desktop is **required** for Windows._</u>

#### System Requirements

- **OS**: Windows 10 64-bit (Pro, Enterprise, Education) or Windows 11
- **CPU**: 64-bit processor with Second Level Address Translation (SLAT)
- **RAM**: Minimum 4GB
- **Virtualization**: Must be enabled in BIOS

#### Step 1: Enable Virtualization

1. **Check if already enabled:**

   - Open Task Manager (Ctrl+Shift+Esc)
   - Go to "Performance" tab
   - Check if "Virtualization" says "Enabled"

2. **If disabled, enable in BIOS:**
   - Restart computer
   - Enter BIOS (usually F2, F10, F12, or Del key during boot)
   - Find "Virtualization Technology" or "Intel VT-x" or "AMD-V"
   - Set to "Enabled"
   - Save and exit

#### Step 2: Install WSL 2 (Windows Subsystem for Linux)

Open PowerShell as Administrator and run:

```powershell
wsl --install
```

Restart your computer when prompted.

#### Step 3: Download Docker Desktop

1. Visit: https://www.docker.com/products/docker-desktop/
2. Click "Download for Windows"
3. Run the installer (Docker Desktop Installer.exe)

#### Step 4: Installation

1. **Run installer**

   - Double-click the downloaded file
   - Follow installation wizard
   - Check "Use WSL 2 instead of Hyper-V" (recommended)
   - Click "Ok" and wait for installation

2. **Restart computer** when prompted

3. **Start Docker Desktop**
   - Find "Docker Desktop" in Start Menu
   - Launch application
   - Accept the service agreement
   - Wait for Docker Engine to start (whale icon becomes steady in system tray)

#### Step 5: Verify Installation

Open Command Prompt or PowerShell:

```powershell
docker --version
# Output: Docker version 24.x.x, build ...

docker run hello-world
# Should download and run test container
```

---

### macOS Installation

Docker Desktop is **required** for macOS.

#### System Requirements

- **OS**: macOS 11 (Big Sur) or later
- **CPU**: 2010 or newer Mac (Apple Silicon or Intel)
- **RAM**: Minimum 4GB

#### Step 1: Determine Your Mac Type

**Check if you have Apple Silicon (M1/M2/M3) or Intel:**

1. Click Apple menu → "About This Mac"
2. Look at "Chip" or "Processor"
   - **Apple Silicon**: "Apple M1", "Apple M2", "Apple M3"
   - **Intel**: "Intel Core i5", "Intel Core i7", etc.

#### Step 2: Download Docker Desktop

1. Visit: https://www.docker.com/products/docker-desktop/
2. Choose correct version:
   - **Mac with Apple chip** (M1/M2/M3)
   - **Mac with Intel chip**
3. Download the .dmg file

#### Step 3: Installation

1. **Open the .dmg file**

   - Double-click downloaded Docker.dmg
   - Drag Docker icon to Applications folder

2. **Launch Docker**

   - Open Applications folder
   - Double-click Docker
   - Grant necessary permissions when prompted

3. **Initial setup**
   - Accept the service agreement
   - Docker Desktop will request privileged access
   - Enter your Mac password
   - Wait for Docker Engine to start (whale icon in menu bar becomes steady)

#### Step 4: Verify Installation

Open Terminal:

```bash
docker --version
# Output: Docker version 24.x.x, build ...

docker run hello-world
# Should download and run test container
```

---

### Linux Installation

Docker Engine is used on Linux (not Docker Desktop).

#### Ubuntu / Debian Installation

##### Step 1: Remove Old Versions

```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
```

##### Step 2: Set Up Repository

```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

##### Step 3: Install Docker Engine

```bash
# Update package index
sudo apt-get update

# Install Docker Engine
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

##### Step 4: Start Docker Service

```bash
# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker
```

##### Step 5: Add User to Docker Group

**IMPORTANT**: This allows running Docker without `sudo`

```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and log back in for this to take effect
# Or run: newgrp docker
```

##### Step 6: Verify Installation

```bash
docker --version
# Output: Docker version 24.x.x, build ...

docker run hello-world
# Should download and run test container
```

#### Fedora / RHEL / CentOS Installation

```bash
# Install dependencies
sudo dnf -y install dnf-plugins-core

# Add Docker repository
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

# Install Docker
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

#### Arch Linux Installation

```bash
# Install Docker
sudo pacman -S docker

# Start Docker service
sudo systemctl start docker.service
sudo systemctl enable docker.service

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

---

## Docker Image Specifications

### Code Porter Image Details

**Image Name**: `code-porter-benchmark:latest`

**Base Image**: `ubuntu:22.04`

**Installed Software:**

| Software    | Version   | Purpose                    | Size    |
| ----------- | --------- | -------------------------- | ------- |
| Ubuntu      | 22.04 LTS | Base OS                    | ~80 MB  |
| Python 3    | 3.10.12   | Python execution           | ~50 MB  |
| GCC/G++     | 11.4.0    | C++ compilation            | ~150 MB |
| Rust/Cargo  | 1.70+     | Rust compilation           | ~500 MB |
| OpenJDK     | 17        | Java compilation/execution | ~300 MB |
| Build tools | Various   | Compilation dependencies   | ~200 MB |

**Total Image Size**: ~1.5 GB (compressed)

### Build Process

The image is built automatically when you first run Code Porter:

1. **Download base Ubuntu image** (~30 seconds)
2. **Install system packages** (~60 seconds)
3. **Install Python** (~15 seconds)
4. **Install C++ compiler** (~30 seconds)
5. **Install Rust** (~90 seconds)
6. **Install Java** (~45 seconds)
7. **Configure environment** (~10 seconds)

**Total first build time**: 2-5 minutes

**Subsequent runs**: Instant (image is cached)

### Dockerfile Content

```dockerfile
FROM ubuntu:22.04

# Set non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install essential tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    g++ \
    openjdk-17-jdk \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy benchmark script
COPY benchmark.py /app/

# Default command
CMD ["python3", "/app/benchmark.py"]
```
