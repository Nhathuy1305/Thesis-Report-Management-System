import os
import re
import uuid
import timeit

from dotenv import load_dotenv
from datetime import datetime
from database import Database
from producer import Producer
from refextract import extract_references_from_file
from file_manager import get_file_from_bucket, remove_file_from_dir, write_to_bucket

load_dotenv()

def extract_citations(uploaded_file_location):
    try: 
        citations = extract_references_from_file(uploaded_file_location)
        
        citations = merge_citations(citations)
        
        unique_citations = {}
        
        for citation in citations:
            raw_ref = citation['raw_ref'][0]
            if raw_ref not in unique_citations:
                unique_citations[raw_ref] = citation
            else:
                pass
        
        unique_citations_list = list(unique_citations.values())
        
        return unique_citations_list
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def merge_citations(citations):

    merged_citations = []

    for citation in citations:
        raw_ref = citation['raw_ref'][0]

        ieee_pattern = re.compile(r'^\[\d+\]')  
        apa_pattern = re.compile(r'.*\(.*\d{4}\).*') 

        is_new_ieee_citation = ieee_pattern.search(raw_ref)
        is_new_apa_citation = apa_pattern.search(raw_ref)

        if not merged_citations or is_new_ieee_citation or is_new_apa_citation:
            merged_citations.append(citation)
        else:
            merged_citations[-1]['raw_ref'][0] += ' ' + raw_ref.strip()
            if 'misc' in citation:
                if 'misc' in merged_citations[-1]:
                    merged_citations[-1]['misc'][0] += ' ' + citation['misc'][0].strip()
                else:
                    merged_citations[-1]['misc'] = citation['misc']

    return merged_citations


def check_citations(citations):

    citation_styles = []

    for citation in citations:
        if is_website_apa_style(citation):
            citation_styles.append(("APA Style (Website)", citation['raw_ref'][0]))
        elif is_website_mla_style(citation):
            citation_styles.append(("MLA Style (Website)", citation['raw_ref'][0]))
        elif is_website_ieee_style(citation):
            citation_styles.append(("IEEE Style (Website)", citation['raw_ref'][0]))
        elif is_apa_style(citation):
            citation_styles.append(("APA Style", citation['raw_ref'][0]))
        elif is_mla_style(citation):
            citation_styles.append(("MLA Style", citation['raw_ref'][0]))
        elif is_ieee_style(citation):
            citation_styles.append(("IEEE Style", citation['raw_ref'][0]))
        else:
            citation_styles.append(("Unknown Style", citation['raw_ref'][0]))
    return citation_styles


def is_apa_style(citation):
    return re.match(r".*\(.*\d{4}\).*", citation['raw_ref'][0])

def is_website_apa_style(citation):
    return re.match(r".*\(.*\d{4}\).*(?:http|https)://.*", citation['raw_ref'][0])

def is_mla_style(citation):
    return re.match(r".*\. \d{4}\.$", citation['raw_ref'][0])

def is_website_mla_style(citation):
    return re.match(r".*\d{4},.*(?:http|https)://.*", citation['raw_ref'][0])

def is_ieee_style(citation):
    return re.match(r".*\[\d+\].*(?:\s+\[Online\]\s+Available:\s+\S+)?", citation['raw_ref'][0])

def is_website_ieee_style(citation):
    return re.match(r".*\[\d+\].*(?:http|https)://.*", citation['raw_ref'][0])


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
        citations = extract_citations(uploaded_file_location)
        checked_citations = check_citations(citations)
        
        try:
            output += checked_citations
        except Exception as e:
            print(f"An error occurred while writing to the output file: {e}")
        
        output = ""
        output = "List of Citations:\n"
        count_true_citations = 0

        checked_citations = [{'citation': type, 'type': citation} for citation, type in checked_citations]

        correct_citations = [citation for citation in checked_citations if citation['type'] != "Unknown"]
        incorrect_citations = [citation for citation in checked_citations if citation['type'] == "Unknown"]

        if correct_citations:
            output += "Correct Citations:\n"
            for citation in correct_citations:
                count_true_citations += 1
                output += f"{citation['citation']} (Type: {citation['type']})\n"
        else:
            output += "No correct citations found.\n"

        if incorrect_citations:
            output += "\nCitations with issues:\n"
            for citation in incorrect_citations:
                output += f"{citation['citation']} (Format Unknown)\n"
        else:
            output += "No issues found in citations.\n"

        if checked_citations:
            # Calculate grade
            grade = int(round((count_true_citations / len(checked_citations)) * 100))
            result = "Pass" if grade >= 50 else "Fail"
        else:
            grade = 0
            result = "Fail"

        output += f"\nGrade: {grade}%\n"
        output += f"Service Result: {result}\n"
        
        try:
            output_file_location = write_to_bucket(file_name, output)
        except Exception as e:
            print(f"An error occurred while uploading the file to the bucket: {e}")
            
        print("\nTime for " + os.environ.get("APP_NAME") + " to process file " + file_name + " is " + str(timeit.default_timer() - start_time) + "\n", flush=True)

        print("finished uploading to bucket for " + os.environ.get("APP_NAME"), flush=True)

        remove_file_from_dir(uploaded_file_location)
        
        insert_database(event_id, thesis_id, output_file_location, result)

        producer.publish_message(event_id, thesis_id, service_type, output_file_location, result)

        print("Processing complete in " + os.environ.get("APP_NAME"), flush=True)
    except Exception as e:
        producer.publish_status(event_id, thesis_id, service_type, "Service error")
