import Dexie from 'dexie';

export const db = new Dexie('InventoryDB_v2');

// Fresh database with string primary key
db.version(1).stores({
  products: 'id, name, nomenclature_code, stock_quantity, barcode, actual_quantity'
});

export const initializeDatabase = async (products) => {
  try {
    const count = await db.products.count();
    if (count === 0) {
      await db.products.bulkAdd(products);
      console.log('Database initialized with', products.length, 'products');
    } else {
      console.log('Database already contains', count, 'products');
    }
  } catch (error) {
    console.error('Failed to initialize database:', error);
  }
};

export const getAllProducts = async () => {
  return await db.products.toArray();
};

export const getProductsWithoutBarcode = async () => {
  return await db.products.where('barcode').equals('').toArray();
};

export const getProductsWithBarcode = async () => {
  return await db.products.where('barcode').notEqual('').toArray();
};

export const updateProductBarcode = async (id, barcode, actualQuantity) => {
  return await db.products.update(id, {
    barcode: barcode,
    actual_quantity: actualQuantity !== undefined ? actualQuantity : null
  });
};

export const updateProductActualQuantity = async (id, actualQuantity) => {
  return await db.products.update(id, {
    actual_quantity: actualQuantity
  });
};

export const deleteProductBarcode = async (id) => {
  return await db.products.update(id, {
    barcode: '',
    actual_quantity: null
  });
};

export const searchProducts = async (query) => {
  if (!query) return await getAllProducts();
  
  const lowerQuery = query.toLowerCase();
  return await db.products.filter(product => {
    return product.name.toLowerCase().includes(lowerQuery) ||
           product.nomenclature_code.toLowerCase().includes(lowerQuery);
  }).toArray();
};

export const getProductById = async (id) => {
  return await db.products.get(id);
};