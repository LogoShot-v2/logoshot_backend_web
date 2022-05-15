import torch
import torchvision
from torchvision import transforms, utils, models
from random import randint

import numpy as np
import pandas as pd
from PIL import Image

import shutil

import time


torch.manual_seed(4096)



class Model():
    def __init__(self):
        time_start = time.time() #開始計時

        print("--------------------Initialize model--------------------")
        laten_vec_train = pd.read_csv('/service/trademark/latent_vectors/latent_vectors.csv', header=None)
        self.laten_vec_train = laten_vec_train/np.linalg.norm(laten_vec_train, axis=1, keepdims=True)
        self.latent_vector_path = pd.read_csv('/home/slimon/2021_trademark_project/slimon/model/retrieve/latent_vector_path.csv')

        device = 'cpu'
        PATH = "/home/slimon/2021_trademark_project/slimon/model/lab_img_content_text_gray/resnet152_no_fc.pt"
        checkpoint = torch.load(PATH, map_location=device)

        model_no_fc = models.resnet152(pretrained=True)
        model_no_fc = torch.nn.Sequential(*(list(model_no_fc.children())[:-1]))
        model_no_fc.load_state_dict(checkpoint['model_state_dict'])
        model_no_fc.eval()
        self.model_no_fc = model_no_fc.to(device)

        time_end = time.time()    #結束計時
        time_c= time_end - time_start   #執行所花時間
        # print('time cost', time_c, 's')
        print("-------------------Ready!--------------------")




    def image_loader(self, image_name):
        
        loader = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
        image = Image.open(image_name).convert('L').convert('RGB')
    #     image = Image.open(image_name).convert('RGB')

        image = loader(image).float()
        image = image.clone().detach()
        image = image.unsqueeze(0)
        return image



    def single_img_retrieve(self, img_path):
        img = self.image_loader(img_path)
        img = img.to('cpu')
        out = self.model_no_fc(img).cpu()
        out = torch.squeeze(out)
        out = out.detach().numpy()

        
        out_norm = np.linalg.norm(out)
        
        
        similarities = np.dot(self.laten_vec_train, out / out_norm)
        index = np.argsort(similarities)  # Returns the indices that would sort an array. 取倒數20個也就是前20大的index
        index = np.flip(index)

        caseno_list = []
        for c,p in zip(self.latent_vector_path.caseno[index], self.latent_vector_path.path[index]):
            caseno_list.append(c)

        # print(caseno_list[:10])
        return caseno_list

