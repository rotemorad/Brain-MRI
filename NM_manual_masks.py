import os
import re
import shutil
import numpy as np
import pandas as pd
import nibabel as nib
from glob import glob
from nipype.interfaces import fsl as fsl
from fsl import ApplyMask, ImageStats, FAST, MathsCommand, DilateImage, UnaryMaths, BinaryMaths, Threshold, ErodeImage
from itertools import combinations

# Custom script imports
from basic_functions import find_sub_dirs, convert_dicom_to_nii

# Directory paths
scripts_dir = '/mnt/z/Rotem_Orad/scripts/PhD'
reference_dir = '/mnt/z/Rotem_Orad/'
subjects_dir = '/mnt/z/Rotem_Orad/NM_manual_masks/Updated/'
exclude_paths = ['nipype_bedpostx/', 'tbss/', 'tbss_non_FA/', 'stats/', 'FS_output/', 
                 'Positive/', 'previous_results/', 'problematic/']

def brain_extract(directory, filename, frac_threshold=0.4):
    """
    Perform brain extraction using FSL's BET tool.

    Parameters:
        directory (str): Directory path where the input file is located.
        filename (str): Name of the input NIfTI file.
        frac_threshold (float): Fractional intensity threshold (default is 0.4).
    """
    btr = fsl.BET()
    btr.inputs.in_file = os.path.join(directory, filename)
    btr.inputs.frac = frac_threshold
    btr.inputs.out_file = os.path.join(directory, f'brain_{filename}')
    btr.inputs.functional = True
    btr.run()

def create_bilateral_mask(sub, left_mask, right_mask, output_filename="sliced_bi_sn_mask.nii.gz"):
    """
    Create a bilateral subcortical mask.

    Parameters:
        sub (str): Subject directory path.
        left_mask (str): Left hemisphere input NIfTI mask file name.
        right_mask (str): Right hemisphere input NIfTI mask file name.
        output_filename (str): Output NIfTI file name (default is "sliced_bi_sn_mask.nii.gz").
    """
    l_sn = np.asanyarray(nib.load(os.path.join(sub, right_mask)).dataobj)
    r_sn = np.asanyarray(nib.load(os.path.join(sub, left_mask)).dataobj)
    bi_sn = l_sn + r_sn
    ni_img = nib.Nifti1Image(bi_sn, affine=np.eye(4))
    nib.save(ni_img, output_filename)

def process_t1_images(sub):
    """
    Process T1-weighted images for a given subject.

    Parameters:
        sub (str): Subject directory path.
    """
    for mp_file in ['UNI', 'INV1', 'INV2']:
        if not glob("*" + mp_file + "*.nii"):
            for direct in find_sub_dirs(sub):
                if re.search(r'(%s)+' % mp_file, direct):
                    convert_dicom_to_nii(direct)

# Run RemoveNoise_mp2rage.py
def process_neuromelanin(sub):
    """
    Process neuromelanin images for a subject.

    This function searches for neuromelanin (NM) images and performs necessary conversions
    if the required NM images are not found.

    Parameters:
        sub (str): Subject directory path.

    Returns:
        None
    """
    if not glob("*gre_mt*.nii"):
        for direct in find_sub_dirs(sub, exclude_paths):
            if re.findall(r'.+(gre_mt)+', direct):
                convert_dicom_to_nii(direct)
    if not glob('TE24.nii'):
        for file in os.listdir('.'):
            if re.search(r'(e1).(nii)$', file):
                shutil.copyfile(file, os.path.join('TE8.nii'))
                os.rename(os.path.join(file), os.path.join('NM.nii'))
            if re.search(r'(e2).(nii)$', file):
                os.rename(os.path.join(file), os.path.join('TE16.nii'))
            if re.search(r'(e3).(nii)$', file):
                os.rename(os.path.join(file), os.path.join('TE24.nii'))

def bet_neuromelanin_manual_masks(sub):
    """
    Perform brain extraction on neuromelanin (NM) images using FSL's BET tool.

    Parameters:
        sub (str): Subject directory path.

    Returns:
        None
    """
    print("Running BET")
    brain_extract(sub, "anat.nii.gz", fract=0.35)
    brain_extract(sub, "NM.nii", fract=0.35)

def bbox_ND(img):
    """
    Calculate bounding box indices for a non-zero region in a multi-dimensional image.

    Parameters:
        img (numpy.ndarray): Input image.

    Returns:
        tuple: Bounding box indices for each dimension.
    """
    N = img.ndim
    out = []
    for ax in combinations(reversed(range(N)), N - 1):
        nonzero = np.any(img, axis=ax)
        out.append(np.where(nonzero)[0][[0, -1]])
    return tuple(out)

