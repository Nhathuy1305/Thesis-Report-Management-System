import re
import os
import uuid
import timeit
import pdfplumber

from database import Database
from producer import Producer
from datetime import datetime
from dotenv import load_dotenv
from file_manager import get_file_from_bucket, remove_file_from_dir, write_to_bucket

load_dotenv()

def extract_figure_titles(uploaded_file_location, ignore_pages_with=['contents', 'figures'], exclude_phrases=[]):
    with pdfplumber.open(uploaded_file_location) as pdf:
        figure_titles = []
        figure_title_pattern = re.compile(r'^Figure \d+')
        
        for i, page in enumerate(pdf.pages):
            
            text = page.extract_text().lower()
            if any(keyword.lower() in text for keyword in ignore_pages_with):
                continue  # Skip pages likely to be table of contents, list of figures, etc.
            
            figures = page.images
            
            for figure in figures:
                title_region = (
                    figure['x0'], figure['bottom'],
                    figure['x1'], figure['bottom'] + 60
                )
                
                title_crop = page.within_bbox(title_region)
                title_text = title_crop.extract_text()
                
                if title_text:
                    # Extract text before '\n'
                    clean_title = title_text.split('\n')[0].strip()
                    
                    # Check if the title follows the expected pattern of a figure title (e.g., "Figure 1.")
                    if figure_title_pattern.match(clean_title):
                        # Check if the title contains any exclusion phrases
                        if not any(phrase.lower() in clean_title.lower() for phrase in exclude_phrases):
                            figure_titles.append(clean_title)
                            
    return figure_titles


def extract_table_titles(uploaded_file_location, ignore_pages_with=['contents', 'tables'], exclude_phrases=[]):
    with pdfplumber.open(uploaded_file_location) as pdf:
        table_titles = []

        table_title_pattern = re.compile(r'^Table \d+')

        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text: 
                continue

            if any(keyword.lower() in text.lower() for keyword in ignore_pages_with):
                continue  # Skip pages likely to be table of contents, list of tables, etc.
            
            for line in text.split('\n'):
                # Adjusted for case-insensitive matching, use the `.search()` method
                if table_title_pattern.search(line.strip()):
                    title = line.strip()
                    # Check for exclusion phrases with the original case

                    if not any(phrase.lower() in title.lower() for phrase in exclude_phrases):
                        table_titles.append(title)

            tables = page.extract_tables()
            
            for table in tables:
                if len(table) > 0:
                    title_row = table[0]
                    title_row = [str(item) if item is not None else '' for item in title_row]
                    title_text = ' '.join(title_row).strip()

                    if title_text:
                        # Adjusted for case-insensitive matching, use the `.search()` method
                        if table_title_pattern.search(title_text):
                            # Check if the title contains any exclusion phrases, with the original case
                            if not any(phrase.lower() in title_text.lower() for phrase in exclude_phrases):
                                table_titles.append(title_text)

    return table_titles


def find_figure_mentions(uploaded_file_location, figure_titles):
    with pdfplumber.open(uploaded_file_location) as pdf:
        figure_mentions = {title: [] for title in figure_titles} 
        
        for i, page in enumerate(pdf.pages, start=1):  # Start page numbering at 1
            text = page.extract_text()
            if not text:
                continue

            for title in figure_titles:
                pattern = re.compile(re.escape(title), re.IGNORECASE)
                matches = pattern.findall(text)
                if len(matches) > 0:
                    figure_mentions[title].append((len(matches), i))  # Append mention count and page number

    return figure_mentions


def find_table_mentions(uploaded_file_location, table_titles):
    with pdfplumber.open(uploaded_file_location) as pdf:
        table_mentions = {title: [] for title in table_titles} 
        
        for i, page in enumerate(pdf.pages, start=1):  # Start page numbering at 1
            text = page.extract_text()
            if not text:
                continue

            for title in table_titles:
                pattern = re.compile(re.escape(title), re.IGNORECASE)
                matches = pattern.findall(text)
                if len(matches) > 0:
                    table_mentions[title].append((len(matches), i))  # Append mention count and page number

    return table_mentions


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
        table_titles = extract_table_titles(uploaded_file_location)

        figure_titles = extract_figure_titles(uploaded_file_location)

        table_mentions = find_table_mentions(uploaded_file_location, table_titles)

        figure_mentions = find_figure_mentions(uploaded_file_location, figure_titles)

        total_items = len(figure_mentions) + len(table_mentions)
        mentioned_items = 0
        
        output = "Tables mentioned:\n\n"
        
        for figure, mentions in figure_mentions.items():
            if mentions:
                mentioned_items += 1
            _, slide = mentions[-1] if mentions else (None, None)
            output += (f"{figure} \nMentioned on slide {slide}\n\n")

        output += "\nFigures mentioned:\n\n"

        for table, mentions in table_mentions.items():
            if mentions:
                mentioned_items += 1
            _, slide = mentions[-1] if mentions else (None, None)
            output += (f"{table} \nMentioned on slide {slide}\n\n")

        if total_items == 0:
            grade = 0
            result = "Fail"
            output += "\nNo Figures or Tables found\n"
        else:
            grade = int(round((mentioned_items / total_items) * 100))
            result = "Pass" if grade >= 50 else "Fail"
            output += f"\nGrade: {grade}\n"
            output += f"Service Result: {result}\n"
            
        print("finished processing for " + os.environ.get("APP_NAME"), flush=True   )
        
        output_file_location = write_to_bucket(file_name, output)
        
        print("\nTime for " + os.environ.get("APP_NAME") + " to process file " + file_name + " is " + str(timeit.default_timer() - start_time) + "\n", flush=True)

        print("finished uploading to bucket for " + os.environ.get("APP_NAME"), flush=True)

        remove_file_from_dir(uploaded_file_location)
        
        insert_database(event_id, thesis_id, output_file_location, result)

        producer.publish_message(event_id, thesis_id, service_type, output_file_location, result)

        print("Processing complete in " + os.environ.get("APP_NAME"), flush=True)
    except:
        producer.publish_status(event_id, thesis_id, service_type, "Service error")
