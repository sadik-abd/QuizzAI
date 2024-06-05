from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
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

def decodeImage(data_uri: str, folder_path: str):
    import os
    import base64

    data_uri = data_uri
    media_type, base64_data = data_uri.split(",", 1)

    # Decode the Base64 data
    decoded_image = base64.b64decode(base64_data)

    # Ensure the folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save the decoded image to a file in the specified folder
    file_path = os.path.join(folder_path, "thumbnail.png")
    with open(file_path, "wb") as file:
        file.write(decoded_image)


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
    user_answers : list[str]
    docname : str


class SubjectSchema(BaseModel):
    userid : str
    name : str
    image : str

@app.post("/create_subject")
async def create_subject(data : SubjectSchema):
    if not os.path.isdir(f"data/{data.userid}"):
            os.system(f"mkdir data/{data.userid}")
    if not os.path.isdir(f"data/{data.userid}/{data.name}"): 
        os.system(f"mkdir data/{data.userid}/{data.name}")
    decodeImage(data.image, f"data/{data.userid}/{data.name}")

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
        outp = model.feedback_qna(data.user_answers, json.load(open(saved_path,"r",encoding="utf-8"))["user"])

        # Respond back with the processed data or a success message
        return {"message": "Model Feedback is given", "output": outp}
    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=400, detail={"status": "error", "message": str(e)})

@app.get("/history")
async def get_history(userid : str):
    docs = {}
    for subject in os.listdir(f"data/{userid}/"):
        for doc in os.listdir(f"data/{userid}/{subject}"):
            if ".json" in doc:
                docs[subject] = {"image":f"data/{userid}/{subject}/thumbnail.png","data":{}}
                docs[subject]["data"][doc[:-5]] = json.load(open(f"data/{userid}/{subject}/{doc}","r",encoding="utf-8"))["app"]
    return docs

@app.get("/getimage/{folder}")
async def get_image(image_path: str):
    # Ensure the file exists
    file_path = Path(image_path)
    if file_path.is_file():
        return FileResponse(file_path)
    else:
        return {"error": "File does not exist"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)