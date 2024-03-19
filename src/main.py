import base64
import json

import openai
import re
import os
from flask import Flask, jsonify, render_template, request
import sqlite3

openai.api_key = ""

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/book_detail', methods=['GET'])
def book_detail():
    book_id = request.args.get('book_id')
    contents, finished_count = get_book(book_id)
    print("here")
    print(contents)
    checkboxes_checked = []
    for i in range(len(contents)):
        if i < finished_count:
            checkboxes_checked.append(True)
        else:
            checkboxes_checked.append(False)

    print(contents)
    return render_template('book_detail.html', book_detail=contents, checkboxes=checkboxes_checked, finished_count=finished_count, section_len=len(contents))


@app.route('/data', methods=['POST'])
def data():
    print("hit")
    out = {}
    print(request.form['book-title'])
    images = request.files.getlist('files[]')
    image_path = "../images/IMG_1366.jpg"
    directory_path = '../images'
    print(request)
    print(request.files)
    # for each image in images folder
    # loop through and encode then send to openai
    # append results to dictionary

    count = 0
    for entry in images:
        image_bytes = entry.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "This is a table of contents, "
                                                 "you are a computer analysing this table of contents, for each "
                                                 "chapter &"
                                                 "corresponding subchapter you are directed to give what page each "
                                                 "chapter is on and the chapter name."
                                                 "This should be formatted as a list of comma seperated key:value "
                                                 "pairings with the key as the page number and the value as the "
                                                 "chapter name, only provide this list. there should be no space in "
                                                 "between the key:value. for example"
                                                 "A chapter named 'The Start' on page 5 would look like '5:'The "
                                                 "Start'. Each chapter should be a single string not broken up in any "
                                                 "way besides spaces"
                                                 "Only consider the chapters and subchapters with numbers "
                                                 "corresponding to them. Each chapter Name should start and end with "
                                                 "a ' with no spaces between them, for example 'Chapter Name' not ' "
                                                 "Chapter Name'"
                         },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000,
        )

        pairs = response.choices[0].message.content.split(',')
        for pair in pairs:
            split_pair = pair.split(':')
            if len(split_pair) == 2:
                key, value = split_pair
                cleaned_key = re.sub(r'[^\d]', '', key.strip())
                cleaned_val = value.replace("'", "")
                if cleaned_key:
                    int_key = int(cleaned_key.strip())
                    out[int_key] = cleaned_val.strip()

    sorted_dict = {k: out[k] for k in sorted(out)}
    table_of_contents = json.dumps(sorted_dict)
    title = request.form['book-title']
    add_book(title, table_of_contents)
    print(sorted_dict)
    return {'status': 'success'}


@app.route('/get-books', methods=['GET'])
def get_all_books():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM BOOKS')
    books = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in books])


def get_book(book_id):
    finished_count = 0
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT contents, finished_count FROM BOOKS WHERE id = ?', (book_id,))
    books = cursor.fetchone()
    conn.close()
    if books:
        book_contents = json.loads(books['contents'])
        finished_count = books['finished_count']
    else:
        book_contents = {}

    return book_contents, finished_count


@app.route('/add-book', methods=['POST'])
def update_book():
    book_id = request.get_json().get('bookId')
    contents = request.get_json().get('bookContents')
    finished_count = request.get_json().get('finishedCount')
    finished_count = int(finished_count)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Convert the new contents to a JSON string
    new_contents_json = json.dumps(contents)
    print(book_id)
    print(new_contents_json)
    # Update the database
    cursor.execute('UPDATE BOOKS SET contents = ?, finished_count = ? WHERE id = ?',
                   (new_contents_json, finished_count, book_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # This allows accessing the columns by name
    return conn


def init_db():
    print("hello")
    conn = get_db_connection()
    conn.execute(
        'CREATE TABLE IF NOT EXISTS BOOKS ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'title TEXT, '
        'contents DICT,'
        'finished_count INT)'
    )
    conn.commit()
    conn.close()


def add_book(title, content):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO BOOKS (title, contents) VALUES (?, ?)', (title, content))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
