#!/usr/bin/env python
# coding: utf-8

# In[17]:
import os
from os import listdir, walk
from os.path import isfile, join
import random   
from os import walk

#label 0:;circle label 1:animals; label 2:plant; label 3:others; label -1:all
def pick_pic(labels):
    mypath = '/service/trademark/gan_images'
    # if label == -1 : from all labels   
    if(labels != -1):
        path = os.path.join(mypath, 'label-'+str(labels))
        pic_path = []
        for root, dirs, files in walk(path):
            for f in files:
                fullpath = join(root, f)
                pic_path.append(fullpath)
            break
        pick = random.sample(pic_path, 200)
    else:
        pick = []
        for i in range(4):
            pic_path = []
            path = os.path.join(mypath, 'label-'+str(i))
            for root, dirs, files in walk(path):
                for f in files:
                    fullpath = join(root, f)
                    pic_path.append(fullpath)
                break
            pick = pick + random.sample(pic_path, 50)
        random.shuffle(pick)
    return([p for p in pick if ".DS_Store" not in p])


# # In[18]:


# from PIL import Image
# import psycopg2
# import ipyplot
# if __name__ == "__main__":
#     pic = pick_pic(-1)
#     print(len(pic))


# # In[19]:


# #print(pic,len(pic))
# imgs = []
# title = []
# #print(new_label)
# for i in range(30):
#     img_temp = Image.open(pic[i])
#     title.append(str(i))
#     imgs.append(img_temp)
                        
# ipyplot.plot_class_representations(imgs, title, img_width = 30)


# # In[ ]:




