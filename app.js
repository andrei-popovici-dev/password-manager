let isRegisterMode = false;

function toggleAuthMode() {
    isRegisterMode = !isRegisterMode;

    const title = document.getElementById('card-title');
    const mainBtn = document.getElementById('main-btn');
    const expandable = document.getElementById('expandable-section');
    const toggleText = document.getElementById('toggle-text');
    const toggleBtnLabel = document.getElementById('toggle-btn-label');
    const msg = document.getElementById('auth-msg');

    const inputs = document.querySelectorAll('input');

    msg.innerText = '';

    if (isRegisterMode) {
        expandable.classList.remove('grid-rows-[0fr]');
        expandable.classList.add('grid-rows-[1fr]');

        title.innerText = "Sign in";
        mainBtn.innerText = "Sign in";
        toggleText.innerText = "Already have an account";
        toggleBtnLabel.innerText = "Login";

        mainBtn.classList.replace('bg-blue-600', 'bg-green-600');
        mainBtn.classList.replace('hover:bg-blue-700', 'hover:bg-green-700');

        inputs.forEach(inp => {
            inp.classList.replace('focus:ring-blue-500', 'focus:ring-green-500');
        });

    } else {
        expandable.classList.remove('grid-rows-[1fr]');
        expandable.classList.add('grid-rows-[0fr]');

        title.innerText = "Login";
        mainBtn.innerText = "Login";
        toggleText.innerText = "Don't have an account?";
        toggleBtnLabel.innerText = "Sign in";

        mainBtn.classList.replace('bg-green-600', 'bg-blue-600');
        mainBtn.classList.replace('hover:bg-green-700', 'hover:bg-blue-700');

        inputs.forEach(inp => {
            inp.classList.replace('focus:ring-green-500', 'focus:ring-blue-500');
        });
    }
}

async function handleAuthAction() {
    const user = document.getElementById('auth-user').value;
    const pass = document.getElementById('auth-pass').value;
    const msgLabel = document.getElementById('auth-msg');

    if (!user || !pass) {
        msgLabel.innerText = "Please fill in the blanks.";
        return;
    }

    let success = false;
    let message = "";

    if (isRegisterMode) {
        const passRepeat = document.getElementById('auth-pass-repeat').value;
        if (pass !== passRepeat) {
            msgLabel.innerText = "Passwords don't match!";
            return;
        }
        const regResponse = await window.pywebview.api.register(user, pass);
        if (regResponse.status === 'success') {
            const logResponse = await window.pywebview.api.login(user, pass);
            if (logResponse.status === 'success') {
                success = true;
            } else {
                message = logResponse.message;
            }
        } else {
            message = regResponse.message;
        }
    } else {
        const response = await window.pywebview.api.login(user, pass);
        if (response.status === 'success') {
            success = true;
        } else {
            message = response.message;
        }
    }

    if (success) {
        document.getElementById('auth-content').classList.add('opacity-0');

        setTimeout(() => {
            const card = document.getElementById('auth-card');
            const container = document.getElementById('auth-container');

            container.classList.remove('p-4');

            card.classList.remove('w-96', 'rounded-xl', 'shadow-2xl');
            card.classList.add('w-full', 'h-full', 'rounded-none');
        }, 200);

        setTimeout(() => {
            document.getElementById('auth-container').classList.add('hidden');

            const dash = document.getElementById('dashboard-content');
            dash.classList.remove('hidden');

            setTimeout(() => {
                dash.classList.remove('opacity-0');
            }, 50);

            dash.classList.add('flex');
            loadCredentials();
        }, 750);

    } else {
        msgLabel.innerText = message;
        msgLabel.className = "mt-4 text-center text-red-500 text-sm font-medium";
    }
}

async function loadCredentials() {
    const list = await window.pywebview.api.get_user_credentials();
    const tbody = document.getElementById('cred-list');
    tbody.innerHTML = '';

    list.forEach(item => {
        const row = `
                    <tr class="hover:bg-gray-50">
                        <td class="p-4 font-medium text-gray-900">${item.website}</td>
                        <td class="p-4 text-gray-500">${item.login}</td>
                        <td class="p-4">
                            <button onclick="revealPass(${item.id}, this)" class="text-blue-600 hover:text-blue-800 text-sm font-semibold">
                                Vezi Parola
                            </button>
                        </td>
                    </tr>
                `;
        tbody.innerHTML += row;
    });
}

