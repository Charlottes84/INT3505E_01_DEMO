import { Elysia, t } from 'elysia';
import { db } from '../db';
import { productsTable } from '../db/schema';
import { eq } from 'drizzle-orm';

export const products = (app: Elysia) => 
  app.group('/products', (app) => 
    app
      .get('/', () => {
        return db.query.productsTable.findMany({
          with: { artist: true, images: true },
        });
      })
      .get('/:id', async ({ params, set }) => {
        const product = await db.query.productsTable.findFirst({
            where: eq(productsTable.id, params.id),
            with: { artist: true, images: true }
        });
        if (!product) {
            set.status = 404;
            return { error: `Không tìm thấy sản phẩm` };
        }
        return product;
      }, {
        params: t.Object({ id: t.Numeric() })
      })
  );