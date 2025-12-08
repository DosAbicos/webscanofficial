export const exportToExcel = async (products) => {
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
  
  // Log products with barcodes
  const productsWithBarcode = products.filter(p => p.barcode && p.barcode !== '');
  console.log(`📦 Exporting ${products.length} products`);
  console.log(`📊 Products with barcodes: ${productsWithBarcode.length}`);
  productsWithBarcode.slice(0, 3).forEach((p, idx) => {
    console.log(`  Product ${idx + 1}: "${p.name}" | Barcode: ${p.barcode} | Qty: ${p.actual_quantity}`);
  });
  
  // Try backend first (perfect formatting)
  try {
    console.log('🌐 Attempting backend export (perfect formatting)...');
    const response = await fetch(`${BACKEND_URL}/api/export-excel`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(products),
      signal: AbortSignal.timeout(5000) // 5 second timeout
    });
    
    if (response.ok) {
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `updated_inventory_${new Date().toISOString().split('T')[0]}.xls`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      console.log('✅ Backend export successful (perfect formatting)');
      return;
    }
  } catch (backendError) {
    console.log('⚠️ Backend unavailable, using offline mode:', backendError.message);
  }
  
  // Fallback to client-side export
  try {
    console.log('💾 Using offline export (may show Excel warning)...');
    
    // Load XLSX library
    const XLSX = await import('xlsx');
    
    // Load original Excel file
    const response = await fetch('/sample_file.xls');
    if (!response.ok) {
      throw new Error('Failed to load original Excel file');
    }
    
    const arrayBuffer = await response.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { 
      type: 'array',
      cellStyles: true 
    });
    
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    const range = XLSX.utils.decode_range(sheet['!ref']);
    
    console.log(`📄 Original Excel loaded: ${range.e.r + 1} rows`);
    
    // Create product map by nomenclature_code
    const productMap = {};
    products.forEach(p => {
      if (p.nomenclature_code) {
        productMap[p.nomenclature_code] = p;
      }
    });
    
    console.log(`🗺️ Product map created: ${Object.keys(productMap).length} products`);
    
    // STEP 1: Clear all data in columns 8 and 9
    console.log('🧹 Clearing old data in columns 8 and 9...');
    for (let row = 9; row <= range.e.r; row++) {
      const cellAddr8 = XLSX.utils.encode_cell({ r: row, c: 8 });
      const cellAddr9 = XLSX.utils.encode_cell({ r: row, c: 9 });
      
      if (sheet[cellAddr8]) sheet[cellAddr8].v = '';
      if (sheet[cellAddr9]) sheet[cellAddr9].v = '';
    }
    
    // STEP 2: Write new data
    console.log('✍️ Writing new data...');
    let rowIdx = 9;
    let updatedCount = 0;
    
    while (rowIdx <= range.e.r) {
      const cellAAddr = XLSX.utils.encode_cell({ r: rowIdx, c: 0 });
      const cellBAddr = XLSX.utils.encode_cell({ r: rowIdx + 1, c: 1 });
      
      const cellA = sheet[cellAAddr];
      const cellB = sheet[cellBAddr];
      
      if (!cellA || !cellA.v) {
        rowIdx++;
        continue;
      }
      
      const cellValue = String(cellA.v).trim();
      const nextCellValue = cellB && cellB.v ? String(cellB.v).trim() : '';
      
      if (nextCellValue === 'Кол.') {
        const cleanName = cellValue.replace(/\s/g, '');
        const isCode = /^\d+$/.test(cleanName);
        
        if (!isCode && cellValue && cellValue !== 'Итого') {
          // Get nomenclature code from 2 rows down
          let nomenclatureCode = '';
          if (rowIdx + 2 <= range.e.r) {
            const codeAddr = XLSX.utils.encode_cell({ r: rowIdx + 2, c: 0 });
            const codeCell = sheet[codeAddr];
            if (codeCell && codeCell.v) {
              const potentialCode = String(codeCell.v).trim();
              const cleanCode = potentialCode.replace(/\s/g, '');
              if (/^\d+$/.test(cleanCode)) {
                nomenclatureCode = potentialCode;
              }
            }
          }
          
          // Match by nomenclature code
          if (nomenclatureCode && productMap[nomenclatureCode]) {
            const product = productMap[nomenclatureCode];
            
            // Write barcode to column 8
            if (product.barcode) {
              const barcodeAddr1 = XLSX.utils.encode_cell({ r: rowIdx, c: 8 });
              const barcodeAddr2 = XLSX.utils.encode_cell({ r: rowIdx + 2, c: 8 });
              
              sheet[barcodeAddr1] = { v: product.barcode, t: 's' };
              sheet[barcodeAddr2] = { v: product.barcode, t: 's' };
            }
            
            // Write actual quantity to column 9
            if (product.actual_quantity !== null && product.actual_quantity !== undefined) {
              const qtyAddr1 = XLSX.utils.encode_cell({ r: rowIdx, c: 9 });
              const qtyAddr2 = XLSX.utils.encode_cell({ r: rowIdx + 2, c: 9 });
              
              sheet[qtyAddr1] = { v: product.actual_quantity, t: 'n' };
              sheet[qtyAddr2] = { v: product.actual_quantity, t: 'n' };
            }
            
            updatedCount++;
            console.log(`  ✓ Updated row ${rowIdx + 1}: ${cellValue.substring(0, 40)} | Code: ${nomenclatureCode}`);
          }
        }
        
        rowIdx += 2;
      } else {
        rowIdx++;
      }
    }
    
    console.log(`✅ Updated ${updatedCount} products`);
    
    // Generate Excel file in XLSX format (better compatibility)
    const wbout = XLSX.write(workbook, { 
      bookType: 'xlsx',  // Modern format - works perfectly!
      type: 'array',
      cellStyles: true 
    });
    
    const blob = new Blob([wbout], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    // Download
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `updated_inventory_${new Date().toISOString().split('T')[0]}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    console.log('✅ Offline export completed (.xlsx format)');
    console.log('ℹ️ Modern .xlsx format - no errors on Android!');
    
  } catch (error) {
    console.error('❌ Error exporting Excel file:', error);
    throw error;
  }
};