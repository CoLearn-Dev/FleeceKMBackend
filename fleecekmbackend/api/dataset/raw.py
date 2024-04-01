from fastapi import APIRouter, Depends
from fleecekmbackend.db.helpers import get_random_samples_raw
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fleecekmbackend.db.models import Paragraph
from fleecekmbackend.db.ctl import get_db

router = APIRouter()

@router.get("/rand-sample")
def random_samples(n: int, db: Session = Depends(get_db)):
    samples = get_random_samples_raw(n, db)
    return samples

def get_random_samples_raw(n: int, db: Session):
    query = select(Paragraph).order_by(func.random()).limit(n)
    result = db.execute(query)
    samples = result.fetchall()
    return samples
