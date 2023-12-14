from processor import extract_citations, check_citations, process_citations


def main():
    test_pdf = "/home/daniel/Documents/Thesis/BuiMinhQuang_ITITIU19044.pdf"
    
    citations = extract_citations(test_pdf)
    checked_citations = check_citations(citations)
    output, result = process_citations(checked_citations)
    print(output, result)
    

if __name__ == '__main__':
    main()