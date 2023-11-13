import os
import re
import shutil
import fnmatch
from glob import glob
from nipype.interfaces import mrtrix3 as mrt

# Custom module imports
from utils import find_sub_dirs, remove_files, convert_dicom_to_nii

# Paths
scripts_dir = '//mnt/z/Rotem_Orad/scripts/PhD'
reference_dir = '//mnt/z/Rotem_Orad/'
subjects_dir = '//mnt/z/Rotem_Orad/NM_manual_masks/Updated/'
path_avoid = ['tbss/', 'tbss_non_FA/', 'stats/', 'FS_output/', 'Positive/', 'previous_results/', 'problematic/']



def process_dti(subjects_dir):
    """
    Processes DTI data by iterating over each subject's folder within the given directory.
    Converts specific DICOM files to NIfTI format and organizes outputs.

    Parameters:
    subjects_dir (str): Directory containing subjects' data.
    """
    for subject_folder in find_sub_dirs(subjects_dir, path_avoid):
        subject_path = os.path.join(subjects_dir, subject_folder)
        remove_files(subject_path, ['JustName.mat', 'Analysis', 'Logs'])

        process_mp2rage(subject_path)
        process_dti_files(subject_path)

        output_dir = os.path.join(subject_path, 'output')
        os.makedirs(output_dir, exist_ok=True)
        save_dti_files(subject_path, output_dir)

def process_mp2rage(subject_path):
    """ Processes mp2rage and mprage files if they are not already in NIfTI format. """
    if not glob.glob(os.path.join(subject_path, "*mp2rage*.nii")):
        for file in find_sub_dirs(subject_path):
            if re.search(r'(Se[0-1][0-9]).+(mp2rage)+', file):
                convert_dicom_to_nii(file)
            elif re.search(r'(mprage)+', file):
                convert_dicom_to_nii(file)
                os.rename(os.path.join(file, ".nii"), os.path.join('mp2rage_denoised.nii.gz'))

def process_dti_files(subject_path):
    """ Converts DTI related DICOM files to NIfTI format if not already done. """
    if not glob.glob(os.path.join(subject_path, "*DTI*.nii")):
        for file in find_sub_dirs(subject_path):
            if re.search(r'DFC(_MIX)?/$', file):
                convert_dicom_to_nii(file)

def save_dti_files(subject_path, output_dir):
    """ Saves DTI related NIfTI, bvec, and bval files to the output directory. """
    for file in os.listdir(subject_path):
        if os.path.isfile(os.path.join(subject_path, file)) and re.search('DTI', file):
            ext = file.split('.')[-1]
            if ext in ['nii', 'bvec', 'bval']:
                output_filename = f'DTI4D.{ext}' if ext == 'nii' else f'{ext}.{ext}'
                shutil.copyfile(os.path.join(subject_path, file), os.path.join(output_dir, output_filename))

def preprocess_dti(subjects_output_dir):
    """
    Preprocess DTI data through a series of steps: conversion, denoising,
    de-Gibbs, motion correction, and bias correction.

    Parameters:
    subjects_output_dir (str): Directory for the output of DTI preprocessing.
    """
    convert_to_mif(subjects_output_dir)
    denoise_dwi(subjects_output_dir)
    remove_gibbs_ringing(subjects_output_dir)
    correct_motion(subjects_output_dir)
    correct_bias(subjects_output_dir)
                            
def convert_to_mif(directory):
    """
    Converts DTI data to .mif format.

    Parameters:
    directory (str): Directory containing DTI data.
    """
    mrconvert = mrt.MRConvert()
    mrconvert.inputs.in_file = os.path.join(directory, 'DTI4D.nii')
    mrconvert.inputs.in_bval = os.path.join(directory, 'bvals.bval')
    mrconvert.inputs.in_bvec = os.path.join(directory, 'bvecs.bvec')
    mrconvert.out_file = os.path.join(directory, 'dwi.mif')
    mrconvert.run()

def denoise_dwi(directory):
    """
    Applies denoising to DWI data.

    Parameters:
    directory (str): Directory containing DWI data in .mif format.
    """
    denoise = mrt.DWIDenoise()
    denoise.inputs.in_file = os.path.join(directory, 'dwi.mif')
    denoise.out_file = os.path.join(directory, 'dwi_denoised.mif')
    denoise.run()

def remove_gibbs_ringing(directory, axes=[0, 1]):
    """
    Removes Gibbs ringing from DWI data.

    Parameters:
    directory (str): Directory containing denoised DWI data.
    axes (list of int): Axes along which to apply the de-Gibbs process. Axial = [0,1]; coronal = [0,2]; sagittal = [1,2]. 
    """
    unring = mrt.MRDeGibbs()
    unring.inputs.in_file = os.path.join(directory, 'dwi_denoised.mif')
    unring.inputs.axes = axes
    unring.out_file = os.path.join(directory, 'dwi_denoised_unringed.mif')
    unring.run()
 
def correct_motion(directory, phase_encoding_direction='AP'):
    """
    Corrects motion artifacts in DWI data.

    Parameters:
    directory (str): Directory containing DWI data.
    phase_encoding_direction (str): Phase encoding direction for motion correction.
    """
    preproc = mrt.DWIPreproc()
    preproc.inputs.in_file = os.path.join(directory, 'dwi_denoised_unringed.mif')
    preproc.inputs.rpe_options = 'none'
    preproc.inputs.pe_dir = phase_encoding_direction
    preproc.outfile = os.path.join(directory, 'dwi_denoised_unringed_preproc.mif')
    preproc.run()

def correct_bias(directory):
    """
    Applies bias correction to DWI data.

    Parameters:
    directory (str): Directory containing DWI data after motion correction.
    """
    bias_correct = mrt.DWIBiasCorrect()
    bias_correct.inputs.in_file = os.path.join(directory, 'dwi_denoised_unringed_preproc.mif')
    bias_correct.inputs.use_ants = True
    bias_correct.outfile = os.path.join(directory, 'dwi_denoised_unringed_preproc_unbiased.mif')
    bias_correct.run()


def main():
    process_dti(subjects_dir)
    for sub in find_sub_dirs(subjects_dir, path_avoid):
        subname = sub.split('/')[-2]
        print(subname)        
        os.chdir(sub)
        out_dir = os.path.join(sub, 'output')
        preprocess_dti(out_dir)

if __name__ == '__main__':
    main()

