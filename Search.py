import fasttext
import pickle as pk
import jieba
from opencc import OpenCC
from sklearn.metrics.pairwise import linear_kernel
import numpy as np

# /service/trademark/text

jieba.load_userdict("/service/trademark/text/userdict_final.txt")
model_w = fasttext.load_model("/service/trademark/text/model_w2.bin")
model_t = fasttext.load_model("/service/trademark/text/model_t2.bin")


with open('/service/trademark/text/tf_idf_add_wiki.pk', 'rb') as d:
     tfidf = pk.load(d)
with open('/service/trademark/text/caseno_list.pk', 'rb') as d:
     casenos = pk.load(d)
        
with open('/service/trademark/text/name.pk', 'rb') as d:
     tm_dict_1_inv = pk.load(d)
with open('/service/trademark/text/people.pk', 'rb') as d:
     tm_dict_2_inv = pk.load(d)
with open('/service/trademark/text/goods.pk', 'rb') as d:
     tm_dict_3_inv = pk.load(d)
dict_inv = [tm_dict_1_inv,tm_dict_2_inv,tm_dict_3_inv]
print("-------------------Ready2!--------------------")
        
def find_k_similiar(tfidf,caseno_list,caseno, k = 1):
    index = caseno_list.index(caseno)
    cosine_similarities = linear_kernel(tfidf[index:(index+1)], tfidf).flatten()
    #print(cosine_similarities)
    related_docs_indices = cosine_similarities.argsort()[:-(k+1):-1]
    #print(cosine_similarities[related_docs_indices])
    len_case = len(caseno_list)
    related_docs_indices = related_docs_indices[related_docs_indices < len_case]
    caseno_arr = np.array(caseno_list)
    return list(caseno_arr[related_docs_indices])

def getnn(text,model):
    result = model.get_nearest_neighbors(text)
    return result

def good_neighbors(w,t):
#     wt = w + t
#     wt = sorted(wt,key = lambda i:i[0],reverse = True)
    w2 = sorted(w,key = lambda i:i[0],reverse = True)
    t2 = sorted(t,key = lambda i:i[0],reverse = True)
    wt = [w2[0],w2[1],w2[2],t2[0],t2[1],t2[2]]
    wt = sorted(wt,key = lambda i:i[0],reverse = True)
    return [wt[i][1] for i in range(len(wt))]


def ustr(in_str):
    etc = False
    out = ["",""]
    for i in range(len(in_str)):
        res = uchar(in_str[i])
        if res == 1 and etc:
            out[0] = out[0] + in_str[i]
            out[1] = out[1] + " "
            etc = False
        elif res == 1:
            out[0] = out[0] + in_str[i]
        elif res == 2:
            out[1] = out[1] + in_str[i]
            etc = True
        elif res == 11:
            out[0] = out[0] + " "
        elif res == 22:
            out[1] = out[1] + " "
    c = out[0].split(" ")
    e = out[1].split(" ")
    return [c,e]

