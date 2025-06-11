// SIBI Detector - JavaScript for UI Interactivity - Clean Version
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const recordBtn = document.getElementById('record-btn');
    const stopBtn = document.getElementById('stop-btn');
    const recordingIndicator = document.getElementById('recording-indicator');
    const currentWord = document.getElementById('current-word');
    const audioPlayer = document.getElementById('audio-player');
    const audioElement = document.getElementById('audio-element');
    const audioText = document.getElementById('audio-text');
    const noAudioMessage = document.getElementById('no-audio-message');
    const historyList = document.getElementById('history-list');
    const noHistoryMessage = document.getElementById('no-history-message');

    // State variables
    let isRecording = false;
    let recordingInterval = null;
    let detectionHistory = [];

    // Event Listeners
    recordBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);

    // Functions
    function startRecording() {
        fetch('/start_recording', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                isRecording = true;
                recordBtn.disabled = true;
                stopBtn.disabled = false;
                recordingIndicator.style.display = 'flex';
                currentWord.textContent = '';
                
                // Start polling for current detection
                recordingInterval = setInterval(updateCurrentDetection, 1000);
            }
        })
        .catch(error => {
            console.error('Error starting recording:', error);
        });
    }

    function stopRecording() {
        fetch('/stop_recording', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                isRecording = false;
                recordBtn.disabled = false;
                stopBtn.disabled = true;
                recordingIndicator.style.display = 'none';
                
                // Clear polling interval
                if (recordingInterval) {
                    clearInterval(recordingInterval);
                    recordingInterval = null;
                }
                
                // Update UI with detected word
                if (data.word) {
                    currentWord.textContent = data.word;
                    
                    // Add to history
                    addToHistory(data.word, data.audio_file);
                    
                    // Play audio if available
                    if (data.audio_file) {
                        playAudio(data.audio_file, data.word);
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error stopping recording:', error);
        });
    }

    function updateCurrentDetection() {
        fetch('/get_recording_status')
        .then(response => response.json())
        .then(data => {
            if (data.is_recording) {
                currentWord.textContent = data.word || '';
            }
        })
        .catch(error => {
            console.error('Error updating detection:', error);
        });
    }

    function playAudio(audioFile, text) {
        // Update audio player
        audioElement.src = audioFile;
        audioText.textContent = text;
        
        // Show audio player, hide no audio message
        noAudioMessage.style.display = 'none';
        audioPlayer.style.display = 'block';
        
        // Play audio
        audioElement.play();
    }

    function addToHistory(word, audioFile) {
        // Create timestamp
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        
        // Create history item
        const historyItem = {
            word: word,
            audioFile: audioFile,
            timestamp: timeString,
            id: Date.now()
        };
        
        // Add to history array
        detectionHistory.unshift(historyItem);
        
        // Limit history to 10 items
        if (detectionHistory.length > 10) {
            detectionHistory.pop();
        }
        
        // Update UI
        updateHistoryUI();
    }

    function updateHistoryUI() {
        // Hide no history message if we have history
        if (detectionHistory.length > 0) {
            noHistoryMessage.style.display = 'none';
        }
        
        // Clear current list
        historyList.innerHTML = '';
        
        // Add history items
        detectionHistory.forEach(item => {
            const li = document.createElement('li');
            
            const wordSpan = document.createElement('span');
            wordSpan.className = 'history-word';
            wordSpan.textContent = item.word;
            
            const timeSpan = document.createElement('span');
            timeSpan.className = 'history-time';
            timeSpan.textContent = item.timestamp;
            
            li.appendChild(wordSpan);
            li.appendChild(timeSpan);
            
            // Add click event to play audio
            if (item.audioFile) {
                li.style.cursor = 'pointer';
                li.title = 'Klik untuk memutar audio';
                li.addEventListener('click', () => {
                    playAudio(item.audioFile, item.word);
                });
            }
            
            historyList.appendChild(li);
        });
    }
});
