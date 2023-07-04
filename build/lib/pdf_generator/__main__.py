import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit
import time
from PyPDF2 import PdfMerger
import math
import os

def main():

    def generate_pdf_from_json(json_file_path):

        current_directory = os.getcwd()
        wkhtmltopdf_path = os.path.join(current_directory, 'pdf_generator', 'wkhtmltopdf', 'bin', 'wkhtmltopdf.exe')

        # Import JSON data from file # to read new added JSON make changes here
        json_file_path = os.path.join(current_directory, 'pdf_generator', 'public', 'reports', 'json', '25-05-2023', 'GateBook.json')
        print(current_directory, "pppppppppp")


        # Convert JSON to DataFrame
        df = pd.read_json(json_file_path)

        # Convert DataFrame to list of dictionaries
        data = df.to_dict(orient='records')

        # Specify the template directory path
        template_directory = os.path.join(current_directory, 'pdf_generator', 'views', 'aakdashastra')

        # Specify the path to the template file
        template_path = os.path.join(template_directory, 'gatebookData.html')

        # Load HTML template using Jinja2
        env = Environment(loader=FileSystemLoader(template_directory))
        template = env.get_template(os.path.basename(template_path))


        # Render HTML from the template with dynamic data
        html_content = template.render(data=data)

        # Specify the path to save the output HTML file
        output_directory = os.path.join(current_directory, 'pdf_generator','public', 'reports', 'html', '25-05-2023')
        output_html_path = os.path.join(output_directory, 'output.html')

        with open(output_html_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f'HTML file created: {output_html_path}')

        # Rest of the code...
        start_time = time.time()
        print(f'PDF file creation starts: {0} minutes')

        # Calculate the total number of lines in the HTML content
        total_lines = len(html_content.split('\n'))
        print(f'Total lines: {total_lines}')

        # Define the number of lines per chunk
        lines_per_chunk = total_lines  # Adjust this value as per your requirement

        # Calculate the number of chunks based on the lines per chunk
        total_chunks = math.ceil(total_lines / lines_per_chunk)
        print(f'Total chunks: {total_chunks}')

        # Generate PDF for each chunk
        pdf_files = []
        for i in range(total_chunks):
            # Calculate the starting and ending line numbers for the current chunk
            start_line = i * lines_per_chunk + 1
            end_line = min((i + 1) * lines_per_chunk, total_lines)

            # Extract the chunk from the HTML content
            chunk = html_content.split('\n')[start_line - 1:end_line]
            chunk_html = '\n'.join(chunk)

            # Configure options for PDF generation (including orientation)
            options = {
                'encoding': 'UTF-8',
                'margin-top': '0px',
                'margin-right': '30px',
                'margin-bottom': '30px',
                'margin-left': '30px',
                'footer-right': "Page [page] of [topage]",
                'footer-font-size': "9",
                'orientation': 'Landscape',
                'page-size': 'A4',
            }

            # Specify the path to save the chunk PDF file
            output_pdf_directory = os.path.join(current_directory, 'pdf_generator', 'public', 'reports', 'pdf', '25-05-2023')
            os.makedirs(output_pdf_directory, exist_ok=True)
            pdf_file = os.path.join(output_pdf_directory, f'output_{i}.pdf')

            # Convert HTML chunk to PDF with specified options
            pdfkit.from_string(chunk_html, pdf_file, options=options)
            pdf_files.append(pdf_file)

        # Specify the path to save the merged PDF file
        merged_pdf_file = os.path.join(output_pdf_directory, 'merged_output.pdf')

        # Merge the individual PDF files into a single PDF
        merger = PdfMerger()
        for pdf_file in pdf_files:
            merger.append(pdf_file)

        # Output the merged PDF file
        merger.write(merged_pdf_file)
        merger.close()

        elapsed_time = time.time() - start_time

        print(f'Chunk files created: {pdf_files}')
        print(f'Merged PDF file created: {merged_pdf_file}')
        print(f'Elapsed time: {elapsed_time / 60} minutes')

        # Delete the individual PDF files (optional)
        for pdf_file in pdf_files:
            os.remove(pdf_file)

if __name__ == "__main__":
    main()