def cut_da_image(sub, input, background_mask, mask_l, mask_r, out_cut='sliced_NM.nii.gz', contrast=''):
    """
    Cut and extract a region of interest from an input image based on masks.

    Parameters:
        sub (str): Subject directory path.
        input (str): Input NIfTI image file name.
        background_mask (str): Background mask NIfTI image file name.
        mask_l (str): Left hemisphere mask NIfTI image file name.
        mask_r (str): Right hemisphere mask NIfTI image file name.
        out_cut (str): Output NIfTI image file name (default is 'sliced_NM.nii.gz').
        contrast (str): Contrast information (optional).

    Returns:
        None
    """
    input_img = nib.load(os.path.join(sub, input)).get_fdata()
    seg_img = nib.load(os.path.join(sub, background_mask)).get_fdata()
    mask_l_img = nib.load(os.path.join(sub, mask_l)).get_fdata()
    mask_r_img = nib.load(os.path.join(sub, mask_r)).get_fdata()

    input_axes = np.argsort(-np.array(input_img.shape))
    input_axes = [0, 1, 2]

    bbox_idxs = bbox_ND(seg_img)
    bbox_x, bbox_y, bbox_z = bbox_idxs

    bbox_factor = 320

    bbox_w = bbox_x[1] - bbox_x[0]
    bbox_h = bbox_y[1] - bbox_y[0]
    bbox_cx = bbox_x[1] - bbox_w / 2.
    bbox_cy = bbox_y[1] - bbox_h / 2.

    bbox_dim = max((bbox_w, bbox_h))

    bbox_x = (int(bbox_cx - bbox_dim * bbox_factor / 2), int(bbox_cx + bbox_dim * bbox_factor / 2))
    bbox_y = (int(bbox_cy - bbox_dim * bbox_factor / 2), int(bbox_cy + bbox_dim * bbox_factor / 2))
    bbox_slice = (slice(*bbox_x), slice(*bbox_y), slice(*bbox_z))
    img_out = input_img[bbox_slice]

    nib_out = nib.Nifti1Image(img_out.transpose(input_axes), affine=np.eye(4))
    nib.save(nib_out, os.path.join(sub, out_cut))

    background_mask_cut = seg_img[bbox_slice]
    nib_background_out = nib.Nifti1Image(background_mask_cut.transpose(input_axes), affine=np.eye(4))
    nib.save(nib_background_out, os.path.join(sub, f'sliced_{background_mask}'))

    mask_l_cut = mask_l_img[bbox_slice]
    nib_mask_out = nib.Nifti1Image(mask_l_cut.transpose(input_axes), affine=np.eye(4))
    nib.save(nib_mask_out, os.path.join(sub, f'sliced_{contrast}_{mask_l}'))

    mask_r_cut = mask_r_img[bbox_slice]
    nib_mask_out = nib.Nifti1Image(mask_r_cut.transpose(input_axes), affine=np.eye(4))
    nib.save(nib_mask_out, os.path.join(sub, f'sliced_{contrast}_{mask_r}'))

def process_subject_space(sub):
    """
    Process subject's space for different images and masks.

    This function performs various operations to process different image and mask files
    in the subject's space, including creating masks and cutting images based on regions of interest.

    Parameters:
        sub (str): Subject directory path.

    Returns:
        None
    """
    cut_da_image(sub, "brain_NM.nii.gz", "MIDBRAIN.nii.gz", "L_SN.nii.gz", "R_SN.nii.gz")
    cut_da_image(sub, "brain_anat.nii.gz", "MIDBRAIN.nii.gz", "L_SN.nii.gz", "R_SN.nii.gz", "sliced_anat.nii.gz")
    try:
        create_bilateral_mask(sub, "star_L_SN.nii.gz", "star_R_SN.nii.gz", "star_bi_sn_mask.nii.gz")
        cut_da_image(sub, "star_map2.nii", "star_bi_sn_mask.nii.gz", "star_L_SN.nii.gz", "star_R_SN.nii.gz", "sliced_star_sn.nii.gz")
        create_bilateral_mask(sub, "star_L_NC.nii.gz", "star_R_NC.nii.gz", "star_bi_nc_mask.nii.gz")
        cut_da_image(sub, "star_map2.nii", "star_bi_nc_mask.nii.gz", "star_L_NC.nii.gz", "star_R_NC.nii.gz", "sliced_star_nc.nii.gz")
        cut_da_image(sub, "star_map2.nii", "MIDBRAIN.nii.gz", "L_SN.nii.gz", "R_SN.nii.gz", "sliced_star_nm_sn.nii.gz", "star_nm")
    except FileNotFoundError:
        print("T2star images not found")


