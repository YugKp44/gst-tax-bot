const body = document.getElementById("chat-body");
const input = document.getElementById("question-input");
const btn = document.getElementById("send-btn");
// NEW: Get the placeholder element
const placeholder = document.getElementById("chat-placeholder");

// Helper: render a bubble
function renderBubble(role, htmlContent) {
    const div = document.createElement("div");
    div.className = `bubble ${role}`;
    div.innerHTML = htmlContent;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
}

// Helper: render sources
function renderSources(sources) {
    if (!sources || !sources.length) return;
    const label = document.createElement("div");
    label.className = "source-label";
    label.textContent = "Sources:";
    body.appendChild(label);

    const container = document.createElement("div");
    container.className = "sources";
    sources.forEach(s => {
        const span = document.createElement("div");
        span.className = "source";
        span.textContent = s;
        container.appendChild(span);
    });
    body.appendChild(container);
    body.scrollTop = body.scrollHeight;
}

// Show typing animation
function showTyping() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "typing";
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement("div");
        dot.className = "typing-dot";
        typingDiv.appendChild(dot);
    }
    body.appendChild(typingDiv);
    body.scrollTop = body.scrollHeight;
    return typingDiv;
}

// Process raw answer into HTML with bullet lists
function formatAnswer(raw) {
    const lines = raw.split("\n");
    let html = "";
    let inList = false;

    lines.forEach(line => {
        if (line.trim().startsWith("-")) {
            if (!inList) {
                inList = true;
                html += "<ul>";
            }
            html += `<li>${line.replace(/^-+\s*/, "")}</li>`;
        } else {
            if (inList) {
                html += "</ul>";
                inList = false;
            }
            if (line.trim()) { // Avoid creating empty <p> tags
                html += `<p>${line}</p>`;
            }
        }
    });
    if (inList) html += "</ul>";
    return html;
}

// Send handler (called by button or Enter key)
async function send() {
    const q = input.value.trim();
    if (!q) return;

    // NEW: Hide the placeholder if it's visible
    if (placeholder) {
        placeholder.style.display = "none";
    }

    // render user bubble
    renderBubble("user", q);
    input.value = "";
    input.focus();

    // show typing
    const typingDiv = showTyping();

    try {
        // call backend
        const resp = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: q })
        });

        if (!resp.ok) {
            throw new Error(`HTTP error! status: ${resp.status}`);
        }

        const { answer, sources } = await resp.json();

        // remove typing
        typingDiv.remove();

        // render bot bubble
        const html = formatAnswer(answer);
        renderBubble("bot", html);

        // render sources
        renderSources(sources);

    } catch (error) {
        // Handle errors gracefully
        typingDiv.remove();
        renderBubble("bot", "Sorry, something went wrong. Please try again.");
        console.error("Error fetching response:", error);
    }
}

// click
btn.onclick = send;
// enter key
input.addEventListener("keydown", e => {
    if (e.key === "Enter") {
        e.preventDefault();
        send();
    }
});
