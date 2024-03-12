from typing import Dict
from fastapi import FastAPI
from firehose_tracker.tracker import Tracker

app = FastAPI()

# Create a tracker object
tracker = Tracker("firehose-tracker", "page_view")
tracker.ensure_active()


@app.post("/track")
async def track(data: Dict[str, str]):
    event_type = data["event_type"]
    tracker = Tracker("firehose-tracker", event_type)
    tracker.put_record(data)
    return {"message": "success"}


@app.get("/health")
async def health():
    return {"message": "Healthy"}
