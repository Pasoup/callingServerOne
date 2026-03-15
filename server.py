import socketio
from fastapi import FastAPI
import uvicorn

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
sio_app = socketio.ASGIApp(sio, app)

@app.get("/")
def home():
    return "Relay Server Running"

@sio.event
async def connect(sid, environ):
    print(f"✅ User Connected: {sid}")
    await sio.enter_room(sid, "global_room")

@sio.event
async def disconnect(sid):
    print(f"❌ User Disconnected: {sid}")

@sio.event
async def send_video(sid, data):
    # skip_sid=sid is CRITICAL: Don't send my video back to me
    await sio.emit('receive_video', data, room="global_room", skip_sid=sid)

@sio.event
async def send_audio(sid, data):
    # skip_sid=sid is CRITICAL: Prevents lethal feedback loops
    await sio.emit('receive_audio', data, room="global_room", skip_sid=sid)

if __name__ == "__main__":
    # Use loop='uvloop' for better performance on Linux servers
    uvicorn.run(sio_app, host="0.0.0.0", port=8000)