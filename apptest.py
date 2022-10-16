from crypt import methods
import email
from http.client import HTTPException
from urllib.error import HTTPError
from flask import Flask, jsonify, send_file, request, make_response, session
from flask_cors import CORS
import os
import time
import datetime
import base64
import sys
from superApp202210 import esQuery
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from requests import session
from waitress import serve
import smtplib
from tools.token import make_token, parseToken, decode_token
import cv2
# import os
from yolov5.logo_detect import Yolo_Detect

import pyrebase

config = {
    'apiKey': "AIzaSyA_xMc3DtQQp8GmAb9JkTHNWMcyhFiQrNM",
    'authDomain': "logoshot-7c6a9.firebaseapp.com",
    'projectId': "logoshot-7c6a9",
    'storageBucket': "logoshot-7c6a9.appspot.com",
    'messagingSenderId': "256049641924",
    'appId': "1:256049641924:web:8e8a278f6b2186b9340c91",
    'databaseURL': ''
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()


app = Flask(__name__)
CORS(app, resources={r"/.*": {"origins": ["*"]}})
# routes
imgFolderRoutes = "imagelog/"
# official email
officialEmail = "ntuim2022@gmail.com"
officialEmailPassword = "cdmqxdubwtbimvif"
# ip to out
ip = "http://140.112.106.82:8081/"


@app.route("/registerVerify", methods=['POST'])
def registerVerify():
    content = request.json
    email = content['email']
    password = content['password']
    name = content['name']

    content = MIMEMultipart()  # 建立MIMEMultipart物件
    content["subject"] = "LogoShot 註冊驗證"  # 郵件標題
    content["from"] = officialEmail  # 寄件者
    content["to"] = email  # 收件者
    jwtEncodedUser = make_token(
        {'name': name, 'email': email, 'password': password})
    print(jwtEncodedUser)
    print("點擊以下連結驗證並註冊\n{}register?token={}".format(
        ip, jwtEncodedUser.decode("utf-8")))
    content.attach(MIMEText("點擊以下連結驗證並註冊\n{}register?token={}".format(
        ip, jwtEncodedUser.decode("utf-8"))))  # 郵件內容

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

    token = request.args.get('token')
    decodedUser = decode_token(token)

    user = auth.create_user_with_email_and_password(
        decodedUser['email'], decodedUser['password'])
    print(user)
    # doc_Ref = dbFireBase.collection(u'Users').document(decodedUser['name'])
    # doc_Ref.set(decodedUser)

    print(decodedUser)
    return {"res": {"status": "complete"}}


@app.route("/login", methods=['POST'])
def login():
    content = request.json
    email = content['email']
    password = content['password']
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        # print(user)
    except Exception as err:
        # print(err.__doc__)
        message = eval(err.args[1])['error']['message']
        return message, 400

    return {"res": {"userId": user['localId']}}


@app.route("/postImageSearch", methods=['POST'])
def imageSearch():
    startTime = time.time()
    photo = request.form["file_attachment"]
    photoWidth = request.form["photoWidth"]
    photoHeight = request.form["photoHeight"]
    indicatorX = request.form["indicatorX"]
    indicatorY = request.form["indicatorY"]
    userId = request.form["userId"]

    # searchKeywords = request.form["searchKeywords"]
    # isSimSound = eval(request.form["isSimSound"].capitalize())
    # isSimShape = eval(request.form["isSimShape"].capitalize())
    # target_classcodes = eval(request.form["target_classcodes"])
    # target_color = request.form["target_color"]
    # target_applicant = request.form["target_applicant"]
    # target_startTime = request.form["target_startTime"]
    # target_endTime = request.form["target_endTime"]

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

    returnVal = esQuery(isImageSearchFilter=True)

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
        'data': returnVal
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
    # target_draft_c = request.form["target_draft_c"]
    # target_draft_e = request.form["target_draft_e"]
    # target_draft_j = request.form["target_draft_j"]

    print(searchKeywords, isSimSound, isSimShape, target_classcodes,
          target_color, target_applicant, target_startTime, target_endTime)
    # print("Type:", type(target_classcodes))
    # returnVal = []
    returnVal = esQuery(searchKeywords, False, isSimSound, isSimShape, "", "", "", target_classcodes,
                        "", target_applicant, target_startTime, target_endTime)

    print(returnVal)
    return jsonify({
        'resultData': returnVal
    })


if __name__ == "__main__":
    app.run('0.0.0.0', 8081, debug=True)
    # serve(app, host="0.0.0.0", port=8081)
