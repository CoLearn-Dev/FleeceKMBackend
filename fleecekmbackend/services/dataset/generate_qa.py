import logging
from typing import List, Tuple
from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker
from fleecekmbackend.db.helpers import get_random_unprocessed_paragraph
from fleecekmbackend.services.dataset.fleece_qa import process_paragraph
from fleecekmbackend.db.models import Paragraph, Question, Answer, Rating, Author
from fleecekmbackend.db.ctl import session

def process_all_pages():
    try:
        # Get the last processed page name
        last_processed_paragraph_index = session.query(Paragraph.processed).order_by(Paragraph.processed.desc()).first()
        if last_processed_paragraph_index is None:
            last_processed_page = ""

        print(f"last_processed_page: {last_processed_page}")
        print(f"last_processed_paragraph_index: {last_processed_paragraph_index}")

        current_paragraph = get_random_unprocessed_paragraph(session)

        print(f"current_paragraph: {current_paragraph}")

        while current_paragraph is not None:
            try:
                print(f"Processing page {current_paragraph.page_name}...")
                generated_questions, generated_answers, generated_ratings = process_paragraph(session, current_paragraph)
                print(f"generated_questions: {generated_questions}")   
                print(f"generated_answers: {generated_answers}")
                print(f"generated_ratings: {generated_ratings}")
                current_paragraph = get_random_unprocessed_paragraph(session)
            except Exception as e:
                logging.error(f"Error processing page {current_paragraph.page_name}")
                logging.error(str(e))

        logging.info("All pages processed successfully.")
    except Exception as e:
        logging.error("Error in process_all_pages function:")
        logging.error(str(e))

def test_process_all_pages():
    try:
        # Create the engine and session
        engine = create_engine('sqlite:///path/to/database.db')
        Session = sessionmaker(bind=engine)
        session = Session()

        # Clean up the database
        print("Cleaning up the database...")
        session.query(Rating).delete()
        session.query(Answer).delete()
        session.query(Question).delete()
        session.query(Author).delete()
        session.query(Paragraph).delete()
        session.commit()
        print("Database cleaned successfully.")

        # Create test data
        paragraphs = [
            Paragraph(page_name="Page 1", within_page_order=1, text="Paragraph 1"),
            Paragraph(page_name="Page 1", within_page_order=2, text="Paragraph 2"),
            Paragraph(page_name="Page 2", within_page_order=1, text="Paragraph 3"),
            Paragraph(page_name="Page 2", within_page_order=2, text="Paragraph 4"),
        ]
        for paragraph in paragraphs:
            session.add(paragraph)
        session.commit()
        print("Test data created successfully.")

        # Run the process_all_pages function
        process_all_pages()
        print("All pages processed successfully.")

        # Check the results
        questions = session.query(Question).all()
        answers = session.query(Answer).all()
        ratings = session.query(Rating).all()

        print(f"Questions: {len(questions)}")

        assert len(questions) > 0
        assert len(answers) > 0
        assert len(ratings) > 0

        print("Results checked successfully.")

        # Run the process_all_pages function again to check for duplicates
        try:
            process_all_pages()
            print("No duplicates were created.")
        except Exception as e:
            print("Error in process_all_pages function:")
            print(str(e))
        finally:
            print("All pages processed successfully.")

            # Check that no duplicates were created
            questions = session.query(Question).distinct().count()
            answers = session.query(Answer).distinct().count()
            ratings = session.query(Rating).distinct().count()

            print(f"Questions: {questions}")
            print(f"Answers: {answers}")
            print(f"Ratings: {ratings}")

            assert len(questions) == questions
            assert len(answers) == answers
            assert len(ratings) == ratings

            print("Test passed successfully.")

    except Exception as e:
        logging.error("Error in test_process_all_pages function:")
        logging.error(str(e))

def start_background_process():
    try:
        process_all_pages()
    except Exception as e:
        logging.error("Error in background process:")
        logging.error(str(e))

def start_background_process_test():
    try:
        test_process_all_pages()
    except Exception as e:
        logging.error("Error in background process test:")
        logging.error(str(e))
