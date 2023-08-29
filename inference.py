import time
from options.test_options import TestOptions
from data.data_loader import CreateDataLoader
from models.networks import ResUnetGenerator, load_checkpoint
from models.afwm import AFWM_Vitonhd_lrarms
import torch.nn as nn
import os
import torch
import cv2
import torch.nn.functional as F
from tqdm.auto import tqdm
import numpy as np

opt = TestOptions().parse()

#  list human-cloth pairs
with open('demo.txt', 'w') as file:
    lines = [f'input.png {cloth_img_fn}\n' for cloth_img_fn in os.listdir('dataset/VITON-HD/test/image')]
    file.writelines(lines)

data_loader = CreateDataLoader(opt)
dataset = data_loader.load_data()
dataset_size = len(data_loader)
print('[INFO] Data Loaded')

warp_model = AFWM_Vitonhd_lrarms(opt, 51)
warp_model.eval()
warp_model.cuda()
load_checkpoint(warp_model, opt.warp_checkpoint)
print('[INFO] Warp Model Loaded')

gen_model = ResUnetGenerator(7, 4, 5, ngf=64, norm_layer=nn.BatchNorm2d)
gen_model.eval()
gen_model.cuda()
load_checkpoint(gen_model, opt.gen_checkpoint)
print('[INFO] Gen Model Loaded')

def get_result_images():

    result_images = []
    for i, data in tqdm(enumerate(dataset)):


        person_clothes_edge = data['person_clothes_mask'].cuda()
        real_image = data['image'].cuda()
        clothes = data['color'].cuda()
        preserve_mask = data['preserve_mask3'].cuda()
        preserve_region = real_image * preserve_mask
        warped_cloth = data['warped_cloth'].cuda()
        warped_prod_edge = data['warped_edge'].cuda()
        arms_color = data['arms_color'].cuda()
        arms_neck_label= data['arms_neck_lable'].cuda()
        pose = data['pose'].cuda()

        gen_inputs = torch.cat([preserve_region, warped_cloth, warped_prod_edge, arms_neck_label, arms_color, pose], 1)

        gen_outputs = gen_model(gen_inputs)
        p_rendered, m_composite = torch.split(gen_outputs, [3, 1], 1)
        p_rendered = torch.tanh(p_rendered)
        m_composite = torch.sigmoid(m_composite)
        m_composite = m_composite * warped_prod_edge
        # m_composite =  person_clothes_edge.cuda()*m_composite1
        p_tryon = warped_cloth * m_composite + p_rendered * (1 - m_composite)

        a = real_image
        c = clothes
        k = p_tryon

        combine = k[0].squeeze()
        cv_img = (combine.permute(1, 2, 0).detach().cpu().numpy()+1)/2
        rgb = (cv_img*255).astype(np.uint8)

        result_images.append(rgb)


    return result_images