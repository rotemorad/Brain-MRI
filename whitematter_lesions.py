import os
import csv
import numpy as np
import nibabel as nib
import re
from glob import glob
from nipype.interfaces import fsl
from basic_functions import find_sub_dirs, convert_dicom_to_nii

# Constants
MRI_TYPES = ['FLAIR', 'T1', 'T1C', 'T2']
SUBJECTS_DIRECT = "//mnt/z/Rotem_Orad/White_Matter_Lesions/BET_SCANS"
PATH_MNI_BRAIN = "//mnt/z/Rotem_Orad/scripts/PhD/Talairach_moran/rMNI152_T1_2mm_brain.nii"
PATH_MNI_LABELS = "//mnt/z/Rotem_Orad/scripts/PhD/Talairach_moran/TalLobes.nii.gz"
LABELS_FILE = "//mnt/z/Rotem_Orad/scripts/PhD/Talairach_moran/modLabels.txt"

def load_labels(labels_path):
    labels_dic = {}
    with open(labels_path) as labels_file:
        lines = labels_file.readlines()
        for line in lines:
            items = line.strip().split()
            if len(items) == 2:
                labels_dic[items[0]] = items[1]
    return labels_dic

def perform_registration(sub, study):
    flt_brain = fsl.FLIRT(bins=640, cost_func='mutualinfo',
                          in_file=PATH_MNI_BRAIN,
                          reference=os.path.join(sub, study, "FLAIR.nii.gz"),
                          output_type='NIFTI_GZ',
                          out_file=os.path.join(sub, study, "_MNI_reg.nii.gz"),
                          out_matrix_file=os.path.join(sub, study, "trans_matrix.nii.gz"))
    flt_brain.run()

    flt_labels = fsl.FLIRT(bins=1000, cost_func='mutualinfo',
                           in_file=PATH_MNI_LABELS,
                           reference=os.path.join(sub, study, "FLAIR.nii.gz"),
                           output_type="NIFTI_GZ",
                           out_file=os.path.join(sub, study, "labels_reg.nii.gz"),
                           in_matrix_file=os.path.join(sub, study, "trans_matrix.nii.gz"),
                           apply_xfm=True)
    flt_labels.run()

    # Apply mask to obtain lesions in MNI space
    mask = fsl.ApplyMask(
        in_file=os.path.join(sub, study, "labels_reg.nii.gz"),
        mask_file=os.path.join(sub, study, "prediction.nii.gz"),
        out_file=os.path.join(sub, study, "lesions_in_mni.nii.gz"),
        output_type="NIFTI_GZ")
    mask.run()

    
from collections import namedtuple

# Define the named tuple for results
LesionVolumeResults = namedtuple('LesionVolumeResults', ['count_voxels', 'voxel_dims', 'lesions_volume', 'lesions_volume_percent'])

def calculate_lesion_volume(sub, study, labels_dic):
    # Load lesions MNI image
    full_path = os.path.join(sub, study, "lesions_in_mni.nii.gz")
    lesions_mni_img = nib.load(full_path)
    lesion_data = lesions_mni_img.get_fdata()

    voxel_dims = lesions_mni_img.header["pixdim"][1:4]
    voxel_volume = np.prod(voxel_dims)
    
    # Calculate voxel counts for each label
    max_label = len(labels_dic)
    voxel_counts = np.zeros(max_label, dtype=int)
    for label in range(1, max_label + 1):
        voxel_counts[label - 1] = np.sum(lesion_data == label)

    # Calculate lesion volumes in mm^3
    lesions_volume = voxel_volume * voxel_counts
    total_lesion_volume = np.sum(lesions_volume)  # Total volume of all lesions
    
    # Calculate lesions volume percentage
    lesions_volume_percent =np.round((lesions_volume * 100 / total_lesion_volume), 3 )
    
    # Create results named tuple
    results = LesionVolumeResults(voxel_counts, voxel_dims, lesions_volume, lesions_volume_percent)
    
    # Write results to CSV
    write_lesion_volume_results(sub, study, results, labels_dic)

def write_lesion_volume_results(sub, study, results, labels_dic):
    csv_path = os.path.join(sub, study, "lesion_volumes_by_location.csv")
    with open(csv_path, 'a', newline='') as f:
        writer = csv.writer(f)
        
    # Write header row with label names
    headers = ["Label"] + [str(labels_dic[str(i)]) for i in range(1, len(labels_dic) + 1)]
    with open(csv_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        # Write count of voxels row
        writer.writerow(["Count of Voxels"] + [str(value) for value in results.count_voxels])
        
        # Write lesions volume row
        writer.writerow(["Lesions Volume"] + [str(value) for value in results.lesions_volume])
        
        # Write lesions volume percent row
        writer.writerow(["Lesions Volume Percent"] + [str(value) for value in results.lesions_volume_percent])
        



def main():
    labels_dic = load_labels(LABELS_FILE)
    print(labels_dic)
    for sub in find_sub_dirs(SUBJECTS_DIRECT):
        subname = sub.split('/')[-2]
        print(subname)
        for study in find_sub_dirs(sub):
            if "lesion_volumes_by_location.csv" not in os.listdir(os.path.join(sub, study)):
                for MR_contrast in MRI_TYPES:
                    if MR_contrast + '.nii.gz' in os.listdir(os.path.join(sub, study)):
                        if MR_contrast == "FLAIR":
                            print("Performing registrations...")
                            perform_registration(sub, study)
                        
                print("Calculating lesion volume...")
                calculate_lesion_volume(sub, study, labels_dic)

if __name__ == '__main__':
    main()