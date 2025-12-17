function openModal() {
    editingId = null;

    document.getElementById('modal-title').innerText = "Add a new password";
    document.getElementById('modal-save-btn').innerText = "Save";
    document.getElementById('new-site').value = '';
    document.getElementById('new-login').value = '';
    document.getElementById('new-pass').value = '';
    document.getElementById('feedback-message-modal').textContent = '';

    document.getElementById('add-modal').classList.remove('hidden');
}

async function openEditModal(id) {
    editingId = id;

    website = document.getElementById(`website-${id}`).innerText
    login = document.getElementById(`login-${id}`).innerText

    document.getElementById('modal-title').innerText = "Edit password";
    document.getElementById('modal-save-btn').innerText = "Update";

    document.getElementById('new-site').value = website;
    document.getElementById('new-login').value = login;

    const passInput = document.getElementById('new-pass');
    passInput.value = "Loading...";
    document.getElementById('add-modal').classList.remove('hidden');

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

async function handleFormSubmit() {
    const site = document.getElementById('new-site').value;
    const login = document.getElementById('new-login').value;
    const pass = document.getElementById('new-pass').value;
    const messageBox = document.getElementById('feedback-message-modal');

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
            closeModal();
        }, 500);
    } else {
        messageBox.textContent = message;
        messageBox.style.color = "red";
    }
}

function closeModal() {
    document.getElementById('add-modal').classList.add('hidden');
    editingId = null;
}

async function togglePasswordVisibilityInputBox(input_id, icon_id) {

    const input = document.getElementById(input_id);
    const icon = document.getElementById(icon_id);

    const isFetched = input.getAttribute('data-fetched') === 'true';
    const dbId = input.getAttribute('data-id');

    if (!isFetched) {
        icon.style.opacity = "0.5";
        try {

            const numericId = Number(dbId);

            const realPassword = await window.pywebview.api.reveal_password(numericId);

            if (!realPassword || realPassword === "Error") {
                alert("Error: couldn't decrypt password");
                return;
            }

            input.value = realPassword;
            input.setAttribute('data-fetched', 'true');

        } catch (e) {
            console.error("Python error:", e);
            alert("");
            return;
        } finally {
            icon.style.opacity = "1";
        }
    }


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

async function handleDelete(id, btn) {

    const isConfirming = btn.getAttribute('data-confirm') === 'true';

    if (!isConfirming) {

        btn.setAttribute('data-confirm', 'true');

        btn.setAttribute('data-original-class', btn.className);
        btn.className = "p-2 bg-red-600 text-white rounded-full shadow-lg transition duration-300 transform scale-110";

        btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;

        const timeoutId = setTimeout(() => {
            resetDeleteButton(btn);
        }, 3000);

        btn.setAttribute('data-timeout', timeoutId);

    } else {

        clearTimeout(btn.getAttribute('data-timeout'));

        const response = await window.pywebview.api.delete_credential(Number(id));

        if (response[0] === true) {
            loadCredentials();
        } else {
            alert("Delete Error");
            resetDeleteButton(btn);
        }
    }
}

function resetDeleteButton(btn) {

    btn.setAttribute('data-confirm', 'false');

    const originalClass = btn.getAttribute('data-original-class');
    if (originalClass) btn.className = originalClass;

    btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>`;
}

async function loadCredentials() {
    const list = await window.pywebview.api.get_user_credentials();
    const tbody = document.getElementById('cred-list');
    tbody.innerHTML = '';

    list.forEach((item, index) => {
        let website = item.website || item[0];
        let login = item.login || item[1];

        let dbIndex = item.id !== undefined ? item.id : index;

        const row = document.createElement('tr');
        row.className = "hover:bg-slate-50 transition border-b border-slate-100";

        row.innerHTML = `
        <td id="website-${dbIndex}" class="px-6 py-4 font-medium text-slate-900 align-middle">${website}</td>
            
            <td id="login-${dbIndex}" class="px-6 py-4 text-slate-600 align-middle">${login}</td>
            
            <td class="px-6 py-4 align-middle text-center">
                <div class="flex items-center justify-center gap-2">
                    <button onclick="openEditModal(${dbIndex})" class="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition" title="Edit">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
                    </button>

                    <button onclick="handleDelete(${dbIndex}, this)" class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-full transition duration-300" title="Delete">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>
                        </svg>
                    </button>
                </div>
            </td>

            <td class="px-6 py-4 align-middle">
                <div class="relative w-full min-w-[250px]">
                    
                    <input type="password" value="........" readonly 
                        id="pass-input-${index}"
                        data-fetched="false"
                        data-id="${dbIndex}"
                        class="w-full p-2.5 pr-10 border border-gray-300 rounded-lg text-sm text-gray-700 
                               focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm">
                    
                    <button type="button" onclick="togglePasswordVisibility(${index})" tabindex="-1"
                        class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-blue-600 cursor-pointer p-1 rounded-full hover:bg-gray-100 transition-colors">
                        
                        <svg id="eye-icon-${index}" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                        </svg>

                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function togglePasswordVisibility(index) {
    const input = document.getElementById(`pass-input-${index}`);
    const icon = document.getElementById(`eye-icon-${index}`);

    const isFetched = input.getAttribute('data-fetched') === 'true';
    const dbId = input.getAttribute('data-id');

    if (!isFetched) {
        icon.style.opacity = "0.5";
        try {

            const numericId = Number(dbId);

            const realPassword = await window.pywebview.api.reveal_password(numericId);

            if (!realPassword || realPassword === "Error") {
                alert("Error: couldn't decrypt password");
                return;
            }

            input.value = realPassword;
            input.setAttribute('data-fetched', 'true');

        } catch (e) {
            console.error("Python error:", e);
            alert("");
            return;
        } finally {
            icon.style.opacity = "1";
        }
    }


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

async function addCred() {
    const site = document.getElementById('new-site').value;
    const login = document.getElementById('new-login').value;
    const pass = document.getElementById('new-pass').value;
    const messageBox = document.getElementById('feedback-message-passwords');

    let response = await window.pywebview.api.add_new_credential(site, login, pass);

    const success = response[0];
    const error = response[1];

    if (!site || !login || !pass) {
        messageBox.textContent = "Complete all blanks!";
        messageBox.style.color = "red";
        return;
    }

    if (!success) {
        messageBox.textContent = error;
        messageBox.style.color = "red";
        return;
    }

    messageBox.textContent = error;
    messageBox.style.color = "green";
    closeModal()

    document.getElementById('new-site').value = '';
    document.getElementById('new-login').value = '';
    document.getElementById('new-pass').value = '';
    loadCredentials();
}

async function revealPass(id, btnElement) {
    const password = await window.pywebview.api.reveal_password(id);
    btnElement.parentElement.innerHTML = `<span class="font-mono bg-gray-100 px-2 py-1 rounded select-all">${password}</span>`;
}

function toggleModalPasswordVisibility() {
    const input = document.getElementById('new-pass');
    const icon = document.getElementById('eye-icon-pass');

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