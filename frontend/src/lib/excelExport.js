export const exportToExcel = async (products) => {
  try {
    const XLSX = await import('xlsx');
    
    // Load the original file
    const response = await fetch('/sample_file.xls');
    const arrayBuffer = await response.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    const range = XLSX.utils.decode_range(sheet['!ref']);
    
    // Create a map of products by name for quick lookup
    const productMap = new Map();
    products.forEach(p => {
      productMap.set(p.name, p);
    });
    
    let rowIdx = 9;
    
    while (rowIdx < range.e.r) {
      const cellA = sheet[XLSX.utils.encode_cell({ r: rowIdx, c: 0 })];
      const cellB = sheet[XLSX.utils.encode_cell({ r: rowIdx + 1, c: 1 })];
      
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
          
          // Add barcode column (assuming column 6 or add new column)
          if (product.barcode) {
            const barcodeCell = XLSX.utils.encode_cell({ r: rowIdx, c: 6 });
            sheet[barcodeCell] = { v: product.barcode, t: 's' };
          }
          
          // Update actual quantity in row below (where "Кол." is)
          if (product.actual_quantity !== null && product.actual_quantity !== undefined) {
            const actualQtyCell = XLSX.utils.encode_cell({ r: rowIdx + 1, c: 3 });
            sheet[actualQtyCell] = { v: product.actual_quantity, t: 'n' };
          }
        }
        
        rowIdx += 2;
      } else {
        rowIdx++;
      }
    }
    
    // Extend range if needed for new column
    const newRange = {
      s: { r: range.s.r, c: range.s.c },
      e: { r: range.e.r, c: Math.max(range.e.c, 6) }
    };
    sheet['!ref'] = XLSX.utils.encode_range(newRange);
    
    // Generate file
    const wbout = XLSX.write(workbook, { bookType: 'xls', type: 'array' });
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