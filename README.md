# Bill Mate-Effortless Invoice Management with Intelligent AI 
This project is a Flask-based web application that processes invoices by uploading image files, extracting key information (e.g., vendor name, invoice number, date, and amount) using Google's Gemini Vision AI model, and storing the extracted data in an SQLite database.
## Features
- **Invoice Image Upload**: Users can upload invoice images through the web interface.

- **AI-Powered Extraction**: The app uses Google Gemini's model to extract details like vendor name, invoice number, date, and amount from the uploaded invoice images.

- **Data Storage**: Extracted information is stored in an SQLite database for easy access and retrieval.

- **Search and Display**: Users can search the database for specific invoices based on various criteria like vendor name or invoice number and view the results in an HTML table format.

- **User Authentication**: Basic login functionality is implemented for access to the application (credentials are hard-coded for now).
## Prerequisites
- Python 3.x

- Flask

- SQLite3

- PIL (Python Imaging Library)

- Google Generative AI SDK
## Usage
**Start the Flask Application**: python app.py

**Access the Web Interface**: Open your browser and navigate to http://127.0.0.1:5000/.

**Login** - Email: example@example.com, Password: password
## API and Libraries
- **Flask**: Used for web routing and serving HTML templates.

- **Pillow (PIL)**: Used to process and resize images.

- **Google Generative AI (Gemini)**: API used to extract invoice details from images.

- **SQLite**: Database used to store extracted invoice data.

- **Pandas**: For managing dataframes and converting data to HTML tables.
## How It Works
**Image Upload**: The user uploads an invoice image

**Gemini Model**: The application sends the image to Google’s Gemini model, which analyzes the invoice and extracts the vendor name, invoice number, date, and amount.

**Database Insertion**: The extracted data is saved into an SQLite database.

**Search & Display**: The user can search for specific invoices or view all the invoices in a tabular format.
## Future Enhancements
Implement dynamic user authentication and authorization using a proper user database.

Add advanced filtering options for searching invoices.

Implement pagination for large datasets.

Deploy the app on a cloud platform (e.g., Heroku, AWS) for public access.
