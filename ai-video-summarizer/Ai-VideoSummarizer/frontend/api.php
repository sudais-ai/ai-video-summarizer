<?php
// api.php - PHP backend for handling file uploads and API requests

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

$action = $_GET['action'] ?? '';

switch ($action) {
    case 'upload_video':
        handleVideoUpload();
        break;
    case 'process_url':
        processVideoUrl();
        break;
    case 'get_stats':
        getStatistics();
        break;
    default:
        echo json_encode(['error' => 'Invalid action']);
        break;
}

function handleVideoUpload() {
    if (!isset($_FILES['video'])) {
        echo json_encode(['error' => 'No video file uploaded']);
        return;
    }
    
    $file = $_FILES['video'];
    $maxSize = 500 * 1024 * 1024; // 500MB
    
    if ($file['size'] > $maxSize) {
        echo json_encode(['error' => 'File size exceeds 500MB limit']);
        return;
    }
    
    $allowedTypes = ['video/mp4', 'video/mov', 'video/avi', 'video/mkv'];
    if (!in_array($file['type'], $allowedTypes)) {
        echo json_encode(['error' => 'Unsupported file type']);
        return;
    }
    
    $uploadDir = 'uploads/';
    if (!is_dir($uploadDir)) {
        mkdir($uploadDir, 0777, true);
    }
    
    $filename = uniqid() . '_' . basename($file['name']);
    $filepath = $uploadDir . $filename;
    
    if (move_uploaded_file($file['tmp_name'], $filepath)) {
        // In a real implementation, you would call Python backend here
        $response = [
            'success' => true,
            'filename' => $filename,
            'message' => 'Video uploaded successfully'
        ];
        echo json_encode($response);
    } else {
        echo json_encode(['error' => 'Failed to upload file']);
    }
}

function processVideoUrl() {
    $data = json_decode(file_get_contents('php://input'), true);
    $url = $data['url'] ?? '';
    
    if (empty($url)) {
        echo json_encode(['error' => 'No URL provided']);
        return;
    }
    
    // Validate URL
    if (!filter_var($url, FILTER_VALIDATE_URL)) {
        echo json_encode(['error' => 'Invalid URL']);
        return;
    }
    
    // In a real implementation, forward to Python backend
    $pythonResponse = callPythonBackend('process_video', ['url' => $url]);
    
    echo json_encode([
        'success' => true,
        'message' => 'Video URL received',
        'url' => $url,
        'processing_started' => true
    ]);
}

function getStatistics() {
    // In a real implementation, get from database
    $stats = [
        'videos_processed' => 1247,
        'questions_generated' => 8592,
        'time_saved_hours' => 2154,
        'active_users' => 342
    ];
    
    echo json_encode(['success' => true, 'stats' => $stats]);
}

function callPythonBackend($endpoint, $data) {
    // Call Python Flask backend
    $url = 'http://localhost:5000/api/' . $endpoint;
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json'
    ]);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($response, true);
}
?>