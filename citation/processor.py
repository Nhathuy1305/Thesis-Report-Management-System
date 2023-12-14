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

def extract_citations(uploaded_file_location):
    citations = []
    references_page = -1
    
    try: 
        with pdfplumber.open(uploaded_file_location) as pdf:
            chapter_regex = re.compile(r'References|REFERENCES|REFERENCE|Reference', re.I)
            citation_regex = re.compile(r'\[\d+\].*?\d{4}', re.MULTILINE | re.DOTALL)

            for i in range(len(pdf.pages)):
                page = pdf.pages[i]
                text = page.extract_text()

                text = text.replace('\n', ' ')

                if chapter_regex.search(text):
                    references_page = i  

            for i in range(references_page, len(pdf.pages)):
                page = pdf.pages[i]
                text = page.extract_text()

                text = text.replace('\n', ' ')
                
                individual_citations = re.findall(citation_regex, text)

                for citation in individual_citations:
                    citations.append({'citation': citation, 'page': i})

        return citations
    except Exception as e:
        print(f"An error occurred 1: {e}")
        return citations


def check_citations(citations):
    checked_citations = []

    apa_regex = re.compile(r"(([\w\s-]+),\s([\w\s-]+)\.\s\((\d{4})\).+)")
    mla_regex = re.compile(r"(([\w\s-]+),\s([\w\s-]+)\.\s.+\d+\.)")
    chicago_regex = re.compile(r"(([\w\s-]+),\s\"(.+?)\",\s([\w\s-]+),\s(\d{4})\.)")
    ieee_regex = re.compile(r'^\[(\d+)\] ([\w\s,]+), “(.+?)” in (\d{4}) ([\w\s]+): ([A-Za-z]+), ([A-Za-z]+), (\d{4}), pp. (\d+–\d+)\.\s?doi: (\d{2}\.\d{4}/\w+$)')


    for citation in citations:
        citation_text = citation['citation']
        citation_type = 'Unknown'
        authors = 'Unknown'
        year = 'Unknown'
        
        match_apa = apa_regex.match(citation_text)
        match_mla = mla_regex.match(citation_text)
        match_chicago = chicago_regex.match(citation_text)
        match_ieee = ieee_regex.match(citation_text)

        if match_apa:
            citation_type = 'APA'
            authors = f"{match_apa.group(2)}, {match_apa.group(3)}"
            year = match_apa.group(4)
        elif match_mla:
            citation_type = 'MLA'
            authors = f"{match_mla.group(2)}, {match_mla.group(3)}"
        elif match_chicago:
            citation_type = 'Chicago'
            authors = match_chicago.group(2)
            year = match_chicago.group(5)
        elif match_ieee:
            citation_type = 'IEEE'
            authors = match_ieee.group(3)
            year = match_ieee.group(5)

        checked_citations.append({
            'citation': citation_text, 
            'type': citation_type, 
            'authors': authors, 
            'year': year, 
            'page': citation['page']
        })

    return checked_citations


def process_citations(checked_citations):
    output = ""
    count_true_citations = 0

    print("Checked Citations:", checked_citations)

    correct_citations = [citation for citation in checked_citations if citation['type'] != "Unknown"]
    incorrect_citations = [citation for citation in checked_citations if citation['type'] == "Unknown"]

    if correct_citations:
        output += "Correct Citations:\n"
        for citation in correct_citations:
            count_true_citations += 1
            output += f"{citation['citation']} (Type: {citation[1]})\n"
    else:
        output += "No correct citations found.\n"
    
    if incorrect_citations:
        output += "\nCitations with issues:\n"
        for citation in incorrect_citations:
            output += f"{citation['citation']} (Format Unknown)\n"
    else:
        output += "No issues found in citations.\n"

    # Calculate grade
    grade = int(round((count_true_citations / len(checked_citations)) * 100))
    result = "Pass" if grade >= 50 else "Fail" 

    output += f"\nGrade: {grade}%\n"
    output += f"Service Result: {result}\n"

    return output, result


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

    try:
        citations = extract_apa_citations(uploaded_file_location)
        checked_citations = check_citations(citations)
        output, result = process_citations(checked_citations)
        
        output_file_location = write_to_bucket(file_name, output)
        print("\nTime for " + os.environ.get("APP_NAME") + " to process file " + file_name + " is " + str(timeit.default_timer() - start_time) + "\n", flush=True)

        print("finished uploading to bucket for " + os.environ.get("APP_NAME"), flush=True)

        remove_file_from_dir(uploaded_file_location)
        
        insert_database(event_id, thesis_id, output_file_location, result)

        producer.publish_message(event_id, thesis_id, service_type, output_file_location, result)

        print("Processing complete in " + os.environ.get("APP_NAME"), flush=True)
    except Exception as e:
        print(f"An error occurred: {e}")
        if isinstance(event_id, str) and isinstance(thesis_id, str) and isinstance(service_type, str):
            producer.publish_status(event_id, thesis_id, service_type, "Service Error")
        else:
            print("Unable to publish status due to invalid argument types.")