def process_t2star_masks(sub, mask_list, contrast_input):
    """
    Process T2* star masks for a subject.

    This function applies masks to T2* star images and computes the mean values of the masked regions.

    Parameters:
        sub (str): Subject directory path.
        mask_list (list): List of mask filenames.
        contrast_input (str): Input contrast image filename.

    Returns:
        None
    """
    for mask in mask_list:
        ApplyMask(in_file=os.path.join(sub, contrast_input), out_file=os.path.join(sub, mask), mask_file=os.path.join(sub, mask)).run()
        mean = ImageStats(in_file=os.path.join(sub, mask), terminal_output='file', op_string='-M')
        mean.run()
        os.rename("output.nipype", os.path.join(os.path.join(sub, ''.join([mask, '_mask_mean.txt']))))


def neuromelanin_manual_masks_anat(sub):
    """
    Perform manual masks segmentation on anatomical images using FSL's FAST and MathsCommand tools.

    Parameters:
        sub (str): Subject directory path.

    Returns:
        None
    """
    FAST(in_files=os.path.join(sub, "sliced_anat.nii.gz"), number_classes=3, output_type='NIFTI_GZ', segments=True).run()
    MathsCommand(in_file=os.path.join(sub, "sliced_anat_pve_2.nii.gz"), args='-thr %s -bin' % '0.99').run()


def process_val_background(sub):
    """
    Process validation background information.

    This function calculates Signal-to-Noise Ratio (SNR) and Contrast-to-Noise Ratio (CNR) using
    midbrain, SN (substantia nigra), and background regions of interest for neuromelanin images.
    It also creates masks and computes statistics for different ROIs.

    Parameters:
        sub (str): Subject directory path.

    Returns:
        None
    
    SNR = Mean_over_slices{(SigSN / SigBND) * 100)}
    CNR = Mean_over_slices{(SigSN -SigBND) / STDBND}
    SigSN is the signal intensity in SN ROI,
    SigBND the signal intensity in background ROI,
    STDBND the standard deviation in background ROI.
    """
    create_bilateral_mask(sub, "sliced__L_SN.nii.gz", "sliced__R_SN.nii.gz", "sliced_bi_sn_mask.nii.gz")
    if not os.path.isfile(os.path.join(sub, "sliced_background_mask.nii.gz")):
        print("Creating background mask by subtracting SN from the midbrain")
        midbrain = np.asanyarray(nib.load(os.path.join(sub, "sliced_midbrain.nii.gz")).dataobj)
        DilateImage(in_file="sliced_bi_sn_mask.nii.gz", operation='max', nan2zeros=True).run()
        bilateral_sn = np.asanyarray(nib.load(os.path.join(sub, "sliced_bi_sn_mask_dil.nii.gz")).dataobj)
        background = midbrain - bilateral_sn
        ni_img = nib.Nifti1Image(background, affine=np.eye(4))
        nib.save(ni_img, "sliced_background_mask.nii.gz")
    ApplyMask(in_file=os.path.join(sub, "sliced_NM.nii.gz"), out_file=os.path.join(sub, 'nm_background.nii.gz'), mask_file=os.path.join(sub, "sliced_background_mask.nii.gz")).run()
    background_mean = ImageStats(in_file=os.path.join(sub, "nm_background.nii.gz"), op_string='-M')
    mean = background_mean.run().outputs
    bg_mean = float(str(mean).split()[-1])
    print(f"background mean is {bg_mean}")

    background_std = ImageStats(in_file=os.path.join(sub, "nm_background.nii.gz"), op_string='-S')
    std = background_std.run().outputs
    bg_std = float(str(std).split()[-1])
    print(f"Background std is {bg_std}")

    threshold_val = bg_mean + bg_std
    print(f"Threshold value is {threshold_val}")

    sub_snr = []
    sub_cnr = []
    for mask in ["sliced_bi_sn_mask", "sliced__L_SN", "sliced__R_SN"]:
        """
        SNR and CNR calculations for each mask
        """
        ApplyMask(in_file=os.path.join(sub, ''.join(["sliced_NM.nii.gz"])), out_file=os.path.join(sub, ''.join(['nm_', mask, '.nii.gz'])), mask_file=os.path.join(sub, ''.join([mask, '.nii.gz']))).run()

        mask_mean = ImageStats(in_file=os.path.join(sub, ''.join(['nm_', mask, '.nii.gz'])), op_string='-M')
        mean_mask = mask_mean.run().outputs
        mean_mask = float(str(mean_mask).split()[-1])
        print(f"Mean {mask} signal is {mean_mask}")

        mask_snr = (mean_mask / bg_mean) * 100
        print(f"{mask} SNR is {mask_snr}")
        sub_snr.append(mask_snr)
        with open(os.path.join(os.path.join(sub, ''.join(['bg_snr_', mask, '_mask.txt']))), "w+") as file:
            file.write(str(mask_snr))

        mask_cnr = (mean_mask - bg_mean) / bg_std
        print(f"{mask} CNR is {mask_cnr}")
        sub_cnr.append(mask_cnr)
        with open(os.path.join(os.path.join(sub, ''.join(['bg_cnr_', mask, '_mask.txt']))), "w+") as file:
            file.write(str(mask_cnr))

        UnaryMaths(in_file=os.path.join(sub, ''.join(['nm_', mask, '.nii.gz'])), operation='bin', out_file=os.path.join(sub, ''.join(['nm_', mask, '_mask.nii.gz']))).run()

        mean = ImageStats(in_file=os.path.join(sub, ''.join(["sliced_NM.nii.gz"])), terminal_output='file', mask_file=os.path.join(sub, ''.join(['nm_', mask, '_mask.nii.gz'])), op_string='-k %s -M')
        mean.run()
        os.rename("output.nipype", os.path.join(os.path.join(sub, ''.join(['manual_mean_', mask, '_mask.txt']))))
        """
        Volume calculations for each mask
        """
        volume_mask = os.path.join(os.path.join(sub, ''.join(['nm_', mask, '_mask.nii.gz'])))
        img = nib.load(volume_mask)
        nii_img = img.get_fdata()
        sx, sy, sz = img.header.get_zooms()
        voxel_volume = sx * sy * sz
        print('VoxelVol: ', voxel_volume)
        vol = np.sum(nii_img)
        print('Number of voxels: ', vol)
        volume = np.sum(nii_img) * 0.6 * 0.6 * 1.3
        print('Volume: ', volume)
        with open(os.path.join(os.path.join(sub, ''.join(['manual_vol_', mask, '_mask.txt']))), "w+") as file:
            file.write(str(volume))

