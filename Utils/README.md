# Password Manager
Descrierea aplicatiei: aplicatia este un password manager care stocheaza sub un singur utilizator mai multe conturi ale utilizatorului. Practic o persoana va trebui sa retina doar o singura parola pentru a avea acces la toate parolele sale. Aplicatia include si un analizator de parole care analizeaza parolele stocate si cere utilizatorului sa le modifice astfel incat acestea sa fie mai puternice, dar si un generator de parole care creeaza parole din diferite caractere si de diferite marimi.

Link github: https://github.com/andrei-popovici-dev/password-manager/

Implementarea folosete:

1. BackApp.py care se ocupa de logica in sine;

2. crypto.py care se ocupa cu criptarea/decriptarea parolelor;

3. data.json in care stocam toate datele despre useri: numele si parola(criptate, parola pentru cont nu trebuie afisata niciodata, doar testata, in schimb parolele pentru diversele conturi ale userului trebuie afisate deci trebuie decriptate), si credentialele pentru diverse website-uri, care la randul lor vor retine: numele site-ului/ contului, user/mail/numar de telefon si parola.

4. Main.py care reprezinta un API expus de BackApp.py catre frontend, dar si punctul de start al aplicatiei.

5. Frontend-ul alcatuit din:
   - index.html - fisierul principal care incarca toate datele din celalalte fisiere ale frontend-ului;
   - views - director care contine alte fisiere html ale frontend-ului : login.html - contine interfata de login in cont ;dashboard.html - contine dashboard-ul(vizualizare parole slabe, vizualizare tabela de parole, generare de parole);
   - js - fisierele javascript responsabile pentru logica intre Main.py si frontend, cat si unele functionalitati

Utilizare: Aplicatia va fi rulata din Main.py

Calin Gabriel-Stefan : a implementat criptarea parolelor, stocarea datelor despre utilizatori

Popovici Andrei-Razvan : a implementat frontend-ul si bridge-ul dintre frontend si backend (Main.py)