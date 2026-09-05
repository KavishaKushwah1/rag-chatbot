import { useEffect, useState } from "react";
import { useAuth } from "./context/AuthContext";
import AuthScreen from "./components/AuthScreen";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import SettingsModal from "./components/SettingsModal";
import DeleteConfirmModal from "./components/DeleteConfirmModal";
import { fetchMe, deleteSession } from "./api";

export default function App() {
  const { session, loading, token, email, signOut } = useAuth();
  const [me, setMe] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  useEffect(() => {
    if (token) fetchMe(token).then((m) => setMe(m || { email }));
  }, [token]);

  if (loading) return null;
  if (!session) return <AuthScreen />;

  return (
    <div className="flex" style={{ background: "var(--bg)" }}>
      <Sidebar
        token={token}
        currentSessionId={sessionId}
        onNewChat={() => setSessionId(null)}
        onOpenSession={(id) => setSessionId(id)}
        onDeleteRequest={(id, isCurrent) => setDeleteTarget({ id, isCurrent })}
        me={me}
        refreshKey={refreshKey}
        onSignOut={signOut}
        onOpenSettings={() => setShowSettings(true)}
      />

      <div className="flex-1">
        <ChatWindow
          token={token}
          me={me}
          sessionId={sessionId}
          setSessionId={setSessionId}
          onSessionsChanged={() => setRefreshKey((k) => k + 1)}
          onSignOutExpired={signOut}
        />
      </div>

      {showSettings && (
        <SettingsModal
          me={me}
          token={token}
          onClose={() => setShowSettings(false)}
          onSaved={(name) => setMe((m) => ({ ...m, display_name: name }))}
        />
      )}

      {deleteTarget && (
        <DeleteConfirmModal
          onCancel={() => setDeleteTarget(null)}
          onConfirm={async () => {
            await deleteSession(token, deleteTarget.id);
            if (deleteTarget.isCurrent) setSessionId(null);
            setDeleteTarget(null);
            setRefreshKey((k) => k + 1);
          }}
        />
      )}
    </div>
  );
}