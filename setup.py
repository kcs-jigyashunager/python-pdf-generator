from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='pdfGeneratorpython',
    version='0.2.1',
    packages=['pdf_generator'],
    install_requires=[
        'pandas',
        'jinja2',
        'pdfkit',
        'PyPDF2'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
)
