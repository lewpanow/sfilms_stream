import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import router as auth_router

app = FastAPI(title="Films App")

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:63342",
    "http://127.0.0.1:63342",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "API is running"}


def main():
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8011,
        reload=True,
    )

if __name__ == '__main__':
    main()