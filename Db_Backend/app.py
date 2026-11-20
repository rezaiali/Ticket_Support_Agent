from fastapi import FastAPI
from dotenv import load_dotenv
import os
import uvicorn
import Service.ticketService as ticketService

app=FastAPI()

load_dotenv()

app.include_router(ticketService.ticket_router, prefix="/api")
@app.get("/")
def greetingMessage():
    gMessage={"messages":"AI Support Ticket Agent endpoint started"}
    return gMessage

def startApiService():
    try:
        thehost = os.getenv("API_HOST", "0.0.0.0")
        uvicorn.run(app, port=4046, host=thehost, reload=False)
        
    except Exception as error:
        print (f"Api service error: {error}")

if __name__=="__main__":
    startApiService()