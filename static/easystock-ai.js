(() => {
  const toggle = document.getElementById('aiToggle');
  const panel = document.getElementById('aiPanel');
  const close = document.getElementById('aiClose');
  const form = document.getElementById('aiForm');
  const input = document.getElementById('aiInput');
  const send = document.getElementById('aiSend');
  const messages = document.getElementById('aiMessages');
  const mode = document.getElementById('aiMode');
  if (!toggle || !panel || !form) return;
  const setOpen = (open) => {
    panel.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    if (open) input.focus(); else toggle.focus();
  };
  toggle.addEventListener('click', () => setOpen(panel.hidden));
  close.addEventListener('click', () => setOpen(false));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !panel.hidden) setOpen(false);
  });
  const addMessage = (message, who) => {
    const bubble = document.createElement('p');
    bubble.className = `ai-bubble ${who === 'user' ? 'ai-user' : 'ai-bot'}`;
    bubble.textContent = message; // Sem innerHTML: respostas não executam código.
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  };
  if (mode) {
    mode.addEventListener('change', () => {
      addMessage(mode.value === 'local' ? 'Modo local selecionado. Consultas sem uso da API.' : 'Modo OpenAI selecionado. É necessário configurar a chave e ter créditos.', 'bot');
    });
  }
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const mensagem = input.value.trim();
    if (!mensagem || send.disabled) return;
    addMessage(mensagem, 'user');
    input.value = '';
    send.disabled = true;
    send.textContent = 'Aguarde...';
    try {
      const resp = await fetch('/api/ai/chat', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        credentials: 'same-origin', body: JSON.stringify({mensagem, modo: mode ? mode.value : "local"})
      });
      const data = await resp.json();
      addMessage(data.resposta || data.erro || 'Não foi possível obter uma resposta.', 'bot');
    } catch (error) {
      addMessage('Falha de conexão. Verifique o servidor e tente novamente.', 'bot');
    } finally {
      send.disabled = false;
      send.textContent = 'Enviar';
      input.focus();
    }
  });
})();
