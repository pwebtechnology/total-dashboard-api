from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging
import uvicorn
from pymongo import MongoClient

# Define constants and settings
SECRET_KEY = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
DATABASE_URL = "mongodb://NikKimp:NikKimp@172.23.2.15:27017/?tls=false&authMechanism=DEFAULT"

app = FastAPI()

# Initialize MongoDB
client = MongoClient(DATABASE_URL)
db = client['Users']
users_collection = db['user_creds']

# JWT Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Crypt Context for Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic Models
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

# Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    print("request headers:",Request.headers)
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        logging.error(f"JWT Error: {e}")
        raise credentials_exception
    return token_data

# FastAPI Routes
@app.post("/token", response_model=Token)
async def login(user: User):
    db_user = users_collection.find_one({"username": user.username})
    if db_user and verify_password(user.password, db_user['password']):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

@app.get("/get_builder_data_props")
async def get_builder_data_props(
    pageIndex: int = 0,
    pageSize: int = 10,
    dimentions: Optional[List[str]] = None,
    metrics: Optional[List[str]] = None,
    current_user: TokenData = Depends(get_current_user)
):
    try:
        # Example props structure
        props = {
            'pageIndex': pageIndex,
            'pageSize': pageSize,
            'dimentions': dimentions or [],
            'metrics': metrics or []
        }
        # Replace the following line with the actual data fetching logic
        data = await get_total_builder_data_props(props)  # Ensure this function is implemented
        return data
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    except JWTError as e:
        logging.error(f"JWT Error during refresh: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
async def protected_route(current_user: TokenData = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}, this is a protected route!"}

@app.post("/logout")
async def logout():
    # Logic to handle logout (In a real scenario, this might involve token blacklisting or invalidation)
    return {"message": "Logged out successfully"}

# Placeholder function for fetching builder data
async def get_total_builder_data_props(props):
    # Replace this with your actual data fetching logic
    # Here, we just return a mock response
    return {
        "props": props,
        "data": "This is mock data. Replace with actual data fetching."
    }

# Run FastAPI Application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")
