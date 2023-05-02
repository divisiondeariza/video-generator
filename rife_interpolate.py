#!/usr/bin/env python3
# write a function that interpolates between two images using the model.RIFE_HD and returns the interpolated image

from model.RIFE_HDv3 import Model
import torch
import cv2
import torch.nn.functional as F
import os
from tqdm import tqdm

class RIFEModel(Model):
    def inference(self, img0, img1, scale=1):
        imgs = torch.cat((img0, img1), 1)
        scale_list = [4/scale, 2/scale, 1/scale]
        flow, mask, merged = self.flownet(imgs, scale_list)
        return merged[2]

# write a method that returns the model already initialized
def get_model():
    model = Model()
    model.load_model("model/train_log", -1)
    model.eval()
    model.device()
    return model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = get_model()

def interpolate(img0, img1):
    """
    Interpolates between two images using the model.RIFE_HD and returns the interpolated image
    """
    image = model.inference(img0, img1)
    return image


def get_image_for_interpolation(img, device):
    """
    Returns the images for interpolation
    """
    return (torch.tensor(img.transpose(2, 0, 1)).to(device) / 255.).unsqueeze(0)

def resize_frames_for_interpolation(img0, img1):
    n, c, h, w = img0.shape
    ph = ((h - 1) // 32 + 1) * 32
    pw = ((w - 1) // 32 + 1) * 32
    padding = (0, pw - w, 0, ph - h)
    img0 = F.pad(img0, padding)
    img1 = F.pad(img1, padding)
    return img0, img1

def generate_frames(img0, img1, n=1):
    """
    Generates 2**n - 1 frames between img0 and img1
    """
    frames = [img0, img1]
    for i in range(n):
        new_frames = []
        for image0, image1 in zip(frames, frames[1:]):
            mid = interpolate(image0, image1).cpu().detach().numpy()
            mid = torch.tensor(mid).to(device)
            new_frames.append(image0)
            new_frames.append(mid)
        new_frames.append(frames[-1])
        frames = new_frames
    return frames[1:-1]

def generate_frames_for_dir(device, frames_path, n=1):
    """
    Generate frames for a given directory of frames. frames_path should contain the frames in the format 0000_0000.png, 0001_0000.png, etc.
    
    Args:
        device (torch.device): Device to be used for interpolation.
        frames_path (str): Path to the folder where the frames are to be saved.
        n (int): log base 2 of the number of frames to be generated plus one between each pair of frames. For example, if n = 1, then 1 frames will be generated between each pair of frames, if n = 2, then 3 frames will be generated between each pair of frames, if n = 3, then 7 frames will be generated between each pair of frames, etc.

    Returns:
        None
    
    Raises:
        None
    """
    files_tuples = [(filename0, filename1) for filename0, filename1 in zip(sorted(os.listdir(frames_path)), sorted(os.listdir(frames_path))[1:])]
    for filename0, filename1 in tqdm(files_tuples):
        img0 = cv2.imread(os.path.join(frames_path, filename0), cv2.IMREAD_UNCHANGED)
        img1 = cv2.imread(os.path.join(frames_path, filename1), cv2.IMREAD_UNCHANGED)
        img0 = get_image_for_interpolation(img0, device)
        img1 = get_image_for_interpolation(img1, device)
        img0, img1 = resize_frames_for_interpolation(img0, img1)
        frames = generate_frames(img0, img1, n)
        for index, frame in enumerate(frames):
            _, _, h, w = img0.shape
            start_frame_name = int(filename0.split(".")[0].split("_")[0])
            # save the image in frames like 0000_0000.png if it was interpolated between 0000.png and 0001.png, 0000_0001.png if it was interpolated between 0000.png and 0001.png, etc.
            output_name = "{:04d}_{:04d}.png".format(start_frame_name, index + 1)
            ffmpeg_command = (frame[0] * 255).cpu().byte().numpy().transpose(1, 2, 0)[:h, :w]
            cv2.imwrite(os.path.join(frames_path, output_name), ffmpeg_command)
        
if __name__ == "__main__":  
    for filename0, filename1 in zip(sorted(os.listdir("frames")), sorted(os.listdir("frames"))[1:]):
        img0 = cv2.imread('frames/' + filename0, cv2.IMREAD_UNCHANGED)
        img1 = cv2.imread('frames/' + filename1, cv2.IMREAD_UNCHANGED)
        img0 = get_image_for_interpolation(img0, device)
        img1 = get_image_for_interpolation(img1, device)
        img0, img1 = resize_frames_for_interpolation(img0, img1)
        frames = generate_frames(img0, img1, 2)
        for index, frame in enumerate(frames):
            n, c, h, w = img0.shape
            start_frame_name = int(filename0.split(".")[0].split("_")[0])
            # save the image in frames like 0000_0000.png if it was interpolated between 0000.png and 0001.png, 0000_0001.png if it was interpolated between 0000.png and 0001.png, etc.
            output_name = "{:04d}_{:04d}.png".format(start_frame_name, index + 1)
            new_var = (frame[0] * 255).byte().numpy().transpose(1, 2, 0)[:h, :w]
            cv2.imwrite('frames/{}'.format(output_name), new_var)
        
# for concatenating all the frames into a video called output.mp4 use this ffmpeg command
# ffmpeg -framerate 30 -pattern_type glob -i 'frames/*_*.png' -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p output.mp4
 