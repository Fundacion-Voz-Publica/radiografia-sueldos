import type { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";

// Dominios de correo permitidos, ej: "fundacionvozpublica.cl,fundacionvozpublica.onmicrosoft.com"
const ALLOWED_DOMAINS = (process.env.ALLOWED_EMAIL_DOMAINS ?? "")
  .split(",")
  .map((d) => d.trim().toLowerCase())
  .filter(Boolean);

// Correos individuales permitidos aunque no calcen con un dominio de la lista de arriba
const ALLOWED_EMAILS = (process.env.ALLOWED_EMAILS ?? "")
  .split(",")
  .map((e) => e.trim().toLowerCase())
  .filter(Boolean);

const providers: NextAuthOptions["providers"] = [];

if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
  providers.push(
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    })
  );
}

export const authOptions: NextAuthOptions = {
  providers,
  session: { strategy: "jwt" },
  pages: {
    signIn: "/login",
    error: "/login",
  },
  callbacks: {
    async signIn({ user }) {
      const email = user.email?.toLowerCase();
      if (!email) return false;

      // Sin listas configuradas todavía: no dejar pasar a nadie por error de despliegue,
      // salvo que se haya definido explícitamente ALLOW_ALL=true (útil solo para pruebas locales).
      if (ALLOWED_DOMAINS.length === 0 && ALLOWED_EMAILS.length === 0) {
        return process.env.ALLOW_ALL === "true";
      }

      if (ALLOWED_EMAILS.includes(email)) return true;

      const domain = email.split("@")[1];
      if (domain && ALLOWED_DOMAINS.includes(domain)) return true;

      return false; // -> redirige a /login?error=AccessDenied
    },
    async session({ session }) {
      return session;
    },
  },
};
