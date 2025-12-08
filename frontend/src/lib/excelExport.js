export const exportToExcel = async (products) => {
  try {
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
    
    console.log(`📦 Exporting ${products.length} products to backend`);
    
    // Log first few products with barcodes for debugging
    const productsWithBarcode = products.filter(p => p.barcode && p.barcode !== '');
    console.log(`📊 Products with barcodes: ${productsWithBarcode.length}`);
    productsWithBarcode.slice(0, 3).forEach((p, idx) => {
      console.log(`  Product ${idx + 1}: "${p.name}" | Barcode: ${p.barcode} | Qty: ${p.actual_quantity}`);
    });
    
    // Send products to backend for proper Excel export with formatting preservation
    const response = await fetch(`${BACKEND_URL}/api/export-excel`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(products),
    });
    
    if (!response.ok) {
      throw new Error(`Export failed: ${response.status} ${response.statusText}`);
    }
    
    // Get the file as blob
    const blob = await response.blob();
    
    // Download the file
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `updated_inventory_${new Date().toISOString().split('T')[0]}.xls`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error exporting Excel file:', error);
    throw error;
  }
};