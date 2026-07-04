import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import { useEventStream } from "./hooks/useEventStream";
import { AppShell } from "./components/AppShell";
import { MonitorPage } from "./pages/MonitorPage";
import { SignalPage } from "./pages/SignalPage";
import { GatePage } from "./pages/GatePage";
import "./tokens.css";

const API_URL = import.meta.env.VITE_API_URL ?? ""; // Empty string allows relative paths via nginx proxy

function AppContent() {
  const navigate = useNavigate();
  const { events, connected, frozenAction } = useEventStream();

  const handleRunAgent = async (scenario: string) => {
    try {
      const response = await fetch(`${API_URL}/api/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario }),
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

  const decided = events.some((e) => e.event_type === "OPERATOR_DECISION");
  const gateNeedsAttention = Boolean(frozenAction) && !decided;

  return (
    <AppShell connected={connected} gateNeedsAttention={gateNeedsAttention} wide>
      <Routes>
        <Route
          path="/"
          element={
            <MonitorPage
              events={events}
              frozenAction={gateNeedsAttention ? frozenAction : null}
              onViewGate={() => navigate("/gate")}
              onRunAgent={handleRunAgent}
            />
          }
        />
        <Route
          path="/signals"
          element={
            <SignalPage
              events={events}
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
            />
          }
        />
      </Routes>
    </AppShell>
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
