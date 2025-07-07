from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import FileResponse
from utils.audio import speech_to_text, text_to_speech
from langchain_agent.hybrid_agent import get_context_aware_hybrid_agent
import os
from vector_store.index_faiss import search
from vector_store.embedder import get_embedding


router = APIRouter()

@router.post("/voice-chat")
async def voice_chat(audio: UploadFile = File(...), request: Request = None):
    try:
        # Save uploaded audio file
        file_path = f"temp/{audio.filename}"
        with open(file_path, "wb") as f:
            f.write(await audio.read())

        # Transcribe speech to text
        query = speech_to_text(file_path)

        # Get user ID for memory tracking
        user_id = request.headers.get("X-User-ID", "voice_user")

        # Run hybrid agent (MongoDB + Vector + Memory)
        agent = get_context_aware_hybrid_agent(user_id)
        response = agent.run(query)

        # Convert agent response to audio
        output_path = "temp/response.mp3"
        text_to_speech(response, output_path)

        return FileResponse(output_path, media_type="audio/mpeg")

    except Exception as e:
        return {"error": str(e)}
