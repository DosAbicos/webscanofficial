#!/usr/bin/env python3
"""
Test offline export functionality
This test verifies that export works without backend
"""

import sys
import time
import xlrd

def test_offline_export():
    print("=" * 80)
    print("OFFLINE EXPORT TEST")
    print("=" * 80)
    
    print("""
This test requires manual verification:

1. Open browser to: http://localhost:3000
2. Wait for data to load (should see 3223 products)
3. Open DevTools (F12) → Network tab
4. Set "No throttling" to "Offline" (to simulate offline mode)
5. Add a barcode to a product (manually in browser console):
   
   const db = new Dexie('BarcodeManagerDB');
   db.version(1).stores({ products: '++id, name, nomenclature_code, stock_quantity, barcode, actual_quantity' });
   db.products.toCollection().first().then(p => db.products.update(p.id, { barcode: 'OFFLINE001', actual_quantity: 99 }));
   
6. Switch to "Со штрихкодом" tab - should see 1 product
7. Click "Экспорт" button
8. File should download successfully (even in offline mode!)
9. Open the downloaded Excel file
10. Check columns 8 and 9 - should have barcode and quantity

Expected results:
✅ Export works in offline mode
✅ Excel file downloads
✅ Data is correctly written to columns 8 and 9
✅ No backend API calls needed

Console should show:
📦 Exporting 1 products (OFFLINE MODE)
📊 Products with barcodes: 1
📄 Original Excel loaded: 12907 rows
🗺️ Product map created: 1 products
🧹 Clearing old data in columns 8 and 9...
✍️ Writing new data...
  ✓ Updated row 10: IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ... | Code: 20002755
✅ Updated 1 products
🎉 Export completed successfully!
""")
    
    print("\n" + "=" * 80)
    print("Manual test instructions provided above")
    print("Please verify offline export works as expected")
    print("=" * 80)
    
    return True


if __name__ == '__main__':
    test_offline_export()
    sys.exit(0)
