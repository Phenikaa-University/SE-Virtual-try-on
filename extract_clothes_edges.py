import os

import cv2
import numpy as np
from tqdm.auto import tqdm

def extract_edges(demo=False):

    if demo:
        clothes_dir = 'dataset/upload_clothes'
        clothes_edges_dir = 'dataset/upload_edge'
    else:

        clothes_dir = 'dataset/upload_clothes'
        clothes_edges_dir = 'dataset/upload_edge'


    for img_fn in tqdm(os.listdir(clothes_dir)):
        cloth_img_fp = os.path.join(clothes_dir, img_fn)
        img = cv2.imread(cloth_img_fp)
        OLD_IMG = img.copy()
        mask = np.zeros(img.shape[:2], np.uint8)
        SIZE = (1, 65)
        bgdModle = np.zeros(SIZE, np.float64)

        fgdModle = np.zeros(SIZE, np.float64)
        rect = (1, 1, img.shape[1], img.shape[0])
        cv2.grabCut(img, mask, rect, bgdModle, fgdModle, 10, cv2.GC_INIT_WITH_RECT)

        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        img *= mask2[:, :, np.newaxis]

        mask2 *= 255

        cloth_edges_img_fp = os.path.join(clothes_edges_dir, img_fn)
        cv2.imwrite(cloth_edges_img_fp, mask2)

