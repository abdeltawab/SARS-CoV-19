import requests
from Bio import Entrez, SeqIO
from io import StringIO


# Set email for NCBI Entrez (required)
Entrez.email = "ckoh04@uri.edu"


def fetch_ncbi_sequence(accession_id):
    
    try:
        # Try protein database first
        handle = Entrez.efetch(db="protein", id=accession_id, rettype="fasta", retmode="text")
        fasta_data = handle.read()
        handle.close()
        
        if fasta_data:
            return fasta_data
        
        # Try nucleotide database if protein fails
        handle = Entrez.efetch(db="nucleotide", id=accession_id, rettype="fasta", retmode="text")
        fasta_data = handle.read()
        handle.close()
        
        return fasta_data
        
    except Exception as e:
        raise Exception(f"Failed to fetch sequence from NCBI: {str(e)}")


def fetch_uniprot_sequence(accession_id):
    
    try:
        url = f"https://www.uniprot.org/uniprot/{accession_id}.fasta"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"UniProt returned status code {response.status_code}")
            
    except Exception as e:
        raise Exception(f"Failed to fetch sequence from UniProt: {str(e)}")


def fetch_sequence(accession_id, database='ncbi'):

    if database.lower() == 'ncbi':
        return fetch_ncbi_sequence(accession_id)
    elif database.lower() == 'uniprot':
        return fetch_uniprot_sequence(accession_id)
    else:
        raise ValueError(f"Unsupported database: {database}")


def validate_fasta(fasta_text):

    try:
        sequences = list(SeqIO.parse(StringIO(fasta_text), "fasta"))
        
        if len(sequences) == 0:
            return False, "No valid sequences found in FASTA format", 0
        
        return True, None, len(sequences)
        
    except Exception as e:
        return False, f"Invalid FASTA format: {str(e)}", 0
