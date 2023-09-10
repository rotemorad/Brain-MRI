import fnmatch
import glob
import os
import re
import shutil
import nipype.interfaces.fsl as fsl


from basic_functions import find_sub_dirs, convert_dicom_to_nii, perform_brain_extraction
from edited_tbss_workflow import create_tbss_all, create_tbss_non_FA


# Define directory paths
scripts_dir = '//mnt/z/Rotem_Orad/scripts'
subjects_direct = '//mnt/z/Rotem_Orad/DLB_P_H'
tbss_direct = os.path.join(scripts_dir, 'tbss')
non_fa_direct = os.path.join(scripts_dir, 'tbss_non_FA')
stat_dir = os.path.join(subjects_direct, 'stats')
path_avoid = [
    'tbss/', 'tbss_non_FA/', 'output', 'stats/', 'FS_output/',
    'previous_results/', 'fsaverage/', 'results_may_23/', 'new_subs/'
]

def preprocess_dti(subjects_dir):
    for sub in find_sub_dirs(subjects_dir, path_avoid):
        subname = os.path.basename(sub)
        os.chdir(sub)
        print(subname)

        # Check for MP2RAGE files and convert them if needed
        mp2rage_files = glob.glob("*mp2rage*.nii")
        if not mp2rage_files:
            for file in find_sub_dirs(sub):
                # Check if the file matches the MP2RAGE naming pattern
                if re.search(r'(Se[0-1][0-9]).+(mp2rage)+', file):
                    nii_filename = convert_dicom_to_nii(file)
                    mp2rage_files.append(nii_filename)

        # Check for DTI files and convert them if needed
        dti_files = glob.glob("*DTI*.nii")
        if not dti_files:
            for file in find_sub_dirs(sub):
                # Check if the file matches the DTI naming pattern
                if re.search(r'DFC(_MIX)?/$', file):
                    nii_filename = convert_dicom_to_nii(file)
                    dti_files.append(nii_filename)

        # Create the 'output' directory if it doesn't exist
        output_directory = os.path.join(sub, 'output')
        os.makedirs(output_directory, exist_ok=True)

        # Define the files you want to copy
        files_to_copy = {
            '*DTI*.nii': 'DTI4D.nii',
            '*DTI*.bvec': 'bvecs.bvec',
            '*DTI*.bval': 'bvals.bval',
        }

        # Copy the specified files if they don't exist in the 'output' directory
        for pattern, output_name in files_to_copy.items():
            matching_files = fnmatch.filter(os.listdir(sub), pattern)
            for file in matching_files:
                source_path = os.path.join(sub, file)
                destination_path = os.path.join(output_directory, output_name)

                if not os.path.exists(destination_path):
                    shutil.copyfile(source_path, destination_path)

        os.chdir(output_directory)
        if not os.path.exists('brain_DTI4D.nii.gz'):
            # Perform brain extraction on the corrected DWI data
            perform_brain_extraction(output_directory, 'DTI4D.nii')
        if not os.path.exists('eddy_corrected.nii.gz'):
            # Perform Eddy Current Correction
            eddy_correct(output_directory)

        # Fit diffusion tensor model
        DTIFit(output_directory)

        # Calculate Da
        Da = fsl.ApplyMask(
            in_file=os.path.join(output_directory, 'DTI__L1.nii.gz'),
            out_file=os.path.join(output_directory, 'Da.nii.gz'),
            mask_file=os.path.join(output_directory, 'brain_DTI4D_mask.nii.gz')
        )
        Da.run()

        # Calculate Dr
        tmpDr = fsl.BinaryMaths(
            in_file=os.path.join(output_directory, 'DTI__L2.nii.gz'),
            operand_file=os.path.join(output_directory, 'DTI__L3.nii.gz'),
            operation='add',
            out_file=os.path.join(output_directory, 'tmpDr.nii.gz')
        )
        tmpDr.run()

        Dr = fsl.BinaryMaths(
            in_file=os.path.join(output_directory, 'tmpDr.nii.gz'),
            operand_value=2.0,
            operation='div',
            out_file=os.path.join(output_directory, 'Dr.nii.gz')
        )
        Dr.run()


# Eddy Correction

def eddy_correct(direct):
    eddycorrect = fsl.EddyCorrect()
    eddycorrect.inputs.ref_num = 0
    eddycorrect.inputs.in_file = os.path.join(direct, 'brain_DTI4D.nii.gz')
    eddycorrect.inputs.out_file = os.path.join(direct, 'eddy_corrected.nii.gz')
    eddycorrect.run()

