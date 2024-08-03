# pass subject code as argument
export PATH=/Users/poldrack/bin/ants-2.5.3/bin:$PATH
RES=$2
BASEDIR=/Users/poldrack
BIDS_BASEDIR=${BASEDIR}/data_unsynced
NILEARN_DIR=${BASEDIR}/nilearn_data/haxby2001

INPUT=${NILEARN_DIR}/subj${1}/mask4_vt.nii.gz

BOLDREF=${BIDS_BASEDIR}/ds000105/derivatives/fmriprep/sub-${1}/func/sub-${1}_task-objectviewing_run-1_boldref.nii.gz

MNI_REF=${BIDS_BASEDIR}/ds000105/derivatives/fmriprep/sub-${1}/func/sub-${1}_task-objectviewing_run-1_space-MNI152NLin2009cAsym_res-${RES}_boldref.nii.gz

OUTPUT=${BIDS_BASEDIR}/ds000105/derivatives/vtmasks/sub-${1}_mask4vt_space-MNI152NLin2009cAsym_res-${RES}.nii.gz

T1_TO_MNI=${BIDS_BASEDIR}/ds000105/derivatives/fmriprep/sub-${1}/anat/sub-${1}_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5

BOLD_TO_T1=${BIDS_BASEDIR}/ds000105/derivatives/fmriprep/sub-${1}/func/sub-${1}_task-objectviewing_run-1_from-scanner_to-T1w_mode-image_xfm.txt

#fslcpgeom sub-2_task-objectviewing_run-1_boldref.nii.gz mask4_vt.nii.gz

#antsApplyTransforms -i mask4_vt.nii.gz -o mask4_singleshot.nii.gz -r sub-2_task-objectviewing_run-1_space-MNI152NLin2009cAsym_res-2_boldref.nii.gz -n GenericLabel -t sub-2_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5 -t sub-2_task-objectviewing_run-1_from-scanner_to-T1w_mode-image_xfm.txt



fslcpgeom $BOLDREF $INPUT

antsApplyTransforms -i $INPUT -r $MNI_REF -o $OUTPUT -n GenericLabel -t  $T1_TO_MNI -t $BOLD_TO_T1
