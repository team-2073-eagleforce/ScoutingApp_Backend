var qrcode = window.qrcode;

const video = document.createElement("video");
const canvasElement = document.getElementById("qr-canvas");
const canvas = canvasElement.getContext("2d");

const qrResult = document.getElementById("qr-result");
const outputData = document.getElementById("outputData");
const btnScanQR = document.getElementById("btn-scan-qr");

let scanning = false;

qrcode.callback = res => {
    if (res) {
        if (outputData.innerText !== res) {
            if (res.split(',').length !== 12) {
                outputData.innerText = "ERROR Not A Valid QR Code"
            } else {
                outputData.innerText = res;
                $.post("/retrieval/detectScan", {
                    data: res
                });
            }
        }
        qrResult.hidden = false;

        tick()
        scan()
    }
};

btnScanQR.onclick = () => {
    if (scanning) {
        scanning = false;

        video.srcObject.getTracks().forEach(track => {
            track.stop();
        });

        qrResult.hidden = true;
        canvasElement.hidden = true;
        btnScanQR.hidden = false;
    } else {
        navigator.mediaDevices
            .getUserMedia({video: {facingMode: "environment"}})
            .then(function (stream) {
                scanning = true;
                qrResult.hidden = true;
                btnScanQR.hidden = false;
                canvasElement.hidden = false;
                video.setAttribute("playsinline", true);
                video.srcObject = stream;
                video.play();
                tick();
                scan();
            });
    }
};

function tick() {
    canvasElement.height = video.videoHeight;
    canvasElement.width = video.videoWidth;
    canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);

    scanning && requestAnimationFrame(tick);
}

function scan() {
    try {
        qrcode.decode();
    } catch (e) {
        setTimeout(scan, 400);
    }
}