from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from fuzzywuzzy import process

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dictionar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'o_cheie_secreta_foarte_sigura'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Termen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), unique=True, nullable=False)
    definition = db.Column(db.String(500), nullable=False)
    approved = db.Column(db.Boolean, default=False)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    term_to_search = None
    definition = None
    dictionar_matematic = None

    if request.method == 'POST':
        term_to_search = request.form['term']
        terms = Termen.query.filter_by(approved=True).all()
        term_names = [term.term for term in terms]
        # Utilizăm Fuzzy String Matching pentru a găsi cel mai apropiat termen din baza de date
        closest_match, score = process.extractOne(term_to_search, term_names)
        if score >= 80:  
            term = Termen.query.filter_by(term=closest_match).first()
            definition = term.definition
        else:
            definition = "Termenul nu a fost găsit."

    
    dictionar_matematic = Termen.query.filter_by(approved=True).all()

    return render_template('index.html', term=term_to_search, definition=definition, dictionar_matematic=dictionar_matematic)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return 'Login eșuat!'
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    termeni_noi = Termen.query.filter_by(approved=False).all()
    return render_template('admin.html', termeni_noi=termeni_noi)

@app.route('/approve/<int:term_id>')
def approve(term_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    term = Termen.query.get(term_id)
    if term:
        term.approved = True
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/reject/<int:term_id>')
def reject(term_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    term = Termen.query.get(term_id)
    if term:
        db.session.delete(term)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/adauga', methods=['POST'])
def adauga():
    new_term = request.form['new_term']
    new_definition = request.form['new_definition']
    termen = Termen(term=new_term, definition=new_definition)
    db.session.add(termen)
    db.session.commit()
    return redirect(url_for('index'))
@app.route('/modifica/<int:term_id>', methods=['GET', 'POST'])
def modifica(term_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    term = Termen.query.get_or_404(term_id)
    
    if request.method == 'POST':
        term.term = request.form['term']
        term.definition = request.form['definition']
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('modifica.html', term=term)
@app.route('/sterge/<int:term_id>')
def sterge(term_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    term = Termen.query.get_or_404(term_id)
    db.session.delete(term)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
