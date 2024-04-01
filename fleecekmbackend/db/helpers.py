from fleecekmbackend.db.ctl import session, engine
from fleecekmbackend.db.models import Paragraph, Author
from sqlalchemy import func, select
from sqlalchemy.orm import Session
import pandas as pd
import logging

logging.getLogger().addHandler(logging.StreamHandler())

def load_csv_data(file):
    with session() as db:
        try:
            # Check if the table exists and has data
            conn = db.connection()
            has_table = conn.dialect.has_table(conn, Paragraph.__tablename__)
            
            if has_table:
                # Check if the table has any data
                result = conn.execute(select(func.count()).select_from(Paragraph))
                count = result.scalar()
                if count > 0:
                    print(f"Dataset is already loaded with {count} entries. Skipping loading process.")
                    return
            
            # Load the dataset if the table doesn't exist or is empty
            df = pd.read_csv(file)
            df['within_page_order'] = df.groupby('page_name').cumcount()
            
            if not has_table:
                # Create the table if it doesn't exist
                conn.run_sync(Paragraph.__table__.create)
                conn.commit()  # Commit the table creation transaction
                
            try:
                # Insert the data into the database
                df.to_sql(
                    name=Paragraph.__tablename__,
                    con=conn,
                    if_exists="append",
                    index=False,
                )
                
                # Commit the data insertion transaction
                conn.commit()
                
            except Exception as e:
                # Rollback the data insertion transaction if an error occurs
                conn.rollback()
                raise e
            
        except Exception as e:
            logging.error(f"Error loading CSV data helper: {str(e)}")
            
        finally:
            logging.info("Data loaded successfully")

def get_random_samples_raw(n: int, db: Session):
    query = select(Paragraph).order_by(func.random()).limit(n)
    result = db.execute(query)
    samples = result.scalars().all()
    return samples

def get_random_samples_raw_as_df(n: int, db: Session):
    query = select(Paragraph).order_by(func.random()).limit(n)
    result = db.execute(query)
    samples = result.scalars().all()
    df = pd.DataFrame([sample.__dict__ for sample in samples])
    df = df.drop(columns=['_sa_instance_state'])
    return df

def get_random_unprocessed_paragraph(db: Session):
    query = select(Paragraph).filter(Paragraph.processed == -1).order_by(func.random()).limit(1)
    result = db.execute(query)
    paragraph = result.scalar()
    if paragraph is None:
        return -1
    return paragraph

def get_page_raw(db: Session, index: int = -1):
    if index == -1: # get all the paragraphs with the same (randomly selected) page_name
        query = select(Paragraph.page_name).distinct().order_by(func.random()).limit(1)
        result = db.execute(query)
        page_name = result.scalar()
        query = select(Paragraph).filter(Paragraph.page_name == page_name)
    else: # get paragraphs with pagename in order
        query = select(Paragraph.page_name).distinct().order_by(Paragraph.page_name).offset(index).limit(1)
        result = db.execute(query)
        page_name = result.scalar()
        query = select(Paragraph).filter(Paragraph.page_name == page_name)
    result = db.execute(query)
    samples = result.scalars().all()
    return samples

def create_author_if_not_exists(prompt: str, model: str):
    with session() as db:
        result = db.execute(select(Author).filter(Author.model == model, Author.prompt == prompt))
        author = result.scalar()
        if author is None:
            author = Author(model=model, prompt=prompt)
            db.add(author)
            db.commit()
            db.refresh(author, ["id"])
        return author
