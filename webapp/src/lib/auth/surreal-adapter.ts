import type { Adapter, AdapterUser, AdapterAccount, AdapterSession } from "next-auth/adapters";
import { getSurrealClient } from "@/lib/surreal/client";

interface SurrealUserRow {
  id: string;
  email: string;
  name: string;
  emailVerified: string;
  image: string;
  role: string;
  subscription_tier: string;
  password_hash?: string;
}

interface SurrealAccountRow {
  userId: string;
  type: string;
  provider: string;
  providerAccountId: string;
  refresh_token?: string;
  access_token?: string;
  expires_at?: number;
  token_type?: string;
  scope?: string;
  id_token?: string;
  session_state?: string;
}

interface SurrealSessionRow {
  sessionToken: string;
  userId: string;
  expires: string;
}

export function SurrealDBAdapter(): Adapter {
  return {
    async createUser(user: AdapterUser): Promise<AdapterUser> {
      const db = await getSurrealClient();
      const id = `users:${user.id}`;
      await db.create(id, {
        id,
        email: user.email,
        name: user.name,
        emailVerified: user.emailVerified?.toISOString() ?? null,
        image: user.image,
        role: "public",
        subscription_tier: "free",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      return { ...user, id: user.id } as AdapterUser;
    },

    async getUser(id: string): Promise<AdapterUser | null> {
      const db = await getSurrealClient();
      const result = await db.query("SELECT * FROM users WHERE id = $id", { id: `users:${id}` });
      const rows = result as unknown[];
      const u = rows?.[0] as SurrealUserRow | undefined;
      if (!u) return null;
      return {
        id: u.id.replace("users:", ""),
        email: u.email,
        name: u.name,
        emailVerified: u.emailVerified ? new Date(u.emailVerified) : null,
        image: u.image,
      } as AdapterUser;
    },

    async getUserByEmail(email: string): Promise<AdapterUser | null> {
      const db = await getSurrealClient();
      const result = await db.query("SELECT * FROM users WHERE email = $email", { email });
      const rows = result as unknown[];
      const u = rows?.[0] as SurrealUserRow | undefined;
      if (!u) return null;
      return {
        id: u.id.replace("users:", ""),
        email: u.email,
        name: u.name,
        emailVerified: u.emailVerified ? new Date(u.emailVerified) : null,
        image: u.image,
      } as AdapterUser;
    },

    async getUserByAccount({ provider, providerAccountId }: Pick<AdapterAccount, "provider" | "providerAccountId">): Promise<AdapterUser | null> {
      const db = await getSurrealClient();
      const result = await db.query("SELECT * FROM accounts WHERE provider = $provider AND providerAccountId = $paid", {
        provider,
        paid: providerAccountId,
      });
      const rows = result as unknown[];
      const acc = rows?.[0] as SurrealAccountRow | undefined;
      if (!acc) return null;
      return this.getUser ? this.getUser(acc.userId) : null;
    },

    async updateUser(user: Partial<AdapterUser> & { id: string }): Promise<AdapterUser> {
      const db = await getSurrealClient();
      await db.merge(`users:${user.id}`, {
        name: user.name,
        email: user.email,
        image: user.image,
        emailVerified: user.emailVerified?.toISOString() ?? null,
        updated_at: new Date().toISOString(),
      });
      return { ...user } as AdapterUser;
    },

    async deleteUser(userId: string): Promise<void> {
      const db = await getSurrealClient();
      await db.delete(`users:${userId}`);
    },

    async linkAccount(account: AdapterAccount): Promise<void> {
      const db = await getSurrealClient();
      const id = `accounts:${crypto.randomUUID()}`;
      await db.create(id, {
        id,
        userId: account.userId,
        type: account.type,
        provider: account.provider,
        providerAccountId: account.providerAccountId,
        refresh_token: account.refresh_token,
        access_token: account.access_token,
        expires_at: account.expires_at,
        token_type: account.token_type,
        scope: account.scope,
        id_token: account.id_token,
        session_state: account.session_state as string,
      });
    },

    async unlinkAccount({ provider, providerAccountId }: Pick<AdapterAccount, "provider" | "providerAccountId">): Promise<void> {
      const db = await getSurrealClient();
      await db.query("DELETE FROM accounts WHERE provider = $provider AND providerAccountId = $paid", {
        provider,
        paid: providerAccountId,
      });
    },

    async createSession(session: { sessionToken: string; userId: string; expires: Date }): Promise<AdapterSession> {
      const db = await getSurrealClient();
      const id = `sessions:${crypto.randomUUID()}`;
      await db.create(id, {
        id,
        sessionToken: session.sessionToken,
        userId: session.userId,
        expires: session.expires.toISOString(),
      });
      return session as AdapterSession;
    },

    async getSessionAndUser(sessionToken: string): Promise<{ session: AdapterSession; user: AdapterUser } | null> {
      const db = await getSurrealClient();
      const result = await db.query("SELECT * FROM sessions WHERE sessionToken = $token", { token: sessionToken });
      const rows = result as unknown[];
      const s = rows?.[0] as SurrealSessionRow | undefined;
      if (!s) return null;
      const user = await (this.getUser ? this.getUser(s.userId) : null);
      if (!user) return null;
      return { session: { sessionToken: s.sessionToken, userId: s.userId, expires: new Date(s.expires) }, user };
    },

    async updateSession(session: { sessionToken: string; userId: string; expires: Date }): Promise<AdapterSession> {
      const db = await getSurrealClient();
      await db.query("UPDATE sessions SET expires = $expires WHERE sessionToken = $token", {
        token: session.sessionToken,
        expires: session.expires.toISOString(),
      });
      return session as AdapterSession;
    },

    async deleteSession(sessionToken: string): Promise<void> {
      const db = await getSurrealClient();
      await db.query("DELETE FROM sessions WHERE sessionToken = $token", { token: sessionToken });
    },

    async createVerificationToken(token: { identifier: string; token: string; expires: Date }): Promise<{ identifier: string; token: string; expires: Date }> {
      const db = await getSurrealClient();
      const id = `verification_tokens:${crypto.randomUUID()}`;
      await db.create(id, { id, identifier: token.identifier, token: token.token, expires: token.expires.toISOString() });
      return token;
    },

    async useVerificationToken({ identifier, token }: { identifier: string; token: string }): Promise<{ identifier: string; token: string; expires: Date } | null> {
      const db = await getSurrealClient();
      const result = await db.query("SELECT * FROM verification_tokens WHERE identifier = $id AND token = $token", { id: identifier, token });
      const rows = result as unknown[];
      const vt = rows?.[0] as { identifier: string; token: string; expires: string } | undefined;
      if (!vt) return null;
      await db.query("DELETE FROM verification_tokens WHERE identifier = $id AND token = $token", { id: identifier, token });
      return { identifier: vt.identifier, token: vt.token, expires: new Date(vt.expires) };
    },
  };
}
