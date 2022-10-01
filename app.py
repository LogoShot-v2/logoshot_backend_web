# flask: https://flask.palletsprojects.com/en/2.0.x/quickstart/#
from crypt import methods
from flask import Flask, jsonify, send_file, request, make_response
import sys
import base64
import psycopg2
from urllib.parse import quote
import time
import random
import os
import io
from base64 import encodebytes
from PIL import Image   
from waitress import serve
import datetime
import pandas as pd
from functools import reduce
from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/.*": {"origins": ["*"]}})

conn = psycopg2.connect(database="trademark1", user="tm_root", password="roottm_9823a", host="trueint.lu.im.ntu.edu.tw", port="5433")
cur = conn.cursor()
cur.execute("SELECT caseno FROM trademark fetch first 1000 rows only")
caseno_1000 = cur.fetchall()
caseno_1000 = [x[0] for x in caseno_1000]
conn.close()



@app.route('/function1', methods=["GET"])
def function1():
    return jsonify({"Hello":"World"})




# trademark
trademark_columns = ["doc", "caseno", "registerno", "trademark_name", "trademark_design", "filing_date", "censor", "priority_date", "sdate", "edate", "word_description", "mark_type", "memo", "wavpath", "servicemark"]
# rca(agent)
rca_columns = ["caseno", "bchinese"]
# rcc(class)
rcc_columns = ["caseno", "enforcement_rules", "class", "goods_denomination"]
# rco(owner)
rco_columns = ["caseno", "achinese", "aenglish", "address"]
# rcp(picture)
rcp_columns = ["caseno", "filename", "displayname", "path"]
# text
text_columns = ["caseno", "chinese", "english", "japanese"]

def sql_command2(cur, colnames, tablename, caseno_list):
    selected = ",".join(colnames)
    conditions = " OR ".join(["caseno = " + str(x) for x in caseno_list])
    # print(colnames)
    # print("conditions: ", conditions, file=sys.stdout)
    # print("SQL: ", "SELECT {} FROM {} WHERE {}".format(selected, tablename, conditions), file=sys.stdout)
    cur.execute("SELECT {} FROM {} WHERE {}".format(selected, tablename, conditions))
    df = pd.DataFrame(cur.fetchall(), columns=colnames).astype(str)
    df = df.groupby(df['caseno'], as_index=False).aggregate(lambda x: "/".join(x))
    return df


def fetchdata4(caseno_list): 
    conn = psycopg2.connect(database="trademark1", user="tm_root", password="roottm_9823a", host="trueint.lu.im.ntu.edu.tw", port="5433")
    cur = conn.cursor()
    main_df = sql_command2(cur, trademark_columns, "trademark", caseno_list)
    rca_df = sql_command2(cur, rca_columns, "rca", caseno_list)
    rcc_df = sql_command2(cur, rcc_columns, "rcc", caseno_list)
    rco_df = sql_command2(cur, rco_columns, "rco", caseno_list)
    rcp_df = sql_command2(cur, rcp_columns, "rcp", caseno_list)
    text_df = sql_command2(cur, text_columns, "text", caseno_list)
    conn.close()

    # display("main_df:", main_df)
    # display("rca_df:", rca_df)
    # display("rcc_df:", rcc_df)
    # display("rco_df:", rco_df)
    # display("rcp_df:", rcp_df)
    caseno_list = [str(x) for x in caseno_list]
    df_all = reduce(lambda left,right: pd.merge(left,right,how='left',on='caseno'), [main_df,rca_df,rcc_df,rco_df,rcp_df, text_df]).astype(str)
    df_all = df_all.set_index('caseno')
    df_all = df_all.reindex(caseno_list)
    df_all = df_all.reset_index()
    # display(df_all)
    result_list = []
    for i in df_all.to_dict(orient='records'):
        result = dict()
        result["Path"] = '/service/trademark/raw_register_data/' + i['doc'] + "/" + i['filename']
        # print("Path: ", result["Path"], file=sys.stdout)
        result["metadata"] = i
        # print("metadata: ", result["metadata"], file=sys.stdout)    
        result_list.append(result)
    return result_list      


import slimon
model = slimon.Model()
from Search import search

