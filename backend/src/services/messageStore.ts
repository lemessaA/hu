import { pool } from "../db/pool.js";

export type DbMessage = {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  image_url: string | null;
  created_at: Date;
};

export async function ensureConversation(
  conversationId: string | undefined
): Promise<string> {
  if (conversationId) {
    const check = await pool.query(
      `SELECT id FROM conversations WHERE id = $1`,
      [conversationId]
    );
    if (check.rows.length) return conversationId;
  }
  const res = await pool.query<{ id: string }>(
    `INSERT INTO conversations (title) VALUES ($1) RETURNING id`,
    ["Climate chat"]
  );
  return res.rows[0].id;
}

export async function insertMessage(params: {
  conversationId: string;
  role: "user" | "assistant" | "system";
  content: string;
  imageUrl?: string | null;
}): Promise<DbMessage> {
  const res = await pool.query<DbMessage>(
    `INSERT INTO messages (conversation_id, role, content, image_url)
     VALUES ($1, $2, $3, $4)
     RETURNING id, conversation_id, role, content, image_url, created_at`,
    [
      params.conversationId,
      params.role,
      params.content,
      params.imageUrl ?? null,
    ]
  );
  return res.rows[0];
}

export async function listRecentAdvice(limit = 20): Promise<
  {
    id: string;
    content: string;
    created_at: Date;
    conversation_id: string;
  }[]
> {
  const res = await pool.query(
    `SELECT id, content, created_at, conversation_id
     FROM messages
     WHERE role = 'assistant' AND content <> ''
     ORDER BY created_at DESC
     LIMIT $1`,
    [limit]
  );
  return res.rows;
}

export async function listMessagesForConversation(
  conversationId: string,
  limit = 100
): Promise<DbMessage[]> {
  const res = await pool.query<DbMessage>(
    `SELECT id, conversation_id, role, content, image_url, created_at
     FROM messages
     WHERE conversation_id = $1
     ORDER BY created_at ASC
     LIMIT $2`,
    [conversationId, limit]
  );
  return res.rows;
}
