import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import { useEventStream } from "./hooks/useEventStream";
import { MonitorPage } from "./pages/MonitorPage";
import { SignalPage } from "./pages/SignalPage";
import { GatePage } from "./pages/GatePage";
import "./tokens.css";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function AppContent() {
  const navigate = useNavigate();
  const { events, connected, frozenAction } = useEventStream();

  const handleRunAgent = async () => {
    try {
      const response = await fetch(`${API_URL}/api/run`, {
        method: "POST",
      });
      if (!response.ok) {
        console.error("Failed to start agent:", response.statusText);
      }
    } catch (error) {
      console.error("Error starting agent:", error);
    }
  };

  const handleDecision = async (approved: boolean) => {
    if (!frozenAction?.action_id) return;

    try {
      const response = await fetch(`${API_URL}/api/decide`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action_id: frozenAction.action_id,
          approved,
        }),
      });

      if (!response.ok) {
        console.error("Failed to submit decision:", response.statusText);
      }
    } catch (error) {
      console.error("Error submitting decision:", error);
    }
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <MonitorPage
            events={events}
            connected={connected}
            frozenAction={frozenAction}
            onViewSignals={() => navigate("/signals")}
            onRunAgent={handleRunAgent}
          />
        }
      />
      <Route
        path="/signals"
        element={
          <SignalPage
            events={events}
            onBack={() => navigate("/")}
            onProceedToGate={() => navigate("/gate")}
          />
        }
      />
      <Route
        path="/gate"
        element={
          <GatePage
            events={events}
            frozenAction={frozenAction}
            onDecision={handleDecision}
            onBack={() => navigate("/signals")}
          />
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
