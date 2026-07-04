import { type CSSProperties, type ReactNode } from "react";
import { NavLink } from "react-router-dom";

interface AppShellProps {
  connected: boolean;
  gateNeedsAttention: boolean;
  wide?: boolean;
  children: ReactNode;
}

const NAV_ITEMS = [
  { to: "/", label: "Monitor" },
  { to: "/signals", label: "Signals" },
  { to: "/gate", label: "Gate" },
];

export function AppShell({ connected, gateNeedsAttention, wide, children }: AppShellProps) {
  const shellStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
  };

  const navStyle: CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "32px",
    padding: "0 24px",
    height: "52px",
    borderBottom: "1px solid var(--color-border)",
    background: "var(--color-surface)",
    flexShrink: 0,
  };

  const brandStyle: CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    fontSize: "15px",
    fontWeight: 600,
    fontFamily: "var(--font-mono)",
    letterSpacing: "0.08em",
    color: "var(--color-text)",
  };

  const brandMarkStyle: CSSProperties = {
    color: "var(--color-pending)",
    fontSize: "13px",
  };

  const linksStyle: CSSProperties = {
    display: "flex",
    gap: "4px",
    flex: 1,
  };

  const linkStyle = (active: boolean): CSSProperties => ({
    display: "flex",
    alignItems: "center",
    gap: "6px",
    padding: "6px 14px",
    fontSize: "13px",
    fontWeight: 500,
    borderRadius: "var(--radius-md)",
    color: active ? "var(--color-text)" : "var(--color-text-muted)",
    background: active ? "rgba(242, 240, 235, 0.08)" : "transparent",
  });

  const attentionDotStyle: CSSProperties = {
    width: "7px",
    height: "7px",
    borderRadius: "50%",
    background: "var(--color-frozen)",
  };

  const connectionStyle: CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    fontSize: "12px",
    fontFamily: "var(--font-mono)",
    color: "var(--color-text-muted)",
  };

  const statusDotStyle: CSSProperties = {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    background: connected ? "var(--color-executed)" : "var(--color-frozen)",
  };

  const mainStyle: CSSProperties = {
    flex: 1,
    overflow: "hidden",
    display: "flex",
    justifyContent: "center",
  };

  const contentStyle: CSSProperties = {
    width: "100%",
    maxWidth: wide ? "1440px" : "1100px",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  };

  return (
    <div style={shellStyle}>
      <nav style={navStyle}>
        <div style={brandStyle}>
          <span style={brandMarkStyle}>◆</span>
          SENTINEL
        </div>
        <div style={linksStyle}>
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === "/"} style={{ textDecoration: "none" }}>
              {({ isActive }) => (
                <span style={linkStyle(isActive)}>
                  {item.label}
                  {item.to === "/gate" && gateNeedsAttention && <span style={attentionDotStyle} />}
                </span>
              )}
            </NavLink>
          ))}
        </div>
        <div style={connectionStyle}>
          <div style={statusDotStyle} />
          {connected ? "Connected" : "Disconnected"}
        </div>
      </nav>
      <main style={mainStyle}>
        <div style={contentStyle}>{children}</div>
      </main>
    </div>
  );
}