async function addCred() {
    const site = document.getElementById('new-site').value;
    const login = document.getElementById('new-login').value;
    const pass = document.getElementById('new-pass').value;

    await window.pywebview.api.add_new_credential(site, login, pass);

    document.getElementById('new-site').value = '';
    document.getElementById('new-login').value = '';
    document.getElementById('new-pass').value = '';
    loadCredentials();
}

async function revealPass(id, btnElement) {
    const password = await window.pywebview.api.reveal_password(id);
    btnElement.parentElement.innerHTML = `<span class="font-mono bg-gray-100 px-2 py-1 rounded select-all">${password}</span>`;
}

function logout() {
    const dash = document.getElementById('dashboard-content');
    const authContainer = document.getElementById('auth-container');
    const card = document.getElementById('auth-card');
    const authContent = document.getElementById('auth-content');

    dash.classList.add('opacity-0');

    setTimeout(() => {
        dash.classList.add('hidden');
        dash.classList.remove('flex');
        authContainer.classList.remove('hidden');

        card.classList.remove('w-96', 'rounded-xl', 'shadow-2xl');
        card.classList.add('w-full', 'h-full', 'rounded-none');
        authContainer.classList.remove('p-4');

        setTimeout(() => {
            card.classList.add('w-96', 'rounded-xl', 'shadow-2xl');
            card.classList.remove('w-full', 'h-full', 'rounded-none');
            authContainer.classList.add('p-4');

            document.getElementById('auth-user').value = '';
            document.getElementById('auth-pass').value = '';
            document.getElementById('auth-pass-repeat').value = '';
            authContent.classList.remove('opacity-0');
        }, 50);

    }, 300)

}

function initDashboard() {

    if (window.lucide) {
        lucide.createIcons();
    } else {
        console.warn("Lucide library not loaded");
    }

    switchTab('overview');
}

// ---------------- DASHBOARD UI LOGIC ----------------

function switchTab(tabId) {

    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));

    const target = document.getElementById('view-' + tabId);
    if (target) target.classList.remove('hidden');

    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.remove('bg-indigo-600', 'text-white', 'shadow-lg');
        btn.classList.add('text-slate-400', 'hover:bg-slate-800', 'hover:text-white');
    });

    const activeBtn = document.getElementById('nav-' + tabId);
    if (activeBtn) {
        activeBtn.classList.remove('text-slate-400', 'hover:bg-slate-800');
        activeBtn.classList.add('bg-indigo-600', 'text-white', 'shadow-lg');
    }

    const titleEl = document.getElementById('header-title');
    if (titleEl) titleEl.innerText = tabId.charAt(0).toUpperCase() + tabId.slice(1);

    if (window.innerWidth < 1024) {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar.classList.contains('-translate-x-full')) {
            toggleMobileSidebar();
        }
    }
}

let isSidebarCollapsed = false;
function toggleDesktopSidebar() {
    const sidebar = document.getElementById('sidebar');
    const texts = document.querySelectorAll('.sidebar-text');
    const icon = document.getElementById('sidebar-toggle-icon');

    isSidebarCollapsed = !isSidebarCollapsed;

    if (isSidebarCollapsed) {
        sidebar.classList.replace('w-64', 'w-20');
        texts.forEach(t => t.classList.add('opacity-0', 'hidden'));
        icon.style.transform = 'rotate(180deg)';
    } else {
        sidebar.classList.replace('w-20', 'w-64');
        texts.forEach(t => t.classList.remove('opacity-0', 'hidden'));
        icon.style.transform = 'rotate(0deg)';
    }
}

function toggleMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const isClosed = sidebar.classList.contains('-translate-x-full');

    if (isClosed) {
        sidebar.classList.remove('-translate-x-full');
        overlay.classList.remove('hidden');
        setTimeout(() => overlay.classList.remove('opacity-0'), 10);
    } else {
        sidebar.classList.add('-translate-x-full');
        overlay.classList.add('opacity-0');
        setTimeout(() => overlay.classList.add('hidden'), 300);
    }
}