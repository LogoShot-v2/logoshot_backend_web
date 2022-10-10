from flask import Flask, jsonify, send_file, request, make_response
from flask_cors import CORS
import os
import time
import datetime
import base64
import sys

from waitress import serve


app = Flask(__name__)
CORS(app, resources={r"/.*": {"origins": ["*"]}})
## routes
imgFolderRoutes = "imagelog/"

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
        dirr = imgFolderRoutes + request.form['userId']
        os.makedirs(dirr, exist_ok=True)
        photoName = time.strftime("%Y-%m-%d-%H:%M:%S")

        # save photo
        filePath = "{}/{}.png".format(dirr, photoName)
        print(request.remote_addr, datetime.datetime.now(),
              "ImageSearch:", filePath, file=sys.stdout)
        with open(filePath, "wb") as f:
            img = base64.decodebytes(photo.encode('ascii'))
            f.write(img)

        # loadModel
        startTime2 = time.time()
        # caseno_list1 = model.single_img_retrieve(filePath)[:50]
        EndTime2 = time.time()

        print("Time Spent(Image_Model): {}s".format(
            EndTime2 - startTime2), file=sys.stdout)

    # loadImage and metadatalist
    # startTime4 = time.time()
    # base64Image_list, metadata_list = [], []
    # if photo != "null":
    #     base64Image_list, metadata_list = load_images(
    #         "Image", filePath, request.form['name'], caseno_list1)

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


if __name__ == "__main__":
    app.run('0.0.0.0', 8081)
    # serve(app, host="0.0.0.0", port=8081)
