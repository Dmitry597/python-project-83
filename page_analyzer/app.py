import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from page_analyzer.url_repository import UrlRepository

load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

url_repo = UrlRepository(app.config['DATABASE_URL'])

@app.route('/')
def index():
    return render_template('home.html')



@app.post('/')
def add_url():
    url = request.form['url']
    
    url_repo.save(url)
    flash('Url successfully added', 'success')
    
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
