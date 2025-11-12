import { Elysia } from "elysia";

export const app = new Elysia()
  .get("/users", () => [{ id: 1, name: "Alice" }])
  .post("/users", ({ body }) => {
    if (!body?.name) return new Response("Name required", { status: 400 });
    return { id: 2, name: body.name };
  });

if (import.meta.main) {
  app.listen(3000);
  console.log("🚀 Server running at http://localhost:3000");
}
