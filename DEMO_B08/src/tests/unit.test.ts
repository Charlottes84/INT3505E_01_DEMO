import { test, expect } from "bun:test";
import { formatUserName } from "../userService";

test("should convert to uppercase", () => {
  expect(formatUserName("john")).toBe("JOHN");
});

test("should trim spaces", () => {
  expect(formatUserName("  alice ")).toBe("ALICE");
});

test("should throw error if invalid", () => {
  expect(() => formatUserName(123 as any)).toThrow("Invalid name");
});