def create_html(TYPE, SEARCH, TIME, resultPath_list):
    dirr = time.strftime("/home/metadragons/backend/SearchHtmlResults/{}/%Y-%m-%d").format(TYPE)
    # print("dirr: ", dirr)
    os.makedirs(dirr, exist_ok=True)
    html_str = '<div class="t">\n'
    html_str += '\t<h2>{} Search:</h2>\n'.format(TYPE)
    if TYPE == "Image":
        html_str += '\t<img src="../../../../../..{}" width="300"/>\n'.format(SEARCH)
    elif TYPE == "Text":
        html_str += '\t<h3>QUERY={}</h3>\n'.format(SEARCH)
    html_str += '\t<h2>Results:</h2>\n'
    for i in range(len(resultPath_list)):
        html_str += '\t<h3>{}.</h3>\n'.format(i+1)
        html_str += '\t<img src="../../../../../..{}" width="300"/>\n'.format(resultPath_list[i])
    html_str += '</div>'
    Html_file= open("{}/{}.html".format(dirr, TIME),"w")
    Html_file.write(html_str)
    Html_file.close()
    return html_str

def load_images(TYPE, SEARCH, TIME, caseno_list):
    result_list = []
    # caseno_list = [99018887, 100048442, 100006294, 100036013, 100015475, 100045485, 100053242, 100053158, 98017486, 100048244, 100034136, 100015575, 99059834, 100039852, 100020857, 100039089, 100015683, 100030430, 99059734, 100050261, 100041025, 100034969, 100058002, 100035279, 100047596, 100048242, 100047022, 100033212, 100047019, 100048739, 99056287, 99042253, 99022071, 100018260, 100043720, 100035291, 99061105, 99055598, 100055899, 100022190, 100037752, 100032097, 98030087, 100041404, 100034168, 100012916, 99040055, 100047249, 100037818, 100046101, 100000214, 100039351, 100043045, 100046931, 100040241, 100010120, 99057907, 100036572, 100035000, 100027168, 100037388, 99042111, 100028773, 100032160, 100018054, 100001572, 99038458, 100040028, 100008473, 99054248, 100040320, 100034946, 100029091, 100038959, 99035163, 100027546, 99041348, 100021585, 99059678, 97049456, 100053398, 100022946, 100040031, 100028393, 100039333, 100010723, 100034580, 100046150, 100041676, 100030440, 99057980, 100036995, 100045130, 100025812, 100036394, 100015200, 100044424, 100021701, 100040164, 100040873]
    # for caseno in caseno_list:
    #     result_list.append(fetchdata3(caseno))       
    if(len(caseno_list) != 0):
        result_list = fetchdata4(caseno_list)    
    base64Image_list = []
    metadata_list = []
    for r in result_list:
        try:
            # print('r["Path"]: ', r["Path"], file=sys.stdout)   
            # print('r["metadata"]: ', r["metadata"], file=sys.stdout)            
            pil_img = Image.open(r["Path"], mode='r') # reads the PIL image
            # print(os.path.getsize(r["Path"]))
            (width, height) = (pil_img.width // 2, pil_img.height // 2)
            # print((width, height))
            pil_img = pil_img.resize((width, height))
            byte_arr = io.BytesIO()
            pil_img.save(byte_arr, format='PNG', quality=50) # convert the PIL image to byte array
            encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64        
            base64Image_list.append(encoded_img)
            metadata_list.append(r["metadata"])
        except:
            pass
    html_str = create_html(TYPE, SEARCH, TIME, [r["Path"] for r in result_list])
    return base64Image_list, metadata_list

@app.route('/function5', methods=['POST'])
def function5():
    startTime = time.time()
    # print(request.method, file=sys.stdout)   
    photo = request.form["file_attachment"]
    # print(type(photo), file=sys.stdout) # <class 'str'>
    searchQuery = request.form["searchQuery"] 
    caseno_list1 = []
    if photo != "null":
        # print(request.form['name'], file=sys.stdout)   
        dirr = time.strftime("/home/metadragons/backend/uploadedImages/%Y-%m-%d")
        # print("dirr: ", dirr)
        os.makedirs(dirr, exist_ok=True)        
        filePath = "{}/{}.png".format(dirr, request.form['name'])
        print(request.remote_addr, datetime.datetime.now(), "ImageSearch:", filePath, file=sys.stdout) 
        with open(filePath, "wb") as f:
            img = base64.decodebytes(photo.encode('ascii'))
            f.write(img)
        startTime2 = time.time()
        # caseno_list1 = random.sample(caseno_1000, 50)
        caseno_list1 = model.single_img_retrieve(filePath)[:50]
        # print("caseno_list1:", caseno_list1, file=sys.stdout) 
        EndTime2 = time.time()
        print("Time Spent(Image_Model): {}s".format(EndTime2 - startTime2), file=sys.stdout)
        
    caseno_list2 = []    
    if searchQuery != "":
        print(request.remote_addr, datetime.datetime.now(), "TextSearch:", searchQuery, file=sys.stdout) 
        check1 = True if request.form["check1"] == "true" else False
        check2 = True if request.form["check2"] == "true" else False
        check3 = True if request.form["check3"] == "true" else False
        check4 = True if request.form["check4"] == "true" else False
        startTime3 = time.time()
        caseno_list2 = search(searchQuery,50,[check1,check2,check3])
        EndTime3 = time.time()
        print("Time Spent(Text_Model): {}s".format(EndTime3 - startTime3), file=sys.stdout)        
    startTime4 = time.time()
    base64Image_list1, metadata_list1, base64Image_list2, metadata_list2 = [], [], [], []
    if photo != "null":   
        base64Image_list1, metadata_list1 = load_images("Image", filePath, request.form['name'], caseno_list1) 
    if searchQuery != "":
        base64Image_list2, metadata_list2 = load_images("Text", searchQuery, request.form['name'], caseno_list2) 
    EndTime4 = time.time()
    print("Time Spent(load_images): {}s".format(EndTime4 - startTime4), file=sys.stdout)
    EndTime = time.time()
    print("Time Spent(function5): {}s".format(EndTime - startTime), file=sys.stdout)           
    # print(len(base64Image_list), file=sys.stdout)        
    return jsonify({
        'base64Images1': base64Image_list1,
        'metadatas1': metadata_list1,
        'base64Images2': base64Image_list2,
        'metadatas2': metadata_list2        
    })
    
@app.route("/postImageSearch", methods=['POST'])
def imageSearch():
    startTime = time.time()
    # print(request.method, file=sys.stdout)   
    photo = request.form["file_attachment"]
    caseno_list1 = []
    if photo != "null":
        # print(request.form['name'], file=sys.stdout)   
        dirr = time.strftime("/home/metadragons/backend/uploadedImages/%Y-%m-%d")
        # print("dirr: ", dirr)
        os.makedirs(dirr, exist_ok=True)        
        filePath = "{}/{}.png".format(dirr, request.form['name'])
        print(request.remote_addr, datetime.datetime.now(), "ImageSearch:", filePath, file=sys.stdout) 
        with open(filePath, "wb") as f:
            img = base64.decodebytes(photo.encode('ascii'))
            f.write(img)
        startTime2 = time.time()
        # caseno_list1 = random.sample(caseno_1000, 50)
        caseno_list1 = model.single_img_retrieve(filePath)[:50]
        # print("caseno_list1:", caseno_list1, file=sys.stdout) 
        EndTime2 = time.time()
        print("Time Spent(Image_Model): {}s".format(EndTime2 - startTime2), file=sys.stdout)
        
    startTime4 = time.time()
    base64Image_list, metadata_list = [], []
    if photo != "null":   
        base64Image_list, metadata_list = load_images("Image", filePath, request.form['name'], caseno_list1)    
        
    EndTime4 = time.time()
    print("Time Spent(load_images): {}s".format(EndTime4 - startTime4), file=sys.stdout)
    
    EndTime = time.time()
    print("Time Spent(postImageSearch): {}s".format(EndTime - startTime), file=sys.stdout)  
    
    return jsonify({
        'base64Images': base64Image_list,
        'metadatas': metadata_list      
    })

from pick_gan_pic import pick_pic
@app.route('/function6', methods=['GET'])
def function6():
    label = request.args["label"]
    # print("label: ", label, file=sys.stdout) 
    startTime = time.time()
    path_list = pick_pic(label)[:50]
    # print("path_list:", path_list, file=sys.stdout) 
    base64Image_list = []
    for path in path_list:
        # print('path: ', path, file=sys.stdout)          
        pil_img = Image.open(path, mode='r') # reads the PIL image
        # print(os.path.getsize(path)) 
        pil_img = pil_img.resize((128, 128))
        byte_arr = io.BytesIO()
        pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
        encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64        
        base64Image_list.append(encoded_img)         
    EndTime = time.time()
    print(request.remote_addr, "Time Spent(function6): {}s".format(EndTime - startTime), file=sys.stdout)                
    return jsonify({
        'base64Images': base64Image_list,
    })
if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8081)