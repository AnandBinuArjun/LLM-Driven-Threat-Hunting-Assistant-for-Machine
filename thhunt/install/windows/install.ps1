# Install script for Windows Service
# This is a placeholder. In a real scenario, we would use pywin32 to register the service.

Write-Host "Installing Threat Hunt Assistant Service..."

# 1. Install dependencies
pip install -r requirements.txt

# 2. Register Service (Conceptual)
# New-Service -Name "ThreatHuntAssistant" -BinaryPathName "python -m thhunt.core.service" -StartupType Automatic

Write-Host "Installation complete. Run 'python -m thhunt.core.service' to start manually."
