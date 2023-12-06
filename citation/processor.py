import os
import re
import uuid
import timeit
import pdfplumber

from dotenv import load_dotenv
from datetime import datetime
from database import Database
from producer import Producer
from file_manager import get_file_from_bucket, remove_file_from_dir, write_to_bucket

load_dotenv()

def extract_citation(uploaded_file_location):
    citations = []
    
    with pdfplumber.open(uploaded_file_location) as pdf:
        last_page = len(pdf.pages) - 1
        last_page_text = pdf.pages[last_page].extract_text()
        
        # Extract citations using regular expressions
        citation_pattern = r"\[(\d+)\]\s(.+)"
        matches = re.findall(citation_pattern, last_page_text)
        
        # Add matches to citations array
        for match in matches:
            citation_number = match[0]
            citation_text = match[1]
            citations.append((citation_number, citation_text))
    
    return citations


def check_citations(citations):
    for citation in citations:
        citation_number, citation_text = citation

        if "APA" in citation_text:
            print(f"Citation {citation_number} is in APA format.")
        if "MLA" in citation_text:
            print(f"Citation {citation_number} is in MLA format.")
        if "Chicago" in citation_text:
            print(f"Citation {citation_number} is in Chicago format.")
        elif "IEEE" in citation_text:
            print(f"Citation {citation_number} is in IEEE format.")
        else:
            print(f"Citation {citation_number} does not match any known format.")


def insert_database(event_id, thesis_id, file_location, result):
    file_name = os.path.basename(file_location)
    uploaded_time = datetime.utcnow()

    db = Database()
    db.insert("INSERT INTO output (id, thesis_id, file_name, file_location, result, uploaded_time) VALUES (%s, %s, %s, %s, %s, %s)", (event_id, thesis_id, file_name, file_location, result, uploaded_time))

    print("inserted in db", flush=True)
    

def output_file(cloud_file_location):
    start_time = timeit.default_timer()

    event_id = str(uuid.uuid4())
    file_name = os.path.basename(cloud_file_location).split(".")[0]
    service_type = os.environ.get("APP_NAME")
    thesis_id = file_name

    producer = Producer()

    uploaded_file_location = get_file_from_bucket(cloud_file_location)
    producer.publish_status(event_id, thesis_id, service_type, "Processing")
    
    count_false_citations = 0
    
    try:
        citations = extract_citation(uploaded_file_location)
        incorrect_citations = check_citations(citations)
        
        output += "\nCitations:\n"
        
        if(len(incorrect_citations) > 0):
            output += "Citations with issues:\n"
            for citation in incorrect_citations:
                count_false_citations += 1
                output += citation + "\n"
            output += "\n"
        else:
            output += "No issues found in citations.\n"

        grade = int(round(100 - (count_false_citations * 0.3)))
    
        result = "Pass" if grade > 50 else "Fail"
        output += "\nGrade: " + str(grade) + "%\n"
        output += "Service Result: " + result + "\n"
        
        output_file_location = write_to_bucket(file_name, output)
        print("\nTime for " + os.environ.get("APP_NAME") + " to process file " + file_name + " is " + str(timeit.default_timer() - start_time) + "\n", flush=True)

        print("finished uploading to bucket for " + os.environ.get("APP_NAME"), flush=True)

        remove_file_from_dir(uploaded_file_location)
        
        insert_database(event_id, thesis_id, output_file_location, result)

        producer.publish_message(event_id, thesis_id, service_type, output_file_location, result)

        print("Processing complete in " + os.environ.get("APP_NAME"), flush=True)
    except:
        producer.publish_status(event_id, thesis_id, service_type, "Service Error")