def process_val_nawm(sub):
    """
    Process validation of Normal-Appearing White Matter (NAWM).

    This function calculates statistics and generates masks for Normal-Appearing White Matter (NAWM) regions.
    It also applies thresholds and performs various operations on neuroimaging data.

    Parameters:
        sub (str): Subject directory path.

    Returns:
        None
    """
    MathsCommand(in_file=os.path.join(sub, "sliced_anat_pve_2_maths.nii.gz"), args='-sub %s -bin' % '0.99').run()
    ErodeImage(in_file=os.path.join(sub, "sliced_anat_pve_2_maths_maths.nii.gz"), nan2zeros=True, out_file="WM_ero.nii.gz").run()
    ApplyMask(in_file="sliced_NM.nii.gz", out_file=''.join(["NAWM.nii.gz"]), mask_file=''.join(["WM_ero.nii.gz"])).run()
    nawm_mean = ImageStats(in_file=os.path.join(sub, "NAWM.nii.gz"), op_string='-M')
    mean = nawm_mean.run().outputs
    mean = float(str(mean).split()[-1])
    BinaryMaths(in_file=os.path.join(sub, "sliced_NM.nii.gz"), operand_value=mean, operation='div', output_type='NIFTI_GZ', out_file=os.path.join(sub, 'NM_maths.nii.gz')).run()
    Threshold(in_file=os.path.join(sub, 'NM_maths.nii.gz'), thresh=1.1, output_type='NIFTI_GZ').run()
    for mask in ["sliced_bi_sn_mask", "sliced__L_SN", "sliced__R_SN"]:
        """
        Calculate statistics and generate masks for each ROI
        """
        ApplyMask(in_file=os.path.join(sub, 'NM_maths_thresh.nii.gz'), out_file=os.path.join(sub, ''.join(['thresh_', mask, '_mask.nii.gz'])), mask_file=os.path.join(sub, ''.join([mask, '.nii.gz']))).run()
        UnaryMaths(in_file=os.path.join(sub, ''.join(['thresh_', mask, '_mask.nii.gz'])), operation='bin', out_file=os.path.join(sub, ''.join(['thresh_', mask, '_mask.nii.gz']))).run()

        mean = ImageStats(in_file=os.path.join(sub, 'NM_maths_thresh.nii.gz'), terminal_output='file', mask_file=os.path.join(sub, ''.join(['thresh_', mask, '_mask.nii.gz'])), op_string='-k %s -M')
        mean.run()
        os.rename("output.nipype", os.path.join(os.path.join(sub, ''.join(['thresh_mean_', mask, '.txt']))))

        volume_mask = os.path.join(os.path.join(sub, ''.join(['thresh_', mask, '_mask.nii.gz'])))
        img = nib.load(volume_mask)
        nii_img = img.get_fdata()
        sx, sy, sz = img.header.get_zooms()
        voxel_volume = sx * sy * sz
        print('VoxelVol: ', voxel_volume)
        vol = np.sum(nii_img)
        print('Number of voxels: ', vol)
        volume = np.sum(nii_img) * 0.6 * 0.6 * 1.3
        print('Volume: ', volume)
        with open(os.path.join(os.path.join(sub, ''.join(['volume_', mask, '_mask.txt']))), "w+") as file:
            file.write(str(volume))


