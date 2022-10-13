from crypt import methods
from flask import Flask, jsonify, send_file, request, make_response
from flask_cors import CORS
import os
import time
import datetime
import base64
import sys
from superApp202210 import esQuery

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from waitress import serve
import smtplib
import jwt

app = Flask(__name__)
CORS(app, resources={r"/.*": {"origins": ["*"]}})
# routes
imgFolderRoutes = "imagelog/"
## official email
officialEmail = "ntuim2022@gmail.com"
officialEmailPassword = "cdmqxdubwtbimvif"
## ip to out
ip = "http://10.129.214.198:8081/"

@app.route("/registerVerify", methods=['POST'])
def registerVerify():
    content = request.json
    email = content['email']
    password = content['password']

    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = "Learn Code With Mike"  #郵件標題
    content["from"] = officialEmail  #寄件者
    content["to"] = email #收件者
    
    content.attach(MIMEText("點擊以下連結驗證\n" + ip + 'register'))  #郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(officialEmail, officialEmailPassword)  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)

    return {"res": {"email": email}}

@app.route("/register", methods=['GET'])
def register():
    print('register')
    return {"res": {"status": "complete"}}


@app.route("/postImageSearch", methods=['POST'])
def imageSearch():
    startTime = time.time()
    photo = request.form["file_attachment"]
    photoWidth = request.form["photoWidth"]
    photoHeight = request.form["photoHeight"]
    indicatorX = request.form["indicatorX"]
    indicatorY = request.form["indicatorY"]
    userId = request.form["userId"]

    caseno_list1 = []
    if photo != "null":
        dirr = imgFolderRoutes + userId
        os.makedirs(dirr, exist_ok=True)
        photoName = time.strftime("%Y-%m-%d-%H:%M:%S")

        # save photo
        phtoPath = "{}/{}.png".format(dirr, photoName)
        infoPath = "{}/{}.txt".format(dirr, photoName)
        print(request.remote_addr, datetime.datetime.now(),
              "ImageSearch:", phtoPath, file=sys.stdout)
        with open(phtoPath, "wb") as f:
            img = base64.decodebytes(photo.encode('ascii'))
            f.write(img)

        with open(infoPath, "w") as f:
            f.write(photoWidth + ' ' + photoHeight +
                    ' ' + indicatorX + ' ' + indicatorY)

        # loadModel
        startTime2 = time.time()
        # caseno_list1 = model.single_img_retrieve(phtoPath)[:50]
        EndTime2 = time.time()

        print("Time Spent(Image_Model): {}s".format(
            EndTime2 - startTime2), file=sys.stdout)

    # loadImage and metadatalist
    # startTime4 = time.time()
    # base64Image_list, metadata_list = [], []
    # if photo != "null":
    #     base64Image_list, metadata_list = load_images(
    #         "Image", phtoPath, request.form['name'], caseno_list1)

    # EndTime4 = time.time()
    # print("Time Spent(load_images): {}s".format(
    #     EndTime4 - startTime4), file=sys.stdout)

    # EndTime = time.time()
    # print("Time Spent(postImageSearch): {}s".format(
    #     EndTime - startTime), file=sys.stdout)

    return jsonify({
        'base64Images': [],
        'metadatas': [],
    })


@app.route("/postTextSearch", methods=['POST'])
def textSearch():
    searchKeywords = request.form["searchKeywords"]
    isSimSound = eval(request.form["isSimSound"].capitalize())
    isSimShape = eval(request.form["isSimShape"].capitalize())
    target_classcodes = eval(request.form["target_classcodes"])
    target_color = request.form["target_color"]
    target_applicant = request.form["target_applicant"]
    target_startTime = request.form["target_startTime"]
    target_endTime = request.form["target_endTime"]
    print(searchKeywords, isSimSound, isSimShape, target_classcodes,
          target_color, target_applicant, target_startTime, target_endTime)
    print("Type:", type(target_classcodes))
    # returnVal = []
    returnVal = esQuery(searchKeywords, isSimSound, isSimShape, target_classcodes,
                        target_color, target_applicant, target_startTime, target_endTime)

    return jsonify({
        'resultData': returnVal
    })


if __name__ == "__main__":
    app.run('0.0.0.0', 8081, debug=True)
    # serve(app, host="0.0.0.0", port=8081)
