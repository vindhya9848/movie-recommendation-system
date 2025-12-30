const messages = document.getElementById("messages");
const recs = document.getElementById("recs");
const input = document.getElementById("input");
const send = document.getElementById("send");

function addMessage(role, text){
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  wrap.appendChild(bubble);
  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
}

function setLoading(isLoading){
  send.disabled = isLoading;
  input.disabled = isLoading;
  if(isLoading){
    addMessage("bot", "Thinking…");
    const last = messages.lastElementChild.querySelector(".bubble");
    last.innerHTML = `<span class="loader"></span>Thinking…`;
  }
}

function renderRecs(items){
  if(!items || items.length === 0){
    recs.classList.add("empty");
    recs.innerHTML = `<div class="empty-state">No recommendations yet.</div>`;
    return;
  }
  recs.classList.remove("empty");
  recs.innerHTML = "";

  items.slice(0,5).forEach((m, idx) => {
    const card = document.createElement("div");
    card.className = "card";

    const score = (m.final_score ?? m.similarity_score ?? 0).toFixed(3);
    const genres = (m.genres || "").split("|").filter(Boolean).join(", ");
    const lang = (m.language || "").toString();
    const runtime = (m.runtime != null) ? `${m.runtime} mins` : "runtime N/A";
    const year = (m.release_year != null) ? `${m.release_year}` : "";

    card.innerHTML = `
      <div class="row">
        <div>
          <div class="title">${idx+1}. ${m.title || "Untitled"}</div>
          <div class="meta">
            ${genres ? `Genres: ${genres}<br/>` : ""}
            ${lang ? `Language: ${lang}<br/>` : ""}
            ${runtime}${year ? ` • ${year}` : ""}
          </div>
        </div>
        <div class="badge">Score ${score}</div>
      </div>
      <div class="score">
        ${m.vote_average != null ? `<span class="pill">⭐ ${Number(m.vote_average).toFixed(1)}</span>` : ""}
        ${m.vote_count != null ? `<span class="pill">${m.vote_count} votes</span>` : ""}
        ${m.similarity_score != null ? `<span class="pill">sim ${Number(m.similarity_score).toFixed(3)}</span>` : ""}
      </div>
    `;
    recs.appendChild(card);
  });
}

// Ask the first question on page load
// window.addEventListener("load", async () => {
//   try {
//     const res = await fetch("/api/message", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ text: "" })
//     });
//     const data = await res.json();
//     addMessage("bot", data.reply);
//   } catch (e) {
//     console.error("Failed to load first question", e);
//   }
// });

async function sendMessage(){
  const text = input.value.trim();
  if(!text) return;

  addMessage("user", text);
  input.value = "";

  setLoading(true);

  try{
    const res = await fetch("/api/message", {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ text })
    });

    const data = await res.json();

    // Replace the “Thinking…” bubble with actual bot response
    const lastBot = messages.lastElementChild;
    if(lastBot && lastBot.classList.contains("bot")){
      lastBot.querySelector(".bubble").textContent = data.reply;
    } else {
      addMessage("bot", data.reply);
    }

    renderRecs(data.recommendations);
  } catch(e){
    addMessage("bot", "Something went wrong calling the server.");
  } finally {
    send.disabled = false;
    input.disabled = false;
    input.focus();
  }
}

send.addEventListener("click", sendMessage);
input.addEventListener("keydown", (e) => {
  if(e.key === "Enter") sendMessage();
});
