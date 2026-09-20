"use client";

import { signIn } from "next-auth/react";
import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

function LoginInner() {
  const params = useSearchParams();
  const error = params.get("error");

  return (
    <main style={styles.wrap}>
      <div style={styles.card}>
        <span style={styles.eyebrow}>Fundación Voz Pública</span>
        <h1 style={styles.title}>Radiografía de Sueldos</h1>
        <p style={styles.desc}>
          Acceso restringido a colaboradores de la fundación. Inicia sesión
          con tu cuenta institucional.
        </p>

        {error && (
          <div style={styles.error}>
            {error === "AccessDenied"
              ? "Esa cuenta no pertenece a Fundación Voz Pública. Si crees que es un error, contacta al administrador del sitio."
              : "No se pudo iniciar sesión. Intenta de nuevo."}
          </div>
        )}

        <button
          style={{ ...styles.btn, ...styles.google }}
          onClick={() => signIn("google", { callbackUrl: "/" })}
        >
          Continuar con Google
        </button>
      </div>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginInner />
    </Suspense>
  );
}

const styles: Record<string, React.CSSProperties> = {
  wrap: {
    minHeight: "100dvh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#f9f9f7",
    fontFamily:
      'system-ui, -apple-system, "Segoe UI", sans-serif',
    padding: 16,
  },
  card: {
    background: "#fcfcfb",
    border: "1px solid rgba(11,11,11,0.10)",
    borderRadius: 16,
    padding: "32px 28px",
    maxWidth: 380,
    width: "100%",
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  eyebrow: {
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: "#2a78d6",
  },
  title: { fontSize: 24, fontWeight: 800, margin: "2px 0 4px" },
  desc: { fontSize: 14, color: "#52514e", lineHeight: 1.5, marginBottom: 12 },
  error: {
    background: "#fbe9e9",
    color: "#8a2020",
    fontSize: 13,
    padding: "10px 12px",
    borderRadius: 10,
    marginBottom: 4,
  },
  btn: {
    border: "1px solid rgba(11,11,11,0.14)",
    borderRadius: 10,
    padding: "11px 16px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    background: "#fff",
    color: "#0b0b0b",
  },
  google: {},
};
