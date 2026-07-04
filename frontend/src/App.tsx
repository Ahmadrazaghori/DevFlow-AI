import { useEffect, useState } from "react";

/**
 * Bootstrap component for Phase 1 (scaffolding validation).
 * Replaced by the full router + layout structure in Phase 7
 * (Frontend Foundation) and Phase 8 (Dashboard & Modules).
 */
function App() {
  const [apiStatus, setApiStatus] = useState<"checking" | "up" | "down">("checking");

  useEffect(() => {
    fetch("/health")
      .then((res) => setApiStatus(res.ok ? "up" : "down"))
      .catch(() => setApiStatus("down"));
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background text-foreground">
      <h1 className="font-display text-3xl font-semibold">DevFlow AI</h1>
      <p className="text-muted-foreground">Scaffolding is live. Backend status: {apiStatus}</p>
    </div>
  );
}

export default App;
