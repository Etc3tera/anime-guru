from typing import Union

from fastapi import FastAPI

from pydantic import BaseModel

from extract import retrieve_anime_information
from inference import check_self_knowledge

class KnowledgeCheckModel(BaseModel):
    anime_name: str

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/check-anime-knowledge")
async def check_anime_knowledge(payload: KnowledgeCheckModel):
    return { "anime_name": payload.anime_name, "has_knowledge": check_self_knowledge(payload.anime_name) }

@app.post("/fetch-anime-info")
async def get_anime_info(payload: KnowledgeCheckModel):
    info = retrieve_anime_information(payload.anime_name)
    return { "anime_name": payload.anime_name, "info": info }