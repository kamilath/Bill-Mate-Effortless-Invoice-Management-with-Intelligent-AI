from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from PIL import Image
import pandas as pd
import google.generativeai as genai
import sqlite3
import os

app = Flask(__name__)
genai.configure(api_key='')

# Function to generate Gemini response
def generate_gemini_response(input_prompt, image_loc, question_prompts):
    model = genai.GenerativeModel(model_name="gemini-pro-vision",
                                  generation_config={"temperature": 0.4, "top_p": 1, "top_k": 32, "max_output_tokens": 4096},
                                  safety_settings=[
                                      {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                      {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                      {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                      {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
                                  ])

    # Resize the image
    max_size = (800, 800)  # Maximum dimensions
    image = Image.open(image_loc)
    image.thumbnail(max_size)
    image.save(image_loc)

    # Set up image data
    image_prompt = [{"mime_type": "image/jpeg", "data": Path(image_loc).read_bytes()}]

    # Create a dictionary to store questions and responses
    responses = {}

    for question_prompt in question_prompts:
        prompt_parts = [input_prompt, image_prompt[0], question_prompt]
        response = model.generate_content(prompt_parts)

        # Use the original question as the key
        responses[question_prompt] = response.text

    return responses

# Function to insert Gemini response into the database
def insert_response_into_db(image_loc, input_prompt, responses):
    conn = sqlite3.connect('responses.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Responses (Vendor_Name, Invoice_Number, Invoice_Date, Invoice_Amount) VALUES (?, ?, ?, ?)",
                   (responses["vendor_name"], responses["Invoice_number"], responses["Invoice_date"], responses["Invoice_amount"]))

    conn.commit()
    conn.close()

# Function to fetch all response data from the database
def get_response_data():
    conn = sqlite3.connect('responses.db')
    df = pd.read_sql_query("SELECT * FROM Responses", conn)
    conn.close()
    return df

# Function to convert DataFrame to HTML table
def df_to_html_table(df):
    return df.to_html(index=False)
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home', methods=['POST'])
def home():
    # Validate login credentials (you'll need to implement this)
    email = request.form['email']
    password = request.form['password']
    # Check if email and password are valid (e.g., from a database)
    if email == 'example@example.com' and password == 'password':
        return render_template('home.html')
    else:
        return redirect(url_for('login'))
@app.route('/hm')
def hm():
    return render_template('home.html')


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    input_prompt = """
                   You are an expert in understanding invoices.
                   You will receive input images as invoices &
                   you will have to answer questions based on the input image perfectly
                   
                   """
    question_prompts = ["vendor_name", "Invoice_number", "Invoice_date", "Invoice_amount"]
    
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        image_loc = Path("uploads") / uploaded_file.filename
        uploaded_file.save(image_loc)

        responses = generate_gemini_response(input_prompt, image_loc, question_prompts)

        insert_response_into_db(str(image_loc), input_prompt, responses)

        return redirect(url_for('display_responses'))

@app.route('/display_responses', methods=['GET', 'POST'])
def display_responses():
    response_df = get_response_data()
    search_results = None
    
    # Search functionality
    if request.method == 'POST':
        vendor_name = request.form.get('vendor_name', '')
        invoice_number = request.form.get('invoice_number', '')
        invoice_date = request.form.get('invoice_date', '')
        invoice_amount = request.form.get('invoice_amount', '')

        # Filter the DataFrame based on the search criteria
        filtered_df = response_df[response_df['Vendor_Name'].str.contains(vendor_name, case=False)]
        filtered_df = filtered_df[filtered_df['Invoice_Number'].str.contains(invoice_number, case=False)]
        filtered_df = filtered_df[filtered_df['Invoice_Date'].str.contains(invoice_date, case=False)]
        filtered_df = filtered_df[filtered_df['Invoice_Amount'].str.contains(invoice_amount, case=False)]

        # Check if any results are found
        if not filtered_df.empty:
            # Extract the relevant information for the search results
            search_results = {
                'vendor_name': filtered_df['Vendor_Name'].tolist(),
                'invoice_numbers': filtered_df['Invoice_Number'].tolist(),
                'invoice_dates': filtered_df['Invoice_Date'].tolist(),
                'invoice_amounts': filtered_df['Invoice_Amount'].tolist(),
                'invoice_count': len(filtered_df)  # Calculate the invoice count
            }

        # Convert the filtered DataFrame to HTML table
        html_table = df_to_html_table(filtered_df)
    else:
        # If no search criteria provided, display all responses
        html_table = df_to_html_table(response_df)

    # Pass search_results to the template
    return render_template('excel.html', html_table=html_table, search_results=search_results)



@app.route('/clear_search', methods=['POST'])
def clear_search():
    # Redirect back to the display_responses route to reset the search criteria
    return redirect(url_for('display_responses'))

@app.route('/table')
def display_table():
    response_df = get_response_data()
    html_table = df_to_html_table(response_df)
    # Fetch data from the database and convert to HTML table
    # html_table = ... # Get your table data here
    return render_template('database.html', html_table=html_table)


if __name__ == '__main__':
    conn = sqlite3.connect('responses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Responses (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Vendor_Name TEXT,
            Invoice_Number TEXT,
            Invoice_Date TEXT,
            Invoice_Amount TEXT
        )
    ''')
    conn.commit()
    conn.close()

    app.run(debug=True)
