from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes.categories import router as cat_router
from routes.shortcuts import router as sc_router
from routes.ebooks import router as ebook_router

app = FastAPI(title="Web Shortcut Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(cat_router)
app.include_router(sc_router)
app.include_router(ebook_router)
