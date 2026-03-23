from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
import re


load_dotenv()

app = Flask(__name__)
app.secret_key = 'hello_world'

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'phonebook')
DB_USER = os.getenv('DB_USER', 'phonebook_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=psycopg2.extras.DictCursor
    )
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id SERIAL PRIMARY KEY,
                last_name VARCHAR(100) NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                middle_name VARCHAR(100),
                phone_number VARCHAR(20) NOT NULL UNIQUE,
                note TEXT
                
            )
        ''')
        
        
        cur.execute('CREATE INDEX IF NOT EXISTS idx_contacts_last_name ON contacts(last_name)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_contacts_phone_number ON contacts(phone_number)')
        
        cur.execute('SELECT COUNT(*) FROM contacts')
        count = cur.fetchone()[0]
        
        if count == 0:
            cur.execute('''
                INSERT INTO contacts (last_name, first_name, middle_name, phone_number, note) VALUES
                ('Иванов', 'Иван', 'Иванович', '+7(999)123-45-67', 'Коллега по работе'),
                ('Петров', 'Петр', 'Петрович', '+7(999)234-56-78', 'Старый друг'),
                ('Сидорова', 'Анна', 'Сергеевна', '+7(999)345-67-89', 'Бухгалтер')
            ''')
        
        conn.commit()
        cur.close()
        conn.close()
        print("Table contacts was created")
    
    except Exception as e:
        print(f"Error to create table: {e}")

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM contacts ORDER BY last_name, first_name')
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['POST'])
def add_contact():
    last_name = request.form['last_name']
    first_name = request.form['first_name']
    middle_name = request.form.get('middle_name', '')
    phone_number = request.form['phone_number']
    note = request.form.get('note', '')
    
    phone_pattern = r'^(\+7|8)[\- \(]?\d{3}\)?[\- ]?\d{3}[\- ]?\d{2}[\- ]?\d{2}$'
    
    if not re.match(phone_pattern, phone_number):
        flash('Error: wrong format of number! Try +7(999)123-45-67 or 89991234567', 'error')
        return redirect(url_for('index'))

    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO contacts (last_name, first_name, middle_name, phone_number, note) VALUES (%s, %s, %s, %s, %s)',
            (last_name, first_name, middle_name, phone_number, note)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash('Saving contact success!', 'success')
    except psycopg2.IntegrityError:
        flash('Error: exist!', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('index'))


@app.route('/get_contact/<int:id>')
def get_contact(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM contacts WHERE id = %s', (id,))
    contact = cur.fetchone()
    cur.close()
    conn.close()
    
    if contact:
        return jsonify(dict(contact))
    return jsonify({'error': 'Contact not found'})

@app.route('/update/<int:id>', methods=['POST'])
def update_contact(id):
    last_name = request.form['last_name']
    first_name = request.form['first_name']
    middle_name = request.form.get('middle_name', '')
    phone_number = request.form['phone_number']
    note = request.form.get('note', '')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            '''UPDATE contacts 
               SET last_name=%s, first_name=%s, middle_name=%s, phone_number=%s, note=%s 
               WHERE id=%s''',
            (last_name, first_name, middle_name, phone_number, note, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash('Success!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
def delete_contact(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM contacts WHERE id = %s', (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Success!', 'success')
    except Exception as e:
        flash(f'Error {str(e)}', 'error')
    
    return redirect(url_for('index'))


@app.route('/search')
def search_contacts():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        '''SELECT * FROM contacts 
           WHERE last_name ILIKE %s 
           OR first_name ILIKE %s 
           OR phone_number ILIKE %s
           ORDER BY last_name, first_name''',
        (f'%{query}%', f'%{query}%', f'%{query}%')
    )
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('index.html', contacts=contacts, search_query=query)

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)