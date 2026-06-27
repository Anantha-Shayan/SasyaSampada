import pymupdf

pdf = pymupdf.open("/home/anantha/Projects/SasyaSampada/data/raw/agriwelfare_annual_report_2024_25.pdf")
print(pdf.page_count)

with pdf:
    for page_num, page in enumerate(pdf, start=1):
        content = page.get_text()  # Call the method
        print(f"--- Page {page_num} ---")
        print(content)