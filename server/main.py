from fastapi import FastAPI,Form,UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
import os
from fastapi.staticfiles import StaticFiles
import jwt
import bcrypt

app=FastAPI()
SECRET_KEY="brn"

app.mount("/uploads",StaticFiles(directory="uploads"),name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class User(BaseModel):
    firstName:str
    lastName:str
    age:int
    email:str
    password:str
    mobileNo:int
    profilePic:str


def check_connection():
    try:
        client = MongoClient("mongodb+srv://vemulajyothi24_db_user:pythonbatch@pythonbatch.xpkdkez.mongodb.net/?appName=pythonbatch")

        db = client["post"]
        collection = db["postUsers"]
        print("Successfully connected to MDB")
        return collection
    except Exception as e:
        print("Unable to connect")
        print(e)    
        return None



@app.post("/signupFD")
async def signupFormData(
    firstName:str=Form(...),
    lastName:str=Form(...),
    age:int=Form(...),
    email:str=Form(...),
    password:str=Form(...),
    mobileNo:int=Form(...),
    profilePic:UploadFile=File(...)  
):
   users = check_connection()

   if users is None:
    return {"status":"Failure","msg":"DB is not connected"}
   
   file_path = os.path.join("uploads",profilePic.filename)

   with open(file_path,"wb") as f:
        f.write(await profilePic.read())

   print(file_path)

   salt_rounds = bcrypt.gensalt(rounds=15)

   hashed_password = bcrypt.hashpw(password.encode('utf-8'),salt_rounds)

   data = {
    "firstName":firstName,
    "lastName":lastName,
    "age":age,
    "email":email,
    "password":hashed_password,
    "mobileNo":mobileNo,
    "profilePic":file_path
   }

   users.insert_one(data)
   
  
   return{
    "status":"Success",
    "msg":"Account Created Successfully" 
   }

@app.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...)
):

    users = check_connection()

    user = users.find_one({"email": email})
    print(user)

    if user:
        # if user["password"] == password:
        if bcrypt.checkpw(password.encode('utf-8'),user["password"]):
            token  = jwt.encode({"email":email,"password":password},SECRET_KEY,algorithm="HS256")

            dataToSend = {
                "firstName": user["firstName"],
                "lastName": user["lastName"],
                "age": user["age"],
                "email": user["email"],
                "mobileNo": user["mobileNo"],
                "profilePic": user["profilePic"],
                "token":token
            }

            return {
                "status": "Success",
                "msg": "Credentials are correct",
                "data": dataToSend
            }

        else:
            return {
                "status": "Failure",
                "msg": "Invalid Password"
            }

    else:
        return {
            "status": "Failure",
            "msg": "User Doesn't exist"
        }

@app.post("/validateToken")
def validate_token(token: str = Form(...)):

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(decoded)
        email = decoded["email"]
        password = decoded["password"]

        users = check_connection()

        user = users.find_one({"email": email})
        print(user)

        if user:
            if user["password"] == password:
                dataToSend = {
                    "firstName": user["firstName"],
                    "lastName": user["lastName"],
                    "age": user["age"],
                    "email": user["email"],
                    "mobileNo": user["mobileNo"],
                    "profilePic": user["profilePic"],
                    
                }

                return {
                    "status": "Success",
                    "msg": "Credentials are correct",
                    "data": dataToSend
                }

            else:
                return {
                    "status": "Failure",
                    "msg": "Invalid Password"
                }

        else:
            return {
                "status": "Failure",
                "msg": "User Doesn't exist"
            }

    except:
        return {
            "status": "Failure",
            "msg": "Invalid Token"
        }



@app.patch("/updateProfile")
async def editprofile(
    firstName: str = Form(None),
    lastName: str = Form(None),
    age: int = Form(None),
    email: str = Form(...),
    password: str = Form(None),
    mobileNo: int = Form(None),
    profilePic: UploadFile = File(None)
):
    users = check_connection()

    update_data = {}

    if firstName:
        update_data["firstName"] = firstName
    if lastName:
        update_data["lastName"] = lastName
    if age:
        update_data["age"] = age
    if password:
        update_data["password"] = password
    if mobileNo:
        update_data["mobileNo"] = mobileNo

    # ✅ HANDLE FILE SAFELY
    if profilePic is not None:
        file_path = os.path.join("uploads", profilePic.filename)

        with open(file_path, "wb") as f:
            f.write(await profilePic.read())

        update_data["profilePic"] = file_path

    # ✅ update only if data exists
    if update_data:
        users.update_one({"email": email}, {"$set": update_data})

    return {
        "status": "Success",
        "msg": "User Updated Successfully"
    }


@app.delete("/deleteProfile")   
async def delete_profile(email:str=Form(...)):
    users = check_connection()

    result = users.delete_many({"email":email})
    if result.deleted_count > 0:
        return {"status":"Success","msg":"User Deleted Successfully"}
    else:
       return {"status":"Failure","msg":"Nothing is deleted"}    
     