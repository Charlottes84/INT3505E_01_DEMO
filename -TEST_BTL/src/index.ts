import { Elysia } from 'elysia';
import { swagger } from '@elysiajs/swagger';
import { products } from './services/products';

export const app = new Elysia()
  .use(swagger({ path: '/openapi' }))
  .group('/api/v1', (app) => app.use(products))
  .listen(3000);

console.log(`🦊 Elysia is running at http://${app.server?.hostname}:${app.server?.port}`);
console.log(`📄 API docs at http://${app.server?.hostname}:${app.server?.port}/openapi`);