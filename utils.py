import os
from PIL import Image
import linecache
import cv2
from torchvision import transforms
import numpy as np
import torch
from models.networks import ResUnetGenerator, load_checkpoint
from models.afwm import AFWM
from options.test_options import TestOptions
import torch.nn as nn
from torch.nn import functional as F
from tqdm.auto import tqdm
from torch.utils.data import DataLoader, TensorDataset

opt = TestOptions().parse()

warp_model = AFWM(opt, 3)
warp_model.eval()
warp_model.cuda()
load_checkpoint(warp_model, opt.warp_checkpoint)

gen_model = ResUnetGenerator(7, 4, 5, ngf=64, norm_layer=nn.BatchNorm2d)
gen_model.eval()
gen_model.cuda()
load_checkpoint(gen_model, opt.gen_checkpoint)

def get_edge(image_path, edge_path):
    img = cv2.imread(image_path)
    OLD_IMG = img.copy()
    mask = np.zeros(img.shape[:2], np.uint8)
    SIZE = (1, 65)
    bgdModle = np.zeros(SIZE, np.float64)

    fgModle = np.zeros(SIZE, np.float64)
    rect = (1, 1, img.shape[1], img.shape[0])
    cv2.grabCut(img, mask, rect, bgdModle, fgModle, 10, cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    img *= mask2[:, :, np.newaxis]

    mask2 *= 255

    cloth_edges_img_fp = edge_path
    cv2.imwrite(cloth_edges_img_fp, mask2)

def get_tensor(image_path, edge_path, clothes_path, height, weight):
    I = Image.open(image_path).convert('RGB')
    I = I.resize((weight, height))

    transform = transforms.ToTensor()
    # if normalize:
    #     transforms_list += [transforms.Normalize((0.5, 0.5, 0.5),
    #                                              (0.5, 0.5, 0.5))]
    # transforms = transforms.Compose(transforms_list)
    I_tensor = transform(I)

    C = Image.open(clothes_path).convert('RGB')
    C_tensor = transform(C)

    E = Image.open(edge_path).convert('L')
    E_tensor = transform(E)

    input_dict = {'image': I_tensor, 'clothes': C_tensor, 'edge': E_tensor}
    return input_dict

clothes_path = 'dataset/uploads/006026_1.jpg'
edge_path = 'dataset/uploads/006026_1_edge.jpg'
image_path = 'dataset/uploads/model-5.png'
# input_dict = get_tensor(image_path, edge_path, clothes_path, 256, 192)

def get_image(image_path, clothes_path, edge_path):
    input_dict = get_tensor(image_path, edge_path, clothes_path, 256, 192)
    data = torch.utils.data.DataLoader(input_dict, batch_size=8, shuffle=False)
    real_image = data['image']
    clothes = data['clothes']
    edge = data['edge']
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
    b = clothes.cuda()
    d = p_tryon
    combine = torch.cat([b[0], d[0]], 2).squeeze()
    cv_img = (combine.permute(1, 2, 0).detach().cpu().numpy() + 1) / 2
    rgb = (cv_img * 255).astype(np.uint8)

    return rgb

input_dict = get_tensor(image_path, edge_path, clothes_path, 256, 192)
image_dataset = TensorDataset(input_dict['image'])
clothes_dataset = TensorDataset(input_dict['clothes'])
edge_dataset = TensorDataset(input_dict['edge'])
# Tạo các DataLoader cho từng dataset
image_dataloader = DataLoader(image_dataset, batch_size=8, shuffle=False)
clothes_dataloader = DataLoader(clothes_dataset, batch_size=8, shuffle=False)
edge_dataloader = DataLoader(edge_dataset, batch_size=8, shuffle=False)

# Lặp qua từng DataLoader để lấy dữ liệu
for i, (image, clothes, edge) in tqdm(enumerate(zip(image_dataloader, clothes_dataloader, edge_dataloader))):
    # Bây giờ bạn có thể sử dụng image, clothes và edge như bạn cần
    real_image = image
    # edge = torch.FloatTensor((edge.detach().numpy() > 0.5).astype(np.int64))
    clothes = clothes * edge

    flow_out = warp_model(real_image.cuda(), clothes.cuda())
    warped_cloth, last_flow, = flow_out
    warped_edge = F.grid_sample(edge.cuda(), last_flow.permute(0, 2, 3, 1),
                                mode='bilinear', padding_mode='zeros')
    gen_inputs = torch.cat([real_image.cuda(), warped_cloth, warped_edge], 1)
    gen_outputs = gen_model(gen_inputs)