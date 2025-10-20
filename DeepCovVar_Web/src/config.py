import os

class Config:
    
    # Base directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    JOBS_FOLDER = os.path.join(BASE_DIR, 'jobs')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'fasta', 'fa', 'faa', 'fna', 'txt'}
    MAX_SEQUENCES = 1000
    
    # Job settings
    JOB_RETENTION_DAYS = 7  # Keep job files for 7 days
    
    # Email settings (configure these if email notifications are needed)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@deepcovvar.com')
    
    # DeepCovVar settings
    DEEPCOVVAR_MODELS_PATH = os.environ.get('DEEPCOVVAR_MODELS_PATH', '')
    DEEPCOVVAR_BATCH_SIZE = 32
    
    # Ensure directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(JOBS_FOLDER, exist_ok=True)
