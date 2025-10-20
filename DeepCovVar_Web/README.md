# DeepCovVar Web Application

A web-based interface for the DeepCovVar CLI tool, providing an intuitive platform for COVID-19 variant classification using deep learning.

## Features

- **Multiple Input Methods**: Upload FASTA files, paste sequences, or fetch from NCBI/UniProt
- **Flexible Phase Selection**: Run individual phases or the complete 5-phase pipeline
- **Real-time Progress Tracking**: Monitor job status with live updates
- **Result Visualization**: Interactive charts showing variant distribution
- **Multiple Export Formats**: Download results as CSV, Excel, or PDF
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Installation

### Prerequisites

- Python 3.7+
- DeepCovVar CLI tool installed and configured
- Prodigal (for nucleotide sequence conversion)

### Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd DeepCovVar_Web
   ```

2. **Activate the virtual environment**:
   ```bash
   # Option 1: Use the provided activation script
   ./activate_env.sh
   
   # Option 2: Manual activation
   source venv/bin/activate
   ```

3. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure DeepCovVar paths** (optional):
   
   Set environment variables if your DeepCovVar installation is in a non-standard location:
   ```bash
   export DEEPCOVVAR_MODELS_PATH=/path/to/deepcovvar/models
   ```

5. **Set up SECRET_KEY** (required for security):
   
   Generate a secure secret key for Flask sessions:
   ```bash
   # Generate a secure random key
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Set the environment variable
   export SECRET_KEY="your-generated-secret-key-here"
   ```
   
   **Important**: Never commit the actual SECRET_KEY to version control!

## Running the Application

### Development Server

Start the Flask development server:

```bash
cd DeepCovVar_Web
source venv/bin/activate

# Set SECRET_KEY (if not already set)
export SECRET_KEY="your-secret-key-here"

python src/main.py
```

The application will be available at `http://localhost:5000`

### Configuration

Edit `src/config.py` to customize:
- Upload file size limits
- Job retention period
- Email notification settings
- DeepCovVar model paths

## API Endpoints

### POST /api/predict
Submit a new prediction job

**Request**: Form data with sequence input and options
**Response**: Job ID and status

### GET /api/status/<job_id>
Check job status

**Response**: Job status, progress, and message

### GET /api/results/<job_id>
Retrieve completed job results

**Response**: JSON with all phase results and statistics

### GET /api/download/<job_id>/<format>
Download results in specified format

**Formats**: csv, excel, pdf

### POST /api/fetch_sequence
Fetch sequence from NCBI or UniProt

**Request**: Accession ID and database type
**Response**: FASTA formatted sequence

## Usage

1. **Navigate to the home page** (`http://localhost:5000`)

2. **Provide input**:
   - Enter an accession ID (e.g., P0DTC2)
   - Upload a FASTA file
   - Paste FASTA sequences
   - Or click "Load Demo FASTA"

3. **Select phases**:
   - Check individual phases or click "Select All Phases"

4. **Configure options**:
   - Choose model type (Optimized/Standard)
   - Enable verbose output if needed
   - Optionally provide email for notifications

5. **Run prediction**:
   - Click "Run Prediction"
   - You'll be redirected to the results page

6. **View results**:
   - Monitor progress in real-time
   - View visualizations and detailed tables
   - Download results in your preferred format

## Integration with DeepCovVar CLI

This web application wraps the DeepCovVar CLI tool. Ensure that:

1. DeepCovVar is installed and accessible:
   ```bash
   python -m deepcovvar --help
   ```

2. Required model files are in place

3. Prodigal is installed for nucleotide sequence processing

## Troubleshooting

### DeepCovVar not found
- Ensure DeepCovVar is installed: `pip install /path/to/DeepCovVar`
- Check that the virtual environment has access to DeepCovVar

### Model files missing
- Set `DEEPCOVVAR_MODELS_PATH` environment variable
- Ensure model files are in the correct location

### Jobs failing
- Check job logs in `jobs/<job_id>/status.json`
- Enable verbose mode for detailed error messages
- Verify input sequences are in valid FASTA format

### Port already in use
- Change the port in `src/main.py`:
  ```python
  app.run(host='0.0.0.0', port=5001, debug=True)
  ```

## Development

### Testing

Test the API endpoints:
```bash
# Submit a job
curl -X POST -F "file=@test.fasta" -F "phases[]=1" http://localhost:5000/api/predict

# Check status
curl http://localhost:5000/api/status/<job_id>

# Get results
curl http://localhost:5000/api/results/<job_id>
```

## License

This project follows the same license as DeepCovVar (GPL-3.0).

## Acknowledgments

- University of Rhode Island
- University of South Dakota
- DeepCovVar research group

## Support

For issues or questions:
- Check the Help page in the application
- Visit the [DeepCovVar GitHub repository](https://github.com/ckoh04/DeepCovVar)
- Submit issues on GitHub
