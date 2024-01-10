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
        
        return matches
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    

def process_printable_text(uploaded_file_location):
    matches = check_grammar(uploaded_file_location)

    # Iterate over the matches and print out the details
    for match in matches:
        print(f"Rule ID: {match.ruleId}")
        print(f"Message: {match.message}")
        print(f"Replacements: {', '.join(match.replacements)}")
        print(f"Offset in Context: {match.offsetInContext}")
        print(f"Context: {match.context}")
        print(f"Offset: {match.offset}")
        print(f"Error Length: {match.errorLength}")
        print(f"Category: {match.category}")
        print(f"Rule Issue Type: {match.ruleIssueType}")
        print(f"Sentence: {match.sentence}")
        print("\n")
        

def insert_database(event_id, thesis_id, file_location, result):
    file_name = os.path.basename(file_location)
    uploaded_time = datetime.utcnow()

    db = Database()
    db.insert("INSERT INTO output (id, thesis_id, file_name, file_location, result, uploaded_time) VALUES (%s, %s, %s, %s, %s, %s)", (event_id, thesis_id, file_name, file_location, result, uploaded_time))

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

    try:
        
        grade = 0
        result = "Pass" if grade > 50 else "Fail"
        output += "Percentage: " + str(grade) + "%\n"
        output += "Service result: " + result + "\n"

        output_file_location = write_to_bucket(file_name, output)
        print("\nTime for " + os.environ.get("APP_NAME") + " to process file " + file_name + " is " + str(timeit.default_timer() - start_time) + "\n", flush=True)

        print("finished uploading to bucket for " + os.environ.get("APP_NAME"), flush=True)

        remove_file_from_dir(uploaded_file_location)
        
        insert_database(event_id, thesis_id, output_file_location, result)

        producer.publish_message(event_id, thesis_id, service_type, output_file_location, result)

        print("Processing complete in " + os.environ.get("APP_NAME"), flush=True)
    except:
        producer.publish_status(event_id, thesis_id, service_type, "Service error")  

