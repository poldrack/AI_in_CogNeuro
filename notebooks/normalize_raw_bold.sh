# normalize a raw bold image to MNI space for confound modeling example

export PATH=/Users/poldrack/bin/ants-2.5.3/bin:$PATH

BASEDIR=/Users/poldrack/data_unsynced/ds000105
INFILE=${BASEDIR}/sub-1/func/sub-1_task-objectviewing_run-01_bold.nii.gz
OUTFILE=${BASEDIR}/derivatives/confound_example/sub-1_task-objectviewing_run-01_space-MNI152NLin2009cAsym_res-2_bold.nii.gz
FMRIPREPDIR=${BASEDIR}/derivatives/fmriprep/sub-1
REF=${FMRIPREPDIR}/func/sub-1_task-objectviewing_run-1_space-MNI152NLin2009cAsym_res-2_boldref.nii.gz

antsApplyTransforms -e 3 -i $INFILE -o $OUTFILE -r $REF -n LanczosWindowedSinc \
    -t ${FMRIPREPDIR}/anat/sub-1_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5 \
    -t ${FMRIPREPDIR}/func/sub-1_task-objectviewing_run-1_from-scanner_to-T1w_mode-image_xfm.txt

