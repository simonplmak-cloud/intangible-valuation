import type { NextAuthOptions } from "next-auth";
import type { Adapter } from "next-auth/adapters";
import GoogleProvider from "next-auth/providers/google";
import GitHubProvider from "next-auth/providers/github";
import CredentialsProvider from "next-auth/providers/credentials";

const providers: NextAuthOptions["providers"] = [];

if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
  providers.push(
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    })
  );
}

if (process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET) {
  providers.push(
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
    })
  );
}

providers.push(
  CredentialsProvider({
    id: "credentials",
    name: "Email & Password",
    credentials: {
      email: { label: "Email", type: "email", placeholder: "you@example.com" },
      password: { label: "Password", type: "password" },
    },
    async authorize(credentials) {
      if (!credentials?.email || !credentials?.password) return null;

      if (process.env.NODE_ENV === "development") {
        if (credentials.email === "demo@intangiable.dev" && credentials.password === "demo") {
          return { id: "demo-user", email: credentials.email, name: "Demo User", role: "public" };
        }
        return null;
      }

      const { compare } = await import("bcryptjs");
      try {
        const { getSurrealClient } = await import("@/lib/surreal/client");
        const db = await getSurrealClient();
        const [rows] = await db.query<
          [{ id: string; email: string; name: string; password_hash: string; role: string }[]]
        >("SELECT * FROM users WHERE email = $email", { email: credentials.email });

        const user = rows?.[0];
        if (!user || !user.password_hash) return null;

        const valid = await compare(credentials.password, user.password_hash);
        if (!valid) return null;

        return { id: user.id.replace("users:", ""), email: user.email, name: user.name, role: user.role };
      } catch {
        return null;
      }
    },
  })
);

let adapter: Adapter | undefined;

function initAdapter(): Adapter | undefined {
  if (!process.env.SURREALDB_URL) return undefined;
  try {
    const { SurrealDBAdapter } = require("@/lib/auth/surreal-adapter");
    return SurrealDBAdapter();
  } catch {
    return undefined;
  }
}

export const authOptions: NextAuthOptions = {
  adapter: initAdapter(),
  providers,
  session: { strategy: "jwt", maxAge: 30 * 24 * 60 * 60 },
  pages: {
    signIn: "/sign-in",
    error: "/sign-in",
    newUser: "/calculator",
  },
  callbacks: {
    async jwt({ token, user, account, trigger }) {
      if (user) {
        token.id = user.id;
        token.role = (user as { role?: string }).role ?? "public";
      }
      if (account) {
        token.provider = account.provider;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        const u = session.user as { id?: string; role?: string };
        u.id = token.sub ?? (token.id as string);
        u.role = (token.role as string) ?? "public";
      }
      return session;
    },
    async signIn({ account }) {
      return true;
    },
  },
  events: {
    async createUser({ user }) {
      if (!process.env.SURREALDB_URL) return;
      try {
        const { getSurrealClient } = await import("@/lib/surreal/client");
        const db = await getSurrealClient();
        const exists = await db.query("SELECT * FROM users WHERE id = $id", { id: `users:${user.id}` });
        const existsArr = exists as unknown[];
        if (existsArr?.length) return;

        await db.create(`users:${user.id}`, {
          id: `users:${user.id}`,
          email: user.email,
          name: user.name ?? null,
          role: "public",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          subscription_tier: "free",
        });
      } catch { /* non-critical */ }
    },
  },
};
