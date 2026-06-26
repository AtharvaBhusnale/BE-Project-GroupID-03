// --- 1. FIREBASE SETUP ---
const firebaseConfig = {
    apiKey: "AIzaSyCTokhR7dFJ9ApPZgv3U--6a4CJAQ7NJRs",
    authDomain: "mri-enhancement.firebaseapp.com",
    projectId: "mri-enhancement",
    storageBucket: "mri-enhancement.firebasestorage.app",
    messagingSenderId: "119965839774",
    appId: "1:119965839774:web:ee8faafb8408b8e71c668f",
    measurementId: "G-2K4D7LDK6Y"
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

// --- 2. GLOBAL VARIABLES ---
let currentUser = null;
let idToken = null;
let userRole = 'patient';
let userName = 'Patient';
let currentDoctorCode = '';

// --- 3. DOM ELEMENT REFERENCES ---
const authView = document.getElementById('auth-view');
const appView = document.getElementById('app-view');
const logoutBtn = document.getElementById('logout-btn');
const authSubmitBtn = document.getElementById('auth-submit-btn');
const authToggleLogin = document.getElementById('auth-toggle-login');
const authToggleSignup = document.getElementById('auth-toggle-signup');
const authEmail = document.getElementById('auth-email');
const authPassword = document.getElementById('auth-password');
const authError = document.getElementById('auth-error');

const patientDashboard = document.getElementById('patient-dashboard');
const doctorDashboard = document.getElementById('doctor-dashboard');

const demoPatientBtn = document.getElementById('demo-login-patient');
const demoDoctorBtn = document.getElementById('demo-login-doctor');

let isLogin = true;

// --- 4. AUTHENTICATION UI LOGIC ---
if (authToggleLogin && authToggleSignup) {
    authToggleLogin.onclick = () => {
        isLogin = true;
        authToggleLogin.classList.add('bg-white', 'shadow-sm', 'text-slate-800', 'font-semibold');
        authToggleLogin.classList.remove('text-slate-500', 'hover:text-slate-700');
        authToggleSignup.classList.remove('bg-white', 'shadow-sm', 'text-slate-800', 'font-semibold');
        authToggleSignup.classList.add('text-slate-500', 'hover:text-slate-700');
        authSubmitBtn.textContent = 'Sign In via Firebase';
        authError.textContent = '';
        const nameCont = document.getElementById('auth-name-container');
        if (nameCont) {
            nameCont.classList.remove('max-h-[120px]', 'opacity-100', 'mb-5');
            nameCont.classList.add('max-h-0', 'opacity-0', 'mb-0');
            // Remove space-y-5 gap artifact when collapsed by forcing margin logic
            nameCont.style.marginBottom = "0px";
        }
    };

    authToggleSignup.onclick = () => {
        isLogin = false;
        authToggleSignup.classList.add('bg-white', 'shadow-sm', 'text-slate-800', 'font-semibold');
        authToggleSignup.classList.remove('text-slate-500', 'hover:text-slate-700');
        authToggleLogin.classList.remove('bg-white', 'shadow-sm', 'text-slate-800', 'font-semibold');
        authToggleLogin.classList.add('text-slate-500', 'hover:text-slate-700');
        authSubmitBtn.textContent = 'Create Account';
        authError.textContent = '';
        const nameCont = document.getElementById('auth-name-container');
        if (nameCont) {
            nameCont.classList.remove('max-h-0', 'opacity-0', 'mb-0', 'hidden');
            nameCont.classList.add('max-h-[120px]', 'opacity-100');
            nameCont.style.marginBottom = ""; // reset inline style
        }
    };
}


if (authSubmitBtn) {
    authSubmitBtn.onclick = async () => {
        const email = authEmail.value;
        const password = authPassword.value;
        const nameInput = document.getElementById('auth-name');
        const nameVal = nameInput ? nameInput.value.trim() : "";
        authError.textContent = '';
        authSubmitBtn.innerHTML = '<span class="loader border-t-white mx-auto w-6 h-6 border-2"></span>';
        try {
            if (isLogin) {
                await auth.signInWithEmailAndPassword(email, password);
            } else {
                if (!nameVal) {
                    throw new Error("Please enter your full name.");
                }
                const userCred = await auth.createUserWithEmailAndPassword(email, password);
                idToken = await userCred.user.getIdToken();
                const res = await fetchWithAuth('/api/set_profile', {
                    method: 'POST',
                    body: JSON.stringify({ name: nameVal }) // Sets the custom profile fields
                });
                if (res.ok) {
                    userName = nameVal;
                    const headerNameEl = document.getElementById('header-user-name');
                    if (headerNameEl) headerNameEl.textContent = userName;
                }
            }
        } catch (error) {
            authError.textContent = error.message;
            authSubmitBtn.textContent = isLogin ? 'Sign In via Firebase' : 'Create Account';
        }
    };
}

if (logoutBtn) {
    logoutBtn.onclick = () => auth.signOut();
}

// --- 5. AUTH STATE LISTENER ---
auth.onAuthStateChanged(async (user) => {
    if (user) {
        currentUser = user;
        try {
            idToken = await user.getIdToken();
            try {
                const profileResponse = await fetchWithAuth(`/api/get_profile?t=${Date.now()}`);
                if (profileResponse.ok) {
                    const profileData = await profileResponse.json();
                    userRole = profileData.role || 'patient';
                    userName = profileData.name || 'Patient';
                } else {
                    throw new Error("Failed to fetch profile");
                }
            } catch (apiError) {
                console.error("Profile fetch error:", apiError);
                userRole = 'patient';
                userName = 'Patient';
            }

            // Update Header Name
            const headerNameEl = document.getElementById('header-user-name');
            const headerRoleEl = document.getElementById('header-user-role');
            const headerInitials = document.getElementById('header-user-initials');

            if (headerNameEl) headerNameEl.textContent = userName;
            if (headerRoleEl) headerRoleEl.textContent = userRole.charAt(0).toUpperCase() + userRole.slice(1);
            if (headerInitials) {
                const initials = userName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
                headerInitials.textContent = initials || 'U';
            }

            authView.classList.add('hidden');
            appView.classList.remove('hidden');

            patientDashboard.classList.add('hidden');
            doctorDashboard.classList.add('hidden');

            if (userRole === 'doctor') {
                doctorDashboard.classList.remove('hidden');
                // Fetch doctor code from DB if possible locally, or via an API update
                const doctorCodeEl = document.getElementById('doctor-id-badge');
                if (doctorCodeEl) doctorCodeEl.textContent = "Code: DOC-123"; // Mocking, we can fetch real later
                document.getElementById('doc-ws-title').textContent = "Dr. " + userName.replace("Dr. ", "");
                initDoctorLog();
            } else {
                patientDashboard.classList.remove('hidden');
                document.getElementById('patient-greeting').textContent = `Welcome back, ${userName}. How can we assist you today?`;
                initChatbot();
                initPatientUpload();
            }
        } catch (e) {
            console.error("Login init error:", e);
            auth.signOut();
        }
    } else {
        currentUser = null;
        idToken = null;
        userRole = 'patient';
        authView.classList.remove('hidden');
        appView.classList.add('hidden');
        if (authSubmitBtn) {
            authSubmitBtn.textContent = isLogin ? 'Sign In via Firebase' : 'Create Account';
        }
    }
});

// --- 6. API CALL HELPER ---
async function fetchWithAuth(url, options = {}) {
    if (!idToken) throw new Error("User not authenticated");
    const headers = {
        ...(options.headers || {}),
        'Authorization': `Bearer ${idToken}`,
    };
    if (options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }
    return fetch(url, { ...options, headers });
}

// Helper to load secure images with the required auth token
async function getSecureImageUrl(url) {
    if (!url) return "";
    try {
        const res = await fetchWithAuth(url);
        if (!res.ok) throw new Error("Load failed");
        const blob = await res.blob();
        return window.URL.createObjectURL(blob);
    } catch (e) {
        console.error("Secure image fetch error:", e);
        return "";
    }
}

// Download PDF securely 
window.downloadReport = async function (logId) {
    try {
        const res = await fetchWithAuth(`/api/download_report/${logId}`);
        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`Server error: ${res.status} ${errText || "Failed to authenticate download"}`);
        }
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `report_${logId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (e) {
        alert("Download error: " + e.message);
    }
}

// --- 7. CHATBOT FUNCTIONALITY ---
function initChatbot() {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    // Reset Chat UI to initial message
    if (chatBox) {
        chatBox.innerHTML = `
        <div class="flex justify-start mb-4">
            <div class="mr-3 mt-1 flex-shrink-0">
                <div class="w-8 h-8 rounded bg-teal-100 flex items-center justify-center text-teal-600">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                </div>
            </div>
            <div class="bg-teal-50 text-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[90%] border border-teal-100 text-sm leading-relaxed shadow-sm">
                Hello! I am your Neurological Symptom Assessor. How are you feeling today? Please describe any symptoms you're experiencing. <br><br>
                <span class="text-teal-700/70 font-medium text-xs">(Disclaimer: Not a medical diagnosis. Type 'stop' to finish.)</span>
            </div>
        </div>
        `;
    }

    // Ping backend to clear session history
    fetchWithAuth('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message: "init" }),
    }).catch(e => console.error("Could not reset chat session:", e));

    function addMessage(message, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `flex mb-4 ${sender === 'user' ? 'justify-end' : 'justify-start'}`;

        let bubbleCss = "";
        if (sender === 'user') {
            bubbleCss = "bg-teal-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-[80%]";
        } else {
            bubbleCss = "bg-teal-50 text-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[90%] border border-teal-100";
            // Add icon for bot
            const iconHtml = `
            <div class="mr-3 mt-1 flex-shrink-0">
                <div class="w-8 h-8 rounded bg-teal-100 flex items-center justify-center text-teal-600">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                </div>
            </div>`;
            messageDiv.innerHTML = iconHtml;
        }

        const span = document.createElement("div");
        span.className = bubbleCss;

        if (sender === 'bot') {
            const pre = document.createElement("p");
            pre.innerHTML = message.replace(/\n/g, "<br>");
            pre.className = "text-sm leading-relaxed";
            span.appendChild(pre);
            messageDiv.appendChild(span);
        } else {
            span.textContent = message;
            messageDiv.appendChild(span);
        }

        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function handleChat() {
        const message = userInput.value.trim();
        if (!message) return;
        addMessage(message, 'user');
        userInput.value = "";

        // Typing indicator
        const typingId = "typing-" + Date.now();
        const typingDiv = document.createElement("div");
        typingDiv.id = typingId;
        typingDiv.className = "flex justify-start mb-4 text-slate-400 text-sm ml-11";
        typingDiv.textContent = "Neurolumen is typing...";
        chatBox.appendChild(typingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetchWithAuth('/api/chat', {
                method: 'POST',
                body: JSON.stringify({ message: message }),
            });
            const data = await response.json();
            document.getElementById(typingId).remove();

            if (data.error) throw new Error(data.error);
            addMessage(data.reply, 'bot');
        } catch (error) {
            document.getElementById(typingId).remove();
            addMessage(`Error: ${error.message}`, 'bot');
        }
    }

    if (sendBtn && userInput) {
        // Clear old ones to prevent duplicates upon re-init
        sendBtn.onclick = handleChat;
        userInput.onkeypress = (e) => { if (e.key === "Enter") handleChat(); };
    }
}

// --- 8. PATIENT UPLOAD FUNCTIONALITY ---
function initPatientUpload() {
    const uploadForm = document.getElementById("upload-form");
    const fileInput = document.getElementById("image-upload");
    const fileArea = document.getElementById("file-drop-area");
    const fileNameDisplay = document.getElementById("file-name");
    const doctorCodeInput = document.getElementById("doctor-code");
    const submitBtnBase = document.getElementById("upload-submit-btn");

    // Custom logic to open file dialog from the custom area
    if (fileArea) {
        fileArea.onclick = () => fileInput.click();
    }

    if (fileInput) {
        fileInput.onchange = () => {
            if (fileInput.files.length > 0) {
                fileNameDisplay.textContent = fileInput.files[0].name;
                fileNameDisplay.classList.remove('text-slate-400');
                fileNameDisplay.classList.add('text-teal-700', 'font-semibold');
            } else {
                fileNameDisplay.textContent = "DICOM, PNG, JPG (Max 50MB)";
                fileNameDisplay.classList.add('text-slate-400');
                fileNameDisplay.classList.remove('text-teal-700', 'font-semibold');
            }
        };
    }

    if (uploadForm) {
        uploadForm.onsubmit = async (e) => {
            e.preventDefault();
            const file = fileInput.files[0];
            const doctorCode = doctorCodeInput.value.trim();

            if (!file || !doctorCode) {
                alert("Please select a file and enter a doctor's code.");
                return;
            }

            // Change button state
            const originalBtnHtml = submitBtnBase.innerHTML;
            submitBtnBase.innerHTML = '<span class="loader border-t-white mx-auto w-5 h-5 border-2 inline-block align-middle mr-2"></span> Transmitting...';
            submitBtnBase.disabled = true;
            submitBtnBase.classList.add('opacity-75');

            const formData = new FormData();
            formData.append('image', file);
            formData.append('doctorCode', doctorCode);
            // We use the global userName populated during auth check
            formData.append('patientName', userName);

            try {
                const response = await fetchWithAuth('/api/upload_image', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.error) throw new Error(data.error);

                // Show success
                submitBtnBase.innerHTML = '<svg class="w-5 h-5 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg> Transmitted Successfully';
                submitBtnBase.classList.remove('bg-teal-500', 'hover:bg-teal-600');
                submitBtnBase.classList.add('bg-green-600');

                setTimeout(() => {
                    uploadForm.reset();
                    fileNameDisplay.textContent = "DICOM, PNG, JPG (Max 50MB)";
                    fileNameDisplay.classList.add('text-slate-400');
                    fileNameDisplay.classList.remove('text-teal-700', 'font-semibold');
                    submitBtnBase.innerHTML = originalBtnHtml;
                    submitBtnBase.disabled = false;
                    submitBtnBase.classList.remove('opacity-75', 'bg-green-600');
                    submitBtnBase.classList.add('bg-teal-500', 'hover:bg-teal-600');
                }, 3000);

            } catch (error) {
                alert("Upload failed: " + error.message);
                submitBtnBase.innerHTML = originalBtnHtml;
                submitBtnBase.disabled = false;
                submitBtnBase.classList.remove('opacity-75');
            }
        };
    }
}

async function deleteMyData() {
    if (!confirm("Are you sure? This will permanently delete all your MRI scans and conversation history.")) return;

    try {
        const response = await fetchWithAuth('/api/delete_my_data', { method: 'DELETE' });
        const data = await response.json();
        if (data.success) {
            alert("Your account has been permanently deleted.");
            auth.signOut();
            window.location.reload();
        } else {
            alert("Error: " + data.error);
        }
    } catch (e) {
        alert("Server error: " + e.message);
    }
}

// --- 9. DOCTOR LOG FUNCTIONALITY ---
async function initDoctorLog() {
    const container = document.getElementById("log-cards-container");
    const loader = document.getElementById("log-loader");
    const pendingCount = document.getElementById("pending-reviews-count");

    if (!container) return;

    container.innerHTML = "";
    if (loader) loader.classList.remove("hidden");

    try {
        const response = await fetchWithAuth('/api/patient_log');
        const data = await response.json();

        if (loader) loader.classList.add("hidden");

        if (data.error) throw new Error(data.error);

        const logs = data.log || [];
        if (pendingCount) pendingCount.textContent = logs.length;

        if (logs.length === 0) {
            container.innerHTML = `<div class="col-span-1 md:col-span-2 lg:col-span-3 text-center py-12 text-slate-500 bg-white rounded-xl shadow-sm border border-slate-200">No patient scans found assigned to you.</div>`;
            return;
        }

        for (const log of logs) {
            // Check if segmented
            const isSegmented = !!log.segmentedImageUrl;
            const badgeHtml = isSegmented
                ? `<span class="bg-green-500 text-white px-2 py-1 rounded text-xs font-bold shadow-sm absolute top-3 left-3">Analyzed</span>`
                : `<span class="bg-teal-200 text-teal-800 px-2 py-1 rounded text-xs font-bold shadow-sm absolute top-3 left-3">New Scan</span>`;

            const btnHtml = isSegmented
                ? `<button onclick="window.downloadReport('${log.id}')" class="flex-1 bg-white border border-slate-200 text-slate-700 font-medium py-2 px-4 rounded-lg hover:bg-slate-50 transition-colors flex items-center justify-center text-sm shadow-sm"><svg class="w-4 h-4 mr-2 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg> Report PDF</button>`
                : `<button onclick="segmentImage('${log.id}')" class="flex-1 bg-teal-600 text-white font-medium py-2 px-4 rounded-lg hover:bg-teal-700 transition-colors flex items-center justify-center text-sm shadow-sm"><svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg> Run Segmentation</button>`;

            // Format time nicely
            const ts = new Date(log.timestamp);
            const timeStr = ts.toLocaleDateString() + ' ' + ts.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            let fullSymp = log.symptomSummary || "No symptoms discussed.";
            // We use whitespace-pre-wrap in CSS so we don't necessarily need to replace \n with <br>, but it's safer just in case.
            fullSymp = fullSymp.replace(/\n/g, '<br>');

            // Resolve securely
            const displayUrl = log.enhancedImageUrl || log.originalImageUrl;
            const secureUrl = await getSecureImageUrl(displayUrl);

            const card = document.createElement('div');
            card.className = "bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden flex flex-col";
            card.innerHTML = `
                <div class="relative h-64 bg-slate-900 overflow-hidden cursor-pointer" onclick="openCompareModal('${log.originalImageUrl}', '${log.enhancedImageUrl}', '${log.segmentedImageUrl || ''}')">
                    <img src="${secureUrl}" class="w-full h-full object-cover opacity-90 hover:opacity-100 transition duration-300" alt="MRI Scan">
                    ${badgeHtml}
                </div>
                <div class="p-5 flex-1 flex flex-col">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="font-bold text-lg text-slate-800">${log.patientName || 'Unknown Patient'}</h3>
                        <span class="text-xs font-medium text-slate-400 mt-1">${timeStr}</span>
                    </div>
                    <div class="text-sm text-slate-500 mb-4 flex-1">
                        <details class="group">
                            <summary class="font-semibold text-teal-600 cursor-pointer hover:text-teal-700 list-none flex items-center text-xs uppercase tracking-wider">
                                <span class="mr-1">View Symptom Summary</span>
                                <svg class="w-4 h-4 transform group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                            </summary>
                            <div class="mt-2 text-xs leading-relaxed bg-slate-50/80 p-3 rounded-xl border border-slate-100 max-h-40 overflow-y-auto shadow-inner text-slate-600">
                                ${fullSymp}
                            </div>
                        </details>
                    </div>
                    <div class="flex items-center space-x-3 mt-auto">
                        ${btnHtml}
                        <button onclick="deletePatientLog('${log.id}')" class="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors border border-transparent hover:border-red-100" title="Delete record">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </button>
                    </div>
                </div>
            `;
            container.appendChild(card);
        }

    } catch (error) {
        if (loader) loader.classList.add("hidden");
        container.innerHTML = `<div class="text-red-500 p-4">Error loading patients: ${error.message}</div>`;
    }
}

