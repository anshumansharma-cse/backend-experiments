from fastapi import FastAPI #(fastapi-framework & FASTAPI-Class) ??
import uvicorn #uvicorn - waht, why

app = FastAPI() #What?-> Self constructor?

# Meaning-> saying fastapi to show in '/' root dir?
@app.get("/") #Decorator does what? '/' -> Routing?
def read_root():
    return {"message": "First FastAPI", "Status": "Gold"}

# __name__ dunder usage here?
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
