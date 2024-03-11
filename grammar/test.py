from processor import check_grammar, process_printable_text

test_pdf = "/home/daniel/Desktop/Thesis.pdf"
test_pdf2 = "/home/daniel/Documents/Thesis/BuiMinhQuang_ITITIU19044.pdf"

if __name__ == "__main__":
    matches, full_text = check_grammar(test_pdf)
    output = ""
    total_issues = len(matches)
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
        
    print(output)