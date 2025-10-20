import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';
import * as schema from './schema';

const client = createClient({
  url: process.env.TURSO_PRODUCTS_DATABASE_URL!,
  authToken: process.env.TURSO_PRODUCTS_AUTH_TOKEN,
});

export const db = drizzle(client, { schema, logger: true });