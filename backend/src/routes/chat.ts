import { Router } from "express";
import { z } from "zod";
import {
  ensureConversation,
  insertMessage,
  listMessagesForConversation,
} from "../services/messageStore.js";
import {
  appendToShortTermMemory,
  getShortTermMemory,
} from "../services/redisMemory.js";
import { completeChat, streamChat } from "../services/aiAgent.js";
import { uploadMiddleware, publicUploadPath } from "../middleware/upload.js";

const chatBody = z.object({
  conversationId: z.string().uuid().optional(),
  message: z.string().min(1).max(16_000),
  stream: z.boolean().optional(),
});

export const chatRouter = Router();

/** POST /api/chat — JSON message, optional streaming via SSE */
chatRouter.post("/", async (req, res, next) => {
  try {
    const parsed = chatBody.parse(req.body);
    const conversationId = await ensureConversation(parsed.conversationId);

    const userContent = parsed.message.trim();
    await insertMessage({
      conversationId,
      role: "user",
      content: userContent,
    });
    await appendToShortTermMemory(conversationId, {
      role: "user",
      content: userContent,
    });

    const memory = await getShortTermMemory(conversationId);
    const prior = memory.slice(0, -1);

    if (parsed.stream) {
      res.setHeader("Content-Type", "text/event-stream; charset=utf-8");
      res.setHeader("Cache-Control", "no-cache");
      res.setHeader("Connection", "keep-alive");
      res.flushHeaders?.();

      let full = "";
      try {
        for await (const chunk of streamChat(prior, userContent)) {
          full += chunk;
          res.write(`data: ${JSON.stringify({ token: chunk })}\n\n`);
        }
      } catch (e) {
        res.write(`data: ${JSON.stringify({ error: String(e) })}\n\n`);
      }

      const saved = await insertMessage({
        conversationId,
        role: "assistant",
        content: full || "(no content)",
      });
      await appendToShortTermMemory(conversationId, {
        role: "assistant",
        content: saved.content,
      });

      res.write(
        `data: ${JSON.stringify({
          done: true,
          conversationId,
          messageId: saved.id,
        })}\n\n`
      );
      res.end();
      return;
    }

    const reply = await completeChat(prior, userContent);
    const saved = await insertMessage({
      conversationId,
      role: "assistant",
      content: reply,
    });
    await appendToShortTermMemory(conversationId, {
      role: "assistant",
      content: reply,
    });

    res.json({
      conversationId,
      reply,
      messageId: saved.id,
      createdAt: saved.created_at,
    });
  } catch (e) {
    next(e);
  }
});

/**
 * POST /api/chat/with-image — multipart: message (text), image (file)
 */
chatRouter.post(
  "/with-image",
  uploadMiddleware.single("image"),
  async (req, res, next) => {
    try {
      const conversationId = await ensureConversation(
        req.body.conversationId
          ? String(req.body.conversationId)
          : undefined
      );
      const message = z
        .string()
        .min(1)
        .max(16_000)
        .parse(req.body.message || "");

      if (!req.file) {
        res.status(400).json({
          error: "Image file required",
          code: "IMAGE_REQUIRED",
        });
        return;
      }

      const imageUrl = publicUploadPath(req.file.filename);
      const userContent = `${message}\n\n[User attached image: ${imageUrl}]`;

      await insertMessage({
        conversationId,
        role: "user",
        content: message,
        imageUrl,
      });
      await appendToShortTermMemory(conversationId, {
        role: "user",
        content: userContent,
      });

      const memory = await getShortTermMemory(conversationId);
      const prior = memory.slice(0, -1);
      const reply = await completeChat(prior, userContent);
      const saved = await insertMessage({
        conversationId,
        role: "assistant",
        content: reply,
      });
      await appendToShortTermMemory(conversationId, {
        role: "assistant",
        content: reply,
      });

      res.json({
        conversationId,
        reply,
        imageUrl,
        messageId: saved.id,
        createdAt: saved.created_at,
      });
    } catch (e) {
      next(e);
    }
  }
);

/** GET /api/chat/history/:conversationId */
chatRouter.get("/history/:conversationId", async (req, res, next) => {
  try {
    const id = z.string().uuid().parse(req.params.conversationId);
    const rows = await listMessagesForConversation(id);
    res.json({ conversationId: id, messages: rows });
  } catch (e) {
    next(e);
  }
});

/** GET /api/chat/memory/:conversationId — short-term Redis window */
chatRouter.get("/memory/:conversationId", async (req, res, next) => {
  try {
    const id = z.string().uuid().parse(req.params.conversationId);
    const memory = await getShortTermMemory(id);
    res.json({ conversationId: id, memory });
  } catch (e) {
    next(e);
  }
});
