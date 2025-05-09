# Deployment Instructions for Yojna Khojna

This document outlines how to make the Yojna Khojna application accessible over the internet for demonstration purposes.

## Local Deployment

The simplest way to run the application locally is using the `serve_demo.sh` script in the project root:

```bash
# Make the script executable (if not already)
chmod +x serve_demo.sh

# Run the script
./serve_demo.sh
```

This script:
1. Starts the FastAPI backend on port 8000
2. Starts the Vite development server for the frontend on port 3000
3. Keeps both processes running until you press Ctrl+C

## Exposing the Application Over the Internet

To make the application accessible to others over the internet, use Cloudflare Tunnel:

### Setting Up Cloudflare Tunnel

1. **Install cloudflared** (if not already installed):
   ```bash
   # macOS
   brew install cloudflared
   
   # Linux
   curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared.deb
   
   # Windows (using Scoop)
   scoop install cloudflared
   ```

2. **Start a Tunnel**:
   In a separate terminal window (while `serve_demo.sh` is running), execute:
   ```bash
   cloudflared tunnel --url http://localhost:3000
   ```

3. **Share the URL**:
   Cloudflared will display a URL like `https://random-words-random.trycloudflare.com`. Share this URL with anyone who needs to test the application.

### Important Technical Details

The following changes were made to make the application work with Cloudflare Tunnel:

1. **Updated Vite Configuration**:
   Modified `frontend/vite.config.ts` to:
   - Listen on all network interfaces (`host: true`)
   - Change port to 3000 for easier configuration
   - Allow any subdomain from `.trycloudflare.com` in `allowedHosts`
   - Configure HMR (Hot Module Replacement) correctly

2. **CORS Configuration**:
   The backend FastAPI server was configured to accept requests from any origin (`*`) for demo purposes.

3. **API URL Handling**:
   Relative API URLs are used in the frontend to ensure requests correctly route through Cloudflare Tunnel to the backend.

## Limitations and Considerations

- **Temporary Access**: The free Cloudflare Tunnel provides a temporary URL that changes each time you restart the tunnel
- **Security**: This configuration is for demonstration purposes only and not suitable for production use
- **Resource Usage**: Both the backend and frontend run on your local machine, so your computer needs to remain on and connected to the internet during the demo
- **Performance**: Users may experience some latency depending on their geographic location relative to Cloudflare's network

## For More Permanent Deployments

For a more permanent solution:

1. **Named Cloudflare Tunnels**:
   You can configure a named tunnel with Cloudflare Teams (free tier available):
   ```bash
   cloudflared tunnel login
   cloudflared tunnel create yojna-khojna
   cloudflared tunnel route dns yojna-khojna demo.yourdomain.com
   cloudflared tunnel run --url http://localhost:3000 yojna-khojna
   ```

2. **Cloud Hosting**:
   For a more production-ready deployment, consider hosting on platforms like:
   - Render.com
   - Railway.app 
   - Fly.io
   - AWS, Google Cloud, or Azure 