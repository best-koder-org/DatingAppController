#!/bin/bash
# Initialize all DatingApp repos as submodules

set -e

echo "🔧 Initializing DatingApp Controller with all repositories..."

mkdir -p repos
cd repos

# Main config repo
git submodule add https://github.com/best-koder-ever/DatingApp-Config.git DatingApp-Config || echo "DatingApp-Config already added"

# Services
git submodule add https://github.com/best-koder-ever/UserService.git UserService || echo "UserService already added"
git submodule add https://github.com/best-koder-ever/MatchmakingService.git MatchmakingService || echo "MatchmakingService already added"
git submodule add https://github.com/best-koder-ever/swipe-service.git swipe-service || echo "swipe-service already added"
git submodule add https://github.com/best-koder-ever/photo-service.git photo-service || echo "photo-service already added"
git submodule add https://github.com/best-koder-ever/messaging-service.git messaging-service || echo "messaging-service already added"
git submodule add https://github.com/best-koder-ever/safety-service.git safety-service || echo "safety-service already added"

# Gateway
git submodule add https://github.com/best-koder-ever/dejting-yarp.git dejting-yarp || echo "dejting-yarp already added"

# Mobile
git submodule add https://github.com/best-koder-ever/mobile_dejtingapp.git mobile_dejtingapp || echo "mobile_dejtingapp already added"

cd ..

git submodule update --init --recursive

echo "✅ All repositories initialized as submodules"
echo "📊 Repository count: $(find repos -maxdepth 1 -type d | wc -l) directories"
