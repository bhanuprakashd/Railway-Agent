#!/bin/bash
# Set -e makes the script exit immediately if any command fails
set -e

echo "🚀 Installing Node.js..."

# 1. Update package lists
apt-get update

# 2. Install curl
apt-get install -y curl

# 3. Run the nodesource setup script
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -

# 4. Install nodejs (which includes npm and npx)
apt-get install -y nodejs

echo "--- Verification Step ---"

# 5. Verify that npx and node are available
if command -v npx &> /dev/null && command -v node &> /dev/null; then
    echo "✅ Node.js and npx commands are found."
    
    # --- ADDED as requested ---
    echo "Node version (from 'node --version'):"
    node --version  
    
    echo "npm version (from 'npm --version'):"
    npm --version
    
    echo "Location of npx (from 'which npx'):"
    which npx     
    # --- End of additions ---
    
    echo "--------------------------"
else
    echo "❌ Node.js or npx installation failed (command not found)"
    exit 1
fi

echo "🎉 Installation complete. The agent can now use npx."