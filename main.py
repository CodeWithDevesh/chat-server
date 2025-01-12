from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groclake.cataloglake import CatalogLake
from groclake.modellake import ModelLake
import os


# Environment variable setup
GROCLAKE_API_KEY = 'a3c65c2974270fd093ee8a9bf8ae7d0b'
GROCLAKE_ACCOUNT_ID = 'cecf88db41531add5d0cefaa83fedb38'

os.environ['GROCLAKE_API_KEY'] = GROCLAKE_API_KEY
os.environ['GROCLAKE_ACCOUNT_ID'] = GROCLAKE_ACCOUNT_ID

# Initialize FastAPI app and Groclake services
app = FastAPI()
catalog = CatalogLake()
model_lake = ModelLake()
# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:5175"] for stricter security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define the chatbot settings
chatbot_name = "Well Wise"
chatbot_description = "I am a virtual doctor/therapist here to assist you with medical questions specially mental health."
chatbot_instructions = "Please provide helpful and accurate medical advice based on the symptoms described."

# Pydantic model for request payload
class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []

# Root endpoint
@app.get("/")
def read_root():
    return {
        "chatbot_name": chatbot_name,
        "description": chatbot_description,
        "instructions": chatbot_instructions
    }

# Chat endpoint for interacting with the chatbot
@app.post("/chat/")
def chat_endpoint(request: ChatRequest):
    try:
        # Prepare the conversation history
        conversation_history = request.conversation_history
        conversation_history.append({"role": "user", "content": request.message})

        # Create the payload for model interaction
        payload = {
            "messages": conversation_history,
            "token_size": 300
        }

        # Get response from the model
        response = model_lake.chat_complete(payload=payload)
        bot_reply = response.get('answer', "Sorry, I couldn't process that.")

        # Add the assistant's reply to conversation history
        conversation_history.append({"role": "assistant", "content": bot_reply})

        return {
            "chatbot_name": chatbot_name,
            "response": bot_reply,
            "conversation_history": conversation_history
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during chat processing: {e}")

# Run the API server (for local testing)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)