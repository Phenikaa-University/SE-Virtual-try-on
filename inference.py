import time
from options.test_options import TestOptions
from data.data_loader import CreateDataLoader, CreateDataUploadLoader
from models.networks import ResUnetGenerator, load_checkpoint
from models.afwm import AFWM
import torch.nn as nn
import os
import torch
import cv2
import torch.nn.functional as F
from tqdm.auto import tqdm
import numpy as np
from util import flow_util
from PIL import Image
opt = TestOptions().parse()

f2c = flow_util.flow2color()

def de_offset(s_grid):
    [b,_,h,w] = s_grid.size()


    x = torch.arange(w).view(1, -1).expand(h, -1).float()
    y = torch.arange(h).view(-1, 1).expand(-1, w).float()
    x = 2*x/(w-1)-1
    y = 2*y/(h-1)-1
    grid = torch.stack([x,y], dim=0).float().cuda()
    grid = grid.unsqueeze(0).expand(b, -1, -1, -1)

    offset = grid - s_grid

    offset_x = offset[:,0,:,:] * (w-1) / 2
    offset_y = offset[:,1,:,:] * (h-1) / 2

    offset = torch.cat((offset_y,offset_x),0)
    
    return  offset

#  list human-cloth pairs
with open('demo.txt', 'w') as file:
    lines = [f'input.png {cloth_img_fn}\n' for cloth_img_fn in os.listdir('dataset/test_clothes')]
    file.writelines(lines)

data_loader = CreateDataLoader(opt)
dataset = data_loader.load_data()
dataset_size = len(data_loader)
print('[INFO] Data Loaded')

upload_data_loader = CreateDataUploadLoader(opt)
upload_dataset = upload_data_loader.load_data()
upload_dataset_size = len(upload_data_loader)
print('[INFO] Upload Data Loaded')

warp_model = AFWM(opt, 3)
warp_model.eval()
warp_model.cuda()
load_checkpoint(warp_model, opt.warp_checkpoint)
print('[INFO] Warp Model Loaded')

gen_model = ResUnetGenerator(7, 4, 5, ngf=64, norm_layer=nn.BatchNorm2d)
gen_model.eval()
gen_model.cuda()
load_checkpoint(gen_model, opt.gen_checkpoint)
print('[INFO] Gen Model Loaded')

def get_demo_images():

    result_images = []
    for i, data in tqdm(enumerate(dataset)):
        # print(data)
        real_image = data['image']
        clothes = data['clothes']
        ##edge is extracted from the clothes image with the built-in function in python
        edge = data['edge']
        # print(edge)
        edge = torch.FloatTensor((edge.detach().numpy() > 0.5).astype(np.int64))
        clothes = clothes * edge   

        flow_out = warp_model(real_image.cuda(), clothes.cuda())
        warped_cloth, last_flow, = flow_out
        warped_edge = F.grid_sample(edge.cuda(), last_flow.permute(0, 2, 3, 1),
                          mode='bilinear', padding_mode='zeros')

        gen_inputs = torch.cat([real_image.cuda(), warped_cloth, warped_edge], 1)
        gen_outputs = gen_model(gen_inputs)
        p_rendered, m_composite = torch.split(gen_outputs, [3, 1], 1)
        p_rendered = torch.tanh(p_rendered)
        m_composite = torch.sigmoid(m_composite)
        m_composite = m_composite * warped_edge
        p_tryon = warped_cloth * m_composite + p_rendered * (1 - m_composite)

        a = real_image.float().cuda()
        b= clothes.cuda()
        # flow_offset = de_offset(last_flow)
        # flow_color = f2c(flow_offset).cuda()
        # c = warped_cloth.cuda()
        d = p_tryon
        # combine = torch.cat([a[0],b[0], flow_color, c[0], d[0]], 2).squeeze()
        # combine = torch.cat([b[0], d[0]], 2).squeeze()
        cv_img = (d.permute(0, 2, 3, 1).squeeze().detach().cpu().numpy() + 1) / 2
        rgb = (cv_img * 255).astype(np.uint8)


        result_images.append(rgb)


    return result_images

def get_upload_images():
    result_images = []
    for i, data in tqdm(enumerate(upload_dataset)):
        # print(data)
        real_image = data['image']
        clothes = data['clothes']
        ##edge is extracted from the clothes image with the built-in function in python
        edge = data['edge']
        # print(edge)
        edge = torch.FloatTensor((edge.detach().numpy() > 0.5).astype(np.int64))
        clothes = clothes * edge   

        flow_out = warp_model(real_image.cuda(), clothes.cuda())
        warped_cloth, last_flow, = flow_out
        warped_edge = F.grid_sample(edge.cuda(), last_flow.permute(0, 2, 3, 1),
                          mode='bilinear', padding_mode='zeros')

        gen_inputs = torch.cat([real_image.cuda(), warped_cloth, warped_edge], 1)
        gen_outputs = gen_model(gen_inputs)
        p_rendered, m_composite = torch.split(gen_outputs, [3, 1], 1)
        p_rendered = torch.tanh(p_rendered)
        m_composite = torch.sigmoid(m_composite)
        m_composite = m_composite * warped_edge
        p_tryon = warped_cloth * m_composite + p_rendered * (1 - m_composite)

        a = real_image.float().cuda()
        b= clothes.cuda()
        # flow_offset = de_offset(last_flow)
        # flow_color = f2c(flow_offset).cuda()
        # c = warped_cloth.cuda()
        d = p_tryon
        # combine = torch.cat([a[0],b[0], flow_color, c[0], d[0]], 2).squeeze()
        # combine = torch.cat([b[0], d[0]], 2).squeeze()
        # cv_img = (combine.permute(1, 2, 0).detach().cpu().numpy() + 1) / 2
        cv_img = (d.permute(0, 2, 3, 1).squeeze().detach().cpu().numpy() + 1) / 2
        rgb = (cv_img * 255).astype(np.uint8)


        result_images.append(rgb)


    return result_images