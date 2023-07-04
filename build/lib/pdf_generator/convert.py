import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit
import time
from PyPDF2 import PdfMerger
import math
import os
import winreg
import sys
import subprocess

def generate(json_file, template_directory, output_html_path, new_pdf_path):

    
    # System path
    current_directory = os.getcwd()

    # Specify the path to add to the user environment variables
    path_to_add = os.path.join(current_directory, 'wkhtmltopdf', 'bin')

    try:
        # Open the registry key for user environment variables
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)

        # Get the current value of the PATH variable from the registry
        path_value, _ = winreg.QueryValueEx(key, 'PATH')

        # Split the PATH value by the appropriate separator (semicolon on Windows, colon on Unix-like systems)
        path_list = path_value.split(';') if os.name == 'nt' else path_value.split(':')

        # Check if the path already exists in the PATH variable
        if path_to_add in path_list:
            print("The path is already included in the user environment variables.")
        else:
            # Append the new path to the existing value (separated by a semicolon)
            new_path_value = f'{path_value};{path_to_add}'

            # Update the PATH value in the registry
            winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path_value)

            print("The path has been added to the user environment variables.")

            # Update the PATH variable in the current process
            os.environ['PATH'] = new_path_value

            # Start a new process using the current Python executable
            subprocess.Popen([sys.executable] + sys.argv)

        # Close the registry key
        winreg.CloseKey(key)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # Rest of the code...
    # wkhtmltopdf configuration required for pdfkit
    wkhtmltopdf_path = os.path.join(current_directory, 'PDF-Python-json', 'wkhtmltopdf', 'bin', 'wkhtmltopdf.exe')

    # Import JSON data from file # to read new added json make changes here
    with open(json_file, 'r', encoding='utf-8') as file:
        json_text = file.read()

    # Convert JSON to DataFrame
    df = pd.read_json(json_text)

    # Convert DataFrame to list of dictionaries
    data = df.to_dict(orient='records')

    # Specify the template directory path

    # Specify the path to the template file
    template_path = os.path.join(template_directory, 'template.html')

    # Load HTML template using Jinja2
    env = Environment(loader=FileSystemLoader(template_directory))
    template = env.get_template(os.path.basename(template_path))

    # Render HTML from the template with dynamic data
    html_content = template.render(data=data)

    # Specify the path to save the output HTML file
    output_html_path = os.path.join(output_html_path, 'output.html')

    with open(output_html_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f'HTML file created: {output_html_path}')

    # Rest of the code...
    start_time = time.time()
    print("PDF Creation Started")

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
            'orientation': 'Portrait',
            'page-size': 'A4',
        }
        
        # Specify the path to save the chunk PDF file
        output_pdf_directory = os.path.join(new_pdf_path, 'pdf')
        os.makedirs(output_pdf_directory, exist_ok=True)
        pdf_file = os.path.join(output_pdf_directory, f'output_{i}.pdf')

        # Convert HTML chunk to PDF with specified options
        pdfkit.from_string(chunk_html, pdf_file, options=options)
        pdf_files.append(pdf_file)

    # Merge the individual PDF files into a single PDF
    merger = PdfMerger()
    for pdf_file in pdf_files:
        merger.append(pdf_file)

    merged_pdf_file = os.path.join(output_pdf_directory, 'merged_output.pdf')

    merger.write(merged_pdf_file)
    merger.close()
    elapsed_time = time.time() - start_time

    print(f'PDF file created: {merged_pdf_file}')
    print(f'PDF created in time: {elapsed_time / 60:.2f} minutes')

    # Delete the individual PDF files (optional)
    for pdf_file in pdf_files:
        os.remove(pdf_file)