def DTIFit(direct):
    # Fit a diffusion tensor model at each voxel
    os.chdir(direct)
    dti = fsl.DTIFit()
    dti.inputs.dwi = os.path.join(direct, 'eddy_corrected.nii.gz')
    dti.inputs.bvecs = os.path.join(direct, 'bvecs.bvec')
    dti.inputs.bvals = os.path.join(direct, 'bvals.bval')
    dti.inputs.base_name = 'DTI_'
    dti.inputs.mask = os.path.join(direct, 'brain_DTI4D_mask.nii.gz')
    dti.run()


# TBSS functions

def tbss_FA(fa_list, base_direct):
    # Perform TBSS on FA images
    tbss_wf = create_tbss_all('tbss', estimate_skeleton=True)
    tbss_wf.inputs.inputnode.skeleton_thresh = 0.2
    tbss_wf.inputs.inputnode.fa_list = fa_list
    tbss_wf.inputs.inputnode.base_dir = base_direct
    tbss_wf.run()

def tbss_non_FA(parm_list, field_list, base_direct):
    # Perform TBSS on non-FA images
    tbss_no_fa = create_tbss_non_FA()
    tbss_no_fa.inputs.inputnode.file_list = parm_list
    tbss_no_fa.inputs.inputnode.field_list = field_list
    tbss_no_fa.inputs.inputnode.skeleton_thresh = 0.2
    tbss_no_fa.inputs.inputnode.groupmask = os.path.join(base_direct, 'tbss3', 'groupmask',
                                                         'DTI__FA_prep_warp_merged_mask.nii.gz')
    tbss_no_fa.inputs.inputnode.meanfa_file = os.path.join(base_direct, 'tbss3', 'meanfa',
                                                           'DTI__FA_prep_warp_merged_masked_mean.nii.gz')
    tbss_no_fa.inputs.inputnode.all_FA_file = os.path.join(base_direct, 'tbss3', 'mergefa',
                                                           'DTI__FA_prep_warp_merged.nii.gz')
    tbss_no_fa.inputs.inputnode.distance_map = os.path.join(base_direct, 'tbss4', 'distancemap',
                                                            'DTI__FA_prep_warp_merged_mask_inv_dstmap.nii.gz')
    tbss_no_fa.inputs.inputnode.base_dir = base_direct
    tbss_no_fa.run()

def TBSS(subjects_dir):
    ALL_PERMISSIONS = 0o777
    fa_list = []
    md_list = []
    da_list = []
    dr_list = []
    field_list = []
    
    os.chdir(subjects_dir)
    
    if not os.path.exists(tbss_direct):
        os.mkdir(tbss_direct, ALL_PERMISSIONS)


    for sub in find_sub_dirs(subjects_dir, path_avoid):
        directory = os.path.join(sub, 'output')
        fa_list.append(os.path.join(directory, 'DTI__FA.nii.gz'))
        md_list.append(os.path.join(directory, 'DTI__MD.nii.gz'))
        da_list.append(os.path.join(directory, 'Da.nii.gz'))
        dr_list.append(os.path.join(directory, 'Dr.nii.gz'))
    
    os.chdir(tbss_direct)
    tbss_FA(fa_list, tbss_direct)


    for subdir in find_sub_dirs(os.path.join(tbss_direct, 'tbss2/fnirt/mapflow')):
        field_list.append(os.path.join(subdir, 'DTI__FA_prep_fieldwarp.nii.gz'))
    
    if not os.path.exists(non_fa_direct):
        os.mkdir(non_fa_direct)
        os.chdir(non_fa_direct)
    
    tbss_non_FA(md_list, field_list, tbss_direct)
    
    for folder_name, nii_pattern in [('MD', '*/*MD*.nii.gz'), ('Da', '*/*Da*.nii.gz'), ('Dr', '*/*Dr*.nii.gz')]:
        target_dir = os.path.join(non_fa_direct, folder_name)
        
        if not os.path.exists(target_dir):
            os.mkdir(target_dir, ALL_PERMISSIONS)
        
        for path in glob.glob(nii_pattern):
            shutil.copyfile(path, os.path.join(target_dir, os.path.basename(path)))


# Statistical analysis

def extract_values(direct):
    """Create an image of significant changes in TBSS."""
    diction = {'FA': 'FA/randomise_tfce_corrp_tstat1.nii.gz', 'MD': 'MD/randomise_tfce_corrp_tstat2.nii.gz',
               'Dr': 'Dr/randomise_tfce_corrp_tstat2.nii.gz', 'Da': 'Da/randomise_tfce_corrp_tstat2.nii.gz'}
    for key in diction.keys():
        math = fsl.ImageMaths(in_file=os.path.join(direct, diction[key]), op_string='-thr 0.95', out_file=os.path.join(
            direct, key, 'significant_results_mask.nii.gz'))
        math.run()

# Main function

def main():
    # preprocess_dti(subjects_direct, )
    TBSS(subjects_direct)
    # extract_values(stat_dir)

if __name__ == '__main__':
    main()
