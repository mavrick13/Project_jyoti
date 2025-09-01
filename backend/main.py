from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import socketio
import uvicorn
import os
from pathlib import Path

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, farmers, tasks, chat, dashboard, users, inventory

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Project Moriarty API",
    description="Farmer Management System Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.ALLOWED_ORIGINS
)

# Combine FastAPI and Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(farmers.router, prefix="/api/farmers", tags=["Farmers"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "message": "Project Moriarty API is running",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Project Moriarty API",
        "docs": "/docs",
        "health": "/health"
    }

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")
    await sio.emit('message', {'data': 'Connected to Project Moriarty'}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")

@sio.event
async def join_room(sid, data):
    room = data.get('room')
    if room:
        await sio.enter_room(sid, room)
        await sio.emit('message', {'data': f'Joined room {room}'}, room=sid)

@sio.event
async def leave_room(sid, data):
    room = data.get('room')
    if room:
        await sio.leave_room(sid, room)
        await sio.emit('message', {'data': f'Left room {room}'}, room=sid)

@sio.event
async def send_message(sid, data):
    room = data.get('room', sid)
    message = data.get('message')
    user = data.get('user')
    
    if message:
        await sio.emit('new_message', {
            'message': message,
            'user': user,
            'timestamp': data.get('timestamp')
        }, room=room)

if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )