export const exportToExcel = async (products) => {
  try {
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
    
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