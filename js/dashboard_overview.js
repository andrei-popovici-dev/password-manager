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
                        <button onclick="openEditModal(${acc.id})" 
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