const form = document.getElementById('chat-form');
const input = document.getElementById('message-input');
const messages = document.getElementById('messages');
const status = document.getElementById('status');

function addBubble(text, role) {
  const bubble = document.createElement('div');
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;
  messages.appendChild(bubble);
  messages.scrollTop = messages.scrollHeight;
}

async function checkHealth() {
  try {
    const res = await fetch('/health');
    const data = await res.json();
    if (data.ollama) {
      status.textContent = 'Connexion au serveur : en ligne';
      status.className = 'status connected';
    } else {
      status.textContent = 'Connexion au serveur : hors ligne';
      status.className = 'status disconnected';
    }
  } catch (err) {
    status.textContent = 'Connexion au serveur : hors ligne';
    status.className = 'status disconnected';
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  addBubble(text, 'user');
  input.value = '';
  addBubble('Pensée en cours…', 'assistant');

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });

    const data = await res.json();
    messages.lastElementChild.remove();
    addBubble(data.reply || 'Aucune réponse.', 'assistant');
    await checkHealth();
  } catch (err) {
    messages.lastElementChild.remove();
    addBubble('Erreur réseau. Vérifiez le backend.', 'assistant');
  }
});

checkHealth();
addBubble('Bonjour ! Posez une question sur la finance ou l’entreprise.', 'assistant');
