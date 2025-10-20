# DeepCovVar Web Application - Quick Start Guide

## Prerequisites

Before running the web application, ensure you have:

1. **Python 3.7+** installed
2. **DeepCovVar CLI tool** installed and working
3. **Prodigal** installed (for nucleotide sequence processing)

## Quick Setup (5 minutes)

### Step 1: Verify DeepCovVar CLI is working

```bash
# Test if DeepCovVar is accessible
python -m deepcovvar --help
```

If this doesn't work, install DeepCovVar first:
```bash
git clone https://github.com/ckoh04/DeepCovVar.git
cd DeepCovVar
pip install -r requirements.txt
pip install .
```

### Step 2: Navigate to the web application directory

```bash
cd /path/to/DeepCovVar_Web
```

### Step 3: Activate the virtual environment

```bash
# Option 1: Use the provided activation script (recommended)
./activate_env.sh

# Option 2: Manual activation
source venv/bin/activate
```

### Step 4: Start the server

```bash
python src/main.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Step 5: Open your browser

Navigate to: **http://localhost:5000**

## Testing the Application

### Option 1: Use Demo Data

1. Click **"Load Demo FASTA"** button
2. Click **"Select All Phases"**
3. Click **"Run Prediction"**
4. Wait for results

### Option 2: Use Accession ID

1. Enter **P0DTC2** in the Accession ID field
2. Select **NCBI** database
3. Select phases you want to run
4. Click **"Run Prediction"**

### Option 3: Upload Your Own File

1. Click **"Browse"** and select a FASTA file
2. Select phases
3. Click **"Run Prediction"**

## Common Issues & Solutions

### Issue: "DeepCovVar module not found"

**Solution**: Install DeepCovVar in the same environment
```bash
source venv/bin/activate
pip install /path/to/DeepCovVar
```

### Issue: "Model files not found"

**Solution**: Set the models path
```bash
export DEEPCOVVAR_MODELS_PATH=/path/to/deepcovvar/models
python src/main.py
```

### Issue: "Port 5000 already in use"

**Solution**: Use a different port

Edit `src/main.py`, change the last line to:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

Then access at: http://localhost:5001

### Issue: "Prodigal not found"

**Solution**: Install Prodigal
```bash
# Using conda
conda install -c bioconda prodigal

# Or from source
git clone https://github.com/hyattpd/Prodigal.git
cd Prodigal
make install
```

## File Locations

- **Uploaded files**: `uploads/` directory
- **Job results**: `jobs/<job_id>/` directories
- **Test files**: `test.fasta`, `test_results.pdf`, `test_results.xlsx`
- **Logs**: Check terminal output where Flask is running or `deepcovvar.log`
- **Database**: `src/database/app.db`

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running

## Next Steps

1. Read the full **README.md** for detailed documentation
2. Visit the **Help** page in the application for usage tutorials
3. Check the **About** page for information about DeepCovVar
4. Visit the **Downloads** page for CLI tool installation
5. Try the test files: `test.fasta` for quick testing
6. Check the **LICENSE** file for usage terms

## Configuration

To customize the application, edit `src/config.py`:

```python
# File upload settings
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max
MAX_SEQUENCES = 1000

# Job retention
JOB_RETENTION_DAYS = 7

# DeepCovVar settings
DEEPCOVVAR_MODELS_PATH = '/path/to/models'
```

## Production Deployment

For production use, consider:

1. Using a production WSGI server (Gunicorn, uWSGI)
2. Setting up a reverse proxy (Nginx, Apache)
3. Configuring proper logging
4. Setting up SSL/TLS certificates
5. Implementing user authentication if needed

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

## Support

For help:
- Check the **Help** page in the application
- Read the **README.md**
- Visit: https://github.com/ckoh04/DeepCovVar
- Submit issues on GitHub

---

**Enjoy using DeepCovVar Web Application!** 🎉
