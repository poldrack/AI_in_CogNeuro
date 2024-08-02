import h5py
import pandas as pd
import os
from bids import BIDSLayout
import templateflow.api as tflow
import templateflow
import nibabel as nib
import numpy as np
from nilearn.image import load_img, mean_img, resample_img


def get_combined_subject_difumo_mask(subject, data_dir):
    sub_mask = get_subject_common_brain_mask(subject, data_dir)

    # get data from the difumo visual mask
    difumo_mask = resample_img(get_difumo_mask(), sub_mask.affine, sub_mask.shape, 
                        interpolation='nearest')
    mask = nib.Nifti1Image(np.logical_and(sub_mask.get_fdata().astype('int32'), 
                                            difumo_mask.get_fdata().astype('int32')).astype('int32'), 
                            sub_mask.affine) 
    return mask


def get_subject_vt_mask(subject, vtmask_dir, res=3):
    vt_mask_file = os.path.join(vtmask_dir, f'sub-{subject}_mask4vt_space-MNI152NLin2009cAsym_res-{res}.nii.gz')
    return nib.load(vt_mask_file) 


def get_bids_filename(subject, run, subdir='func', task='objectviewing', space='MNI152NLin2009cAsym', 
                      res=3, desc='preproc', suffix='bold', extension='nii.gz'):
    return f'sub-{subject}/{subdir}/sub-{subject}_task-{task}_run-{run}_space-{space}_res-{res}_desc-{desc}_{suffix}.{extension}'


def get_subject_common_brain_mask(subject, bids_dir, res=3, fmriprep_dir=None):
    fmriprep_dir = os.path.join(bids_dir, 'derivatives', 'fmriprep') if fmriprep_dir is None else fmriprep_dir
    common_mask_file = os.path.join(
        fmriprep_dir,
        f'sub-{subject}/func/sub-{subject}_task-objectviewing_space-MNI152NLin2009cAsym_res-{res}_desc-brain_mask.nii.gz'
    )
    if os.path.exists(common_mask_file):
        common_mask = nib.load(common_mask_file)
        # print(f'Using existing common mask for subject {subject}')
        return common_mask

    runs = get_subject_runs(subject, bids_dir)
    common_mask = None
    for run in runs:
        run = int(run)
        mask_file = os.path.join(fmriprep_dir, get_bids_filename(subject, run, res=res, desc='brain', suffix='mask'))
        mask_img = nib.load(mask_file)
        assert np.abs(mask_img.affine[0, 0]) == res, f'expected resolution {res} but got {mask_img.affine[0, 0]}'
        mask_data = mask_img.get_fdata().astype(bool)
        common_mask = mask_data if common_mask is None else np.logical_and(common_mask, mask_data)    
    print(f'found {np.sum(common_mask)} voxels in common mask')
    common_mask = nib.Nifti1Image(common_mask.astype("int16"), mask_img.affine)
    common_mask.to_filename(common_mask_file)
    return common_mask


def get_group_common_mask(layout, res=3, overwrite=False):
    derivdir = os.path.join(layout.root, 'derivatives/common_mask')
    if not os.path.exists(derivdir):
        os.makedirs(derivdir)
    maskfile = os.path.join(derivdir, f'group_common_mask_res-{res}.nii.gz')
    if os.path.exists(maskfile):
        return nib.load(maskfile)

    maskdata = None
    for subject in layout.get_subjects():
        subject_mask = get_subject_common_brain_mask(subject, layout.root, res=res)
        if maskdata is None:
            maskdata = subject_mask.get_fdata()
        else:
            maskdata = np.logical_and(maskdata, subject_mask.get_fdata())
    mask = nib.Nifti1Image(maskdata, subject_mask.affine, subject_mask.header)
    print(f'found {np.sum(maskdata)} voxels in group common mask')

    # save mask to derivatives
    mask.to_filename(maskfile)
    print(f'saved group mask to {maskfile}')
    return mask


def get_difumo_mask():
    templateflow.api.TF_S3_ROOT = 'https://templateflow.s3.amazonaws.com'
    atlas = tflow.get('MNI152NLin2009cAsym', resolution=2, atlas='DiFuMo')

    difumo64_file = [i for i in atlas if '64' in i.as_posix()][0]

    # create a mask for visual cortices using the relevant difumo componnets: 2, 3, 16, 29, 31, 35, 42, 46, 55
    # (need to subtract one from these are they are 1-indexed)

    components = [1, 2, 15, 28, 30, 34, 41, 45, 54]
    difumo_mask = nib.load(difumo64_file)
    mask_data = (difumo_mask.get_fdata() > 0).astype(int)
    mask = (mask_data[..., components].sum(axis=-1) > 0).astype('int32')
    mask_img = nib.Nifti1Image(mask, difumo_mask.affine)
    return mask_img


def get_subject_runs(subject, bids_dir, verbose=False):
    layout = BIDSLayout(bids_dir)
    runs = layout.get_runs(subject=subject)
    if verbose:
        print(f'found {len(runs)} runs for subject')
    return [int(i) for i in runs]
   

def list_all_datasets(hdf5_object, path='/'):
    """
    Recursively lists all datasets in an HDF5 file.
    
    :param hdf5_object: HDF5 group or file object
    :param path: Current path (used for recursion)

    Example:

    # Open the HDF5 file in read mode
    with h5py.File(hdf5_file_path, 'r') as file:
        # List all datasets and groups in the file
        list_all_datasets(file)

    """
    for name, item in hdf5_object.items():
        current_path = f"{path}{name}/"
        if isinstance(item, h5py.Dataset):
            # It's a dataset, print its path
            print(f"Dataset: {current_path[:-1]}")
        elif isinstance(item, h5py.Group):
            # It's a group, recurse into it
            print(f"Group: {current_path}")
            list_all_datasets(item, current_path)


def get_data_frame(subject, h5_dir):
    """
    Retrieve subject data from an HDF5 file 
    and convert it into a pandas DataFrame.

    Parameters:
    subject (str): The subject identifier.
    h5_dir (str): The directory path where the HDF5 file is located.

    Returns:
    pandas.DataFrame: The data as a pandas DataFrame.
    """

    data_h5 = h5py.File(os.path.join(h5_dir, 'visctx_data.h5'), "r")
    data_h5.keys()

    runs = list(data_h5[f'sub-{subject}'].keys())

    data_df = None
    for run in runs:

        run_data = data_h5[f'sub-{subject}'][run]['voxdata']
        run_df = pd.DataFrame(run_data)
        run_df.columns = [f'vox_{i}' for i in range(run_data.shape[1])]
        run_df['conditions'] = [i.decode('utf-8') for i in data_h5[f'sub-{subject}'][run]['conditions']]
        run_df['subject'] = subject
        run_df['run'] = int(run.split('-')[1])
        if data_df is None:
            data_df = run_df
        else:
            data_df = pd.concat([data_df, run_df])

    data_df.reset_index(drop=True, inplace=True)

    return data_df


def get_layouts(data_dir, fmriprep_dir):
    
    layout = BIDSLayout(data_dir)
    deriv_layout = BIDSLayout(fmriprep_dir, derivatives=True, validate=False)
    return layout, deriv_layout
