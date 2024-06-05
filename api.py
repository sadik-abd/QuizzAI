from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Query
from fastapi.responses import FileResponse
from pathlib import Path
import json
from typing import List
from configs import *
import os, sys
import crud  # Make sure this is your CRUD operations file
from schemas import User as UserSchema, Camera as CameraSchema, PersonnelCrt,Personnel  # Import your Pydantic schemas
import schemas
import shutil
import logging
from database import Session,PersonnelDB
from recg import Recogniser
import cv2
app = FastAPI(title="api")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

persons = json.load(open(FACES_PATH,"r",encoding="utf-8"))
ai_model = Recogniser()

@app.get("/")
def app_root():
    return {"Message":"App is running. check the docs to call the APIs.","message2":"Hello world my friend"}

####################################################################################### User routes
@app.post("/users/", response_model=UserSchema)
def create_user(user: UserSchema):
    crud.create_user(user)
    return user

@app.get("/users/{username}", response_model=UserSchema)
def read_user(username: str):
    db_user = crud.get_user(username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=List[UserSchema])
def read_users():
    return crud.get_all_users()

@app.delete("/users/{username}")
def delete_user(username: str):
    crud.delete_user(username)
    return {"message": "User deleted"}

####################################################################################### Camera routes
@app.post("/cameras/", response_model=CameraSchema)
def create_camera(camera: CameraSchema):
    crud.create_camera(camera)
    return camera

@app.get("/cameras/{camera_id}", response_model=CameraSchema)
def read_camera(camera_id: int):
    db_camera = crud.get_camera(camera_id)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return db_camera

@app.get("/cameras/", response_model=List[CameraSchema])
def read_cameras():
    return crud.get_all_cameras()

@app.delete("/cameras/{camera_id}")
def delete_camera(camera_id: int):
    crud.delete_camera(camera_id)
    return {"message": "Camera deleted"}

@app.put("/cameras/{camera_id}/ai_algs", response_model=CameraSchema)
def update_camera_ai_algs(camera_id: int, ai_algs_update: schemas.CameraAIAlgsUpdate):
    existing_camera = crud.get_camera(camera_id)
    if not existing_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    out = crud.update_camera_ai_algs(camera_id, ai_algs_update.AI_algs, ai_algs_update.activity_time)
    if out == 0:
        raise HTTPException(status_code=404, detail="Algorithm not implemented yet")
    return crud.get_camera(camera_id)

####################################################################################### Algorithms aAPI

@app.post("/algorithms/", response_model=schemas.Algorithm)
def create_algorithm(algorithm: schemas.Algorithm):
    return crud.create_algorithm(algorithm=algorithm)

@app.get("/algorithms/", response_model=List[schemas.Algorithm])
def read_algorithms():
    algorithms = crud.get_algorithms()
    return algorithms

@app.delete("/algorithms/{alg_name}")
def delete_algorithms(alg_name: str):
    outp = crud.delete_algorithm(alg_name)
    return outp

####################################################################################### Personnel Database APIs
@app.post("/personnels/", response_model=Personnel)
async def create_personnel_api(name: str = Form(...),
                               blist: str = Form(...),
                               Gender: str = Form(...),
                               DateOfBirth: str = Form(...),
                               role: str = Form(...),
                               uid: str = Form(...),
                               file: UploadFile = File(...)):
    sess = Session()
    len_pers = len(sess.query(PersonnelDB).all())
    file_location = os.path.join(f"{PERSONNEL_ASSET_PATH}",f"{name.replace(' ','_')+str(len_pers)+'.'+file.filename.split('.')[-1]}")
    fname = f"{name.replace(' ','_')+str(len_pers)+'.'+file.filename.split('.')[-1]}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Assuming 'path' is the attribute where you want to store the file path
    personnel_data = Personnel(name=name, path=fname, blist=blist,
                                  Gender=Gender, DateOfBirth=DateOfBirth,
                                  role=role, uid=uid)
    
    # Use your CRUD operation for creating personnel
    return crud.create_personnel(personnel_data)

@app.get("/personnels/", response_model=List[Personnel])
async def read_personnels():
    return crud.get_personnels()

@app.get("/personnels/{personnel_id}", response_model=Personnel)
async def read_personnel(personnel_id: int):
    personnel = crud.get_personnel_by_id(personnel_id)
    if personnel is None:
        raise HTTPException(status_code=404, detail="Personnel not found")
    return personnel

@app.delete("/personnels/{personnel_id}", response_model=bool)
async def delete_personnel_api(personnel_id: int):
    result = crud.delete_personnel(personnel_id)
    if not result:
        raise HTTPException(status_code=404, detail="Personnel not found")
    return result


################################# AI Events API
@app.post("/events/")
async def upload_event(name: str,dtime:str,message:str,camname:str, file: UploadFile = File(...)):
    filename = f"{camname}-{name}-{dtime}{os.path.splitext(file.filename)[1]}"  # NAME+FILE_EXTENSION
    file_path = os.path.join(FOOTAGEPATH, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create event in the database
    event = crud.create_event(name,dtime,camname,message, filename)
    frame = cv2.imread(file_path)
    results = ai_model.detect(frame)
    if results is not None:
        boxes, scores, classids, kpts = results
        persons[filename] = []
        for boxe, score, kpt in zip(boxes, scores, kpts):
            name,scor = ai_model.search_flatten(ai_model.get_embeds(frame, boxe, score, kpt ))#*[np.array(i,dtype=np.float64) for i in [boxe, score, kpt]]))
            
            persons[filename].append(name)
            json.dump(persons,open(FACES_PATH,"w",encoding="utf-8"))
    return {"filename": filename}

@app.get("/faces_in_event")
async def get_event_faces(name: str):
    try:
        retr = persons[name]
        return retr
    except KeyError as K:
        return ["No Persons"]
@app.get("/get_all_faces")
async def get_event_faces():
    return persons
@app.get("/events/")
async def read_events():
    events = crud.get_all_events()
    return events

@app.get("/events/{event_id}")
async def read_event(event_id: int):
    db_event = crud.get_event(event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@app.put("/events/{event_id}")
async def update_event_api(event_id: int, event: schemas.EventUpdate):
    db_event = crud.update_event(event_id, event.name, event.date, event.camname)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@app.delete("/events/{event_name}")
async def delete_event_api(event_name: str):
    db_event = crud.delete_event(event_name)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@app.get("/search_events/")
async def search_evnt(
    name: str = Query(None),
    camname: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
):
    dtime_results = crud.search_events(name,camname,start_date,end_date)
    return dtime_results

@app.get("/getimage/{folder}")
async def get_image(folder : int,image_path: str):
    # Ensure the file exists
    fl_path = PERSONNEL_ASSET_PATH if folder == 0 else FOOTAGEPATH
    file_path = Path(os.path.join(fl_path,image_path))
    logger.info(file_path)
    if file_path.is_file():
        return FileResponse(file_path)
    else:
        return {"error": "File does not exist"}

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(app,host="0.0.0.0",port=8232)
