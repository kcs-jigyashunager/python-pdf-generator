from setuptools import setup

setup(
    name='pdf_generator',
    version='1.0.0',
    packages=['pdf_generator'],
    install_requires=[
        'pandas',
        'jinja2',
        'pdfkit',
        'PyPDF2'
    ],
)
