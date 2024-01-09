from processor import check_grammar, process_printable_text

test_pdf = "/home/daniel/Desktop/Thesis.pdf"
test_pdf2 = "/home/daniel/Documents/Thesis/BuiMinhQuang_ITITIU19044.pdf"

if __name__ == "__main__":
    print(process_printable_text(test_pdf))