def uchar(uchar):
    """????????????unicode???????????????"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
            return 1
    """????????????unicode???????????????"""
    if uchar >= u'\u0030' and uchar<=u'\u0039':
            return -1      
    """????????????unicode?????????????????????"""
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
            return 2
    if uchar in ('???','???','???','???','???','???','???','???','#','???'):
            return 11
    if uchar in ('-',',','.',';','!','?',' ','"',"'",'(',')'):
            return 22
    return -1
    
def tokenize(text):
    cc = OpenCC('s2t')
    text = cc.convert(text)
    result = ustr(text)
    conly = result[0]
    eonly = result[1]
    
    tokens = []
    for i in conly:
        ts =  jieba.cut_for_search(i)
#         ts =  jieba.cut(i)
        ts = [t for t in ts if t != '' and t != ' ']
        tokens = tokens + ts
        
    eonly = [t for t in eonly if t != '' and t != ' ']
    tokens = tokens + eonly
    
    return [text,tokens]

# New Dict Version (11/14)
def weight_dict(words,dicts,weights,mode,w_flag):
    result = {}
        
    for word in words:
        if w_flag:
            new_weights = [(len(word)-2)*k for k in weights]
        else:
            new_weights = weights
            
        for i,t_dict in enumerate(dicts):
            if mode[i]:
                try:
                    r_dict = t_dict[word]
                    for j in r_dict:
                        try:
                            result[j[0]] += j[1] * new_weights[i]
                        except: 
                            result[j[0]] = j[1] * new_weights[i]
                except:
                    continue
    
    result = {k:v for k,v in result.items() if v >= 2}
    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
    
    return result

# Current Version do not have time limit (Since it's very fast)
def search(text,showlimit,mode):
    
    # print(text)
    
    text = text.lower()
    texts = text.split(" ")
    
    case_show = []
    
    sim = set()
    sima = getnn(text,model_t)
    simb = getnn(text,model_w)
    sim = sim.union(set(good_neighbors(sima,simb)))
    
    weights = [4,2,1]
    if sum(mode) == 1:
        weights = [2,2,1]
    
    # 1. ????????????
    r = weight_dict([text],dict_inv,weights,mode,False)
    for i in r.keys():
        if i not in case_show:
            case_show.append(i)
        if len(case_show) >= showlimit:
            break
            
    # print("???Query????????????(??????): ",len(case_show))
    # print("=====")
    
    if len(case_show) >= showlimit:
        return case_show
    
    # 2. N-gram??????
    texts2 = [ustr(i) for i in texts]      
    texts2 = [texts2[i][0][0] for i in range(len(texts2))]
    
    n_grams = []
    two_grams = []
    for i in range(len(texts2)):
        if len(texts2[i]) > 2:
            for l in range(len(texts2[i])-2):
                for j in range(3+l,len(texts2[i])+1):
                    n_gram = texts2[i][l:j]
                    if len(n_gram) < len(texts2[i]):
                        n_grams.append(n_gram)
                        
        for l in range(len(texts2[i])-1):
            two_gram = texts2[i][l:l+2]
            if len(two_gram) < len(texts2[i]):
                two_grams.append(two_gram)
                    
    # print(n_grams)
    # print(two_grams)
    r = weight_dict(n_grams,dict_inv,weights,mode,True)
    
    new_mode = mode
    if mode[2]:
        new_mode[2] = False
    r2 = weight_dict(two_grams,dict_inv,weights,new_mode,False)
              
    rs = list(r.keys()) + list(r2.keys())
    
    for i in rs:
        if i not in case_show:
            case_show.append(i)
        if len(case_show) >= showlimit:
            break
            
    # print("N gram????????????(??????): ",len(case_show))
    # print("=====")
    
    if len(case_show) >= showlimit:
        return case_show
            
        
    # 3. Query ?????? (??????????????????n gram????????????)
    tokens = []
    for i in texts:
        token = tokenize(i)
        tokens = tokens + token[1]
        
    tokens = [i for i in tokens if len(i) > 1]
    # print(tokens)

    for i in tokens:
        sima = getnn(i,model_t)
        simb = getnn(i,model_w)
        sim = sim.union(set(good_neighbors(sima,simb)))

    r = weight_dict(tokens,dict_inv,weights,mode,False)

    for i in r:
        if i not in case_show:
            case_show.append(i)
        if len(case_show) >= showlimit:
            break

    # print("Query?????????????????????(??????): ",len(case_show))
    # print("=====")
    
    if len(case_show) >= showlimit:
        return case_show
    
    
    # 4. ????????????????????????
            
    sim = [i for i in sim if len(i) > 1]
    # print(sim)

    r = weight_dict(sim,dict_inv,weights,mode,False)

    for i in r:
        if i not in case_show:
            case_show.append(i)
        if len(case_show) >= showlimit:
            break
    
    # print("Query???????????????????????????(??????): ",len(case_show))
    # print("=====")
    
    if len(case_show) >= showlimit:
        return case_show
    
    # 5. kNN??????
    i = 0
    while len(case_show) < showlimit:
        try:
            r = find_k_similiar(tfidf,casenos,case_show[i],k = 40)
        except Exception as e:
            print("Encountered error, set return to empyt list. ", e)
            r = []
        for i in r:
            if i not in case_show:
                case_show.append(i)
            if len(case_show) >= showlimit:
                break
        i += 1
        if i > len(case_show):
            break
                
    # print("??????kNN???????????????(??????): ",len(case_show))
    return case_show
        
# ===== Main =====

# test = ["world gym","??????","?????????","??????","??????????????????"]
# r = search(test[-1],100,[True,True,True])

# search??????????????????????????????Query???????????????????????????
#???????????????????????????????????????????????????(????????????)????????????200??????????????????
#????????????????????????????????????[T,T,T]???T????????????????????????????????????????????????
#1:???????????????????????????
#2:??????/?????????/????????????
#3:????????????
#????????????:
# 1. ????????????
# 2. N-gram??????
# 3. Query ?????? (??????????????????n gram????????????)
# 4. ????????????????????????
# 5. kNN??????