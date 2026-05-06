import { Router } from "express";
import { listRecentAdvice } from "../services/messageStore.js";

export const adviceRouter = Router();

/** GET /api/advice/recent — dashboard feed */
adviceRouter.get("/recent", async (_req, res, next) => {
  try {
    const items = await listRecentAdvice(15);
    res.json({ items });
  } catch (e) {
    next(e);
  }
});
