import os

class DTI:

    DTI_REGEX = r'DFC(_MIX)?/$'

    def __init__(self, subject_dir : str):
        self.subject_dir = subject_dir

    
    @staticmethod
    def load_data(subject_dir : str):
        for dir in subject_dir:

            os.walk()

