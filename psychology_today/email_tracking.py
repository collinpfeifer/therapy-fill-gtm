from fastapi import FastAPI, Request
from fastapi.responses import Response, RedirectResponse
from datetime import datetime
import json

app = FastAPI()

TRACKING_PIXELS_FILE = "tracking_pixels.json"
TRACKING_LINKS_FILE = "tracking_links.json"

# Function to save tracking data
def save_tracking_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# Tracking pixel route
@app.get("/pixel/{pixel_id}")
def tracking_pixel(pixel_id: str, request: Request):
    with open(TRACKING_PIXELS_FILE, "r") as f:
        tracking_data = json.load(f)

    if pixel_id not in tracking_data:
        return {"error": "Invalid link"}

    print(pixel_id)
    print(tracking_data[pixel_id])
    print(tracking_data[pixel_id]["opens"])
    tracking_data[pixel_id]["opens"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "ip": getattr(request.client, "host", None),
        "user_agent": request.headers.get("user-agent")
    })

    save_tracking_data(TRACKING_PIXELS_FILE, tracking_data)

    # Return a transparent 1x1 GIF
    transparent_pixel = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;"
    return Response(content=transparent_pixel, media_type="image/gif")

# Track link clicks
@app.get("/track/{link_id}")
def track_click(link_id: str, request: Request):
    with open(TRACKING_LINKS_FILE, "r") as f:
        links_data = json.load(f)

    if link_id not in links_data:
        return {"error": "Invalid link"}

    links_data[link_id]["clicks"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "ip": getattr(request.client, "host", None),
        "user_agent": request.headers.get("user-agent")
    })

    save_tracking_data(TRACKING_LINKS_FILE, links_data)

    return RedirectResponse(url=links_data[link_id]["original_url"])
