import Redis from "ioredis";
import { config } from "../config.js";

/** Number of recent turns kept in Redis for agent context */
export const MEMORY_WINDOW = 5;

export type MemoryMessage = {
  role: "user" | "assistant" | "system";
  content: string;
};

let client: Redis | null = null;

function getRedis(): Redis {
  if (!client) {
    client = new Redis(config.redisUrl, {
      maxRetriesPerRequest: 3,
      lazyConnect: true,
    });
    client.on("error", (e) => console.error("[redis]", e.message));
  }
  return client;
}

function memoryKey(conversationId: string): string {
  return `chat:memory:${conversationId}`;
}

/**
 * Append a message to the short-term list and trim to last MEMORY_WINDOW entries.
 * Uses RPUSH + LTRIM so order is chronological (oldest → newest).
 */
export async function appendToShortTermMemory(
  conversationId: string,
  msg: MemoryMessage
): Promise<void> {
  const r = getRedis();
  const key = memoryKey(conversationId);
  const payload = JSON.stringify(msg);
  const pipeline = r.pipeline();
  pipeline.rpush(key, payload);
  pipeline.ltrim(key, -MEMORY_WINDOW, -1);
  await pipeline.exec();
}

/** Read last N messages from Redis (chronological). */
export async function getShortTermMemory(
  conversationId: string
): Promise<MemoryMessage[]> {
  const r = getRedis();
  const key = memoryKey(conversationId);
  const raw = await r.lrange(key, 0, -1);
  return raw.map((s) => JSON.parse(s) as MemoryMessage);
}

export async function connectRedis(): Promise<void> {
  await getRedis().connect().catch(() => {
    /* already connected */
  });
}
