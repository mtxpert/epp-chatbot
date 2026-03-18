(function() {
  var API_URL = "https://epp-chatbot.onrender.com/chat";
  var history = [];

  // Inject styles
  var style = document.createElement("style");
  style.textContent = `
    #epp-chat-btn {
      position: fixed; bottom: 24px; right: 24px; z-index: 99998;
      width: 60px; height: 60px; border-radius: 50%; border: none;
      background: #1a1a1a; color: #4fc3f7; cursor: pointer;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3); font-size: 28px;
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.2s, background 0.2s;
    }
    #epp-chat-btn:hover { transform: scale(1.1); background: #333; }
    #epp-chat-btn .badge {
      position: absolute; top: -2px; right: -2px; width: 14px; height: 14px;
      background: #4fc3f7; border-radius: 50%; border: 2px solid #1a1a1a;
    }

    #epp-chat-window {
      display: none; position: fixed; bottom: 96px; right: 24px; z-index: 99999;
      width: 380px; max-width: calc(100vw - 48px); height: 500px; max-height: calc(100vh - 120px);
      border-radius: 16px; overflow: hidden; box-shadow: 0 8px 40px rgba(0,0,0,0.35);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      flex-direction: column; background: #1a1a1a;
    }
    #epp-chat-window.open { display: flex; }

    #epp-chat-header {
      background: #1a1a1a; color: #fff; padding: 16px 20px;
      display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #333;
    }
    #epp-chat-header .avatar {
      width: 36px; height: 36px; border-radius: 50%; background: #4fc3f7;
      display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;
    }
    #epp-chat-header .info h4 { margin: 0; font-size: 15px; font-weight: 600; }
    #epp-chat-header .info p { margin: 2px 0 0; font-size: 12px; color: #999; }
    #epp-chat-close {
      margin-left: auto; background: none; border: none; color: #999;
      font-size: 22px; cursor: pointer; padding: 0 4px;
    }
    #epp-chat-close:hover { color: #fff; }

    #epp-chat-messages {
      flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px;
      background: #111;
    }
    #epp-chat-messages::-webkit-scrollbar { width: 6px; }
    #epp-chat-messages::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }

    .epp-msg {
      max-width: 85%; padding: 10px 14px; border-radius: 12px;
      font-size: 14px; line-height: 1.5; word-wrap: break-word;
    }
    .epp-msg a { color: #4fc3f7; text-decoration: underline; }
    .epp-msg.bot {
      background: #222; color: #eee; align-self: flex-start;
      border-bottom-left-radius: 4px;
    }
    .epp-msg.user {
      background: #4fc3f7; color: #000; align-self: flex-end;
      border-bottom-right-radius: 4px; font-weight: 500;
    }
    .epp-msg.typing { color: #888; font-style: italic; }

    #epp-chat-input-area {
      padding: 12px 16px; background: #1a1a1a; border-top: 1px solid #333;
      display: flex; gap: 8px;
    }
    #epp-chat-input {
      flex: 1; padding: 10px 14px; border-radius: 24px; border: 1px solid #333;
      background: #222; color: #fff; font-size: 14px; outline: none;
      font-family: inherit;
    }
    #epp-chat-input::placeholder { color: #666; }
    #epp-chat-input:focus { border-color: #4fc3f7; }
    #epp-chat-send {
      width: 40px; height: 40px; border-radius: 50%; border: none;
      background: #4fc3f7; color: #000; font-size: 18px; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: background 0.2s; flex-shrink: 0;
    }
    #epp-chat-send:hover { background: #81d4fa; }
    #epp-chat-send:disabled { background: #333; color: #666; cursor: default; }

    #epp-chat-footer {
      padding: 6px; text-align: center; font-size: 11px; color: #555; background: #1a1a1a;
    }

    @media (max-width: 480px) {
      #epp-chat-window {
        bottom: 0; right: 0; width: 100%; height: 100%;
        max-width: 100%; max-height: 100%; border-radius: 0;
      }
      #epp-chat-btn { bottom: 16px; right: 16px; width: 52px; height: 52px; font-size: 24px; }
    }
  `;
  document.head.appendChild(style);

  // Chat button
  var btn = document.createElement("button");
  btn.id = "epp-chat-btn";
  btn.innerHTML = '&#128488;<div class="badge"></div>';
  btn.title = "Chat with us";
  document.body.appendChild(btn);

  // Chat window
  var win = document.createElement("div");
  win.id = "epp-chat-window";
  win.innerHTML = `
    <div id="epp-chat-header">
      <div class="avatar">&#9889;</div>
      <div class="info">
        <h4>EPP Support</h4>
        <p>We typically reply instantly</p>
      </div>
      <button id="epp-chat-close">&times;</button>
    </div>
    <div id="epp-chat-messages"></div>
    <div id="epp-chat-input-area">
      <input id="epp-chat-input" type="text" placeholder="Ask about our products..." maxlength="1000" autocomplete="off">
      <button id="epp-chat-send" disabled>&#10148;</button>
    </div>
    <div id="epp-chat-footer">Powered by EcoPowerParts AI</div>
  `;
  document.body.appendChild(win);

  var msgs = document.getElementById("epp-chat-messages");
  var input = document.getElementById("epp-chat-input");
  var sendBtn = document.getElementById("epp-chat-send");
  var closeBtn = document.getElementById("epp-chat-close");
  var badge = btn.querySelector(".badge");
  var isOpen = false;
  var isSending = false;

  function addMsg(text, role) {
    var div = document.createElement("div");
    div.className = "epp-msg " + role;
    // Convert URLs to links
    div.innerHTML = text.replace(
      /(https?:\/\/[^\s<]+)/g,
      '<a href="$1" target="_blank" rel="noopener">$1</a>'
    );
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
  }

  function showTyping() {
    var div = addMsg("Thinking...", "bot typing");
    div.id = "epp-typing";
    return div;
  }

  function removeTyping() {
    var t = document.getElementById("epp-typing");
    if (t) t.remove();
  }

  // Welcome message on first open
  var welcomed = false;
  function showWelcome() {
    if (welcomed) return;
    welcomed = true;
    addMsg("Hey! I'm the EPP assistant. Ask me anything about our aluminum turbo pipes, fitment for your vehicle, pricing, or lead times. How can I help?", "bot");
  }

  btn.addEventListener("click", function() {
    isOpen = !isOpen;
    win.classList.toggle("open", isOpen);
    badge.style.display = "none";
    if (isOpen) {
      showWelcome();
      input.focus();
    }
  });

  closeBtn.addEventListener("click", function() {
    isOpen = false;
    win.classList.remove("open");
  });

  input.addEventListener("input", function() {
    sendBtn.disabled = !input.value.trim() || isSending;
  });

  function sendMessage() {
    var text = input.value.trim();
    if (!text || isSending) return;

    addMsg(text, "user");
    history.push({ role: "user", content: text });
    input.value = "";
    sendBtn.disabled = true;
    isSending = true;

    var typing = showTyping();

    fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: history.slice(-10) })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      removeTyping();
      var reply = data.reply || "Sorry, something went wrong. Try again or email info@ecopowerparts.com.";
      addMsg(reply, "bot");
      history.push({ role: "assistant", content: reply });
    })
    .catch(function() {
      removeTyping();
      addMsg("Connection error — please try again or email info@ecopowerparts.com.", "bot");
    })
    .finally(function() {
      isSending = false;
      sendBtn.disabled = !input.value.trim();
    });
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
})();
