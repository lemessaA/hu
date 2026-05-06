import { createServer } from "http";
import { createApp } from "./app.js";
import { config } from "./config.js";
import { migrate } from "./db/migrate.js";
import { connectRedis } from "./services/redisMemory.js";

async function main(): Promise<void> {
  await migrate();
  await connectRedis();

  const app = createApp();
  const server = createServer(app);

  server.listen(config.port, () => {
    console.log(
      JSON.stringify({
        level: "info",
        msg: "listening",
        port: config.port,
        env: config.nodeEnv,
      })
    );
  });
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
