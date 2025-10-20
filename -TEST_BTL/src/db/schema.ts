import { sqliteTable, text, integer, real, int } from 'drizzle-orm/sqlite-core';
import { relations } from 'drizzle-orm';

export const artistsTable = sqliteTable('artists', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  name: text('name').notNull(),
});

export const productsTable = sqliteTable('products', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  title: text('title').notNull(),
  artistId: integer('artist_id').notNull().references(() => artistsTable.id, { onDelete: 'cascade' }),
  price: real('price').notNull(),
});

export const productImagesTable = sqliteTable('product_images', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  productId: integer('product_id').notNull().references(() => productsTable.id, { onDelete: 'cascade' }),
  imageUrl: text('image_url').notNull(),
});

export const productsRelations = relations(productsTable, ({ one, many }) => ({
  artist: one(artistsTable, {
    fields: [productsTable.artistId],
    references: [artistsTable.id],
  }),
  images: many(productImagesTable),
}));

export const artistsRelations = relations(artistsTable, ({ many }) => ({
    products: many(productsTable),
}));
  
export const productImagesRelations = relations(productImagesTable, ({ one }) => ({
    product: one(productsTable, {
        fields: [productImagesTable.productId],
        references: [productsTable.id],
    }),
}));