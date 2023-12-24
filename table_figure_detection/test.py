from processor import extract_figure_titles, extract_table_titles

def main():
    test_pdf = "/home/daniel/Desktop/Thesis.pdf"
    test_pdf2 = "/home/daniel/Documents/Thesis/BuiMinhQuang_ITITIU19044.pdf"
    
    titles = extract_table_titles(test_pdf2)
    
    print(titles)
        
if __name__ == '__main__':
    main()

