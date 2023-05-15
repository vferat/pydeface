import argparse
import os

from bids import BIDSLayout

import numpy as np
from nibabel import load, Nifti1Image

import pydeface.utils as pdu

def applyto(files, warped_mask_img, force):
    # apply mask to other given images
    print("Defacing mask also applied to:")
    for applyfile in files:
        applyfile_img = load(applyfile)
        applyfile_data = np.asarray(applyfile_img.dataobj)
        warped_mask_data = np.asarray(warped_mask_img.dataobj)
        try:
            outdata = applyfile_data * warped_mask_data
        except ValueError:
            tmpdata = np.stack(warped_mask_data * applyfile_data.shape[-1],
                                axis=-1)
            outdata = applyfile_data * tmpdata
        applyfile_img = Nifti1Image(outdata, applyfile_img.affine,
                                    applyfile_img.header)
        outfile = pdu.output_checks(applyfile, force=force)
        applyfile_img.to_filename(outfile)
        print('  %s' % applyfile)
        return(outfile)

def bids(bids_dir,
         analysis_level,
         subjects=None,
         apply_T2=True,
         force=True):
    
    if not os.path.isdir(bids_dir):
        raise ValueError("bids_dir is not a directory")
    layout = BIDSLayout(bids_dir)

    if not analysis_level in ['participants', 'group']:
        raise ValueError("analysis_level must be either participants or group")
    
    if analysis_level == "participants":
        if subjects is None:
            raise ValueError("Please provide subjects when using participant level analysis.")
        missing_subjects = []
        for subject in subjects:
            if subject not in layout.get_subjects:
                missing_subjects.append(subject)
        if missing_subjects:
            raise ValueError("Subjects {missing_subjects} are not present in bids_dir.")  
    
    elif analysis_level == "group":
        if subjects is not None:
            raise ValueError("Can't provide subjects when using group level analysis.")
        subjects = layout.get_subjects()
    
    for subject in subjects:
        T1s = layout.get(subject=subject, extension='nii.gz', suffix='T1w')
        for T1 in T1s:
            entities = T1.get_entities()
            warped_mask_img, warped_mask, template_reg, template_reg_mat =\
                pdu.deface_image(T1.filename)
            if apply_T2:
                # Apply T1 mask to T2
                T2s = layout.get(subject=subject, extension='nii.gz', suffix='T2w', return_type='filename')
                applyto(T2s, warped_mask_img, force)
        
        if not apply_T2:
            # Compute mask for T2 and apply (do not use T1 mask)
            T2s = layout.get(subject=subject, extension='nii.gz', suffix='T2w')
            for T2 in T2s:
                warped_mask_img, warped_mask, template_reg, template_reg_mat =\
                    pdu.deface_image(T2.filename)
