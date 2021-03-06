# -*- coding:utf-8 -*-
import numpy as np
import os, sys, cv2, uuid, base64, glob, codecs
import pandas as pd


from PIL import Image



import json


def get_json_list(path):
    
    search_path = os.path.join(path, 'ID_JSON', '*.json')
    json_list = glob.glob(search_path)
    
    return json_list

def get_img_list(path):
 
    search_path = os.path.join(path, 'ID_COVER', '*.jpg')
    img_list = glob.glob(search_path)
    
    return img_list

def get_df(json_list, img_list):
    
    get_name = lambda x: os.path.splitext(os.path.basename(x))[0]
    json_dict = dict((get_name(path), path) for path in json_list)
    img_dict = dict((get_name(path), path) for path in img_list)
    inner_name = set(json_dict.keys()) & set(img_dict.keys())
    row = []
    for name in inner_name:
        row.append((name, json_dict[name], img_dict[name]))
    
    df = pd.DataFrame(row, columns=['name','json_path', 'img_path'])
    
    return df

def check_overlap(df): # 检查与训练样本是否重叠
    
    train_path = '/data/IDCARD20180815/Annotations'    
    xml_list = glob.glob(os.path.join(train_path,'*.xml'))
    get_name = lambda x: os.path.splitext(os.path.basename(x))[0]
    xml_dict = dict((get_name(path), path) for path in xml_list)
    name_overlap = set(df['name'].tolist()) & set(xml_dict.keys())
  
    print('The num of overlap ', len(name_overlap))
    
    return xml_dict
    
def ocr_from_faceplusplus(df):
    
    ocr1_list = []
 
    for rowid, row  in df.iterrows():
        with open(row['json_path'], 'r') as f:
            try:
                data1 = json.load(f)
                data1 = data1['cards'][0]
                data1['img_name'] = row['name']
                ocr1_list.append(data1)
            except :
                print(row['json_path']) # 
                continue
        # img_np = cv2.imread(row['img_path'])
        # data2 = model.predict(img_np, recog_model)
        # data2 = json.loads(data2)
        # data2['img_name'] = df['name']
        # ocr2_list.append(data2)
        # return data1, data2
        # print('reading...',rowid)
    return pd.DataFrame(ocr1_list) # , pd.DataFrame(ocr2_list)

def update_birthday(x):
    if len(x) > 0:   
        try:
            s = x.replace('年','-').replace('月','-').replace('日','')
            if s[4] != '-':
                s = s[:4] + '-' + s[5:]
            s = '-'.join(['%.2d' % int(ss) for ss in s.split('-')])
            return s
        except:
            return x
    else:
        return x
    
def ocr_from_self(json_path='../log/pred_out.json'):
    ocr_list = []
    with codecs.open(json_path,'r',encoding='utf-8') as f:
        # while True:
            # try:
                # test_json = json.loads(f.readline())
                # print(test_json)
                # ocr_list.append(test_json)
            # except:
                # break
        for line in f.readlines():
            test_json = json.loads(line)
            ocr_list.append(test_json)
        
    df = pd.DataFrame.from_dict(ocr_list)
    df['img_name'] = df['img_name'].map(lambda x: x.split('.')[0])
    # df['id_card_number'] = df['id_card_number'].map(lambda x: x.replace('O','0').replace('x','X')) # 
    # df['race'] = df['race'].map(lambda x: x[-1].replace('汊','汉') if len(x) > 0 else x)
    # df['gender'] = df['gender'].map(lambda x: x.replace('民','男').replace('歹','女').replace('另','男') if len(x) > 0 else x)
    # df['birthday'] = df['birthday'].map(update_birthday)
    return df
    
def comp_content(df_ocr1, df_ocr2):
        
        comp_key = ['name', 'address', 'gender', 'id_card_number', 'race','birthday']
        df_comp = df_ocr1.merge(df_ocr2, on='img_name')

        for key in comp_key:
            
            accuracy = np.mean(df_comp[key + '_x'] == df_comp[key + '_y'])
            print('the accuracy of', key, '=', round(accuracy,2))

def get_model():

    model = demo_new.ID_CARD()
    recog_model = model.load_model2()
    # img_np = cv2.imread(os.path.join('test', '1341197113120180612153259488862_3.jpg'))
    # output = a.__Cread__(img_np, None, None, basemodel)
    # output = a.predict(img_np, basemodel)
    # print(output)
    return model, recog_model
            
if __name__ == '__main__':

    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    base_path = '/data/1808_face-plus-plus'
    
    json_list = get_json_list(base_path) 
    img_list = get_img_list(base_path)
       
    df_face = get_df(json_list, img_list)
    
    # model, recog_model = get_model()
    
    df_ocr1 = ocr_from_faceplusplus(df_face)
    df_ocr1['birthday'] = df_ocr1['birthday'].map(lambda x: x.split('-')[0] + '年' + str(int(x.split('-')[1])) + '月' + str(int(x.split('-')[2])) + '日')
    df_ocr2 = ocr_from_self(json_path='../log/front.json')
    comp_content(df_ocr1, df_ocr2)
