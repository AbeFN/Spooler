document.getElementById('serverForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const serverType = document.getElementById('serverType').value;
    // Specify the full URL with the Flask server's port
    const apiUrl = serverType === 'windows' 
        ? 'http://127.0.0.1:5000/api/create_server/windows' 
        : 'http://127.0.0.1:5000/api/create_server/linux';

    const formData = {
        vcenter_ip: document.getElementById('vcenter_ip').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
        template_name: document.getElementById('template_name').value,
        vm_name: document.getElementById('vm_name').value
    };

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        const result = await response.json();
        alert(result.message);
    } catch (error) {
        alert("Error creating server: " + error.message);
    }
});
