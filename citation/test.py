from processor import extract_citations, check_citations


def main():
    test_pdf = "/home/daniel/Desktop/Thesis.pdf"
    test_pdf2 = "/home/daniel/Documents/Thesis/BuiMinhQuang_ITITIU19044.pdf"
    
    citations = extract_citations(test_pdf)
    print(citations)
    
    checked_citations = check_citations(citations)
    
    output = "List of Citations:\n"
    count_true_citations = 0
        
    try:
        output += ', '.join(checked_citations)
    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")
        
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

    print(output)

if __name__ == '__main__':
    main()