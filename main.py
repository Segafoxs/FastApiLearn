import uvicorn
from fastapi import FastAPI
from models.dbModels import Base
from database import engine
from api import main_router


app = FastAPI()
app.include_router(main_router)
Base.metadata.create_all(bind=engine)




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")