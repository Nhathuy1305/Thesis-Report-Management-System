import os
import re
import uuid
import timeit
import pdfplumber
import language_tool_python

from dotenv import load_dotenv
from datetime import datetime
from database import Database
from producer import Producer
from file_manager import get_file_from_bucket, remove_file_from_dir, write_to_bucket, get_text_from_bucket

load_dotenv()

def check_grammar(uploaded_file_location):
    try:
        tool = language_tool_python.LanguageTool('en-US')
        
        with pdfplumber.open(uploaded_file_location) as pdf:
            full_text = ''
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
                
        matches = tool.check(full_text)
        
        return matches, full_text
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def insert_database(event_id, thesis_id, file_location, result, grade):
    file_name = os.path.basename(file_location)
    uploaded_time = datetime.utcnow()

    db = Database()
    db.insert("INSERT INTO output (id, thesis_id, file_name, file_location, result, grade, uploaded_time) VALUES (%s, %s, %s, %s, %s, %s, %s)", (event_id, thesis_id, file_name, file_location, result, grade, uploaded_time))

    print("inserted in db", flush=True)


def output_file(cloud_file_location):
    start_time = timeit.default_timer()

    file_name = os.path.basename(cloud_file_location).split(".")[0]
    service_type = os.environ.get("APP_NAME")
    thesis_id = file_name
    event_id = str(uuid.uuid4())

    producer = Producer()

    uploaded_file_location = get_file_from_bucket(cloud_file_location)
    producer.publish_status(event_id, thesis_id, service_type, "Processing")
    output = ""
    
    try:
        matches, full_text = check_grammar(uploaded_file_location)
        
        total_words = len(full_text.split())
        
        words_with_issues = 0
        for match in matches:
            words_with_issues += len(match.context.split())
            output += f"Context: {match.context}\n"
            output += f"Category: {match.category}\n"
            output += f"Suggested correction: {match.replacements}\n"
            output += "\n"
        
        words_without_issues = total_words - words_with_issues
        grade = (int)(round(words_without_issues / total_words * 100)) if total_words != 0 else 100
        result = "Pass" if grade > 50 else "Fail"
        output += "Percentage: " + str(grade) + "%\n"
        output += "Service result: " + result + "\n"

        output_file_location = write_to_bucket(file_name, output)
        print("\nTime for " + os.environ.get("APP_NAME") + " to process file " + file_name + " is " + str(timeit.default_timer() - start_time) + "\n", flush=True)

        print("finished uploading to bucket for " + os.environ.get("APP_NAME"), flush=True)

        remove_file_from_dir(uploaded_file_location)
        
        insert_database(event_id, thesis_id, output_file_location, result, grade)

        producer.publish_message(event_id, thesis_id, service_type, output_file_location, result, grade)

        print("Processing complete in " + os.environ.get("APP_NAME"), flush=True)
    except:
        producer.publish_status(event_id, thesis_id, service_type, "Service error")  

