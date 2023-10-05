import uvicorn
from .config import PORT

def main():
    uvicorn.run(
        "CaaS.__main__:main", 
        host="0.0.0.0",
        port=PORT,
        reload=True
    )

if __name__ == "__main__":
    main()