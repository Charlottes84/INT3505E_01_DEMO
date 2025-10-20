// drizzle.config.ts
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/db/schema.ts', // Đường dẫn tới file schema
  out: './drizzle',              // Thư mục chứa các file migration (nếu có)
  dialect: 'sqlite',             // Loại cơ sở dữ liệu
  driver: 'turso',               // Driver bạn đang dùng
  dbCredentials: {
    url: process.env.TURSO_PRODUCTS_DATABASE_URL!, // Lấy URL từ file .env
    authToken: process.env.TURSO_PRODUCTS_AUTH_TOKEN,   // Lấy token từ file .env
  },
});