async function segmentImage(logId) {
    if (!confirm("Run AI Segmentation on this advanced scan?")) return;
    try {
        const response = await fetchWithAuth('/api/segment_image', {
            method: 'POST',
            body: JSON.stringify({ log_id: logId })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);

        // Refresh to show "Report PDF"
        initDoctorLog();
    } catch (e) {
        alert("Segmentation error: " + e.message);
    }
}

async function deletePatientLog(logId) {
    if (!confirm("Delete this patient record permanently?")) return;
    try {
        const response = await fetchWithAuth(`/api/delete_log/${logId}`, { method: 'DELETE' });
        const data = await response.json();
        if (data.success) {
            initDoctorLog();
        } else {
            alert("Error: " + data.error);
        }
    } catch (e) {
        alert("Server error: " + e.message);
    }
}

// Global modal helpers
window.openCompareModal = async function (origUrl, enhUrl, segUrl = '') {
    // Basic modal opening logic handled inside index.html for simplicity 
    // to avoid token limits. We export it to window object if needed.
    // In our new UI we will just implement it locally.
    const modal = document.getElementById('compare-modal');
    if (!modal) return;

    // Auth-resolve URLs securely to bypass 401 Unauthorized
    const sOrig = await getSecureImageUrl(origUrl);
    const sEnh = await getSecureImageUrl(enhUrl);

    let sSeg = '';
    if (segUrl && segUrl !== 'undefined' && segUrl !== 'null') {
        sSeg = await getSecureImageUrl(segUrl);
    }

    const segImgEl = document.getElementById('side-img-seg');
    const tabEnh = document.getElementById('tab-enhancement');
    const tabSeg = document.getElementById('tab-segmentation');
    const viewEnh = document.getElementById('view-enhancement');
    const viewSeg = document.getElementById('view-segmentation');

    const setTab = (isEnh) => {
        if (!tabEnh || !tabSeg || !viewEnh || !viewSeg) return;
        if (isEnh) {
            tabEnh.classList.add('text-teal-600', 'border-teal-600');
            tabEnh.classList.remove('text-slate-400', 'border-transparent');
            tabSeg.classList.remove('text-teal-600', 'border-teal-600');
            tabSeg.classList.add('text-slate-400', 'border-transparent');
            viewEnh.classList.remove('hidden');
            viewEnh.classList.add('flex');
            viewSeg.classList.add('hidden');
            viewSeg.classList.remove('flex');
        } else {
            tabSeg.classList.add('text-teal-600', 'border-teal-600');
            tabSeg.classList.remove('text-slate-400', 'border-transparent');
            tabEnh.classList.remove('text-teal-600', 'border-teal-600');
            tabEnh.classList.add('text-slate-400', 'border-transparent');
            viewSeg.classList.remove('hidden');
            viewSeg.classList.add('flex');
            viewEnh.classList.add('hidden');
            viewEnh.classList.remove('flex');
        }
    };

    if (tabEnh && tabSeg) {
        tabEnh.onclick = () => setTab(true);
        tabSeg.onclick = () => setTab(false);
    }

    if (segImgEl && tabSeg) {
        if (sSeg) {
            segImgEl.src = sSeg;
            tabSeg.classList.remove('hidden');
        } else {
            segImgEl.src = '';
            tabSeg.classList.add('hidden');
        }
    }

    setTab(true);

    // Slider logic
    const container = document.getElementById('img-comp-container');
    container.innerHTML = '';

    const divAfter = document.createElement('div');
    divAfter.className = 'img-comp-img';
    const iAfter = document.createElement('img');
    iAfter.src = sEnh;
    divAfter.appendChild(iAfter);

    const divBefore = document.createElement('div');
    divBefore.className = 'img-comp-img img-comp-overlay';
    const iBefore = document.createElement('img');
    iBefore.src = sOrig;
    divBefore.appendChild(iBefore);

    container.appendChild(divAfter);
    container.appendChild(divBefore);

    modal.classList.remove('hidden');

    const startComparison = () => {
        container.style.width = iAfter.offsetWidth + "px";
        compareImages(divBefore);
    };

    if (iAfter.complete) startComparison();
    else iAfter.onload = startComparison;
}

window.closeCompareModal = function () {
    const modal = document.getElementById('compare-modal');
    if (modal) modal.classList.add('hidden');
}

function compareImages(img) {
    let slider, clicked = 0, w, h;
    w = img.offsetWidth;
    h = img.offsetHeight;
    img.style.width = (w / 2) + "px";

    slider = document.createElement("DIV");
    slider.setAttribute("class", "img-comp-slider");
    img.parentElement.insertBefore(slider, img);

    slider.style.top = (h / 2) - (slider.offsetHeight / 2) + "px";
    slider.style.left = (w / 2) - (slider.offsetWidth / 2) + "px";

    slider.addEventListener("mousedown", slideReady);
    window.addEventListener("mouseup", slideFinish);
    slider.addEventListener("touchstart", slideReady);
    window.addEventListener("touchend", slideFinish);

    function slideReady(e) {
        e.preventDefault();
        clicked = 1;
        window.addEventListener("mousemove", slideMove);
        window.addEventListener("touchmove", slideMove);
    }
    function slideFinish() {
        clicked = 0;
        window.removeEventListener("mousemove", slideMove);
        window.removeEventListener("touchmove", slideMove);
    }
    function slideMove(e) {
        if (clicked === 0) return;
        let pos = getCursorPos(e);
        if (pos < 0) pos = 0;
        if (pos > w) pos = w;
        img.style.width = pos + "px";
        slider.style.left = img.offsetWidth - (slider.offsetWidth / 2) + "px";
    }
    function getCursorPos(e) {
        e = (e.changedTouches) ? e.changedTouches[0] : e;
        let a = img.getBoundingClientRect();
        let x = e.pageX - a.left - window.pageXOffset;
        return x;
    }
}
