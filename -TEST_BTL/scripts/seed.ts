import { db } from '../src/db';
import { artistsTable, productsTable, productImagesTable } from '../src/db/schema';

async function seed() {
  console.log('🌱 Bắt đầu seeding...');

  await db.delete(productImagesTable);
  await db.delete(productsTable);
  await db.delete(artistsTable);
  console.log('🗑️  Đã xóa dữ liệu cũ.');

  const [artist] = await db.insert(artistsTable).values({ name: 'Vincent van Gogh' }).returning();
  const [product] = await db.insert(productsTable).values({
    title: 'Đêm đầy sao',
    artistId: artist.id,
    price: 999
  }).returning();
  await db.insert(productImagesTable).values({
    productId: product.id,
    imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1200px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg'
  });

  console.log('✨ Seeding hoàn tất!');
  process.exit(0);
}

seed();