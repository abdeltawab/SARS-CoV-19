import os
import sys
import json
import subprocess
import threading
from datetime import datetime
from src.config import Config


class DeepCovVarWrapper:

    
    def __init__(self, job_id, input_file, phases, options, output_dir):

        self.job_id = job_id
        self.input_file = input_file
        self.phases = phases
        self.options = options
        self.output_dir = output_dir
        self.status_file = os.path.join(output_dir, 'status.json')
        
    def update_status(self, status, progress=0, message='', error=None):
        status_data = {
            'job_id': self.job_id,
            'status': status,
            'progress': progress,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'error': error
        }
        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    def run_prediction(self):
        thread = threading.Thread(target=self._execute_prediction)
        thread.daemon = True
        thread.start()
        
    def _execute_prediction(self):
        try:
            self.update_status('running', 10, 'Starting prediction...')
            
            # Build command with proper PYTHONPATH and non-interactive mode
            deepcovvar_path = '/home/ai-lab2/DeepCovVar'
            cmd = [
                'env', 
                f'PYTHONPATH={deepcovvar_path}',
                sys.executable, '-m', 'deepcovvar', 
                '-f', self.input_file, 
                '-o', self.output_dir
            ]
            
            # Add verbose flag if requested
            if self.options.get('verbose', False):
                cmd.append('--verbose')
            
            # Determine which phases to run
            if self.phases == 'all' or len(self.phases) == 5:
                # Run all phases in one command
                cmd.append('--all-phases')
                # Add default thresholds for all phases
                cmd.extend(['--thresholds', '50', '50'])
                
                self.update_status('running', 30, f'Running DeepCovVar with all phases: {" ".join(cmd)}')
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout
                )
                
                if result.returncode == 0:
                    self.update_status('running', 80, 'Processing results...')
                    self._process_results()
                    self.update_status('completed', 100, 'Prediction completed successfully')
                else:
                    error_msg = result.stderr if result.stderr else 'Unknown error occurred'
                    self.update_status('failed', 0, 'Prediction failed', error_msg)
            else:
                # Run each selected phase individually
                phases_to_run = sorted(self.phases)
                total_phases = len(phases_to_run)
                
                for i, phase in enumerate(phases_to_run):
                    phase_cmd = cmd + ['-p', str(phase)]
                    
                    # Add thresholds for this specific phase
                    if self.options.get('thresholds') and phase in self.options['thresholds']:
                        custom_thresholds = self.options['thresholds'][phase]
                        phase_cmd.extend(['--thresholds', str(custom_thresholds[0]), str(custom_thresholds[1])])
                    else:
                        # Use default thresholds
                        phase_cmd.extend(['--thresholds', '50', '50'])
                    
                    progress = 30 + (i * 50 // total_phases)
                    
                    self.update_status('running', progress, f'Running DeepCovVar phase {phase}...')
                    
                    result = subprocess.run(
                        phase_cmd,
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minutes per phase
                    )
                    
                    if result.returncode != 0:
                        error_msg = result.stderr if result.stderr else f'Phase {phase} failed'
                        self.update_status('failed', 0, f'Phase {phase} failed', error_msg)
                        return
                
                # All phases completed successfully
                self.update_status('running', 80, 'Processing results...')
                self._process_results()
                self.update_status('completed', 100, 'Prediction completed successfully')
                
        except subprocess.TimeoutExpired:
            self.update_status('failed', 0, 'Prediction timed out', 'Job exceeded maximum execution time')
        except Exception as e:
            self.update_status('failed', 0, 'Prediction failed', str(e))
    
    def _process_results(self):
        results = {
            'job_id': self.job_id,
            'timestamp': datetime.now().isoformat(),
            'phases': {}
        }
        
        # Read results from each phase
        base_filename = os.path.splitext(os.path.basename(self.input_file))[0]
        
        phases_to_check = self.phases if self.phases != 'all' else [1, 2, 3, 4, 5]
        
        for phase in phases_to_check:
            # Try both naming patterns that DeepCovVar might use
            result_file1 = os.path.join(self.output_dir, f'{base_filename}_phase_{phase}_results.csv')
            result_file2 = os.path.join(self.output_dir, f'phase_{phase}_results.csv')
            
            if os.path.exists(result_file1):
                results['phases'][f'phase_{phase}'] = result_file1
            elif os.path.exists(result_file2):
                results['phases'][f'phase_{phase}'] = result_file2
        
        # Check for summary file
        summary_file = os.path.join(self.output_dir, f'{base_filename}_pipeline_summary.txt')
        if os.path.exists(summary_file):
            results['summary'] = summary_file
        
        # Save consolidated results
        results_file = os.path.join(self.output_dir, 'results.json')
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)


def run_deepcovvar_job(job_id, input_file, phases, options):
    
    # Create job directory
    job_dir = os.path.join(Config.JOBS_FOLDER, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    # Initialize wrapper and run prediction
    wrapper = DeepCovVarWrapper(job_id, input_file, phases, options, job_dir)
    wrapper.update_status('pending', 0, 'Job queued')
    wrapper.run_prediction()
    
    return job_dir
