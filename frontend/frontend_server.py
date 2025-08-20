#!/usr/bin/env python3
"""
Simple static file server for hosting the AI Post Report frontend on Render.
This serves the index.html and static assets for the frontend.
Force deploy: 2025-08-19 23:40
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Post Report Frontend")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (JS, CSS, etc.)
@app.get("/ai-post-report-standalone.js")
async def get_js():
    print("📁 Serving ai-post-report-standalone.js")
    return FileResponse("ai-post-report-standalone.js", media_type="application/javascript")

@app.get("/favicon.ico")
async def get_favicon():
    # Return a 204 No Content for favicon requests to avoid 404s
    return Response(status_code=204)

# Serve the main HTML page for all routes
@app.get("/", response_class=HTMLResponse)
@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_frontend(request: Request, path: str = ""):
    """Serve the main HTML page for all routes (SPA behavior)"""
    print(f"📄 Serving HTML for path: {path}")
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
