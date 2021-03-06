# -*- coding: utf-8 -*-
import math
import sys
import time

import torch
from torch import nn
import torch.nn.functional as F
from torchvision import transforms
import numpy as np
import matplotlib.pyplot as plt

sys.path.append('../../')
from models.fpnssd import FPNSSD512, SSDBboxCoder
from visualizations import vis_image_bbox
from transforms import resize
from PIL import Image


def main(args):
    print('Loading fpnssd model...')
    net = FPNSSD512(num_classes=21).cuda(3)
    box_coder = SSDBboxCoder(net)
    net = nn.DataParallel(net, [3])
    net.load_state_dict(torch.load('./checkpoint/ckpt.pt')['net'])
    # net.load_state_dict(torch.load('./fpnssd512_20_trained.pth'))
    # net.load_state_dict(torch.load(args[1])['net'])
    net.eval()

    start = time.time()
    print('Loading image...')
    # img = Image.open('/home/yhuangcc/data/voc(07+12)/JPEGImages/000002.jpg')
    # img=Image.open('/home/yhuangcc/data/coco/images/val2017/000000000285.jpg')
    img = Image.open(args[1])
    w, h = img.size
    img = img.resize((512, 512))

    print('Predicting...')
    transform = transforms.Compose([transforms.ToTensor(),
                                    transforms.Normalize((0.485, 0.456, 0.406),
                                                         (0.229, 0.224, 0.225))])
    x = transform(img).cuda(3)
    loc_preds, cls_preds = net(x.unsqueeze(0))

    print('Decoding...')
    loc_preds = loc_preds.squeeze().cpu()
    cls_preds = F.softmax(cls_preds.squeeze().cpu(), dim=1)
    boxes, labels, scores = box_coder.decode(loc_preds, cls_preds)
    print(f'Detection ends... Consuming time {time.time()-start:.4f}s')

    label_names = np.loadtxt('/home/yhuangcc/ObjectDetection/datasets/voc/labels.txt', np.object).tolist()
    # label_names = np.loadtxt(args[3], np.object).tolist()
    img, boxes = resize(img, boxes.cpu(), (w, h))
    vis_image_bbox(img, boxes, [label_names[label] for label in labels], scores)
    plt.close()

if __name__ == '__main__':
    main(sys.argv)