def process_stat(subjects_dir):
    """
    Process statistical data from parsed mask files.

    This function processes parsed mask files and compiles statistical data into an Excel file.

    Parameters:
        subjects_dir (str): Directory containing subject subdirectories.

    Returns:
        None
    """
    df = pd.DataFrame(columns=["PatNum", "xxx"])
    df.set_index("PatNum")
    for elem in glob(os.path.join(subjects_dir, "*/*.txt")):
        elem_pat = elem.split("/")[-2]
        elem_name = os.path.basename(elem).split("_mask")[0]
        elem_value = open(elem).read().strip()
        df.loc[elem_pat, elem_name] = elem_value
    df = df.drop(["PatNum", "xxx"], axis=1)
    df.to_excel(os.path.join(subjects_dir, "full_parse.xlsx"))

def process_stat_two_timepoints(direct):
    """
    Process statistical data from two timepoints.

    This function processes statistical data from parsed mask files in two timepoints and compiles them into a single Excel file.

    Parameters:
        direct (str): Directory containing subject subdirectories with parsed data.

    Returns:
        None
    """
    arr = []
    for elem in glob(os.path.join(direct, "*", "full_parse.xlsx")):
        df_in = pd.read_excel(elem)
        df_in['Pat'] = elem.split("/")[-2]
        arr.append(df_in)
    df_all = pd.concat(arr)
    df_all.to_excel(os.path.join(direct, "all_all.xlsx"))

def main():
    for subject in find_sub_dirs(subjects_dir, exclude_paths):
        subject_name = os.path.basename(subject.rstrip('/'))
        print(subject_name)
        # Copying T2star images
        try:
            if not os.path.exists(os.path.join(subject, "star_map2.nii")):
                    original = os.path.join('//mnt/z/Rotem_Orad/NM_subs_updated', subject_name,  "star_map2.nii")
                    target = os.path.join(subject, "star_map2.nii")
                    shutil.copyfile(original, target)
        except FileNotFoundError:
            print(f'{subject_name} missing t2star')
        # Change to subject directory and process images
        os.chdir(subject)
        process_t1_images(subject)
        process_neuromelanin(subject)
        bet_neuromelanin_manual_masks(subject)
        process_subject_space(subject)
        neuromelanin_manual_masks_anat(subject)
        process_val_background(subject)
        process_val_nawm(subject)

        # Error handling for T2star images
        try:
            process_t2star_masks(subject, ["sliced__star_L_SN.nii.gz", "sliced__star_R_SN.nii.gz"], "sliced_star_sn.nii.gz")
            process_t2star_masks(subject, ["sliced__star_L_NC.nii.gz", "sliced__star_R_NC.nii.gz"], "sliced_star_nc.nii.gz")
            process_t2star_masks(subject, ["sliced_star_nm_L_SN.nii.gz", "sliced_star_nm_R_SN.nii.gz"], "sliced_star_nm_sn.nii.gz")
        except fsl.TraitError:
            print("T2star images not found, pass")

# Compile and process statistical data
process_stat(subjects_dir)


if __name__ == '__main__':
    main()