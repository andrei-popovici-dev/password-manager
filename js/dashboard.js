function initDashboard() {

    if (window.lucide) {
        lucide.createIcons();
    } else {
        console.warn("Lucide library not loaded");
    }

    switchTab('overview');
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