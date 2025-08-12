let alreadyScanned = false;
let scannerInitialized = false;

// Function to check camera availability
async function checkCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: "environment",
                width: { ideal: 1280 },
                height: { ideal: 720 }
            } 
        });
        stream.getTracks().forEach(track => track.stop());
        return true;
    } catch (err) {
        console.error("Camera check failed:", err);
        return false;
    }
}

// Function to initialize scanner
async function initScanner() {
    document.getElementById("scan-result").innerText = "Checking camera...";
    
    // First check if camera is available
    const cameraAvailable = await checkCamera();
    if (!cameraAvailable) {
        document.getElementById("scan-result").innerHTML = 
            "❌ Camera not available. Please check:<br>" +
            "• Camera permissions are allowed<br>" +
            "• No other app is using the camera<br>" +
            "• You're using HTTPS (required for camera)<br>" +
            "<button onclick='retryScanner()'>Retry Camera</button>";
        return;
    }

    document.getElementById("scan-result").innerText = "Initializing scanner...";

    Quagga.init({
        inputStream: {
            name: "Live",
            type: "LiveStream",
            target: '#scanner',
            constraints: {
                width: { min: 640, ideal: 1280, max: 1920 },
                height: { min: 480, ideal: 720, max: 1080 },
                facingMode: "environment",
                aspectRatio: { min: 1, max: 2 }
            }
        },
        decoder: {
            readers: [
                "code_128_reader",
                "ean_reader", 
                "ean_8_reader",
                "code_39_reader",
                "code_39_vin_reader",
                "codabar_reader",
                "upc_reader",
                "upc_e_reader",
                "i2of5_reader",
                "2of5_reader",
                "code_93_reader"
            ]
        },
        locate: true,
        frequency: 10
    }, function(err) {
        if (err) {
            console.error("Quagga init error:", err);
            document.getElementById("scan-result").innerHTML = 
                "❌ Scanner initialization failed:<br>" + err.message + "<br>" +
                "<button onclick='retryScanner()'>Retry Camera</button>";
            return;
        }
        
        scannerInitialized = true;
        Quagga.start();
        document.getElementById("scan-result").innerText = "✅ Camera ready! Please scan an ID card...";
        
        // Add a timeout to check if video is actually showing
        setTimeout(() => {
            const video = document.getElementById('scanner');
            if (video.videoWidth === 0 || video.videoHeight === 0) {
                document.getElementById("scan-result").innerHTML = 
                    "⚠️ Camera started but no video feed detected.<br>" +
                    "Please check camera permissions and refresh.<br>" +
                    "<button onclick='location.reload()'>Refresh Page</button>";
            }
        }, 3000);
    });
}

// Function to retry scanner
function retryScanner() {
    if (scannerInitialized) {
        Quagga.stop();
    }
    alreadyScanned = false;
    scannerInitialized = false;
    document.getElementById("scan-result").innerText = "Retrying camera...";
    initScanner();
}

// Initialize scanner when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check if camera is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        document.getElementById("scan-result").innerHTML = 
            "❌ Camera not supported in this browser.<br>" +
            "Please use Chrome, Firefox, or Edge.";
        return;
    }
    
    // Check if we're on HTTPS (required for camera)
    if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
        document.getElementById("scan-result").innerHTML = 
            "⚠️ Camera requires HTTPS connection.<br>" +
            "Please access via https:// or localhost.";
        return;
    }
    
    initScanner();
});

Quagga.onDetected(function(result) {
    if (alreadyScanned) return;
    
    const code = result?.codeResult?.code;
    if (!code) return;

    alreadyScanned = true;
    document.getElementById("scan-result").innerHTML = 
        "✅ Scanned: " + code + "<br>" +
        "<button onclick='resetScanner()'>Scan Another</button>";
    document.getElementById("scanned-id").value = code;
    document.getElementById("submit-btn").style.display = "block";
    Quagga.stop();
});

// Function to reset scanner for another scan
function resetScanner() {
    alreadyScanned = false;
    document.getElementById("scanned-id").value = "";
    document.getElementById("submit-btn").style.display = "none";
    document.getElementById("scan-result").innerText = "Camera ready. Please scan an ID card...";
    if (scannerInitialized) {
        Quagga.start();
    }
}

// Handle scanner errors
Quagga.onProcessed(function(result) {
    if (result) {
        if (result.codeResult && result.codeResult.code) {
            console.log("Detected code:", result.codeResult.code);
        }
    }
});

// Handle camera permission errors
Quagga.onError(function(err) {
    console.error("Quagga error:", err);
    if (err.name === 'NotAllowedError') {
        document.getElementById("scan-result").innerHTML = 
            "❌ Camera access denied.<br>" +
            "Please allow camera permissions in your browser settings.<br>" +
            "<button onclick='location.reload()'>Refresh Page</button>";
    } else if (err.name === 'NotFoundError') {
        document.getElementById("scan-result").innerHTML = 
            "❌ No camera found.<br>" +
            "Please connect a camera and refresh the page.<br>" +
            "<button onclick='location.reload()'>Refresh Page</button>";
    } else {
        document.getElementById("scan-result").innerHTML = 
            "❌ Scanner error: " + err.message + "<br>" +
            "<button onclick='retryScanner()'>Retry</button>";
    }
});
