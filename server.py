import socketio
from fastapi import FastAPI
import uvicorn

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
sio_app = socketio.ASGIApp(sio, app)

@app.get("/")
def home():
    return "WebRTC Signaling Server Running"

@sio.event
async def connect(sid, environ):
    print(f"✅ User Connected: {sid}")
    await sio.enter_room(sid, "global_room")
    
    
    await sio.emit('user_joined', {'sid': sid}, room="global_room", skip_sid=sid)

@sio.event
async def disconnect(sid):
    print(f"❌ User Disconnected: {sid}")

    await sio.emit('user_left', {'sid': sid}, room="global_room", skip_sid=sid)


@sio.event
async def offer(sid, data):
    """User A sends a connection offer to User B."""
    target_sid = data.get('target')
    if target_sid:
        await sio.emit('offer', {'sender': sid, 'sdp': data['sdp']}, to=target_sid)

@sio.event
async def answer(sid, data):
    """User B accepts and replies to User A."""
    target_sid = data.get('target')
    if target_sid:
        await sio.emit('answer', {'sender': sid, 'sdp': data['sdp']}, to=target_sid)

@sio.event
async def ice_candidate(sid, data):
    """Peers exchange network routing information to bypass firewalls."""
    target_sid = data.get('target')
    if target_sid:
        await sio.emit('ice_candidate', {'sender': sid, 'candidate': data['candidate']}, to=target_sid)

if __name__ == "__main__":
    uvicorn.run(sio_app, host="0.0.0.0", port=8000)