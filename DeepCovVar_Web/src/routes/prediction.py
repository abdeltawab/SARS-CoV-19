import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from src.config import Config
from src.utils.deepcovvar_wrapper import run_deepcovvar_job
from src.utils.sequence_fetcher import fetch_sequence, validate_fasta
from src.utils.result_processor import (
    consolidate_results, 
    generate_excel_report, 
    generate_pdf_report,
    calculate_statistics
)

prediction_bp = Blueprint('prediction', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@prediction_bp.route('/predict', methods=['POST'])
def submit_prediction():
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Get form data
        sequence_type = request.form.get('sequence_type', 'protein')
        phases = request.form.getlist('phases[]')
        verbose = request.form.get('verbose', 'false') == 'true'
        email = request.form.get('email', '')
        
        # Convert phases to integers or 'all'
        if not phases or 'all' in phases:
            phases = 'all'
        else:
            phases = [int(p) for p in phases]
        
        # Determine input source
        input_file = None
        
        # Check if file was uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                input_file = os.path.join(Config.UPLOAD_FOLDER, f"{job_id}_{filename}")
                file.save(input_file)
        
        # Check if sequence was pasted
        elif 'sequence_text' in request.form and request.form['sequence_text'].strip():
            sequence_text = request.form['sequence_text']
            
            # Validate FASTA format
            is_valid, error_msg, seq_count = validate_fasta(sequence_text)
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            
            if seq_count > Config.MAX_SEQUENCES:
                return jsonify({'error': f'Too many sequences. Maximum is {Config.MAX_SEQUENCES}'}), 400
            
            # Save to file
            input_file = os.path.join(Config.UPLOAD_FOLDER, f"{job_id}_input.fasta")
            with open(input_file, 'w') as f:
                f.write(sequence_text)
        
        # Check if accession ID was provided
        elif 'accession_id' in request.form and request.form['accession_id'].strip():
            accession_id = request.form['accession_id'].strip()
            database = request.form.get('database', 'ncbi')
            
            try:
                # Fetch sequence from database
                fasta_data = fetch_sequence(accession_id, database)
                
                # Save to file
                input_file = os.path.join(Config.UPLOAD_FOLDER, f"{job_id}_{accession_id}.fasta")
                with open(input_file, 'w') as f:
                    f.write(fasta_data)
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        else:
            return jsonify({'error': 'No input provided. Please upload a file, paste sequences, or provide an accession ID.'}), 400
        
        # Collect custom thresholds for binary classification phases
        thresholds = {}
        for phase in phases:
            if phase in ['1', '2', '3']:  # Binary classification phases
                threshold_key = f'phase{phase}_thresholds'
                if threshold_key in request.form:
                    threshold_values = request.form[threshold_key].split(',')
                    if len(threshold_values) == 2:
                        try:
                            thresholds[phase] = [float(t.strip()) for t in threshold_values]
                        except ValueError:
                            return jsonify({'error': f'Invalid threshold values for phase {phase}'}), 400
        
        # Prepare options
        options = {
            'verbose': verbose,
            'sequence_type': sequence_type,
            'email': email,
            'thresholds': thresholds
        }
        
        # Run prediction job
        job_dir = run_deepcovvar_job(job_id, input_file, phases, options)
        
        return jsonify({
            'job_id': job_id,
            'status': 'pending',
            'message': 'Job submitted successfully'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prediction_bp.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    try:
        job_dir = os.path.join(Config.JOBS_FOLDER, job_id)
        status_file = os.path.join(job_dir, 'status.json')
        
        if not os.path.exists(status_file):
            return jsonify({'error': 'Job not found'}), 404
        
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prediction_bp.route('/results/<job_id>', methods=['GET'])
def get_job_results(job_id):
    try:
        job_dir = os.path.join(Config.JOBS_FOLDER, job_id)
        
        if not os.path.exists(job_dir):
            return jsonify({'error': 'Job not found'}), 404
        
        # Check if job is completed
        status_file = os.path.join(job_dir, 'status.json')
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        if status['status'] != 'completed':
            return jsonify({'error': 'Job not completed yet'}), 400
        
        # Consolidate results
        results = consolidate_results(job_dir)
        
        if not results:
            return jsonify({'error': 'Results not found'}), 404
        
        # Add statistics
        stats = calculate_statistics(job_dir)
        results['statistics_summary'] = stats
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prediction_bp.route('/download/<job_id>/<format>', methods=['GET'])
def download_results(job_id, format):
    try:
        job_dir = os.path.join(Config.JOBS_FOLDER, job_id)
        
        if not os.path.exists(job_dir):
            return jsonify({'error': 'Job not found'}), 404
        
        if format == 'excel':
            output_file = os.path.join(job_dir, f'{job_id}_results.xlsx')
            generate_excel_report(job_dir, output_file)
            return send_file(output_file, as_attachment=True, download_name=f'deepcovvar_results_{job_id}.xlsx')
        
        elif format == 'pdf':
            output_file = os.path.join(job_dir, f'{job_id}_results.pdf')
            generate_pdf_report(job_dir, output_file)
            return send_file(output_file, as_attachment=True, download_name=f'deepcovvar_results_{job_id}.pdf')
        
        elif format == 'csv':
            # Return the first phase CSV file
            results_file = os.path.join(job_dir, 'results.json')
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            if results.get('phases'):
                first_phase_csv = list(results['phases'].values())[0]
                # Make sure the path is absolute
                if not os.path.isabs(first_phase_csv):
                    first_phase_csv = os.path.join(job_dir, first_phase_csv)
                return send_file(first_phase_csv, as_attachment=True, download_name=f'deepcovvar_results_{job_id}.csv')
        
        else:
            return jsonify({'error': 'Invalid format. Supported formats: excel, pdf, csv'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prediction_bp.route('/fetch_sequence', methods=['POST'])
def fetch_sequence_endpoint():
    try:
        data = request.get_json()
        accession_id = data.get('accession_id', '').strip()
        database = data.get('database', 'ncbi')
        
        if not accession_id:
            return jsonify({'error': 'Accession ID is required'}), 400
        
        fasta_data = fetch_sequence(accession_id, database)
        
        return jsonify({
            'fasta': fasta_data,
            'accession_id': accession_id,
            'database': database
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
