import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const API_BASE = 'http://localhost:8000';

export default function App() {
  // Navigation & Layout State
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightDrawer, setRightDrawer] = useState(null); // 'schema' | 'rag' | 'details' | null
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [connectDbModalOpen, setConnectDbModalOpen] = useState(false);
  const [schemaModalOpen, setSchemaModalOpen] = useState(false);
  const [schemaSearchQuery, setSchemaSearchQuery] = useState('');
  const [schemaDetailTab, setSchemaDetailTab] = useState('columns'); // 'columns' | 'samples' | 'fks'
  const [schemaLoading, setSchemaLoading] = useState(false);
  const [keyModalOpen, setKeyModalOpen] = useState(false);
  const [keyModalTab, setKeyModalTab] = useState('list'); // 'list' | 'analytics' | 'create'
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  // Model & Execution Config
  const [selectedModel, setSelectedModel] = useState('Tiny SQL LLM (6.16M)');
  const [executionMode, setExecutionMode] = useState('agent'); // 'agent' | 'raw'
  const [apiHealth, setApiHealth] = useState({ status: 'online', device: 'cpu' });

  // Database Connection State
  const [activeDbInfo, setActiveDbInfo] = useState({
    database_name: 'SQL- Language Model',
    database_type: 'postgresql',
    table_count: 10,
    is_custom: false
  });
  const [connMode, setConnMode] = useState('snowflake'); // 'snowflake' | 'uri'
  const [sfAccount, setSfAccount] = useState('RTVYZKD-JR34931');
  const [sfUser, setSfUser] = useState('ANURAGKATRE');
  const [sfPassword, setSfPassword] = useState('Anurag@28082002');
  const [sfWarehouse, setSfWarehouse] = useState('COMPUTE_WH');
  const [sfDatabase, setSfDatabase] = useState('BANKING_DB');
  const [sfRole, setSfRole] = useState('ACCOUNTADMIN');
  const [sfSchema, setSfSchema] = useState('BANKING_SCHEMA');

  const [dbDialect, setDbDialect] = useState('snowflake');
  const [connectionUriInput, setConnectionUriInput] = useState('Driver={SnowflakeDSIIDriver};Server=RTVYZKD-JR34931.snowflakecomputing.com;Database=BANKING_DB;uid=ANURAGKATRE;pwd=Anurag@28082002');
  const [dbTestLoading, setDbTestLoading] = useState(false);
  const [dbTestResult, setDbTestResult] = useState(null);
  const [dbConnectLoading, setDbConnectLoading] = useState(false);
  const [dbAdaptLoading, setDbAdaptLoading] = useState(false);
  const [adaptStatusMsg, setAdaptStatusMsg] = useState(null);

  // Conversations State
  const [conversations, setConversations] = useState([
    {
      id: 'conv_1',
      title: 'Top Customer Spending Analysis',
      timestamp: 'Just now',
      messages: []
    }
  ]);
  const [currentConvId, setCurrentConvId] = useState('conv_1');

  // Input & Messaging
  const [inputPrompt, setInputPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const chatBottomRef = useRef(null);

  // Schema & RAG Data
  const [schemaData, setSchemaData] = useState(null);
  const [selectedTable, setSelectedTable] = useState(null);
  const [ragQuery, setRagQuery] = useState('');
  const [ragResults, setRagResults] = useState([]);

  // API Key Management & Analytics Data
  const [apiKeys, setApiKeys] = useState([]);
  const [keyAnalytics, setKeyAnalytics] = useState(null);
  const [newKeyName, setNewKeyName] = useState('Analytics Microservice');
  const [newKeyPrefix, setNewKeyPrefix] = useState('AK-nice-');
  const [newKeyQuota, setNewKeyQuota] = useState('500'); // 'unlimited', '100', '500', '1000'
  const [generatedKey, setGeneratedKey] = useState(null);
  const [editingKeyId, setEditingKeyId] = useState(null);
  const [editLimitVal, setEditLimitVal] = useState('1000');

  // Initial Data Fetching
  useEffect(() => {
    checkHealth();
    fetchSchema();
    fetchDbStatus();
    fetchApiKeys();
    fetchKeyAnalytics();

    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversations, loading]);

  const currentConv = conversations.find((c) => c.id === currentConvId) || conversations[0];

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) {
        const data = await res.json();
        setApiHealth(data);
      }
    } catch {
      setApiHealth({ status: 'offline', device: 'cpu' });
    }
  };

  const fetchDbStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/v1/database/status`, {
        headers: { 'X-API-Key': 'dev-preview-token' }
      });
      if (res.ok) {
        const data = await res.json();
        setActiveDbInfo(data);
      }
    } catch (e) {
      console.error('DB Status fetch error:', e);
    }
  };

  const fetchSchema = async () => {
    setSchemaLoading(true);
    try {
      const res = await fetch(`${API_BASE}/v1/schema/detailed`, {
        headers: { 'X-API-Key': 'dev-preview-token' }
      });
      if (res.ok) {
        const data = await res.json();
        setSchemaData(data);
        if (data.tables?.length > 0) {
          setSelectedTable((prev) => (data.tables.some((t) => t.name === prev) ? prev : data.tables[0].name));
        }
      }
    } catch (e) {
      console.error('Schema fetch error:', e);
    } finally {
      setSchemaLoading(false);
    }
  };

  const fetchApiKeys = async () => {
    try {
      const res = await fetch(`${API_BASE}/v1/keys/list`, {
        headers: { 'X-API-Key': 'dev-preview-token' }
      });
      if (res.ok) {
        const data = await res.json();
        setApiKeys(data.keys || []);
      }
    } catch (e) {
      console.error('Keys list fetch error:', e);
    }
  };

  const fetchKeyAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/v1/keys/analytics`, {
        headers: { 'X-API-Key': 'dev-preview-token' }
      });
      if (res.ok) {
        const data = await res.json();
        setKeyAnalytics(data);
      }
    } catch (e) {
      console.error('Key Analytics fetch error:', e);
    }
  };

  // Driver Format Detection Helper
  const detectDriverFormat = (str) => {
    if (!str) return null;
    const s = str.trim().toLowerCase();
    const isSSO = s.includes('authenticator=externalbrowser') || s.includes('authenticator=snowflake_jwt') || s.includes('authenticator=oauth');
    const ssoTag = isSSO ? ' (SSO / Browser Auth)' : '';
    if (s.startsWith('jdbc:snowflake://')) return { label: `Snowflake (JDBC Driver)${ssoTag}`, color: '#38bdf8', icon: '☕' };
    if (s.includes('driver={snowflakedsiidriver}') || (s.includes('driver=') && s.includes('snowflake'))) return { label: `Snowflake (ODBC Driver)${ssoTag}`, color: '#38bdf8', icon: '🔌' };
    if (s.includes('account=') && (s.includes('warehouse=') || s.includes('db=')) && s.includes(';')) return { label: `Snowflake (.NET Driver)${ssoTag}`, color: '#38bdf8', icon: '🔷' };
    if (s.includes('.snowflakecomputing.com') && s.includes('@')) return { label: `Snowflake (Go Driver DSN)${ssoTag}`, color: '#38bdf8', icon: '🐹' };
    if (s.startsWith('snowflake://')) return { label: `Snowflake (SQLAlchemy/Python)${ssoTag}`, color: '#38bdf8', icon: '❄️' };
    if (s.startsWith('postgresql') || s.startsWith('postgres')) return { label: 'PostgreSQL', color: '#3b82f6', icon: '🐘' };
    if (s.startsWith('mysql')) return { label: 'MySQL', color: '#f59e0b', icon: '🐬' };
    if (s.startsWith('mssql') || s.includes('driver={odbc driver')) return { label: 'SQL Server (MSSQL)', color: '#ec4899', icon: '🪟' };
    if (s.startsWith('sqlite')) return { label: 'SQLite', color: '#a855f7', icon: '🪶' };
    return { label: 'Custom Connection String', color: '#94a3b8', icon: '🔗' };
  };

  // Database Connection Handlers
  const handleDialectSelect = (dialect) => {
    setDbDialect(dialect);
    setDbTestResult(null);
    if (dialect === 'postgresql') {
      setConnectionUriInput('postgresql+psycopg2://postgres:Nice123@localhost:5432/SQL- Language Model');
    } else if (dialect === 'mssql') {
      setConnectionUriInput('mssql+pyodbc://sa:password@localhost:1433/EnterpriseDB?driver=ODBC+Driver+17+for+SQL+Server');
    } else if (dialect === 'sqlite') {
      setConnectionUriInput('sqlite:///sandbox.db');
    } else if (dialect === 'mysql') {
      setConnectionUriInput('mysql+pymysql://root:password@localhost:3306/enterprise_db');
    } else if (dialect === 'snowflake_odbc' || dialect === 'snowflake') {
      setConnectionUriInput('Driver={SnowflakeDSIIDriver};Server=xy12345.snowflakecomputing.com;Database=DEMO_DB;Schema=PUBLIC;Warehouse=COMPUTE_WH;UID=my_user;PWD=my_password;Role=SYSADMIN;');
    } else if (dialect === 'snowflake_jdbc') {
      setConnectionUriInput('jdbc:snowflake://xy12345.snowflakecomputing.com/?user=my_user&password=my_password&db=DEMO_DB&schema=PUBLIC&warehouse=COMPUTE_WH&role=SYSADMIN');
    } else if (dialect === 'snowflake_go') {
      setConnectionUriInput('my_user:my_password@xy12345.snowflakecomputing.com/DEMO_DB/PUBLIC?warehouse=COMPUTE_WH&role=SYSADMIN');
    } else if (dialect === 'snowflake_dotnet') {
      setConnectionUriInput('account=xy12345;user=my_user;password=my_password;db=DEMO_DB;schema=PUBLIC;warehouse=COMPUTE_WH;role=SYSADMIN;');
    } else if (dialect === 'snowflake_sa') {
      setConnectionUriInput('snowflake://my_user:my_password@xy12345/DEMO_DB/PUBLIC?warehouse=COMPUTE_WH&role=SYSADMIN');
    }
  };

  const getActiveConnectionUri = () => {
    if (connMode === 'snowflake') {
      const cleanAcc = sfAccount.replace('.snowflakecomputing.com', '').trim();
      const u = encodeURIComponent(sfUser.trim());
      const p = encodeURIComponent(sfPassword.trim());
      const db = sfDatabase.trim();
      const schema = sfSchema.trim() || 'PUBLIC';
      let uri = `snowflake://${u}:${p}@${cleanAcc}/${db}/${schema}`;
      const params = [];
      if (sfWarehouse.trim()) params.push(`warehouse=${encodeURIComponent(sfWarehouse.trim())}`);
      if (sfRole.trim()) params.push(`role=${encodeURIComponent(sfRole.trim())}`);
      if (params.length > 0) uri += `?${params.join('&')}`;
      return uri;
    }
    return connectionUriInput.trim();
  };

  const handleTestDbConnection = async () => {
    const activeUri = getActiveConnectionUri();
    if (!activeUri) return;
    setDbTestLoading(true);
    setDbTestResult(null);
    try {
      const res = await fetch(`${API_BASE}/v1/database/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'dev-preview-token'
        },
        body: JSON.stringify({ connection_uri: activeUri, database_type: connMode === 'snowflake' ? 'snowflake' : dbDialect })
      });
      const data = await res.json();
      setDbTestResult(data);
    } catch (e) {
      setDbTestResult({ success: false, message: e.message || 'Connection test failed' });
    } finally {
      setDbTestLoading(false);
    }
  };

  const handleConnectDb = async () => {
    const activeUri = getActiveConnectionUri();
    if (!activeUri) return;
    setDbConnectLoading(true);
    try {
      const res = await fetch(`${API_BASE}/v1/database/connect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'dev-preview-token'
        },
        body: JSON.stringify({ connection_uri: activeUri, database_type: connMode === 'snowflake' ? 'snowflake' : dbDialect })
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Connection failed');
      }
      const data = await res.json();
      await fetchDbStatus();
      await fetchSchema();
      setConnectDbModalOpen(false);
      setDbTestResult(null);
    } catch (e) {
      alert(`Connection failed: ${e.message}`);
    } finally {
      setDbConnectLoading(false);
    }
  };

  const handleResetDb = async () => {
    try {
      await fetch(`${API_BASE}/v1/database/disconnect`, {
        method: 'POST',
        headers: { 'X-API-Key': 'dev-preview-token' }
      });
      await fetchDbStatus();
      await fetchSchema();
      setConnectDbModalOpen(false);
      setDbTestResult(null);
    } catch (e) {
      alert(`Reset failed: ${e.message}`);
    }
  };

  const handleAdaptSchema = async () => {
    if (!connectionUriInput.trim()) return;
    setDbAdaptLoading(true);
    setAdaptStatusMsg('Introspecting schema, generating shadow replica sandbox, and fine-tuning model on custom tables...');
    try {
      const res = await fetch(`${API_BASE}/v1/database/adapt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'dev-preview-token'
        },
        body: JSON.stringify({ connection_uri: connectionUriInput, database_type: dbDialect })
      });
      const data = await res.json();
      if (res.ok) {
        setAdaptStatusMsg('Schema adaptation complete! Shadow replica sandbox, vector knowledge, and adapted weights are active.');
        await fetchDbStatus();
        await fetchSchema();
      } else {
        setAdaptStatusMsg(`Adaptation error: ${data.detail || 'Failed'}`);
      }
    } catch (e) {
      setAdaptStatusMsg(`Error: ${e.message}`);
    } finally {
      setDbAdaptLoading(false);
    }
  };

  // API Key Actions
  const handleCreateApiKey = async () => {
    if (!newKeyName.trim()) return;
    try {
      const quotaVal = newKeyQuota === 'unlimited' ? null : parseInt(newKeyQuota, 10);
      const res = await fetch(`${API_BASE}/v1/keys/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'dev-preview-token'
        },
        body: JSON.stringify({
          client_name: newKeyName,
          prefix: newKeyPrefix || 'AK-nice-',
          quota_limit: quotaVal,
          rate_limit_rpm: 60
        })
      });
      if (res.ok) {
        const data = await res.json();
        setGeneratedKey(data);
        setNewKeyName('');
        await fetchApiKeys();
        await fetchKeyAnalytics();
        setKeyModalTab('list');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleRevokeApiKey = async (keyId) => {
    try {
      const res = await fetch(`${API_BASE}/v1/keys/revoke`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'dev-preview-token'
        },
        body: JSON.stringify({ key_id: keyId })
      });
      if (res.ok) {
        await fetchApiKeys();
        await fetchKeyAnalytics();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleActivateApiKey = async (keyId) => {
    try {
      const res = await fetch(`${API_BASE}/v1/keys/activate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'dev-preview-token'
        },
        body: JSON.stringify({ key_id: keyId })
      });
      if (res.ok) {
        await fetchApiKeys();
        await fetchKeyAnalytics();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleUpdateKeyLimit = async (keyId) => {
    try {
      const limitVal = editLimitVal === 'unlimited' ? -1 : parseInt(editLimitVal, 10);
      const res = await fetch(`${API_BASE}/v1/keys/limit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'dev-preview-token'
        },
        body: JSON.stringify({ key_id: keyId, quota_limit: limitVal })
      });
      if (res.ok) {
        setEditingKeyId(null);
        await fetchApiKeys();
        await fetchKeyAnalytics();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteApiKey = async (keyId) => {
    if (!window.confirm('Are you sure you want to permanently delete this API key? This cannot be undone.')) return;
    try {
      const res = await fetch(`${API_BASE}/v1/keys/delete/${keyId}`, {
        method: 'DELETE',
        headers: { 'X-API-Key': 'dev-preview-token' }
      });
      if (res.ok) {
        await fetchApiKeys();
        await fetchKeyAnalytics();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateNewChat = () => {
    const newId = `conv_${Date.now()}`;
    const newChat = {
      id: newId,
      title: 'New Query Session',
      timestamp: 'Just now',
      messages: []
    };
    setConversations([newChat, ...conversations]);
    setCurrentConvId(newId);
    setInputPrompt('');
    setRightDrawer(null);
  };

  const handleSendMessage = async (customPrompt) => {
    const textToSend = customPrompt || inputPrompt;
    if (!textToSend.trim() || loading) return;

    const userMessage = {
      id: `msg_user_${Date.now()}`,
      role: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const updatedMessages = [...currentConv.messages, userMessage];
    const isFirstMessage = currentConv.messages.length === 0;
    const newTitle = isFirstMessage
      ? textToSend.length > 34 ? textToSend.substring(0, 34) + '...' : textToSend
      : currentConv.title;

    setConversations((prev) =>
      prev.map((c) => (c.id === currentConvId ? { ...c, title: newTitle, messages: updatedMessages } : c))
    );

    setInputPrompt('');
    setLoading(true);

    const startTime = performance.now();

    try {
      let resData = null;
      if (executionMode === 'agent') {
        const res = await fetch(`${API_BASE}/v1/agent/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'dev-preview-token'
          },
          body: JSON.stringify({ prompt: textToSend, max_retries: 2 })
        });
        if (!res.ok) throw new Error('Query execution failed');
        resData = await res.json();
      } else {
        const res = await fetch(`${API_BASE}/v1/generate_sql`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'dev-preview-token'
          },
          body: JSON.stringify({ question: textToSend, dialect: 'postgres' })
        });
        if (!res.ok) throw new Error('SQL Generation failed');
        const raw = await res.json();
        resData = {
          generated_sql: raw.sql,
          explanation: 'Generated deterministic relational SQL query based on active schema tables.',
          status: 'SUCCESS',
          results: []
        };
      }

      let formattedResults = [];
      if (resData.execution?.rows && resData.execution?.columns) {
        const cols = resData.execution.columns;
        formattedResults = resData.execution.rows.map((row) => {
          if (Array.isArray(row)) {
            const obj = {};
            cols.forEach((col, idx) => {
              obj[col] = row[idx];
            });
            return obj;
          }
          return row;
        });
      }

      const assistantMessage = {
        id: `msg_asst_${Date.now()}`,
        role: 'assistant',
        content: resData.explanation || 'Query processed.',
        generated_sql: resData.generated_sql,
        status: resData.success ? 'SUCCESS' : 'FAILED',
        intent: resData.intent || 'text_to_sql',
        attempts: resData.attempts || [],
        repaired: resData.repaired || false,
        results: formattedResults,
        execution: resData.execution,
        latency_ms: Math.round(performance.now() - startTime),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setConversations((prev) =>
        prev.map((c) =>
          c.id === currentConvId
            ? { ...c, messages: [...updatedMessages, assistantMessage] }
            : c
        )
      );
    } catch (err) {
      const errorMessage = {
        id: `msg_err_${Date.now()}`,
        role: 'assistant',
        content: `Query pipeline encountered an issue: ${err.message}`,
        status: 'FAILED',
        latency_ms: Math.round(performance.now() - startTime),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setConversations((prev) =>
        prev.map((c) =>
          c.id === currentConvId
            ? { ...c, messages: [...updatedMessages, errorMessage] }
            : c
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const copyCode = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleRagSearch = async () => {
    if (!ragQuery.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/v1/rag/search?query=${encodeURIComponent(ragQuery)}&top_k=4`, {
        headers: { 'X-API-Key': 'dev-preview-token' }
      });
      if (res.ok) {
        const data = await res.json();
        setRagResults(data.results || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="app-layout">
      {/* 1. LEFT SIDEBAR */}
      <aside className={`app-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="brand-dot" />
            {!sidebarCollapsed && <span className="brand-text">Tiny SQL LLM</span>}
          </div>
          <button
            className="sidebar-collapse-btn"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            title="Toggle Sidebar"
          >
            {sidebarCollapsed ? '→' : '←'}
          </button>
        </div>

        {!sidebarCollapsed && (
          <>
            <button className="new-chat-btn" onClick={handleCreateNewChat}>
              <span>+</span> New Query Session
            </button>

            <div className="sidebar-section-label">Active Database</div>
            <div
              style={{
                margin: '0 4px 12px 4px',
                padding: '10px 12px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '6px',
                fontSize: '12px',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
              onClick={() => {
                fetchSchema();
                setSchemaModalOpen(true);
              }}
              title="Click to explore database schema & tables"
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontWeight: '600', color: 'var(--text-white)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '140px' }}>
                  {activeDbInfo.database_name}
                </span>
                <span className="status-pill-badge badge-active">
                  {activeDbInfo.database_type.toUpperCase()}
                </span>
              </div>
              <div style={{ color: 'var(--text-dim)', fontSize: '11px', display: 'flex', justifyContent: 'space-between' }}>
                <span>{schemaData?.table_count || activeDbInfo.table_count || 10} tables</span>
                <span>{schemaData?.total_rows ? `${schemaData.total_rows.toLocaleString()} rows` : 'Inspect >'}</span>
              </div>
            </div>

            <div className="sidebar-section-label">Recent Sessions</div>
            <div className="conversation-list">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`conversation-item ${conv.id === currentConvId ? 'active' : ''}`}
                  onClick={() => setCurrentConvId(conv.id)}
                >
                  <span className="conv-title">{conv.title}</span>
                  <span className="conv-time">{conv.timestamp}</span>
                </div>
              ))}
            </div>

            <div className="sidebar-footer">
              <div className="system-health-tag">
                <div className={apiHealth.status === 'online' ? 'status-dot-green' : 'status-dot-red'} />
                <span>API: {apiHealth.status.toUpperCase()} ({apiHealth.device})</span>
              </div>

              <div style={{ display: 'flex', gap: '6px', marginTop: '6px' }}>
                <button
                  className="sidebar-action-btn"
                  onClick={() => {
                    fetchSchema();
                    setSchemaModalOpen(true);
                  }}
                  title="Explore Database Schema"
                  style={{ flex: 1 }}
                >
                  Schema
                </button>
                <button
                  className="sidebar-action-btn"
                  onClick={() => setConnectDbModalOpen(true)}
                  title="Connect External Database"
                  style={{ flex: 1 }}
                >
                  Connect DB
                </button>
                <button
                  className="sidebar-action-btn"
                  onClick={() => {
                    setKeyModalOpen(true);
                    fetchKeyAnalytics();
                  }}
                  title="Manage API Keys"
                  style={{ flex: 1 }}
                >
                  Keys
                </button>
              </div>
            </div>
          </>
        )}
      </aside>

      {/* 2. MAIN WORKSPACE */}
      <div className="main-viewport">
        {/* Top Navbar */}
        <header className="top-navbar">
          <div className="navbar-left">
            <span className="conversation-title-badge">
              {currentConv.messages.length > 0 ? currentConv.title : 'New Query Session'}
            </span>
          </div>

          <div className="navbar-right">
            {/* DB Status Badge / Connector */}
            <div
              className="db-status-pill"
              onClick={() => {
                fetchSchema();
                setSchemaModalOpen(true);
              }}
              title="Click to explore database schema & structures"
              style={{ cursor: 'pointer' }}
            >
              <div className="status-dot-green" />
              <span>
                {activeDbInfo.database_type.toUpperCase()}: {activeDbInfo.database_name} ({schemaData?.table_count || activeDbInfo.table_count} tables)
              </span>
            </div>

            <button
              className="tool-pill-btn"
              onClick={() => {
                fetchSchema();
                setSchemaModalOpen(true);
              }}
              style={{ padding: '4px 10px', fontSize: '11.5px', background: 'rgba(59, 130, 246, 0.12)', color: '#60a5fa', borderColor: 'rgba(59, 130, 246, 0.3)' }}
              title="View all tables, column types, row counts, and live sample data"
            >
              Schema Explorer
            </button>

            <button
              className="tool-pill-btn"
              onClick={() => setConnectDbModalOpen(true)}
              style={{ padding: '4px 10px', fontSize: '11.5px' }}
            >
              Connect DB
            </button>

            <button
              className="tool-pill-btn"
              onClick={() => {
                setKeyModalOpen(true);
                fetchKeyAnalytics();
              }}
              style={{ padding: '4px 10px', fontSize: '11.5px' }}
            >
              API Keys
            </button>

            <button
              className="model-selector-btn"
              onClick={() => setSettingsModalOpen(true)}
            >
              <span>{selectedModel}</span>
            </button>

            <button
              className="icon-btn"
              onClick={() => setSettingsModalOpen(true)}
              title="System Configuration"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
              </svg>
            </button>
          </div>
        </header>

        {/* Workspace Body */}
        <div className="workspace-body">
          {/* STATE A: HERO WELCOME */}
          {currentConv.messages.length === 0 && (
            <div className="hero-container">
              <div className="hero-pill-tag">Autonomous SQL Engine</div>
              <h1 className="hero-heading">Ask your data anything.</h1>
              <p className="hero-subtext">
                Generate, validate, and execute relational SQL using natural language.
                AST-verified with zero data egress.
              </p>
            </div>
          )}

          {/* STATE B: CONVERSATION STREAM */}
          {currentConv.messages.length > 0 && (
            <div className="conversation-stream">
              {currentConv.messages.map((msg) => (
                <div key={msg.id}>
                  {msg.role === 'user' ? (
                    <div className="user-message-row">
                      <div className="user-bubble">{msg.content}</div>
                    </div>
                  ) : (
                    <div className="assistant-message-row">
                      <div className="assistant-avatar-label">AI</div>

                      <div className="assistant-content-wrapper">
                        {/* 1. Markdown-rendered Explanation */}
                        <div className="markdown-body">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {msg.content}
                          </ReactMarkdown>
                        </div>

                        {/* 2. Execution Trace Bar */}
                        {msg.generated_sql && (
                          <div className="execution-trace-bar">
                            <span className="trace-item">
                              Intent: <span className="trace-badge intent">{msg.intent || 'text_to_sql'}</span>
                            </span>
                            <span className="trace-item">
                              Status:{' '}
                              <span className={`trace-badge ${msg.status === 'SUCCESS' ? 'success' : 'failed'}`}>
                                {msg.status === 'SUCCESS' ? '● SUCCESS' : '▲ ' + (msg.status || 'FAILED')}
                              </span>
                            </span>
                            {msg.repaired && (
                              <span className="trace-badge repaired">
                                ⚡ AST Self-Repaired
                              </span>
                            )}
                            {msg.latency_ms && (
                              <span className="trace-item">
                                Latency: <span className="trace-badge latency">⏱ {msg.latency_ms}ms</span>
                              </span>
                            )}
                          </div>
                        )}

                        {/* 3. SQL Query Code Block */}
                        {msg.generated_sql && (
                          <div className="sql-card">
                            <div className="sql-card-header">
                              <span>⚡ Generated SQL Statement</span>
                              <div className="sql-card-actions">
                                <button
                                  className="sql-btn"
                                  onClick={() => copyCode(msg.generated_sql, msg.id)}
                                >
                                  {copiedId === msg.id ? '✓ Copied' : '📋 Copy SQL'}
                                </button>
                              </div>
                            </div>
                            <pre className="sql-code-block">
                              <code>{msg.generated_sql}</code>
                            </pre>
                          </div>
                        )}

                        {/* 4. Results Data Table */}
                        {msg.results && msg.results.length > 0 && (
                          <div className="data-table-container">
                            <div className="table-meta-bar">
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span>📊 Query Results</span>
                                <span className="table-row-count-pill">
                                  {msg.results.length} {msg.results.length === 1 ? 'row' : 'rows'} returned
                                </span>
                              </div>
                              <button
                                className="sql-btn"
                                onClick={() => {
                                  if (!msg.results || !msg.results.length) return;
                                  const headers = Object.keys(msg.results[0]).join(',');
                                  const rows = msg.results.map(r => Object.values(r).map(v => `"${String(v ?? '').replace(/"/g, '""')}"`).join(',')).join('\n');
                                  const csv = `${headers}\n${rows}`;
                                  navigator.clipboard.writeText(csv);
                                  alert('Table copied as CSV to clipboard!');
                                }}
                              >
                                📥 Copy CSV
                              </button>
                            </div>
                            <div className="table-scroll-wrap">
                              <table className="relational-table">
                                <thead>
                                  <tr>
                                    {Object.keys(msg.results[0]).map((col) => (
                                      <th key={col}>{col}</th>
                                    ))}
                                  </tr>
                                </thead>
                                <tbody>
                                  {msg.results.map((row, rIdx) => (
                                    <tr key={rIdx}>
                                      {Object.entries(row).map(([k, val], cIdx) => {
                                        const isNumOrId = typeof val === 'number' || k.toLowerCase().endsWith('_id') || k.toLowerCase() === 'id';
                                        return (
                                          <td key={cIdx} className={isNumOrId ? 'num-cell' : ''}>
                                            {val !== null && val !== undefined ? (
                                              String(val)
                                            ) : (
                                              <span className="null-badge">NULL</span>
                                            )}
                                          </td>
                                        );
                                      })}
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="assistant-message-row">
                  <div className="assistant-avatar-label">AI</div>
                  <div className="assistant-content-wrapper">
                    <div className="typing-indicator-bar">
                      <div className="pulse-spinner" />
                      <span>Introspecting schema, formulating SQL, and validating AST safety...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatBottomRef} />
            </div>
          )}
        </div>

        {/* Workspace Footer / Prompt Composer */}
        <footer className="composer-container">
          <div className="composer-box">
            <textarea
              className="composer-textarea"
              placeholder="Ask a question or describe a query (e.g. 'Show top 5 products by revenue', 'What is CTE?')..."
              rows={2}
              value={inputPrompt}
              onChange={(e) => setInputPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />

            <div className="composer-toolbar">
              <div className="composer-tools-left">
                <button
                  className={`tool-pill-btn ${rightDrawer === 'schema' ? 'active' : ''}`}
                  onClick={() => setRightDrawer(rightDrawer === 'schema' ? null : 'schema')}
                >
                  Schema ({schemaData?.table_count || 10})
                </button>
                <button
                  className={`tool-pill-btn ${rightDrawer === 'rag' ? 'active' : ''}`}
                  onClick={() => setRightDrawer(rightDrawer === 'rag' ? null : 'rag')}
                >
                  RAG Knowledge
                </button>
                <button
                  className={`tool-pill-btn ${executionMode === 'agent' ? 'active' : ''}`}
                  onClick={() => setExecutionMode(executionMode === 'agent' ? 'raw' : 'agent')}
                >
                  Mode: {executionMode.toUpperCase()}
                </button>
              </div>

              <div className="composer-tools-right">
                <button
                  className="composer-send-btn"
                  disabled={!inputPrompt.trim() || loading}
                  onClick={() => handleSendMessage()}
                >
                  Send ↵
                </button>
              </div>
            </div>
          </div>
          <div className="composer-footer-note">
            AST-validated queries are executed strictly against your active database: <strong>{activeDbInfo.database_name}</strong>.
          </div>
        </footer>
      </div>

      {/* 3. RIGHT CONTEXT DRAWER */}
      {rightDrawer && (
        <aside className="context-drawer">
          <div className="drawer-header">
            <span>
              {rightDrawer === 'schema' && 'Schema Catalog'}
              {rightDrawer === 'rag' && 'Knowledge Search'}
              {rightDrawer === 'details' && 'Session Details'}
            </span>
            <button className="icon-btn" onClick={() => setRightDrawer(null)}>
              ✕
            </button>
          </div>

          <div className="drawer-content">
            {rightDrawer === 'schema' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '11.5px', color: 'var(--text-dim)', fontWeight: '600', textTransform: 'uppercase' }}>
                    {schemaData?.database_type || activeDbInfo.database_type.toUpperCase()} • {schemaData?.table_count || schemaData?.tables?.length || 0} Tables
                  </span>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <button
                      className="btn-action-small"
                      onClick={() => setSchemaModalOpen(true)}
                    >
                      Full Explorer
                    </button>
                    <button
                      className="btn-action-small"
                      onClick={() => setConnectDbModalOpen(true)}
                    >
                      Switch DB
                    </button>
                  </div>
                </div>

                {/* Table Tabs List with Row Badges */}
                <div className="table-tabs-list">
                  {schemaData?.tables?.map((tbl) => (
                    <button
                      key={tbl.name}
                      className={`table-tab-pill ${selectedTable === tbl.name ? 'active' : ''}`}
                      onClick={() => setSelectedTable(tbl.name)}
                    >
                      {tbl.name} ({tbl.row_count !== undefined ? `${tbl.row_count}r` : `${tbl.columns?.length}c`})
                    </button>
                  ))}
                </div>

                {selectedTable && schemaData?.tables && (
                  <div className="schema-table-details">
                    {(() => {
                      const t = schemaData.tables.find((tbl) => tbl.name === selectedTable);
                      if (!t) return null;
                      return (
                        <>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                            <h4 style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-white)' }}>
                              {t.name}
                            </h4>
                            <span style={{ fontSize: '10.5px', color: '#4ade80' }}>
                              {t.row_count !== undefined ? `${t.row_count} rows` : ''} • {t.columns?.length || 0} cols
                            </span>
                          </div>

                          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            {t.columns?.map((col, idx) => (
                              <div
                                key={idx}
                                style={{
                                  display: 'flex',
                                  justifyContent: 'space-between',
                                  alignItems: 'center',
                                  padding: '4px 6px',
                                  background: 'var(--bg-surface)',
                                  borderRadius: '3px',
                                  fontSize: '11.5px',
                                  border: '1px solid var(--border-subtle)'
                                }}
                              >
                                <span style={{ fontFamily: 'var(--font-mono)' }}>
                                  {col.name}{' '}
                                  {col.is_primary ? (
                                    <span style={{ fontSize: '9px', padding: '1px 4px', background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa', borderRadius: '3px', marginLeft: '4px' }}>
                                      PK
                                    </span>
                                  ) : null}
                                  {col.is_foreign ? (
                                    <span style={{ fontSize: '9px', padding: '1px 4px', background: 'rgba(168, 85, 247, 0.2)', color: '#c084fc', borderRadius: '3px', marginLeft: '4px' }}>
                                      FK
                                    </span>
                                  ) : null}
                                </span>
                                <span style={{ color: 'var(--text-muted)', fontSize: '10.5px', fontFamily: 'var(--font-mono)' }}>{col.type}</span>
                              </div>
                            ))}
                          </div>

                          <button
                            className="btn-action-small"
                            style={{ marginTop: '8px', width: '100%', textAlign: 'center' }}
                            onClick={() => {
                              setInputPrompt(`SELECT * FROM ${t.name} LIMIT 10;`);
                              setRightDrawer(null);
                            }}
                          >
                            Query {t.name} in Chat
                          </button>
                        </>
                      );
                    })()}
                  </div>
                )}
              </div>
            )}

            {rightDrawer === 'rag' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <input
                    type="text"
                    className="composer-input"
                    style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-strong)', padding: '6px 10px', borderRadius: '4px', fontSize: '12.5px' }}
                    placeholder="Search SQL concepts (e.g. CTE, Window)..."
                    value={ragQuery}
                    onChange={(e) => setRagQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleRagSearch()}
                  />
                  <button className="tool-pill-btn" onClick={() => handleRagSearch()}>
                    Search
                  </button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {ragResults.map((doc, idx) => (
                    <div key={idx} style={{ padding: '10px', background: 'var(--bg-surface)', border: '1px solid var(--border-strong)', borderRadius: '4px', fontSize: '12px' }}>
                      <div style={{ fontWeight: '600', color: 'var(--text-white)', marginBottom: '4px' }}>
                        {doc.metadata?.title || `Document #${idx + 1}`}
                      </div>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '11.5px', lineHeight: '1.5' }}>
                        {doc.document?.substring(0, 160)}...
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </aside>
      )}

      {/* 4. CONNECT DATABASE MODAL */}
      {connectDbModalOpen && (
        <div className="modal-overlay" onClick={() => setConnectDbModalOpen(false)}>
          <div className="modal-dialog-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>Connect External Database to Language Model</span>
              </div>
              <button className="icon-btn" onClick={() => setConnectDbModalOpen(false)}>
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {/* Active DB Status Card */}
                <div style={{ padding: '12px 14px', background: 'var(--bg-secondary)', borderRadius: '6px', border: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '11px', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: '600' }}>Active Database Connection</div>
                    <div style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-white)', marginTop: '2px' }}>
                      {activeDbInfo.database_name} <span className="status-pill-badge badge-active">{activeDbInfo.database_type.toUpperCase()}</span>
                    </div>
                    <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      {schemaData?.table_count || activeDbInfo.table_count || 10} tables currently loaded in agent catalog
                    </div>
                  </div>

                  <button
                    className="btn-action-small"
                    onClick={handleResetDb}
                    title="Reset to default local PostgreSQL sandbox"
                  >
                    Reset to Default DB
                  </button>
                </div>

                {/* Dialect Selector */}
                <div>
                  <label style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '6px', display: 'block' }}>
                    Select Database Dialect / Platform:
                  </label>
                  <div className="preset-dialect-grid">
                    {[
                      { id: 'postgresql', name: 'PostgreSQL' },
                      { id: 'mssql', name: 'SQL Server (SSMS)' },
                      { id: 'sqlite', name: 'SQLite' },
                      { id: 'mysql', name: 'MySQL' },
                      { id: 'snowflake', name: 'Snowflake' }
                    ].map((d) => (
                      <button
                        key={d.id}
                        className={`preset-dialect-card ${dbDialect === d.id ? 'selected' : ''}`}
                        onClick={() => handleDialectSelect(d.id)}
                      >
                        {d.name}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Connection URI Input */}
                <div>
                  <label style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '6px', display: 'block' }}>
                    SQLAlchemy Connection URI:
                  </label>
                  <input
                    type="text"
                    className="composer-input"
                    style={{
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-strong)',
                      padding: '8px 12px',
                      borderRadius: '4px',
                      fontSize: '13px',
                      fontFamily: 'var(--font-mono)'
                    }}
                    placeholder="dialect+driver://username:password@host:port/database"
                    value={connectionUriInput}
                    onChange={(e) => setConnectionUriInput(e.target.value)}
                  />
                  <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
                    Supports live connection pooling, schema reflection, and zero-egress sandbox execution.
                  </div>
                </div>

                {/* Test Result Banner */}
                {dbTestResult && (
                  <div
                    style={{
                      padding: '10px 14px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      background: dbTestResult.success ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                      border: `1px solid ${dbTestResult.success ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                      color: dbTestResult.success ? '#4ade80' : '#f87171'
                    }}
                  >
                    <div style={{ fontWeight: '600', marginBottom: '2px' }}>
                      {dbTestResult.success ? '✓ Connection Successful' : '✕ Connection Test Failed'}
                    </div>
                    <div>{dbTestResult.message}</div>
                    {dbTestResult.tables && (
                      <div style={{ marginTop: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                        Discovered Tables ({dbTestResult.tables.length}): {dbTestResult.tables.join(', ')}
                      </div>
                    )}
                  </div>
                )}

                {/* Adaptation Status Banner */}
                {adaptStatusMsg && (
                  <div style={{ padding: '10px 14px', borderRadius: '4px', fontSize: '12px', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', color: '#60a5fa' }}>
                    {adaptStatusMsg}
                  </div>
                )}

                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', marginTop: '8px', flexWrap: 'wrap' }}>
                  <button
                    className="tool-pill-btn"
                    onClick={handleTestDbConnection}
                    disabled={dbTestLoading || dbAdaptLoading || !connectionUriInput.trim()}
                  >
                    {dbTestLoading ? 'Testing...' : 'Ping / Test Connection'}
                  </button>

                  <button
                    className="tool-pill-btn"
                    style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', borderColor: '#3b82f6' }}
                    onClick={handleAdaptSchema}
                    disabled={dbAdaptLoading || dbConnectLoading || !connectionUriInput.trim()}
                    title="Creates replica sandbox, synthesizes 100+ training pairs, and fine-tunes model on this schema"
                  >
                    {dbAdaptLoading ? 'Adapting & Training Model...' : 'Adapt & Train on Schema'}
                  </button>

                  <button
                    className="composer-send-btn"
                    style={{ padding: '6px 16px', fontSize: '12.5px' }}
                    onClick={handleConnectDb}
                    disabled={dbConnectLoading || dbAdaptLoading || !connectionUriInput.trim()}
                  >
                    {dbConnectLoading ? 'Connecting...' : 'Connect & Load Schema'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 5. API KEY MANAGEMENT & ANALYTICS MODAL */}
      {keyModalOpen && (
        <div className="modal-overlay" onClick={() => setKeyModalOpen(false)}>
          <div className="modal-dialog-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>API Key Management & Usage Analytics</span>
              </div>
              <button className="icon-btn" onClick={() => setKeyModalOpen(false)}>
                ✕
              </button>
            </div>

            {/* Modal Tabs */}
            <div className="modal-tab-nav">
              <button
                className={`modal-tab-btn ${keyModalTab === 'list' ? 'active' : ''}`}
                onClick={() => setKeyModalTab('list')}
              >
                Registered Keys ({apiKeys.length})
              </button>
              <button
                className={`modal-tab-btn ${keyModalTab === 'analytics' ? 'active' : ''}`}
                onClick={() => {
                  setKeyModalTab('analytics');
                  fetchKeyAnalytics();
                }}
              >
                Usage Analytics & Telemetry
              </button>
              <button
                className={`modal-tab-btn ${keyModalTab === 'create' ? 'active' : ''}`}
                onClick={() => setKeyModalTab('create')}
              >
                + Generate New Key
              </button>
            </div>

            <div className="modal-body">
              {/* TAB 1: KEY LIST & CONTROLS */}
              {keyModalTab === 'list' && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <span style={{ fontSize: '12.5px', color: 'var(--text-secondary)' }}>
                      Manage authentication tokens, configure request quotas, and control active status.
                    </span>
                    <button
                      className="btn-action-small"
                      onClick={() => setKeyModalTab('create')}
                    >
                      + New Key
                    </button>
                  </div>

                  {generatedKey && (
                    <div style={{ padding: '10px 14px', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid #3b82f6', borderRadius: '4px', fontSize: '12px', marginBottom: '12px' }}>
                      <div style={{ fontWeight: '600', color: '#60a5fa', marginBottom: '2px' }}>New API Key Generated!</div>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12.5px', color: 'var(--text-white)', wordBreak: 'break-all' }}>
                        {generatedKey.api_key}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
                        Save this key securely. Pass it as <code>Authorization: Bearer AK-nice-...</code> or in <code>X-API-Key</code> header.
                      </div>
                    </div>
                  )}

                  <div style={{ overflowX: 'auto' }}>
                    <table className="key-mgmt-table">
                      <thead>
                        <tr>
                          <th>Client / Application</th>
                          <th>API Key Token</th>
                          <th>Status</th>
                          <th>Usage / Quota</th>
                          <th>Last Active</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {apiKeys.map((k) => {
                          const quota = k.quota_limit;
                          const total = k.total_requests || 0;
                          const pct = quota ? Math.min(100, (total / quota) * 100) : 0;

                          return (
                            <tr key={k.key_id}>
                              <td style={{ fontWeight: '600' }}>{k.client_name}</td>
                              <td>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                  <code style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>{k.masked_key}</code>
                                  <button
                                    className="btn-action-small"
                                    onClick={() => copyCode(k.api_key, k.key_id)}
                                    title="Copy raw key"
                                  >
                                    {copiedId === k.key_id ? '✓' : 'Copy'}
                                  </button>
                                </div>
                              </td>
                              <td>
                                {!k.is_active ? (
                                  <span className="status-pill-badge badge-revoked">Revoked</span>
                                ) : k.is_exhausted ? (
                                  <span className="status-pill-badge badge-exhausted">Quota Exceeded</span>
                                ) : (
                                  <span className="status-pill-badge badge-active">Active</span>
                                )}
                              </td>
                              <td>
                                <div style={{ minWidth: '100px' }}>
                                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
                                    <span>{total} reqs</span>
                                    <span style={{ color: 'var(--text-dim)' }}>
                                      {quota ? `/ ${quota}` : 'Unlimited'}
                                    </span>
                                  </div>
                                  {quota && (
                                    <div className="quota-progress-track">
                                      <div
                                        className="quota-progress-bar"
                                        style={{
                                          width: `${pct}%`,
                                          background: pct > 90 ? '#ef4444' : pct > 70 ? '#f59e0b' : '#3b82f6'
                                        }}
                                      />
                                    </div>
                                  )}
                                </div>
                              </td>
                              <td style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                                {k.last_used || 'Never'}
                              </td>
                              <td>
                                <div style={{ display: 'flex', gap: '4px' }}>
                                  {k.is_active ? (
                                    <button
                                      className="btn-action-small"
                                      onClick={() => handleRevokeApiKey(k.key_id)}
                                      title="Temporarily revoke key"
                                    >
                                      Revoke
                                    </button>
                                  ) : (
                                    <button
                                      className="btn-action-small btn-action-success"
                                      onClick={() => handleActivateApiKey(k.key_id)}
                                      title="Reactivate key"
                                    >
                                      Activate
                                    </button>
                                  )}

                                  {editingKeyId === k.key_id ? (
                                    <div style={{ display: 'flex', gap: '2px' }}>
                                      <select
                                        className="btn-action-small"
                                        value={editLimitVal}
                                        onChange={(e) => setEditLimitVal(e.target.value)}
                                      >
                                        <option value="100">100</option>
                                        <option value="500">500</option>
                                        <option value="1000">1,000</option>
                                        <option value="unlimited">Unlimited</option>
                                      </select>
                                      <button
                                        className="btn-action-small btn-action-success"
                                        onClick={() => handleUpdateKeyLimit(k.key_id)}
                                      >
                                        Save
                                      </button>
                                    </div>
                                  ) : (
                                    <button
                                      className="btn-action-small"
                                      onClick={() => {
                                        setEditingKeyId(k.key_id);
                                        setEditLimitVal(k.quota_limit ? String(k.quota_limit) : 'unlimited');
                                      }}
                                      title="Change request quota limit"
                                    >
                                      Limit
                                    </button>
                                  )}

                                  <button
                                    className="btn-action-small btn-action-danger"
                                    onClick={() => handleDeleteApiKey(k.key_id)}
                                    title="Permanently delete key"
                                  >
                                    Delete
                                  </button>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* TAB 2: USAGE ANALYTICS & TELEMETRY */}
              {keyModalTab === 'analytics' && keyAnalytics && (
                <div>
                  {/* KPI Cards Grid */}
                  <div className="metrics-kpi-grid">
                    <div className="metric-kpi-card">
                      <div className="metric-kpi-label">Registered Keys</div>
                      <div className="metric-kpi-val">{keyAnalytics.total_keys}</div>
                      <div className="metric-kpi-sub">{keyAnalytics.active_keys} active / {keyAnalytics.revoked_keys} revoked</div>
                    </div>
                    <div className="metric-kpi-card">
                      <div className="metric-kpi-label">Total API Calls</div>
                      <div className="metric-kpi-val">{keyAnalytics.total_requests}</div>
                      <div className="metric-kpi-sub">{keyAnalytics.successful_requests} successful</div>
                    </div>
                    <div className="metric-kpi-card">
                      <div className="metric-kpi-label">Success Rate</div>
                      <div className="metric-kpi-val" style={{ color: '#4ade80' }}>
                        {keyAnalytics.success_rate_pct}%
                      </div>
                      <div className="metric-kpi-sub">{keyAnalytics.failed_requests} failed queries</div>
                    </div>
                    <div className="metric-kpi-card">
                      <div className="metric-kpi-label">Avg Latency</div>
                      <div className="metric-kpi-val">{keyAnalytics.average_latency_ms} ms</div>
                      <div className="metric-kpi-sub">Local neural AST execution</div>
                    </div>
                  </div>

                  <h4 style={{ fontSize: '12.5px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-white)' }}>
                    Per-Client Usage Summary:
                  </h4>
                  <table className="key-mgmt-table">
                    <thead>
                      <tr>
                        <th>Client</th>
                        <th>Token</th>
                        <th>Status</th>
                        <th>Total Volume</th>
                        <th>Quota Limit</th>
                        <th>Last Active</th>
                      </tr>
                    </thead>
                    <tbody>
                      {keyAnalytics.keys_summary?.map((ks, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: '600' }}>{ks.client_name}</td>
                          <td><code>{ks.masked_key}</code></td>
                          <td>
                            {ks.is_active ? (
                              <span className="status-pill-badge badge-active">Active</span>
                            ) : (
                              <span className="status-pill-badge badge-revoked">Revoked</span>
                            )}
                          </td>
                          <td style={{ fontWeight: '600' }}>{ks.total_requests} reqs</td>
                          <td>{ks.quota_limit ? `${ks.quota_limit} reqs` : 'Unlimited'}</td>
                          <td style={{ color: 'var(--text-muted)' }}>{ks.last_used}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* TAB 3: GENERATE NEW KEY */}
              {keyModalTab === 'create' && (
                <div style={{ maxWidth: '500px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <div>
                    <label style={{ fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '4px' }}>
                      Client Application / Microservice Name:
                    </label>
                    <input
                      type="text"
                      className="composer-input"
                      style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-strong)', padding: '8px 10px', borderRadius: '4px', fontSize: '13px' }}
                      placeholder="e.g. Production BI Dashboard, Node Service"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '4px' }}>
                      Key Prefix:
                    </label>
                    <input
                      type="text"
                      className="composer-input"
                      style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-strong)', padding: '8px 10px', borderRadius: '4px', fontSize: '13px' }}
                      placeholder="AK-nice-"
                      value={newKeyPrefix}
                      onChange={(e) => setNewKeyPrefix(e.target.value)}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '4px' }}>
                      Request Quota Limit:
                    </label>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '6px' }}>
                      {['100', '500', '1000', 'unlimited'].map((q) => (
                        <button
                          key={q}
                          className={`preset-dialect-card ${newKeyQuota === q ? 'selected' : ''}`}
                          onClick={() => setNewKeyQuota(q)}
                        >
                          {q === 'unlimited' ? 'Unlimited' : `${q} Reqs`}
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    className="composer-send-btn"
                    style={{ marginTop: '8px', padding: '8px 16px', fontSize: '13px' }}
                    onClick={handleCreateApiKey}
                    disabled={!newKeyName.trim()}
                  >
                    Generate Branded API Key
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 5.5 DEDICATED SCHEMA EXPLORER MODAL */}
      {schemaModalOpen && (
        <div className="modal-overlay" onClick={() => setSchemaModalOpen(false)}>
          <div
            className="modal-dialog-large"
            style={{ maxWidth: '920px', width: '92vw', height: '82vh', display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="modal-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 18px', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontWeight: '600', fontSize: '14px' }}>Database Schema Explorer</span>
                <span className="status-pill-badge badge-active">{activeDbInfo.database_type.toUpperCase()}</span>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{schemaData?.database_name || activeDbInfo.database_name}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button
                  className="btn-action-small"
                  onClick={fetchSchema}
                  disabled={schemaLoading}
                  title="Reload live schema & row counts"
                >
                  {schemaLoading ? 'Refreshing...' : 'Refresh Schema'}
                </button>
                <button className="icon-btn" onClick={() => setSchemaModalOpen(false)}>
                  ✕
                </button>
              </div>
            </div>

            {/* Top KPI Metrics Strip */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', padding: '10px 16px', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ padding: '8px 12px', background: 'var(--bg-surface)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Total Tables</div>
                <div style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-white)' }}>{schemaData?.table_count || schemaData?.tables?.length || 0}</div>
              </div>
              <div style={{ padding: '8px 12px', background: 'var(--bg-surface)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Total Live Rows</div>
                <div style={{ fontSize: '16px', fontWeight: '700', color: '#4ade80' }}>
                  {schemaData?.total_rows !== undefined ? schemaData.total_rows.toLocaleString() : 'Loading...'}
                </div>
              </div>
              <div style={{ padding: '8px 12px', background: 'var(--bg-surface)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Total Columns</div>
                <div style={{ fontSize: '16px', fontWeight: '700', color: '#60a5fa' }}>{schemaData?.total_columns || 0}</div>
              </div>
              <div style={{ padding: '8px 12px', background: 'var(--bg-surface)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Database Engine</div>
                <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-white)', marginTop: '2px' }}>{schemaData?.database_type || activeDbInfo.database_type.toUpperCase()}</div>
              </div>
            </div>

            {/* Master-Detail Explorer Body */}
            <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', flex: 1, minHeight: 0, overflow: 'hidden' }}>
              {/* Left Pane: Search & Table List */}
              <div style={{ borderRight: '1px solid var(--border-subtle)', background: 'var(--bg-secondary)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <div style={{ padding: '8px 10px', borderBottom: '1px solid var(--border-subtle)' }}>
                  <input
                    type="text"
                    className="composer-input"
                    placeholder="Search tables..."
                    value={schemaSearchQuery}
                    onChange={(e) => setSchemaSearchQuery(e.target.value)}
                    style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-strong)', padding: '6px 10px', borderRadius: '4px', fontSize: '12px', width: '100%' }}
                  />
                </div>
                <div style={{ flex: 1, overflowY: 'auto', padding: '6px' }}>
                  {schemaData?.tables
                    ?.filter((t) => t.name.toLowerCase().includes(schemaSearchQuery.toLowerCase()))
                    .map((t) => {
                      const isSelected = selectedTable === t.name;
                      return (
                        <div
                          key={t.name}
                          onClick={() => setSelectedTable(t.name)}
                          style={{
                            padding: '8px 10px',
                            marginBottom: '4px',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            background: isSelected ? 'var(--bg-elevated)' : 'transparent',
                            border: `1px solid ${isSelected ? 'var(--border-strong)' : 'transparent'}`,
                            transition: 'all 0.15s ease'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontWeight: isSelected ? '600' : '500', color: isSelected ? 'var(--text-white)' : 'var(--text-primary)', fontSize: '12px', fontFamily: 'var(--font-mono)' }}>
                              {t.name}
                            </span>
                          </div>
                          <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
                            <span style={{ fontSize: '10px', padding: '1px 5px', borderRadius: '3px', background: 'rgba(34, 197, 94, 0.15)', color: '#4ade80' }}>
                              {t.row_count !== undefined ? `${t.row_count} rows` : '0 rows'}
                            </span>
                            <span style={{ fontSize: '10px', padding: '1px 5px', borderRadius: '3px', background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>
                              {t.columns?.length || t.col_count || 0} cols
                            </span>
                          </div>
                        </div>
                      );
                    })}
                </div>
              </div>

              {/* Right Pane: Selected Table Inspection */}
              <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg-primary)' }}>
                {(() => {
                  const currentTbl = schemaData?.tables?.find((t) => t.name === selectedTable) || schemaData?.tables?.[0];
                  if (!currentTbl) {
                    return (
                      <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px' }}>
                        No tables discovered or match your search filter.
                      </div>
                    );
                  }

                  return (
                    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
                      {/* Table Header Bar */}
                      <div style={{ padding: '10px 16px', borderBottom: '1px solid var(--border-subtle)', background: 'var(--bg-secondary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <h3 style={{ fontSize: '13.5px', fontWeight: '700', color: 'var(--text-white)', fontFamily: 'var(--font-mono)' }}>
                            {currentTbl.name}
                          </h3>
                          <span style={{ fontSize: '10.5px', padding: '2px 6px', background: 'rgba(34, 197, 94, 0.15)', color: '#4ade80', borderRadius: '4px' }}>
                            {currentTbl.row_count !== undefined ? `${currentTbl.row_count} total rows` : ''}
                          </span>
                          <span style={{ fontSize: '10.5px', padding: '2px 6px', background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', borderRadius: '4px' }}>
                            {currentTbl.columns?.length || currentTbl.col_count || 0} columns
                          </span>
                        </div>

                        <button
                          className="composer-send-btn"
                          style={{ padding: '4px 12px', fontSize: '11.5px' }}
                          onClick={() => {
                            setInputPrompt(`SELECT * FROM ${currentTbl.name} LIMIT 10;`);
                            setSchemaModalOpen(false);
                          }}
                        >
                          Query Table in Chat
                        </button>
                      </div>

                      {/* Sub-tab Navigation */}
                      <div style={{ display: 'flex', gap: '4px', padding: '6px 16px 0 16px', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)' }}>
                        <button
                          className={`modal-tab-btn ${schemaDetailTab === 'columns' ? 'active' : ''}`}
                          onClick={() => setSchemaDetailTab('columns')}
                          style={{ fontSize: '11.5px', padding: '5px 12px' }}
                        >
                          Columns & Types ({currentTbl.columns?.length || 0})
                        </button>
                        <button
                          className={`modal-tab-btn ${schemaDetailTab === 'samples' ? 'active' : ''}`}
                          onClick={() => setSchemaDetailTab('samples')}
                          style={{ fontSize: '11.5px', padding: '5px 12px' }}
                        >
                          Live Sample Rows ({currentTbl.sample_rows?.length || 0})
                        </button>
                        <button
                          className={`modal-tab-btn ${schemaDetailTab === 'fks' ? 'active' : ''}`}
                          onClick={() => setSchemaDetailTab('fks')}
                          style={{ fontSize: '11.5px', padding: '5px 12px' }}
                        >
                          Foreign Keys ({currentTbl.foreign_keys?.length || 0})
                        </button>
                      </div>

                      {/* Tab Content */}
                      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 16px' }}>
                        {schemaDetailTab === 'columns' && (
                          <div style={{ overflowX: 'auto' }}>
                            <table className="key-mgmt-table" style={{ width: '100%' }}>
                              <thead>
                                <tr>
                                  <th style={{ width: '35px' }}>#</th>
                                  <th>Column Name</th>
                                  <th>Data Type</th>
                                  <th>Key / Constraints</th>
                                  <th>Nullable</th>
                                </tr>
                              </thead>
                              <tbody>
                                {currentTbl.columns?.map((col, idx) => (
                                  <tr key={idx}>
                                    <td style={{ color: 'var(--text-dim)', fontSize: '11px' }}>{idx + 1}</td>
                                    <td>
                                      <code style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-white)' }}>
                                        {col.name}
                                      </code>
                                    </td>
                                    <td>
                                      <span style={{ fontSize: '11.5px', fontFamily: 'var(--font-mono)', color: '#60a5fa' }}>
                                        {col.type}
                                      </span>
                                    </td>
                                    <td>
                                      <div style={{ display: 'flex', gap: '4px' }}>
                                        {col.is_primary && (
                                          <span style={{ fontSize: '9.5px', padding: '1px 5px', background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa', borderRadius: '3px', fontWeight: '700' }}>
                                            PK
                                          </span>
                                        )}
                                        {col.is_foreign && (
                                          <span style={{ fontSize: '9.5px', padding: '1px 5px', background: 'rgba(168, 85, 247, 0.2)', color: '#c084fc', borderRadius: '3px', fontWeight: '700' }}>
                                            FK
                                          </span>
                                        )}
                                        {!col.is_primary && !col.is_foreign && (
                                          <span style={{ color: 'var(--text-dim)', fontSize: '11px' }}>-</span>
                                        )}
                                      </div>
                                    </td>
                                    <td style={{ fontSize: '11px' }}>
                                      {col.nullable ? (
                                        <span style={{ color: 'var(--text-muted)' }}>NULL</span>
                                      ) : (
                                        <span style={{ color: '#f59e0b', fontWeight: '600' }}>NOT NULL</span>
                                      )}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}

                        {schemaDetailTab === 'samples' && (
                          <div>
                            {currentTbl.sample_rows && currentTbl.sample_rows.length > 0 ? (
                              <div style={{ overflowX: 'auto', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
                                <table className="key-mgmt-table" style={{ width: '100%', margin: 0 }}>
                                  <thead>
                                    <tr>
                                      {Object.keys(currentTbl.sample_rows[0]).map((colKey) => (
                                        <th key={colKey} style={{ whiteSpace: 'nowrap' }}>
                                          {colKey}
                                        </th>
                                      ))}
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {currentTbl.sample_rows.map((row, rIdx) => (
                                      <tr key={rIdx}>
                                        {Object.entries(row).map(([k, val], cIdx) => (
                                          <td key={cIdx} style={{ fontSize: '11.5px', whiteSpace: 'nowrap' }}>
                                            {val === null || val === 'NULL' ? (
                                              <span style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>NULL</span>
                                            ) : (
                                              String(val)
                                            )}
                                          </td>
                                        ))}
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            ) : (
                              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px' }}>
                                Table appears to be empty or sample rows could not be retrieved.
                              </div>
                            )}
                          </div>
                        )}

                        {schemaDetailTab === 'fks' && (
                          <div>
                            {currentTbl.foreign_keys && currentTbl.foreign_keys.length > 0 ? (
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                {currentTbl.foreign_keys.map((fk, fIdx) => (
                                  <div key={fIdx} style={{ padding: '8px 12px', background: 'var(--bg-secondary)', borderRadius: '4px', border: '1px solid var(--border-subtle)', fontSize: '12px' }}>
                                    <span style={{ fontWeight: '600', color: 'var(--text-white)' }}>{fk.constrained_columns?.join(', ')}</span>
                                    <span style={{ color: 'var(--text-muted)', margin: '0 6px' }}>→ references →</span>
                                    <span style={{ color: '#60a5fa', fontWeight: '600' }}>{fk.referred_table}.({fk.referred_columns?.join(', ')})</span>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px' }}>
                                No explicit foreign key relationships defined on this table.
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })()}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 5.6 CONNECT DATABASE & MULTI-DRIVER MODAL */}
      {connectDbModalOpen && (
        <div className="modal-overlay" onClick={() => setConnectDbModalOpen(false)}>
          <div
            className="modal-dialog-large"
            style={{ maxWidth: '820px', width: '90vw', padding: '0', overflow: 'hidden' }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="modal-header" style={{ padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontWeight: '600', fontSize: '15px' }}>Connect Enterprise Database / Warehouse</span>
                <span className="status-pill-badge badge-active">{connMode === 'snowflake' ? 'SNOWFLAKE ACCOUNT SETUP' : 'UNIVERSAL URI'}</span>
              </div>
              <button className="icon-btn" onClick={() => setConnectDbModalOpen(false)}>
                ✕
              </button>
            </div>

            <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '18px', maxHeight: '78vh', overflowY: 'auto' }}>
              {/* Navigation Mode Switcher */}
              <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '10px' }}>
                <button
                  className={`btn-action-small ${connMode === 'snowflake' ? 'btn-action-success' : ''}`}
                  onClick={() => { setConnMode('snowflake'); setDbTestResult(null); }}
                  style={{ padding: '8px 16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <span>❄️</span> Snowflake Account Setup
                </button>
                <button
                  className={`btn-action-small ${connMode === 'uri' ? 'btn-action-success' : ''}`}
                  onClick={() => { setConnMode('uri'); setDbTestResult(null); }}
                  style={{ padding: '8px 16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <span>🔗</span> Generic Connection String / URI (Postgres, MSSQL, MySQL)
                </button>
              </div>

              {/* MODE 1: DEDICATED SNOWFLAKE CREDENTIAL SETUP FORM */}
              {connMode === 'snowflake' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                    <div>
                      <label style={{ fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '4px', color: 'var(--text-white)' }}>
                        SNOWFLAKE_ACCOUNT:
                      </label>
                      <input
                        type="text"
                        className="composer-input"
                        placeholder="e.g. RTVYZKD-JR34931"
                        value={sfAccount}
                        onChange={(e) => { setSfAccount(e.target.value); setDbTestResult(null); }}
                        style={{ width: '100%', padding: '8px 10px', background: 'var(--bg-secondary)', border: '1px solid var(--border-strong)', borderRadius: '4px', fontSize: '13px' }}
                      />
                    </div>

                    <div>
                      <label style={{ fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '4px', color: 'var(--text-white)' }}>
                        SNOWFLAKE_USER:
                      </label>
                      <input
                        type="text"
                        className="composer-input"
                        placeholder="e.g. ANURAGKATRE"
                        value={sfUser}
                        onChange={(e) => { setSfUser(e.target.value); setDbTestResult(null); }}
                        style={{ width: '100%', padding: '8px 10px', background: 'var(--bg-secondary)', border: '1px solid var(--border-strong)', borderRadius: '4px', fontSize: '13px' }}
                      />
                    </div>

                    <div>
                      <label style={{ fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '4px', color: 'var(--text-white)' }}>
                        SNOWFLAKE_PASSWORD:
                      </label>
                      <input
                        type="password"
                        className="composer-input"
                        placeholder="••••••••••••"
                        value={sfPassword}
                        onChange={(e) => { setSfPassword(e.target.value); setDbTestResult(null); }}
                        style={{ width: '100%', padding: '8px 10px', background: 'var(--bg-secondary)', border: '1px solid var(--border-strong)', borderRadius: '4px', fontSize: '13px' }}
                      />
                    </div>

                    <div>
                      <label style={{ fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '4px', color: 'var(--text-white)' }}>
                        SNOWFLAKE_WAREHOUSE:
                      </label>
                      <input
                        type="text"
                        className="composer-input"
                        placeholder="e.g. COMPUTE_WH"
                        value={sfWarehouse}
                        onChange={(e) => { setSfWarehouse(e.target.value); setDbTestResult(null); }}
                        style={{ width: '100%', padding: '8px 10px', background: 'var(--bg-secondary)', border: '1px solid var(--border-strong)', borderRadius: '4px', fontSize: '13px' }}
                      />
                    </div>

                    <div>
                      <label style={{ fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '4px', color: 'var(--text-white)' }}>
                        SNOWFLAKE_DATABASE:
                      </label>
                      <input
                        type="text"
                        className="composer-input"
                        placeholder="e.g. BANKING_DB"
                        value={sfDatabase}
                        onChange={(e) => { setSfDatabase(e.target.value); setDbTestResult(null); }}
                        style={{ width: '100%', padding: '8px 10px', background: 'var(--bg-secondary)', border: '1px solid var(--border-strong)', borderRadius: '4px', fontSize: '13px' }}
                      />
                    </div>

                    <div>
                      <label style={{ fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '4px', color: 'var(--text-white)' }}>
                        SNOWFLAKE_SCHEMA:
                      </label>
                      <input
                        type="text"
                        className="composer-input"
                        placeholder="e.g. BANKING_SCHEMA (or PUBLIC)"
                        value={sfSchema}
                        onChange={(e) => { setSfSchema(e.target.value); setDbTestResult(null); }}
                        style={{ width: '100%', padding: '8px 10px', background: 'var(--bg-secondary)', border: '1px solid var(--border-strong)', borderRadius: '4px', fontSize: '13px' }}
                      />
                    </div>

                    <div>
                      <label style={{ fontSize: '12px', fontWeight: '600', display: 'block', marginBottom: '4px', color: 'var(--text-white)' }}>
                        SNOWFLAKE_ROLE (Optional):
                      </label>
                      <input
                        type="text"
                        className="composer-input"
                        placeholder="e.g. ACCOUNTADMIN or SYSADMIN"
                        value={sfRole}
                        onChange={(e) => { setSfRole(e.target.value); setDbTestResult(null); }}
                        style={{ width: '100%', padding: '8px 10px', background: 'var(--bg-secondary)', border: '1px solid var(--border-strong)', borderRadius: '4px', fontSize: '13px' }}
                      />
                    </div>
                  </div>

                  {/* Live Generated URI Preview */}
                  <div style={{ padding: '8px 12px', background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: '4px', fontSize: '11.5px', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', overflowX: 'auto', whiteSpace: 'nowrap' }}>
                    <span style={{ color: '#38bdf8', fontWeight: '600' }}>Configured Snowflake DSN: </span>
                    {`snowflake://${sfUser || '<USER>'}:••••••••@${(sfAccount || '<ACCOUNT>').replace('.snowflakecomputing.com', '')}/${sfDatabase || '<DB>'}/${sfSchema || 'PUBLIC'}?warehouse=${sfWarehouse || '<WH>'}&role=${sfRole || ''}`}
                  </div>
                </div>
              )}

              {/* MODE 2: GENERIC CONNECTION STRING / URI */}
              {connMode === 'uri' && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <label style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-white)' }}>
                      Connection String / URI:
                    </label>
                    {(() => {
                      const detected = detectDriverFormat(connectionUriInput);
                      if (!detected) return null;
                      return (
                        <span
                          style={{
                            fontSize: '11px',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            background: 'rgba(255, 255, 255, 0.08)',
                            color: detected.color,
                            border: `1px solid ${detected.color}40`,
                            fontWeight: '600',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}
                        >
                          {detected.icon} Detected: {detected.label}
                        </span>
                      );
                    })()}
                  </div>
                  <textarea
                    className="composer-input"
                    style={{
                      width: '100%',
                      minHeight: '80px',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '12.5px',
                      padding: '10px 12px',
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-strong)',
                      borderRadius: '6px',
                      resize: 'vertical'
                    }}
                    placeholder="e.g. postgresql+psycopg2://postgres:Nice123@localhost:5432/SQL- Language Model"
                    value={connectionUriInput}
                    onChange={(e) => {
                      setConnectionUriInput(e.target.value);
                      setDbTestResult(null);
                    }}
                  />
                  <div style={{ fontSize: '11.5px', color: 'var(--text-dim)', marginTop: '4px' }}>
                    Supports PostgreSQL, SQLite, MySQL, and Microsoft SQL Server (MSSQL).
                  </div>
                </div>
              )}

              {/* Test Result Message Box */}
              {dbTestResult && (
                <div
                  style={{
                    padding: '12px 14px',
                    borderRadius: '6px',
                    background: dbTestResult.success ? 'rgba(34, 197, 94, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                    border: `1px solid ${dbTestResult.success ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                    fontSize: '12.5px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontWeight: '600', color: dbTestResult.success ? '#4ade80' : '#f87171' }}>
                      {dbTestResult.success ? 'Connection Successful' : 'Connection Failed'}
                    </span>
                    {dbTestResult.latency_ms && (
                      <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                        Latency: {dbTestResult.latency_ms} ms
                      </span>
                    )}
                  </div>
                  <div style={{ color: 'var(--text-primary)', fontSize: '12px' }}>
                    {dbTestResult.message || dbTestResult.error}
                  </div>
                  {dbTestResult.tables && dbTestResult.tables.length > 0 && (
                    <div style={{ marginTop: '6px', display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {dbTestResult.tables.slice(0, 8).map((tbl) => (
                        <span key={tbl} style={{ fontSize: '10.5px', padding: '1px 6px', background: 'var(--bg-surface)', borderRadius: '3px', border: '1px solid var(--border-subtle)', fontFamily: 'var(--font-mono)' }}>
                          {tbl}
                        </span>
                      ))}
                      {dbTestResult.tables.length > 8 && (
                        <span style={{ fontSize: '10.5px', color: 'var(--text-dim)', padding: '1px 4px' }}>
                          +{dbTestResult.tables.length - 8} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Adaptation Status Box */}
              {adaptStatusMsg && (
                <div style={{ padding: '10px 12px', background: 'rgba(59, 130, 246, 0.12)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '6px', fontSize: '12px', color: '#93c5fd' }}>
                  {adaptStatusMsg}
                </div>
              )}

              {/* Action Buttons */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)' }}>
                <button
                  className="btn-action-small btn-action-danger"
                  onClick={handleResetDb}
                  title="Reset to default local PostgreSQL database"
                >
                  Disconnect / Reset to Default
                </button>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    className="btn-action-small"
                    onClick={handleTestDbConnection}
                    disabled={dbTestLoading || !connectionUriInput.trim()}
                    style={{ padding: '8px 14px', fontSize: '12.5px' }}
                  >
                    {dbTestLoading ? 'Testing...' : 'Test Connection'}
                  </button>

                  <button
                    className="composer-send-btn"
                    onClick={handleConnectDb}
                    disabled={dbConnectLoading || !connectionUriInput.trim()}
                    style={{ padding: '8px 18px', fontSize: '12.5px' }}
                  >
                    {dbConnectLoading ? 'Connecting...' : 'Connect & Activate Database'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 6. SETTINGS & PLATFORM MODAL */}
      {settingsModalOpen && (
        <div className="modal-overlay" onClick={() => setSettingsModalOpen(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <span>Platform Configuration</span>
              <button className="icon-btn" onClick={() => setSettingsModalOpen(false)}>
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                  <h3 style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
                    Neural Model Architecture
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', fontSize: '12.5px' }}>
                    <div style={{ padding: '8px 10px', background: 'var(--bg-secondary)', borderRadius: '4px', border: '1px solid var(--border-strong)' }}>
                      <div style={{ color: 'var(--text-dim)' }}>Parameters</div>
                      <div style={{ fontWeight: '600' }}>6.16 Million</div>
                    </div>
                    <div style={{ padding: '8px 10px', background: 'var(--bg-secondary)', borderRadius: '4px', border: '1px solid var(--border-strong)' }}>
                      <div style={{ color: 'var(--text-dim)' }}>Vocabulary</div>
                      <div style={{ fontWeight: '600' }}>4,096 BPE Tokens</div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
                    Active Database Connection
                  </h3>
                  <div style={{ padding: '10px 12px', background: 'var(--bg-secondary)', borderRadius: '4px', border: '1px solid var(--border-strong)', fontSize: '12.5px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: '600' }}>{activeDbInfo.database_name}</div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '11px' }}>{activeDbInfo.database_type.toUpperCase()} ({schemaData?.table_count || 10} tables)</div>
                    </div>
                    <button
                      className="btn-action-small"
                      onClick={() => {
                        setSettingsModalOpen(false);
                        setConnectDbModalOpen(true);
                      }}
                    >
                      Connect DB
                    </button>
                  </div>
                </div>

                <div>
                  <h3 style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
                    API Security & Quota Controls
                  </h3>
                  <div style={{ padding: '10px 12px', background: 'var(--bg-secondary)', borderRadius: '4px', border: '1px solid var(--border-strong)', fontSize: '12.5px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: '600' }}>{apiKeys.length} API Keys Configured</div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Branded AK-nice-* tokens with quota limits</div>
                    </div>
                    <button
                      className="btn-action-small"
                      onClick={() => {
                        setSettingsModalOpen(false);
                        setKeyModalOpen(true);
                        fetchKeyAnalytics();
                      }}
                    >
                      Manage Keys
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 7. COMMAND PALETTE */}
      {commandPaletteOpen && (
        <div className="modal-overlay" onClick={() => setCommandPaletteOpen(false)}>
          <div className="modal-dialog" style={{ maxWidth: '440px' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border-subtle)' }}>
              <input
                type="text"
                autoFocus
                className="composer-input"
                placeholder="Type a command (e.g. database, keys, schema)..."
                style={{ fontSize: '13.5px' }}
                onKeyDown={(e) => {
                  if (e.key === 'Escape') setCommandPaletteOpen(false);
                }}
              />
            </div>
            <div style={{ padding: '6px', display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <button
                className="nav-btn"
                onClick={() => {
                  setConnectDbModalOpen(true);
                  setCommandPaletteOpen(false);
                }}
              >
                <span>Connect External Database</span>
              </button>
              <button
                className="nav-btn"
                onClick={() => {
                  setKeyModalOpen(true);
                  fetchKeyAnalytics();
                  setCommandPaletteOpen(false);
                }}
              >
                <span>Manage API Keys & Quotas</span>
              </button>
              <button
                className="nav-btn"
                onClick={() => {
                  handleCreateNewChat();
                  setCommandPaletteOpen(false);
                }}
              >
                <span>+ Start New Query Session</span>
              </button>
              <button
                className="nav-btn"
                onClick={() => {
                  setRightDrawer('schema');
                  setCommandPaletteOpen(false);
                }}
              >
                <span>Open Schema Catalog</span>
              </button>
              <button
                className="nav-btn"
                onClick={() => {
                  setRightDrawer('rag');
                  setCommandPaletteOpen(false);
                }}
              >
                <span>Search Knowledge Base</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
