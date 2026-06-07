import { useEffect, useMemo, useRef, useState } from "react";
import {
  BarChart3,
  Brain,
  Check,
  LogOut,
  MessageSquare,
  Plus,
  RefreshCw,
  Send,
  Shield,
  Sparkles,
  User,
  X,
} from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5002";

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || "Something went wrong");
  }

  return data;
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isRegister = mode === "register";

  function updateField(event) {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  async function submitAuth(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isRegister) {
        await apiRequest("/api/auth/register", {
          method: "POST",
          body: JSON.stringify(form),
        });
      }

      const loginData = await apiRequest("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: form.email,
          password: form.password,
        }),
      });

      onAuthenticated(loginData.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <div className="brand-mark">
          <Sparkles size={24} />
        </div>
        <h1>PaloraX AI</h1>
        <p className="muted">Your session-based AI workspace for remembered conversations.</p>

        <div className="segmented-control" aria-label="Authentication mode">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
            Login
          </button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>
            Register
          </button>
        </div>

        <form onSubmit={submitAuth} className="auth-form">
          {isRegister && (
            <label>
              Name
              <input
                name="name"
                value={form.name}
                onChange={updateField}
                placeholder="Tonmoy"
                autoComplete="name"
              />
            </label>
          )}
          <label>
            Email
            <input
              name="email"
              type="email"
              value={form.email}
              onChange={updateField}
              placeholder="you@example.com"
              autoComplete="email"
            />
          </label>
          <label>
            Password
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={updateField}
              placeholder="Your password"
              autoComplete={isRegister ? "new-password" : "current-password"}
            />
          </label>

          {error && <p className="error-text">{error}</p>}

          <button className="primary-button" disabled={loading}>
            {loading ? <RefreshCw className="spin" size={18} /> : <Shield size={18} />}
            {isRegister ? "Create Account" : "Login"}
          </button>
        </form>
      </section>
    </main>
  );
}

function Sidebar({
  user,
  conversations,
  activeConversationId,
  memory,
  loadingConversations,
  onSelectConversation,
  onNewChat,
  onRefresh,
  onLogout,
}) {
  const memoryItems = Object.entries(memory || {});

  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <div>
          <p className="eyebrow">Signed in</p>
          <h2>{user?.name || "User"}</h2>
          <p className="muted">{user?.email}</p>
        </div>
        <button className="icon-button" onClick={onLogout} title="Logout" aria-label="Logout">
          <LogOut size={18} />
        </button>
      </div>

      <button className="new-chat-button" onClick={onNewChat}>
        <Plus size={18} />
        New Chat
      </button>

      <section className="sidebar-section">
        <div className="section-heading">
          <MessageSquare size={16} />
          <span>Conversations</span>
          <button className="mini-icon-button" onClick={onRefresh} title="Refresh" aria-label="Refresh">
            <RefreshCw size={14} />
          </button>
        </div>

        <div className="conversation-list">
          {loadingConversations && <p className="muted small">Loading conversations...</p>}
          {!loadingConversations && conversations.length === 0 && (
            <p className="muted small">No conversations yet.</p>
          )}
          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              className={conversation.id === activeConversationId ? "conversation active" : "conversation"}
              onClick={() => onSelectConversation(conversation.id)}
            >
              <span>{conversation.title}</span>
              <small>{formatDate(conversation.updated_at)}</small>
            </button>
          ))}
        </div>
      </section>

      <section className="sidebar-section memory-section">
        <div className="section-heading">
          <Brain size={16} />
          <span>Long-Term Memory</span>
        </div>

        {memoryItems.length === 0 ? (
          <p className="muted small">No saved facts yet. Tell PaloraX something memorable.</p>
        ) : (
          <div className="memory-list">
            {memoryItems.map(([key, value]) => (
              <div className="memory-row" key={key}>
                <span>{key.replaceAll("_", " ")}</span>
                <strong>{Array.isArray(value) ? value.join(", ") : String(value)}</strong>
              </div>
            ))}
          </div>
        )}
      </section>
    </aside>
  );
}

