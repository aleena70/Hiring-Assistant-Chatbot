"""
This file is the data handler for the TalentScout project.
Its job is to safely store and retrieve all the candidate interview data.
It also includes features for data privacy and exporting.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


class DataHandler:
    """Manages all operations related to candidate data, like saving and loading files."""
    
    def __init__(self, data_dir: str = "data/candidates"):
        """
        Sets up our DataHandler.
        
        Args:
            data_dir: The folder where we'll keep all the candidate interview files.
        """
        self.data_dir = data_dir
        # folder
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Creates the data directory if it's not already there."""
        if not os.path.exists(self.data_dir):
            print(f"Data directory not found. Creating it at: {self.data_dir}")
            os.makedirs(self.data_dir)
    
    def save_candidate(self, candidate_data: Dict) -> str:
        """
        Saves a candidate's completed interview data to a neat JSON file.
        
        Args:
            candidate_data: A dictionary holding all the info we gathered.
            
        Returns:
            The filename of the newly created JSON file.
        """
        # Add timestamp and a unique ID 
        candidate_data['timestamp'] = datetime.now().isoformat()
        candidate_data['interview_id'] = self._generate_interview_id()
        
        # Filename
        name = candidate_data.get('name', 'unknown_candidate').replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # Write the data 
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(candidate_data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Success! Candidate data saved to: {filename}")
        return filename
    
    def _generate_interview_id(self) -> str:
        """Helper to create a simple, unique ID for each interview."""
        return f"TS_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def load_candidate(self, filename: str) -> Optional[Dict]:
        """
        Loads a specific candidate's interview data from a JSON file.
        
        Args:
            filename: The name of the file we want to open.
            
        Returns:
            A dictionary with the candidate's data, or None if the file isn't found.
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ Oops! Couldn't find the file: {filename}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    
    def list_all_candidates(self) -> List[str]:
        """
        Provides a list of all the candidate interview files we have saved.
        
        Returns:
            A list of filenames, with the most recent interviews first.
        """
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        return sorted(files, reverse=True)
    
    def export_to_csv(self, output_file: str = "candidates_export.csv"):
        """
        A function to export all candidate data into a single CSV file.
        
        Args:
            output_file: The name for our new CSV file.
        """
        all_candidates = []
        
        for filename in self.list_all_candidates():
            candidate = self.load_candidate(filename)
            if candidate:
                # Flatten the data 
                flat_data = {
                    'interview_id': candidate.get('interview_id', ''),
                    'timestamp': candidate.get('timestamp', ''),
                    'name': candidate.get('name', ''),
                    'email': candidate.get('email', ''),
                    'phone': candidate.get('phone', ''),
                }
                all_candidates.append(flat_data)
        
        if all_candidates:
            df = pd.DataFrame(all_candidates)
            output_path = os.path.join(self.data_dir, output_file)
            df.to_csv(output_path, index=False)
            print(f"✅ Success! Exported {len(all_candidates)} candidates to {output_file}")
        else:
            print("❌ No candidate data to export right now.")
            
    def anonymize_candidate_data(self, candidate_data: Dict) -> Dict:
        """
        Creates a privacy-friendly version of the candidate data.
        This is useful for sharing data while protecting personal information.
        
        Args:
            candidate_data: The original dictionary of candidate info.
            
        Returns:
            A new dictionary with sensitive info like email and phone masked.
        """
        anonymized = candidate_data.copy()
        
        # Mask the sensitive info
        if 'email' in anonymized:
            email_parts = anonymized['email'].split('@')
            anonymized['email'] = f"{email_parts[0][:2]}***@{email_parts[1]}"
        
        if 'phone' in anonymized:
            phone = anonymized['phone']
            anonymized['phone'] = f"***-***-{phone[-4:]}" if len(phone) >= 4 else "***-***"
            
        return anonymized