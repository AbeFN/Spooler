document.getElementById("createServerButton").addEventListener("click", () => {
    const serverType = document.getElementById("serverType").value;
    const data = {
        vcenter_ip: document.getElementById("vcenterIP").value,
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
        template_name: document.getElementById("templateName").value,
        vm_name: document.getElementById("vmName").value
        // add any additional fields here
    };

    const url = `/api/create_server/${serverType}`;
    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert(data.message);
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => console.error("Error:", error));
});
