import { withAuth } from "next-auth/middleware";

export default withAuth({
  pages: {
    signIn: "/login",
    error: "/login",
  },
});

// Protege todo excepto: la ruta de NextAuth, la página de login, y los assets internos de Next.
export const config = {
  matcher: [
    "/((?!api/auth|login|_next/static|_next/image|favicon.ico).*)",
  ],
};
