function updateLengthDisplay() {
    const slider = document.getElementById('pass-length');
    const display = document.getElementById('pass-length-val');
    display.innerText = slider.value;
    generatePassword();
}

function generatePassword() {
    const length = document.getElementById('pass-length').value;
    const useUpper = document.getElementById('opt-uppercase').checked;
    const useNumbers = document.getElementById('opt-numbers').checked;
    const useSymbols = document.getElementById('opt-symbols').checked;

    const charsLower = "abcdefghijklmnopqrstuvwxyz";
    const charsUpper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const charsNum = "0123456789";
    const charsSym = "!@#$%^&*()_+~`|}{[]:;?><,./-=";

    let allowedChars = charsLower;
    if (useUpper) allowedChars += charsUpper;
    if (useNumbers) allowedChars += charsNum;
    if (useSymbols) allowedChars += charsSym;

    let password = "";
    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * allowedChars.length);
        password += allowedChars[randomIndex];
    }

    document.getElementById('generated-password').value = password;

    resetCopyIcon();
}

function copyGeneratedPassword() {
    const passwordBox = document.getElementById('generated-password');
    const password = passwordBox.value;

    navigator.clipboard.writeText(password).then(() => {

        const icon = document.getElementById('copy-icon');
        icon.innerHTML = `<polyline points="20 6 9 17 4 12"></polyline>`;
        icon.parentElement.classList.add('text-green-600');

        setTimeout(() => {
            resetCopyIcon();
        }, 2000);
    });
}

function resetCopyIcon() {
    const icon = document.getElementById('copy-icon');
    if (icon) {

        icon.innerHTML = `<rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path>`;
        icon.parentElement.classList.remove('text-green-600');
    }
}