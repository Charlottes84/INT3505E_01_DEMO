export function formatUserName(name: string): string {
  if (typeof name !== "string") throw new Error("Invalid name");
  return name.trim().toUpperCase();
}
