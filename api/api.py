from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.orm import Session, sessionmaker

from models.users import User, UserData, UserResponse, UpdateUserName
from models.dbModels import Users
from database import engine
from func.func import hash_password, check_password

router = APIRouter()
security = HTTPBasic()

SessionLocal = sessionmaker(autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_user(email, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.email == email).first()
    return user

def get_db_user_from_id(id, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == id).first()
    return user

async def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = get_db_user(credentials.username, db)
    if user is None or check_password(user.password, credentials.password) != True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not auth")
    return user


@router.get("/login/")
async def login_user(userData: UserData = Depends(authenticate_user)):
    return {"message": "You have access to the protected resource!", "user_info": userData}


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def create_user_in_db(user: User, db: Session = Depends(get_db)):
    user_db = get_db_user(user.email, db)
    if user_db is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is busy")
    hash_pass = hash_password(user.password)
    user_create = Users(username=user.username, password=hash_pass, email=user.email)
    db.add(user_create)
    db.commit()
    return {"message": "User create successfully!"}


@router.get("/user/{user_id}", response_model=UserResponse)
async def check_user_in_db(user_id: int, db: Session = Depends(get_db)):
    user = get_db_user_from_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found")
    return user


@router.put("/update/{user_id}", response_model=UserResponse)
async def update_user_in_db(user_id: str, userData: UpdateUserName , db: Session = Depends(get_db)):
    user = get_db_user_from_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found")
    #проверка имени
    user.username = userData.username
    db.commit()
    return user


@router.delete("/delete_user/{user_id}")
async def delete_user_in_db(user_id: int, db: Session = Depends(get_db)):
    user_db = get_db_user_from_id(user_id, db)
    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found")
    db.delete(user_db)
    db.commit()
    return {"message": "User delete successfully!"}


