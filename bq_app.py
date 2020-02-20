#!/usr/local/bin/python3
# ============================================================================
# Bioquant is a (currently undeployed) experimental graphic user intefrace,
# for the Biopython computational biology library.<br> Its aim is to
# facilitate usage of computational molecular biology tools for Life Science
# researchers. Currnet app functionality consists of parsing and rudimentri
# genomic analysis of Fasta records. Bioquant is powered by Python, the Flask
# web framework and the Bootstrap front-end library.
# Code is PEP8 compliant.
# ============================================================================


# Misc
import os
# Flask
from flask import Flask, flash, request, redirect
from flask import url_for, render_template, session
from werkzeug.utils import secure_filename
# Biopython
from Bio import SeqIO
from Bio.SeqUtils import GC


# Starting flask
UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = {'fasta'}
app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask file upload boilerplate
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# More Flask file upload boilerplate
# View template and Fasta file upload
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and not allowed_file(file.filename):
            flash('Error: not a Fasta file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['filename'] = filename
            session['upload_folder'] = UPLOAD_FOLDER
            session.permanent = False
            return redirect(url_for('parse'))
    return render_template('upload_file.html')

# Parsing the uploaded Fasta file and displaying description of organisms
@app.route('/parse', methods=['POST', 'GET'])
def parse():
    descriptions = []
    for record in SeqIO.parse(
            session['upload_folder'] + '/' + session['filename'], "fasta"):
        descriptions.append(record.description)
    if request.method == 'GET':
        return render_template(
            'parse.html', length=len(descriptions),
            descriptions=descriptions, phase='display')
    elif request.method == 'POST':
        for record in SeqIO.parse(
                session['upload_folder'] + '/' + session['filename'], "fasta"):
            if record.id == request.form['ID']:
                print(record.id)
                des = record.description
                return render_template(
                    'parse.html', length=len(descriptions),
                    des=des, phase='found')
        flash('Record not found. Did you enter a valid Fasta ID?')
        return render_template(
            'parse.html', length=len(descriptions),
            descriptions=descriptions, phase='notFound')

# Basic analysis of chosen organism
@app.route('/analyze/<des>/<choice>')
def analyze(des, choice):
    for record in SeqIO.parse(
            session['upload_folder'] + '/' + session['filename'], "fasta"):
        if record.description == des:
            sequence = record.seq
            break
    if choice == '0':
        return render_template(
            'analyze.html', des=des, sequence=sequence)
    elif choice == 'gc':
        return render_template(
            'analyze.html', des=des, sequence=sequence,
            choice='gc', gc=round(GC(sequence)))
    elif choice == 'translate':
        return render_template(
            'analyze.html', des=des, sequence=sequence,
            choice='translate', protein=sequence.translate())
