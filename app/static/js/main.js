// let audioBlob = null; 
// let mediaRecorder;
// let audioChunks = [];
// let isRecording = false; 

// const recordBtn = document.getElementById('record_btn');
// const generateBtn = document.getElementById('generate_btn');
// const statusText = document.getElementById('recording_status');

// // 1. Voice Recording Logic
// recordBtn.addEventListener('click', async () => {
//     if (!isRecording) {
//         // START RECORDING
//         try {
//             const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//             mediaRecorder = new MediaRecorder(stream);
            
//             mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
//             mediaRecorder.onstop = () => {
//                 audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
//                 audioChunks = []; // reset for next time
                
//                 // UI Feedback
//                 statusText.innerText = "Voice recorded!";
//                 statusText.style.color = "#16a34a"; 
//             };
            
//             mediaRecorder.start();
//             isRecording = true;
//             recordBtn.innerText = 'Stop Recording';
            
//             // UI Feedback
//             statusText.innerText = "Recording...";
//             statusText.style.color = "#ef4444"; 
            
//         } catch (err) {
//             alert("Microphone access denied or not available.");
//             console.error("Mic error:", err);
//         }
//     } else {
//         // STOP RECORDING
//         mediaRecorder.stop();
//         isRecording = false;
//         recordBtn.innerText = 'Start Recording';
//     }
// });

// // 2. The Unified Fusion Logic
// generateBtn.addEventListener('click', async () => {
//     const textInput = document.getElementById('user_text').value;

//     // Validation: Check if the user provided AT LEAST text or voice
//     if (!textInput.trim() && !audioBlob) {
//         alert("Please enter text or record a voice message!");
//         return;
//     }

//     // UI Feedback & Prevent double-clicking
//     generateBtn.innerText = "Generating...";
//     generateBtn.disabled = true; 
    
//     // Create the Unified Payload
//     const formData = new FormData();
//     if (textInput.trim()) {
//         formData.append('text_data', textInput);
//     }
//     if (audioBlob) {
//         formData.append('voice_data', audioBlob, 'voice_memo.webm');
//     }
    
//     // NEW LOGIC: Append the Checkbox states (true or false)
//     formData.append('push_to_sheets', document.getElementById('chk_sheets').checked);
//     formData.append('push_to_sql', document.getElementById('chk_sql').checked);
//     if (textInput.trim()) {
//         formData.append('text_data', textInput);
//     }
//     if (audioBlob) {
//         formData.append('voice_data', audioBlob, 'voice_memo.webm');
//     }

//     try {
//         // Send to our NEW unified backend endpoint
//         const response = await fetch('/api/generate-fusion', {
//             method: 'POST',
//             body: formData
//         });

//         // 1. If backend returns 200 OK (Success) -> Expecting HTML Page
//         if (response.ok) {
//             const html = await response.text(); 
            
//             // Overwrite the current page with the result page
//             document.open();
//             document.write(html);
//             document.close();
//         } 
//         // 2. If backend returns Error -> Expecting JSON Error Message
//         else {
//             const errorResult = await response.json();
//             alert("Error: " + errorResult.error);
//         }
        
//     } catch (error) {
//         console.error("Fusion API Error:", error);
//         alert("Failed to process the request. Check terminal logs.");
//     } finally {
//         // Reset UI Button
//         generateBtn.innerText = "Generate Quotation";
//         generateBtn.disabled = false;
//     }
// });

// let mediaRecorder;
// let audioChunks = [];
// let audioBlob = null;

// const recordBtn = document.getElementById('record-btn'); 
// const generateBtn = document.getElementById('generate-btn'); 
// const textInput = document.getElementById('text-input'); 
// const statusText = document.getElementById('status-text'); 

// // 1. Voice Recording Logic
// if (recordBtn) {
//     recordBtn.addEventListener('click', async () => {
//         if (!mediaRecorder || mediaRecorder.state === 'inactive') {
//             try {
//                 const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//                 mediaRecorder = new MediaRecorder(stream);
                
//                 mediaRecorder.ondataavailable = (e) => {
//                     audioChunks.push(e.data);
//                 };
                
//                 mediaRecorder.onstop = () => {
//                     audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
//                     audioChunks = []; 
//                     if (statusText) statusText.innerText = "Voice recorded!";
//                     recordBtn.innerText = "Re-record Voice";
//                     recordBtn.style.backgroundColor = "#4caf50"; 
//                 };
                
//                 mediaRecorder.start();
//                 recordBtn.innerText = "Stop Recording";
//                 recordBtn.style.backgroundColor = "#d32f2f"; 
//                 if (statusText) statusText.innerText = "Listening...";
                
//             } catch (err) {
//                 alert("Microphone access denied or not available.");
//                 console.error(err);
//             }
//         } else if (mediaRecorder.state === 'recording') {
//             mediaRecorder.stop();
//         }
//     });
// }

