# PDF Viewer Application

Overview

Welcome to the PDF Viewer project! This desktop application, built with PyQt5 and PyMuPDF, allows you to view and manage PDF files with a sleek, customizable interface. Whether you need to browse through your documents, zoom in on details, or switch between dark and light themes, this tool provides an intuitive and user-friendly experience.
Features

    View PDF Files: Open and browse through PDF documents seamlessly.
    Page Navigation: Move between pages with next/previous buttons or a slider.
    Zoom: Adjust the zoom level to view details up close or fit the page to the screen.
    File Management: Add, delete, and view a list of previously opened PDF files.
    Dark and Light Themes: Toggle between a dark and light theme to suit your preference.

# Installation

To get started with the PDF Viewer application, you'll need to set up your environment. Follow these steps:

Clone the Repository:

    git clone https://github.com/fx-xf/PDF-Viewer.git
    cd PDF-Viewer

Create a Virtual Environment (optional but recommended):

    python -m venv venv
    source venv/bin/activate  
    
On Windows, use 
    `venv\Scripts\activate`

Install Dependencies:

    pip install -r requirements.txt

Run the Application:

    python main.py

# Usage

Navigating the Application

    Open PDF: Click the "Open File" button to select and open a PDF document.
    View Files: Click "View Files" to open a dialog where you can see and manage previously loaded PDFs.
    Page Controls: Use the "Previous" and "Next" buttons or the slider to navigate between pages.
    Zoom: Use the "Zoom In" and "Zoom Out" buttons to adjust the view.
    Toggle Theme: Switch between light and dark themes using the "Toggle Theme" button.

File Management

    Add Files: Files are automatically saved to the database when opened.
    Delete Files: Select a file in the list and click "Delete" to remove it from the database.

Project Structure

    main.py: The main script that initializes and runs the application.
    File.ui: UI file for the file management dialog.
    Main.ui: UI file for the main application window.
    requirements.txt: List of Python packages required to run the application.
    pdf_viewer.db: SQLite database storing information about loaded PDF files.

License

    This project is licensed under an open-source license. Feel free to use and modify it as per your needs.
