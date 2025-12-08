export const loadExcelFile = async () => {
  try {
    const response = await fetch('/sample_file.xls');
    if (!response.ok) {
      throw new Error('Failed to load Excel file');
    }
    
    const arrayBuffer = await response.arrayBuffer();
    const XLSX = await import('xlsx');
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    const range = XLSX.utils.decode_range(sheet['!ref']);
    
    const products = [];
    let rowIdx = 9; // Start from row 10 (0-indexed)
    
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
        
        if (!isCode && cellValue && cellValue !== 'Итого') {
          const quantityCell = sheet[XLSX.utils.encode_cell({ r: rowIdx + 1, c: 2 })];
          const quantity = quantityCell ? Number(quantityCell.v) : 0;
          
          // Get nomenclature code from 2 rows ahead
          let nomenclatureCode = '';
          const codeCell = sheet[XLSX.utils.encode_cell({ r: rowIdx + 2, c: 0 })];
          if (codeCell) {
            const potentialCode = String(codeCell.v).trim();
            const cleanCode = potentialCode.replace(/\s/g, '');
            if (/^\d+$/.test(cleanCode)) {
              nomenclatureCode = potentialCode;
            }
          }
          
          products.push({
            id: products.length + 1,
            name: cellValue,
            nomenclature_code: nomenclatureCode,
            stock_quantity: quantity,
            barcode: '',
            actual_quantity: null
          });
        }
        
        rowIdx += 2;
      } else {
        rowIdx++;
      }
    }
    
    return products;
  } catch (error) {
    console.error('Error loading Excel file:', error);
    throw error;
  }
};