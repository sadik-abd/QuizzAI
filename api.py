from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import QuizzGenModel
import os
from typing import Optional

app = FastAPI()
model = QuizzGenModel()

# Configure CORS
origins = ["*"]  # Adjust this based on your frontend's domain for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def gen_message(num_questions: int = Form(...), prompt: str = Form(""), ocr_scan: bool = Form(False), language: str = Form("english"), doc_type: str = Form(...), doc: UploadFile = File(...)):
    try:
        # Save the main document
        saved_path = os.path.join("./docs", doc.filename)  # Define your save directory
        with open(saved_path, "wb+") as file_object:
            file_object.write(doc.file.read())

        # Generate the output using the model
        output = model.generate(saved_path, num_questions, user_req=prompt, ocr_scan=ocr_scan, lang=language)

        # Create a response
        return output  # Sending back the JSON response
    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=400, detail={"status": "error", "message": str(e)})

@app.post("/gen_feedback")
async def gen_feedback(user_answers: dict, history: dict, language: str):
    try:
        # Process the data
        outp = model.feedback_qna(user_answers, history, language)

        # Respond back with the processed data or a success message
        return {"message": "Model Feedback is given", "output": outp}
    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=400, detail={"status": "error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)  # Remember to turn off debug mode in production
