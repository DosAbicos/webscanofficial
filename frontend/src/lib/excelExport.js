export const exportToExcel = async (products) => {
  try {
    const XLSX = await import('xlsx');
    
    // Load the original file with full formatting preservation
    const response = await fetch('/sample_file.xls');
    const arrayBuffer = await response.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { 
      type: 'array',
      cellStyles: true,
      cellFormula: true,
      cellHTML: false,
      cellDates: true
    });
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    const range = XLSX.utils.decode_range(sheet['!ref']);
    
    // Create a map of products by name for quick lookup
    const productMap = new Map();
    products.forEach(p => {
      productMap.set(p.name, p);
    });
    
    let rowIdx = 9; // Start from row 10
    
    while (rowIdx < range.e.r) {
      const cellAAddr = XLSX.utils.encode_cell({ r: rowIdx, c: 0 });
      const cellBAddr = XLSX.utils.encode_cell({ r: rowIdx + 1, c: 1 });
      
      const cellA = sheet[cellAAddr];
      const cellB = sheet[cellBAddr];
      
      if (!cellA) {
        rowIdx++;
        continue;
      }
      
      const cellValue = cellA.v ? String(cellA.v).trim() : '';
      const nextCellValue = cellB ? String(cellB.v).trim() : '';
      
      if (nextCellValue === 'Кол.') {
        const cleanName = cellValue.replace(/\s/g, '');
        const isCode = /^\d+$/.test(cleanName);
        
        if (!isCode && cellValue && productMap.has(cellValue)) {
          const product = productMap.get(cellValue);
          
          // Column 8 = Штрихкоды (barcode column)
          if (product.barcode) {
            const barcodeAddr1 = XLSX.utils.encode_cell({ r: rowIdx, c: 8 });
            const barcodeAddr2 = XLSX.utils.encode_cell({ r: rowIdx + 2, c: 8 });
            
            // Preserve existing cell formatting if it exists, or create new cell
            sheet[barcodeAddr1] = sheet[barcodeAddr1] || {};
            sheet[barcodeAddr1].v = product.barcode;
            sheet[barcodeAddr1].t = 's';
            
            sheet[barcodeAddr2] = sheet[barcodeAddr2] || {};
            sheet[barcodeAddr2].v = product.barcode;
            sheet[barcodeAddr2].t = 's';
          }
          
          // Column 9 = Кол-во пофакту (actual quantity column)
          if (product.actual_quantity !== null && product.actual_quantity !== undefined) {
            const actualAddr1 = XLSX.utils.encode_cell({ r: rowIdx, c: 9 });
            const actualAddr2 = XLSX.utils.encode_cell({ r: rowIdx + 2, c: 9 });
            
            // Preserve existing cell formatting if it exists, or create new cell
            sheet[actualAddr1] = sheet[actualAddr1] || {};
            sheet[actualAddr1].v = product.actual_quantity;
            sheet[actualAddr1].t = 'n';
            
            sheet[actualAddr2] = sheet[actualAddr2] || {};
            sheet[actualAddr2].v = product.actual_quantity;
            sheet[actualAddr2].t = 'n';
          }
        }
        
        rowIdx += 2;
      } else {
        rowIdx++;
      }
    }
    
    // Generate file with full formatting preservation
    const wbout = XLSX.write(workbook, { 
      bookType: 'xls', 
      type: 'array',
      cellStyles: true,
      bookSST: true
    });
    const blob = new Blob([wbout], { type: 'application/vnd.ms-excel' });
    
    // Download
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