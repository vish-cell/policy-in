const API = "http://localhost:5000";
const USER_ROLE = "editor"; // Change to "viewer" to test viewer access

// Hide Add button if user is viewer, and bind add function
window.onload = () => {
    if (USER_ROLE === "viewer") {
        document.getElementById("addBtn").style.display = "none";
    } else {
        document.getElementById("addBtn").onclick = addMetadata;
    }

    // Bind search button
    document.getElementById("searchBtn").onclick = searchMetadata;

    // Bind lineage button
    document.getElementById("lineageBtn").onclick = showLineage;
};

// ---------- CRUD ----------

function addMetadata() {
    const data = {
        name: document.getElementById("name").value,
        type: document.getElementById("type").value,
        pii_tags: document.getElementById("pii_tags").value,
        compliance_tags: document.getElementById("compliance_tags").value,
        created_by: document.getElementById("created_by").value
    };

    fetch(`${API}/metadata`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Role": USER_ROLE },
        body: JSON.stringify(data)
    })
    .then(res => {
        if (!res.ok) return res.json().then(err => { throw err });
        return res.json();
    })
    .then(d => {
        alert(d.message);
        // Clear form
        document.getElementById("name").value = "";
        document.getElementById("pii_tags").value = "";
        document.getElementById("compliance_tags").value = "";
        document.getElementById("created_by").value = "";
        searchMetadata(); // Refresh board
    })
    .catch(err => alert("Error: " + (err.error || "Something went wrong")));
}

function searchMetadata() {
    const tag = document.getElementById("search_tag").value.trim();
    const board = document.getElementById("metadata_list");
    board.innerHTML = "";

    if (!tag) return;

    fetch(`${API}/search?tag=${tag}`, { headers: { "Role": USER_ROLE } })
    .then(res => { 
        if (!res.ok) return res.json().then(err => { throw err });
        return res.json();
    })
    .then(data => {
        data.forEach(item => {
            const card = document.createElement("div");
            card.className = "metadata-card";
            card.innerHTML = `
                <strong>${item.name} (${item.type})</strong><br>
                PII: ${item.pii_tags}<br>
                Compliance: ${item.compliance_tags}<br>
                Created By: ${item.created_by}<br>
                ID: ${item.id}
            `;

            // Delete button for editors
            if (USER_ROLE === "editor") {
                const delBtn = document.createElement("button");
                delBtn.textContent = "Delete";
                delBtn.onclick = () => deleteMetadata(item.id);
                card.appendChild(delBtn);
            }

            board.appendChild(card);
        });
    })
    .catch(err => alert("Error: " + (err.error || "Something went wrong")));
}

function deleteMetadata(id) {
    if (!confirm("Are you sure you want to delete this metadata?")) return;

    fetch(`${API}/metadata/${id}`, { method: "DELETE", headers: { "Role": USER_ROLE } })
    .then(res => {
        if (!res.ok) return res.json().then(err => { throw err });
        return res.json();
    })
    .then(d => { alert(d.message); searchMetadata(); })
    .catch(err => alert("Error: " + (err.error || "Something went wrong")));
}

// ---------- Lineage Visualization ----------

function showLineage() {
    fetch(`${API}/lineage`, { headers: { "Role": USER_ROLE } })
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById("lineage_graph");
        container.innerHTML = "";
        const nodes = {};
        data.forEach(n => nodes[n.id] = n);

        function renderNode(id, indent=0) {
            const node = nodes[id];
            const div = document.createElement("div");
            div.className = "node";
            div.style.marginLeft = `${indent * 20}px`;
            div.style.fontWeight = node.type === "policy" ? "bold" : "normal";
            div.style.color = node.type === "reserve_model" ? "green" : "black";
            div.textContent = `${node.name} (${node.type})`;

            // Only add children toggle if node has children
            if (node.children.length > 0) {
                const toggle = document.createElement("button");
                toggle.textContent = "+";
                toggle.style.marginLeft = "5px";
                toggle.onclick = () => {
                    if (toggle.textContent === "+") {
                        node.children.forEach(cid => renderNode(cid, indent+1));
                        toggle.textContent = "-";
                    } else {
                        // collapse children
                        let next = div.nextSibling;
                        while(next && parseInt(next.style.marginLeft) > indent*20){
                            const temp = next;
                            next = next.nextSibling;
                            container.removeChild(temp);
                        }
                        toggle.textContent = "+";
                    }
                };
                div.appendChild(toggle);
            }

            container.appendChild(div);
        }

        // Render all policies as root nodes
        data.filter(n => n.type === "policy").forEach(p => renderNode(p.id));
    })
    .catch(err => alert("Error fetching lineage: " + (err.error || err)));
}
