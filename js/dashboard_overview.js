async function checkWeakPasswords() {
    const resultsContainer = document.getElementById('security-results');
    const cleanContainer = document.getElementById('security-clean');
    const listBody = document.getElementById('weak-list');
    const countSpan = document.getElementById('weak-count');

    resultsContainer.classList.add('hidden');
    cleanContainer.classList.add('hidden');
    listBody.innerHTML = '<tr class="animate-pulse"><td colspan="3" class="p-4 text-center text-slate-400">Scanning...</td></tr>';
    resultsContainer.classList.remove('hidden');

    try {
        const weakAccounts = await window.pywebview.api.verify_weak_passwords();

        listBody.innerHTML = '';

        if (weakAccounts.length > 0) {
            countSpan.innerText = weakAccounts.length;
            resultsContainer.classList.remove('hidden');
            cleanContainer.classList.add('hidden');

            weakAccounts.forEach(acc => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="px-4 py-3 font-medium text-slate-800">${acc.website}</td>
                    <td class="px-4 py-3 text-slate-500">${acc.login}</td>
                    <td class="px-4 py-3 text-right">
                        <button onclick="openEditModalOverview(${acc.id})" 
                            class="text-indigo-600 hover:text-indigo-800 text-xs font-bold border border-indigo-100 bg-indigo-50 px-2 py-1 rounded">
                            Fix
                        </button>
                    </td>
                `;
                listBody.appendChild(row);
            });
        } else {
            resultsContainer.classList.add('hidden');
            cleanContainer.classList.remove('hidden');
        }

        if (window.lucide) lucide.createIcons();

    } catch (error) {
        listBody.innerHTML = `<tr><td colspan="3" class="p-4 text-center text-red-500">Error scanning passwords.</td></tr>`;
    }
}



async function handleFormSubmitOverview() {
    const site = document.getElementById('new-site-overview').value;
    const login = document.getElementById('new-login-overview').value;
    const pass = document.getElementById('new-pass-overview').value;
    const messageBox = document.getElementById('feedback-message-modal-overview');

    if (!site || !login || !pass) {
        messageBox.textContent = "Complete all fields!";
        messageBox.style.color = "red";
        return;
    }

    messageBox.textContent = "Processing...";
    messageBox.style.color = "blue";

    let success, message;

    if (editingId === null) {
        const response = await window.pywebview.api.add_new_credential(site, login, pass);
        success = response[0];
        message = response[1];
    } else {

        const response = await window.pywebview.api.update_credential(editingId, site, login, pass);
        success = response[0];
        message = response[1];
    }

    if (success) {
        messageBox.textContent = message;
        messageBox.style.color = "green";

        loadCredentials();
        setTimeout(() => {
            closeModalOverview();
        }, 500);
    } else {
        messageBox.textContent = message;
        messageBox.style.color = "red";
    }
}

async function toggleModalPasswordVisibilityOverview(index) {
    const input = document.getElementById('new-pass-overview');
    const icon = document.getElementById('eye-icon-pass-overview');

    if (!input || !icon) return;

    if (input.type === "password") {
        input.type = "text";
        icon.style.stroke = "#2563eb";

        icon.innerHTML = `<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"></path><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"></path><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7c.44 0 .87-.03 1.28-.09"></path><line x1="2" y1="2" x2="22" y2="22"></line>`;
    } else {
        input.type = "password";
        icon.style.stroke = "currentColor";

        icon.innerHTML = `<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle>`;
    }
}

function closeModalOverview() {
    document.getElementById('add-modal-overview').classList.add('hidden');
    editingId = null;
}

async function openEditModalOverview(id) {
    editingId = id;

    website = document.getElementById(`website-${id}`).innerText
    login = document.getElementById(`login-${id}`).innerText

    document.getElementById('modal-title-overview').innerText = "Edit password";
    document.getElementById('modal-save-btn-overview').innerText = "Update";

    document.getElementById('new-site-overview').value = website;
    document.getElementById('new-login-overview').value = login;

    const passInput = document.getElementById('new-pass-overview');
    passInput.type = 'password';
    passInput.value = "Loading...";

    const icon = document.getElementById('eye-icon-pass-overview');
    if (icon) {
        icon.style.stroke = "currentColor";
        icon.innerHTML = `<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle>`;
    }
    document.getElementById('add-modal-overview').classList.remove('hidden');

    try {
        const realPass = await window.pywebview.api.reveal_password(Number(id));
        if (realPass !== "Error") {
            passInput.value = realPass;
        } else {
            passInput.value = "";
        }
    } catch (e) {
        passInput.value = "";
    }
}