// // 2. Multimodal Submission Logic
// if (generateBtn) {
//     generateBtn.addEventListener('click', async () => {
//         // Change button state to loading
//         const originalText = generateBtn.innerText;
//         generateBtn.innerText = "Generating...";
//         generateBtn.disabled = true;

//         const formData = new FormData();
        
//         // Append Text
//         if (textInput && textInput.value.trim() !== "") {
//             formData.append("text_data", textInput.value.trim());
//         }
        
//         // Append Voice
//         if (audioBlob) {
//             formData.append("voice_data", audioBlob, "recording.webm");
//         }

//         // Append Google Sheets Toggle (Safely check if it exists)
//         const chkSheets = document.getElementById('chk_sheets') || document.querySelector('input[type="checkbox"]');
//         if (chkSheets) {
//             formData.append("push_to_sheets", chkSheets.checked);
//         } else {
//             formData.append("push_to_sheets", true); // Default to true if checkbox not found
//         }

//         // Send to Backend
//         try {
//             const response = await fetch('/api/generate-fusion', {
//                 method: 'POST',
//                 body: formData
//             });

//             if (!response.ok) {
//                 const errData = await response.json();
//                 alert("Error: " + (errData.error || "Something went wrong"));
//                 generateBtn.innerText = originalText;
//                 generateBtn.disabled = false;
//                 return;
//             }

//             // If successful, the backend returns the HTML for the Verification Screen.
//             // We replace the current page with that new HTML.
//             const html = await response.text();
//             document.open();
//             document.write(html);
//             document.close();

//         } catch (error) {
//             console.error("Network Error:", error);
//             alert("Failed to connect to the server.");
//             generateBtn.innerText = originalText;
//             generateBtn.disabled = false;
//         }
//     });
// }

let mediaRecorder;
let audioChunks = [];
let audioBlob = null;

const recordBtn = document.getElementById('record-btn'); 
const generateBtn = document.getElementById('generate-btn'); 
const textInput = document.getElementById('text-input'); 
const statusText = document.getElementById('status-text'); 

// 1. Voice Recording Logic
if (recordBtn) {
    recordBtn.addEventListener('click', async () => {
        if (!mediaRecorder || mediaRecorder.state === 'inactive') {
            try {
                console.log("Requesting microphone access...");
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.ondataavailable = (e) => {
                    audioChunks.push(e.data);
                };
                
                mediaRecorder.onstop = () => {
                    audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    audioChunks = []; 
                    console.log("Audio successfully captured and stored as Blob.");
                    if (statusText) statusText.innerText = "Voice recorded!";
                    recordBtn.innerText = "Re-record Voice";
                    recordBtn.style.backgroundColor = "#4caf50"; 
                };
                
                mediaRecorder.start();
                console.log("Recording started...");
                recordBtn.innerText = "Stop Recording";
                recordBtn.style.backgroundColor = "#d32f2f"; 
                if (statusText) statusText.innerText = "Listening...";
                
            } catch (err) {
                alert("Microphone access denied or not available.");
                console.error("Microphone Error:", err);
            }
        } else if (mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
    });
}

// 2. Multimodal Submission Logic
if (generateBtn) {
    generateBtn.addEventListener('click', async () => {
        console.log("Generate button clicked. Assembling payload...");
        
        // Change button state to loading
        const originalText = generateBtn.innerText;
        generateBtn.innerText = "Generating...";
        generateBtn.disabled = true;

        const formData = new FormData();
        
        // Append Text
        if (textInput && textInput.value.trim() !== "") {
            formData.append("text_data", textInput.value.trim());
            console.log("Text data attached.");
        }
        
        // Append Voice
        if (audioBlob) {
            formData.append("voice_data", audioBlob, "recording.webm");
            console.log("Voice payload attached.");
        }

        // Append Google Sheets Toggle
        const chkSheets = document.getElementById('chk_sheets') || document.querySelector('input[type="checkbox"]');
        if (chkSheets) {
            formData.append("push_to_sheets", chkSheets.checked);
        } else {
            formData.append("push_to_sheets", true);
        }

        // Send to Backend
        try {
            console.log("Initiating fetch request to relative path: /api/generate-fusion");
            const response = await fetch('/api/generate-fusion', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                console.error("Server responded with HTTP Error:", response.status, errData);
                alert("Error: " + (errData.error || "Something went wrong"));
                generateBtn.innerText = originalText;
                generateBtn.disabled = false;
                return;
            }

            console.log("Success! Backend responded with Verification HTML.");
            const html = await response.text();
            document.open();
            document.write(html);
            document.close();

        } catch (error) {
            // This block ONLY triggers on network/connection drops, not server errors (like 400/500)
            console.error("CRITICAL NETWORK ERROR:", error);
            alert("Failed to connect to the server. Check your internet or ensure the Render server is awake.");
            generateBtn.innerText = originalText;
            generateBtn.disabled = false;
        }
    });
}