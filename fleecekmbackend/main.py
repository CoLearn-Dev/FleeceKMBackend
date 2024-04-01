import logging
import asyncio
import sqlite3
from fastapi import FastAPI, Request
from fleecekmbackend.api.dataset.raw import router as raw_dataset_router
from fleecekmbackend.api.dataset.qa import router as qa_dataset_router
from fleecekmbackend.core.config import DATASET_PATH
from fleecekmbackend.services.dataset.generate_qa import start_background_process_test

background_process_started = False

app = FastAPI()

# Include sub-routers
app.include_router(raw_dataset_router, prefix="/raw", tags=["raw"])
app.include_router(qa_dataset_router, prefix="/qa", tags=["qa"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to the WikiText API!"}

@app.on_event("startup")
async def startup_event():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paragraph (
                
            )
        """)
        conn.commit()
        
        # Load CSV data
        # with open(DATASET_PATH, "r") as file:
        #     reader = csv.reader(file)
        #     for row in reader:
        #         cursor.execute("INSERT INTO your_table_name (column1, column2, ...) VALUES (?, ?, ...)", row)
        #     conn.commit()
        
    except Exception as e:
        logging.error(f"Error creating table or loading CSV data: {str(e)}")
    finally: 
        global background_process_started
        if not background_process_started:
            asyncio.create_task(start_background_process_test())
            background_process_started = True

