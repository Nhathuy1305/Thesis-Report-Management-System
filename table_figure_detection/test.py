from processor import extract_figure_titles, extract_table_titles, find_figure_mentions, find_table_mentions

def main():
    test_pdf = "/home/daniel/Desktop/Thesis.pdf"
    test_pdf2 = "/home/daniel/Documents/Thesis/BuiMinhQuang_ITITIU19044.pdf"
    
    figures_titles = extract_figure_titles(test_pdf)
    table_titles = extract_table_titles(test_pdf)
    
    figure_mentions = find_figure_mentions(test_pdf, figures_titles)
    # print(figure_mentions)
    
    table_mentions = find_table_mentions(test_pdf, table_titles)
    # print(table_mentions)
    output = ""
    output += "Tables mentioned:\n\n"
    
    total_items = len(figure_mentions) + len(table_mentions)
    mentioned_items = 0
        
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
        result = "No Figures or Tables found"
        output += "\nNo Figures or Tables found\n"
    else:
        grade = int(round((mentioned_items / total_items) * 100))
        result = "Pass" if grade >= 50 else "Fail"
        output += f"\nGrade: {grade}\n"
    
    print(output)
    
if __name__ == '__main__':
    main()