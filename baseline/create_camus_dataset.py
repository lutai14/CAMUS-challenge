# Requirements
import os
import numpy as np
import SimpleITK as sitk
import h5py
import cv2

# Path to the training folder
train_path = "../data/training/"

def mhd_to_array(path):
    """
    Read a *.mhd file stored in path and return it as a numpy array.
    """
    return sitk.GetArrayFromImage(sitk.ReadImage(path, sitk.sitkFloat32))

# Define lists storing all images names
train_2ch_frames_list = sorted(os.listdir(train_path + "2ch/frames/"))
train_2ch_masks_list = sorted(os.listdir(train_path + "2ch/masks/"))
train_4ch_frames_list = sorted(os.listdir(train_path + "4ch/frames/"))
train_4ch_masks_list = sorted(os.listdir(train_path + "4ch/masks/"))

train_all_frames_list = sorted(os.listdir(train_path + "2ch/frames/") + os.listdir(train_path + "4ch/frames/"))
train_all_masks_list = sorted(os.listdir(train_path + "2ch/masks/") + os.listdir(train_path + "4ch/masks/"))

# Create hierarchical h5py file, ready to be filled with 4 datasets
f = h5py.File("../data/image_dataset.hdf5", "w")

f.create_dataset("train 2ch frames", (900, 384, 384, 1),
                chunks = (4, 384, 384, 1), dtype = "float32")

f.create_dataset("train 2ch masks", (900, 384, 384, 1),
                chunks = (4, 384, 384, 1), dtype = "int32")

f.create_dataset("train 4ch frames", (900, 384, 384, 1),
                chunks = (4, 384, 384, 1), dtype = "float32")

f.create_dataset("train 4ch masks", (900, 384, 384, 1),
                chunks = (4, 384, 384, 1), dtype = "int32")

f.create_dataset("train all frames", (1800, 384, 384, 1),
                chunks = (4, 384, 384, 1), dtype = "float32")

f.create_dataset("train all masks", (1800, 384, 384, 1),
                chunks = (4, 384, 384, 1), dtype = "int32")



# Iterate over images and save them into the corresponding dataset
j = 0
for i in train_2ch_frames_list:
    if "mhd" in i:
        array = mhd_to_array(os.path.join(train_path, "2ch/frames", i))
        new_array = cv2.resize(array[0,:,:], dsize=(384, 384), interpolation=cv2.INTER_CUBIC)
        new_array = np.reshape(new_array,(384,384,1))
        new_array = new_array/255
        f["train 2ch frames"][j,...] = new_array[...]
        j = j + 1        
        
j = 0
for i in train_2ch_masks_list:
    if "mhd" in i:
        array = mhd_to_array(os.path.join(train_path, "2ch/masks", i))
        new_array = cv2.resize(array[0,:,:], dsize=(384, 384), interpolation=cv2.INTER_NEAREST)
        new_array = np.reshape(new_array,(384,384,1))
        f["train 2ch masks"][j,...] = new_array[...]
        j = j + 1   
        
j = 0
for i in train_4ch_frames_list:
    if "mhd" in i:
        array = mhd_to_array(os.path.join(train_path, "4ch/frames", i))
        new_array = cv2.resize(array[0,:,:], dsize=(384, 384), interpolation=cv2.INTER_CUBIC)
        new_array = np.reshape(new_array,(384,384,1))
        new_array = new_array/255
        f["train 4ch frames"][j,...] = new_array[...]
        j = j + 1        
        
j = 0
for i in train_4ch_masks_list:
    if "mhd" in i:
        array = mhd_to_array(os.path.join(train_path, "4ch/masks", i))
        new_array = cv2.resize(array[0,:,:], dsize=(384, 384), interpolation=cv2.INTER_NEAREST)
        new_array = np.reshape(new_array,(384,384,1))
        f["train 4ch masks"][j,...] = new_array[...]
        j = j + 1

j = 0
for i in train_all_frames_list:
    if "mhd" in i:
        array = mhd_to_array(os.path.join(train_path, f"{'2ch' if '2CH' in i else '4ch'}/frames", i))
        new_array = cv2.resize(array[0,:,:], dsize=(384, 384), interpolation=cv2.INTER_CUBIC)
        new_array = np.reshape(new_array,(384,384,1))
        new_array = new_array/255
        f["train all frames"][j,...] = new_array[...]
        j = j + 1        
        
j = 0
for i in train_all_masks_list:
    if "mhd" in i:
        array = mhd_to_array(os.path.join(train_path, f"{'2ch' if '2CH' in i else '4ch'}/masks", i))
        new_array = cv2.resize(array[0,:,:], dsize=(384, 384), interpolation=cv2.INTER_NEAREST)
        new_array = np.reshape(new_array,(384,384,1))
        f["train all masks"][j,...] = new_array[...]
        j = j + 1       

        
f.close()

