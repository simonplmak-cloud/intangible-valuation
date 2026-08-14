import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import Google from "next-auth/providers/google";
import GitHub from "next-auth/providers/github";
import type { Provider } from "next-auth/providers";

const providers: Provider[] = [
  Credentials({
    credentials: { email: {}, password: {} },
    authorize: async (credentials) => {
      const email = credentials?.email as string | undefined;
      const password = credentials?.password as string | undefined;
      if (!email || !password) return null;

      if (process.env.NODE_ENV === "development" && email === "demo@intangiable.dev" && password === "demo") {
        return { id: "demo-user", email, name: "Demo User", role: "public" };
      }

      const { compare } = await import("bcryptjs");
      try {
        const { getSurrealClient } = await import("@/lib/surreal/client");
        const db = await getSurrealClient();
        const [rows] = await db.query<
          [{ id: string; email: string; name: string; password_hash: string; role: string }[]]
        >("SELECT * FROM users WHERE email = $email", { email });

        const user = rows?.[0];
        if (!user?.password_hash) return null;

        const valid = await compare(password, user.password_hash);
        if (!valid) return null;

        return { id: user.id.replace("users:", ""), email: user.email, name: user.name, role: user.role };
      } catch {
        return null;
      }
    },
  }),
];

if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
  providers.push(
    Google({ clientId: process.env.GOOGLE_CLIENT_ID, clientSecret: process.env.GOOGLE_CLIENT_SECRET })
  );
}
if (process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET) {
  providers.push(
    GitHub({ clientId: process.env.GITHUB_CLIENT_ID, clientSecret: process.env.GITHUB_CLIENT_SECRET })
  );
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers,
  basePath: "/v1/auth",
  trustHost: true,
  session: { strategy: "jwt", maxAge: 30 * 24 * 60 * 60 },
  pages: { signIn: "/sign-in", error: "/sign-in" },
  callbacks: {
    jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.role = (user as { role?: string }).role ?? "public";
      }
      return token;
    },
    session({ session, token }) {
      if (session.user) {
        const u = session.user as { id?: string; role?: string };
        u.id = token.id as string;
        u.role = (token.role as string) ?? "public";
      }
      return session;
    },
  },
});
