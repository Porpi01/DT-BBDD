from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
from typing import List, Dict, Any
import uvicorn

load_dotenv()

app = FastAPI()

# CORS para permitir llamadas desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción ajusta dominio
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión MongoDB
client = None
db = None
startups_collection = None

@app.on_event("startup")
def startup_db_client():
    global client, db, startups_collection
    mongo_url = os.getenv("DATABASE_URL")
    if not mongo_url:
        raise RuntimeError("DATABASE_URL no configurada.")
    client = MongoClient(mongo_url)
    db = client["Cluster0"]
    startups_collection = db["startup"]
    print("✅ Conectado a MongoDB.")

@app.on_event("shutdown")
def shutdown_db_client():
    if client:
        client.close()
        print("👋 Conexión a MongoDB cerrada.")

@app.get("/", response_class=HTMLResponse)
def get_home():
    # Sirve el HTML estático (lo cargas desde 'templates/index.html')
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: index.html no encontrado</h1>"

# ------------------
# Endpoints para los datos de los gráficos y tablas





@app.get("/api/startups/awards-by-sector")
def awards_by_sector():
    # Sumatoria de premios por sector
    pipeline = [
    {"$match": {"awards": {"$ne": None, "$ne": ""}}},
    {"$group": {"_id": "$sector", "total_awards": {"$sum": {"$toInt": "$awards"}}}},
    {"$sort": {"total_awards": -1}}
]
    result = list(startups_collection.aggregate(pipeline))
    data = [{"sector": doc["_id"] or "Otros", "total_awards": doc["total_awards"]} for doc in result]
    return data

@app.get("/api/startups/contact-web-status")
def contact_web_status():
    with_contact = startups_collection.count_documents({"contactPerson": {"$exists": True, "$ne": None}})
    without_contact = startups_collection.count_documents({"$or": [{"contactPerson": {"$exists": False}}, {"contactPerson": None}]})
    with_website = startups_collection.count_documents({"website": {"$exists": True, "$ne": None}})
    without_website = startups_collection.count_documents({"$or": [{"website": {"$exists": False}}, {"website": None}]})

    return [
        {"status": "Con contacto", "count": with_contact},
        {"status": "Sin contacto", "count": without_contact},
        {"status": "Con web", "count": with_website},
        {"status": "Sin web", "count": without_website}
    ]

@app.get("/api/startups/sector-distribution")
def sector_distribution():
    # Contar cuántas startups hay por sector
    pipeline = [
        {"$group": {
            "_id": "$sector",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    result = list(startups_collection.aggregate(pipeline))
    data = [{"sector": doc["_id"] or "Otros", "count": doc["count"]} for doc in result]
    return data


@app.get("/api/startups/top-awards")
def top_awards():
    pipeline = [
        {"$addFields": {
            "awardsInt": {
                "$convert": {
                    "input": "$awards",
                    "to": "int",
                    "onError": 0,
                    "onNull": 0
                }
            }
        }},
        {"$sort": {"awardsInt": -1}},
        {"$limit": 5},
        {"$project": {"company": 1, "awards": "$awardsInt", "_id": 0}}
    ]
    result = list(startups_collection.aggregate(pipeline))
    return result

@app.get("/api/startups/contacts")
def contacts_list():
    # Lista de contactos con campos básicos
    cursor = startups_collection.find(
        {"contact": {"$ne": None}},
        {"company": 1, "contact": 1, "email": 1, "sector": 1, "_id": 0}
    )
    return list(cursor)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
