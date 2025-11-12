import { test, expect } from "bun:test";
import { app } from "../app";

test("GET /users returns array", async () => {
  const res = await app.handle(new Request("http://localhost:3000/users"));
  expect(res.status).toBe(200);
  const data = await res.json();
  expect(Array.isArray(data)).toBe(true);
});

test("POST /users creates new user", async () => {
  const res = await app.handle(
    new Request("http://localhost:3000/users", {
      method: "POST",
      body: JSON.stringify({ name: "Bob" }),
      headers: { "Content-Type": "application/json" },
    })
  );
  expect(res.status).toBe(200);
  const data = await res.json();
  expect(data.name).toBe("Bob");
});
