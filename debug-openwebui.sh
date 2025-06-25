#!/bin/bash

echo "🔍 Open WebUI Debug Script"
echo "========================="
echo ""

# Check if container is running
if docker ps | grep -q "open-webui"; then
    echo "✅ Container is running"
    echo ""
    
    # Get container details
    echo "📦 Container Details:"
    docker ps --filter "name=open-webui" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    # Check environment variables
    echo "🔧 Environment Variables:"
    docker exec open-webui env | grep -E "(OLLAMA|OPENAI|WEBUI|DATABASE)" | sort
    echo ""
    
    # Check recent logs
    echo "📋 Recent Error Logs:"
    docker logs open-webui 2>&1 | grep -i -E "(error|exception|failed|500)" | tail -20
    echo ""
    
    # Check database file
    echo "💾 Database Status:"
    docker exec open-webui ls -la /app/backend/data/ 2>/dev/null || echo "Cannot access data directory"
    echo ""
    
    # Network connectivity
    echo "🌐 Network Tests:"
    echo -n "Container can reach host: "
    docker exec open-webui ping -c 1 host.docker.internal &>/dev/null && echo "✅ Yes" || echo "❌ No"
    
    # Port check
    echo -n "Port 3000 is accessible: "
    curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "500" && echo "❌ Returns 500" || echo "✅ OK"
    
else
    echo "❌ Container is not running!"
    echo ""
    echo "🚀 To start the container, run:"
    echo "docker run -d -p 3000:8080 \\"
    echo "  -e ENABLE_OLLAMA_API=false \\"
    echo "  -e ENABLE_OPENAI_API=true \\"
    echo "  -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/api/v1 \\"
    echo "  -e OPENAI_API_KEY=bedrock \\"
    echo "  -v open-webui:/app/backend/data \\"
    echo "  --name open-webui \\"
    echo "  --restart always \\"
    echo "  open-webui"
fi

echo ""
echo "💡 Common fixes for 500 error:"
echo "1. Clear browser cache and cookies"
echo "2. Try incognito mode"
echo "3. Access http://localhost:3000/ollama first"
echo "4. Remove and recreate the volume"
echo "5. Check if Bedrock Gateway is running on port 8000" 