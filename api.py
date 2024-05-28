from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models import QuizzGenModel
import os
import json

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

class GenSchema(BaseModel):
    userid : str
    subject : str
    docname : str
    num_questions : int = 0 
    prompt : str = ""
    ocr_scan : bool = False

class FeedbackSchema(BaseModel):
    userid : str
    subject : str
    user_answers : list
    docname : str

class HistSchema(BaseModel):
    userid  : str

@app.post("/generate")
async def gen_message(
    userid: str = Form(...),
    subject: str = Form(...),
    docname: str = Form(...),
    num_questions: int = Form(0),
    prompt: str = Form(""),
    ocr_scan: bool = Form(False),
    doc: UploadFile = File(...)
):
    data = GenSchema(
        userid=userid,
        subject=subject,
        docname=docname,
        num_questions=num_questions,
        prompt=prompt,
        ocr_scan=ocr_scan
    )
    try:
        # Save the main document
        if not os.path.isdir(f"data/{data.userid}"):
            os.system(f"mkdir data/{data.userid}")
        if not os.path.isdir(f"data/{data.userid}/{data.subject}"): 
            os.system(f"mkdir data/{data.userid}/{data.subject}")
        saved_path = os.path.join(f"data/{data.userid}/{data.subject}", doc.filename)  # Define your save directory
        with open(saved_path, "wb+") as file_object:
            file_object.write(doc.file.read())

        # Generate the output using the model
        output = model.generate(saved_path, data.num_questions,histpath=f"data/{data.userid}/{data.subject}/{data.docname}.json", user_req=data.prompt, ocr_scan=data.ocr_scan)

        # Create a response
        return output  # Sending back the JSON response
    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=400, detail={"status": "error", "message": str(e)})

@app.post("/gen_feedback")
async def gen_feedback(data : FeedbackSchema):
    try:
        # Process the data
        saved_path = os.path.join(f"data/{data.userid}/{data.subject}", f"{data.docname}.json")
        outp = model.feedback_qna(data.user_answers, json.load(open(saved_path,"r","utf-8"))["user"])

        # Respond back with the processed data or a success message
        return {"message": "Model Feedback is given", "output": outp}
    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=400, detail={"status": "error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
