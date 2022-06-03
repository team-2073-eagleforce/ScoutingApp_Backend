from flask import render_template, Blueprint

retrieval_bp = Blueprint(
    'retrieval_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@retrieval_bp.route("/qrScanner", methods=["GET", "POST"])
def qrScanner():
    return render_template('QRScanner.html')

# @retrieval_bp.route('/requests', methods=['POST', 'GET'])
# def tasks():
#     global switch, camera
#     if request.method == 'POST':
#         if request.form.get('stop') == 'Stop/Start':
#             if switch == 1:
#                 switch = 0
#                 camera.release()
#                 cv2.destroyAllWindows()
#             else:
#                 camera = cv2.VideoCapture(0)
#                 switch = 1
#                 while switch == 1:
#                     ret, frame = camera.read()
#                     cv2.imshow('Image', frame)
#                     code = cv2.waitKey(10)
#
#                     gray_img = cv2.cvtColor(frame, 0)
#                     barcode = decode(gray_img)
#
#                     for obj in barcode:
#                         barcodeData = str(obj.data.decode("utf-8")).split(',')
#                         print(barcodeData)
#                         existing_match = matchEntry.query.filter(
#                             matchEntry.team == barcodeData[0] or matchEntry.matchNumber ==
#                             barcodeData[1]).first()
#                         if not existing_match:
#                             match = matchEntry(
#                                 team=int(barcodeData[0]),
#                                 matchNumber=int(barcodeData[1]),
#                                 autoCrossing=int(barcodeData[2]),
#                                 autoUpper=int(barcodeData[3]),
#                                 autoBottom=int(barcodeData[4]),
#                                 teleUpper=int(barcodeData[5]),
#                                 teleBottom=int(barcodeData[6]),
#                                 level=int(barcodeData[7]),
#                                 driverPerf=int(barcodeData[8]),
#                                 defensePerf=int(barcodeData[9]),
#                                 name=str(barcodeData[10]),
#                                 comment=str(barcodeData[11]),
#                             )
#                             db.session.add(match)
#                             db.session.commit()
#
#     elif request.method == 'GET':
#         return render_template('QRScanner.html')
#     return render_template('QRScanner.html')
