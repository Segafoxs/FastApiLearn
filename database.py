from sqlalchemy import create_engine

dataBaseURL = "postgresql://postgres:admin1@localhost/postgres"
engine = create_engine(dataBaseURL)