function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <article className={isUser ? "message user-message" : "message assistant-message"}>
      <div className="message-icon">{isUser ? <User size={16} /> : <Sparkles size={16} />}</div>
      <div>
        <p>{message.content}</p>
        {message.timestamp && <time>{formatDate(message.timestamp)}</time>}
      </div>
    </article>
  );
}

function AnalyticsDashboard({ analytics, loading, onRefresh }) {
  const summary = analytics?.summary || {};
  const topKeywords = analytics?.top_keywords || [];
  const dailyConversations = analytics?.daily_conversations || [];
  const maxDailyCount = Math.max(
    1,
    ...dailyConversations.map((item) => item.conversation_count || 0)
  );

  return (
    <div className="analytics-panel">
      <div className="analytics-toolbar">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h2>Conversation Analytics</h2>
        </div>
        <button className="secondary-button" onClick={onRefresh} disabled={loading}>
          <RefreshCw className={loading ? "spin" : ""} size={16} />
          Refresh
        </button>
      </div>

      <section className="metric-grid">
        <div className="metric-card">
          <span>Total Conversations</span>
          <strong>{summary.total_conversations ?? 0}</strong>
        </div>
        <div className="metric-card">
          <span>Total Messages</span>
          <strong>{summary.total_messages ?? 0}</strong>
        </div>
        <div className="metric-card">
          <span>User Messages</span>
          <strong>{summary.user_messages ?? 0}</strong>
        </div>
        <div className="metric-card">
          <span>Assistant Messages</span>
          <strong>{summary.assistant_messages ?? 0}</strong>
        </div>
        <div className="metric-card">
          <span>Average Per Chat</span>
          <strong>{summary.average_messages_per_conversation ?? 0}</strong>
        </div>
      </section>

      <section className="analytics-grid">
        <div className="analytics-block">
          <div className="section-heading">
            <BarChart3 size={16} />
            <span>Top Keywords</span>
          </div>

          {topKeywords.length === 0 ? (
            <p className="muted small">No keyword data yet.</p>
          ) : (
            <div className="keyword-list">
              {topKeywords.map((item) => (
                <div className="keyword-row" key={item.keyword}>
                  <span>{item.keyword}</span>
                  <strong>{item.count}</strong>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="analytics-block">
          <div className="section-heading">
            <MessageSquare size={16} />
            <span>Daily Conversations</span>
          </div>

          {dailyConversations.length === 0 ? (
            <p className="muted small">No daily conversation data yet.</p>
          ) : (
            <div className="daily-list">
              {dailyConversations.map((item) => (
                <div className="daily-row" key={item.date}>
                  <span>{item.date}</span>
                  <div className="daily-bar-track">
                    <div
                      className="daily-bar"
                      style={{
                        width: `${Math.max(8, ((item.conversation_count || 0) / maxDailyCount) * 100)}%`,
                      }}
                    />
                  </div>
                  <strong>{item.conversation_count}</strong>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function ChatWorkspace({ user, onUserChange }) {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [memory, setMemory] = useState({});
  const [analytics, setAnalytics] = useState(null);
  const [viewMode, setViewMode] = useState("chat");
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  const activeConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === activeConversationId),
    [conversations, activeConversationId]
  );

  async function loadConversations() {
    setLoadingConversations(true);
    try {
      const data = await apiRequest("/api/conversations");
      setConversations(data.conversations || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingConversations(false);
    }
  }

  async function loadMemory() {
    try {
      const data = await apiRequest("/api/memory");
      setMemory(data.memory || {});
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadAnalytics() {
    setLoadingAnalytics(true);
    try {
      const data = await apiRequest("/api/analytics/dashboard");
      setAnalytics(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingAnalytics(false);
    }
  }

  async function loadConversation(conversationId) {
    setError("");
    try {
      const data = await apiRequest(`/api/conversations/${conversationId}`);
      setActiveConversationId(data.conversation.id);
      setMessages(data.conversation.messages || []);
      setViewMode("chat");
    } catch (err) {
      setError(err.message);
    }
  }

  async function refreshWorkspace() {
    const requests = [loadConversations(), loadMemory()];

    if (viewMode === "analytics") {
      requests.push(loadAnalytics());
    }

    await Promise.all(requests);
  }

  useEffect(() => {
    refreshWorkspace();
  }, []);

  useEffect(() => {
    if (viewMode === "analytics") {
      loadAnalytics();
    }
  }, [viewMode]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(event) {
    event.preventDefault();
    const cleanMessage = draft.trim();
    if (!cleanMessage || loading) return;

    const optimisticUserMessage = {
      role: "user",
      content: cleanMessage,
      timestamp: new Date().toISOString(),
    };

    setDraft("");
    setError("");
    setLoading(true);
    setMessages((current) => [...current, optimisticUserMessage]);

    try {
      const payload = { message: cleanMessage };
      if (activeConversationId) {
        payload.conversation_id = activeConversationId;
      }

      const data = await apiRequest("/api/chat", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      setActiveConversationId(data.conversation_id);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.reply,
          timestamp: new Date().toISOString(),
        },
      ]);
      await refreshWorkspace();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    try {
      await apiRequest("/api/auth/logout", { method: "POST" });
    } finally {
      onUserChange(null);
    }
  }

  function newChat() {
    setActiveConversationId(null);
    setMessages([]);
    setError("");
    setViewMode("chat");
  }

  return (
    <main className="app-shell">
      <Sidebar
        user={user}
        conversations={conversations}
        activeConversationId={activeConversationId}
        memory={memory}
        loadingConversations={loadingConversations}
        onSelectConversation={loadConversation}
        onNewChat={newChat}
        onRefresh={refreshWorkspace}
        onLogout={logout}
      />

      <section className="chat-area">
        <header className="chat-header">
          <div>
            <p className="eyebrow">{activeConversation ? "Conversation" : "Fresh Start"}</p>
            <h1>{viewMode === "analytics" ? "Analytics Dashboard" : activeConversation?.title || "Ask PaloraX AI"}</h1>
          </div>
          <div className="header-actions">
            <button
              className={viewMode === "analytics" ? "analytics-toggle active" : "analytics-toggle"}
              onClick={() => setViewMode((current) => current === "analytics" ? "chat" : "analytics")}
            >
              {viewMode === "analytics" ? <X size={17} /> : <BarChart3 size={17} />}
              {viewMode === "analytics" ? "Close Dashboard" : "Analytics"}
            </button>
            <div className="status-pill">
              <Check size={15} />
              Session Auth
            </div>
          </div>
        </header>

        {viewMode === "analytics" ? (
          <AnalyticsDashboard
            analytics={analytics}
            loading={loadingAnalytics}
            onRefresh={loadAnalytics}
          />
        ) : (
          <div className="messages-panel">
            {messages.length === 0 ? (
              <div className="empty-state">
                <Sparkles size={34} />
                <h2>Start a conversation</h2>
                <p className="muted">
                  Try: Please remember my name is Tonmoy and I am building PaloraX AI with Flask and MongoDB.
                </p>
              </div>
            ) : (
              messages.map((message, index) => <ChatMessage key={`${message.role}-${index}`} message={message} />)
            )}
            {loading && (
              <article className="message assistant-message">
                <div className="message-icon">
                  <RefreshCw className="spin" size={16} />
                </div>
                <div>
                  <p>Thinking...</p>
                </div>
              </article>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        {error && <p className="error-banner">{error}</p>}

        {viewMode === "chat" && (
          <form className="composer" onSubmit={sendMessage}>
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Type your message..."
              rows={2}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  sendMessage(event);
                }
              }}
            />
            <button className="send-button" disabled={loading || !draft.trim()} title="Send" aria-label="Send">
              <Send size={20} />
            </button>
          </form>
        )}
      </section>
    </main>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    async function checkSession() {
      try {
        const data = await apiRequest("/api/auth/me");
        setUser(data.user);
      } catch {
        setUser(null);
      } finally {
        setCheckingSession(false);
      }
    }

    checkSession();
  }, []);

  if (checkingSession) {
    return (
      <main className="loading-shell">
        <RefreshCw className="spin" size={24} />
        <span>Loading PaloraX AI...</span>
      </main>
    );
  }

  if (!user) {
    return <AuthScreen onAuthenticated={setUser} />;
  }

  return <ChatWorkspace user={user} onUserChange={setUser} />;
}
