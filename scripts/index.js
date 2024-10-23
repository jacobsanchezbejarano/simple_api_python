document.getElementById('userForm').addEventListener('submit', function(e) {
    e.preventDefault();  // Evita que el formulario se envíe de manera tradicional

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;

    const userData = {
        name: name,
        email: email
    };

    fetch('http://localhost:8000/users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            document.getElementById('message').textContent = data.message;
            document.getElementById('message').classList.remove('error');
            document.getElementById('message').classList.add('message');
        }
    })
    .catch(error => {
        document.getElementById('message').textContent = 'Error: ' + error;
        document.getElementById('message').classList.add('error');
    });
});

async function fetchUsers() {
        try {
            const response = await fetch('http://localhost:8000/users', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const users = await response.json();
            const tableBody = document.getElementById('userTable').getElementsByTagName('tbody')[0];

            // Limpiar el contenido previo
            tableBody.innerHTML = '';

            // Insertar los registros en la tabla
            users.forEach(user => {
                const row = tableBody.insertRow();
                row.insertCell(0).innerText = user.id;
                row.insertCell(1).innerText = user.name;
                row.insertCell(2).innerText = user.email;
            });
        } catch (error) {
            console.error('Error fetching users:', error);
        }
    }

    // Llamar a la función para obtener usuarios al cargar la página
    window.onload = fetchUsers;