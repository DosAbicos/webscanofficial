#!/usr/bin/env python3
"""
Test products with same names but different nomenclature codes
Ensures they are exported to correct rows
"""

import sys
import xlrd
import requests

def test_duplicate_names():
    print("=" * 80)
    print("TEST: DUPLICATE NAMES - Same name, different codes")
    print("=" * 80)
    
    # Two products with SAME name but DIFFERENT codes (like user's issue)
    products = [
        {
            "id": 1,
            "name": "IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (2,5L)",
            "nomenclature_code": "20002659",  # First code
            "stock_quantity": 25.0,
            "barcode": "CODE_20002659",
            "actual_quantity": 20.0
        },
        {
            "id": 2,
            "name": "IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (2,5L)",  # SAME NAME!
            "nomenclature_code": "20003000",  # Different code
            "stock_quantity": 30.0,
            "barcode": "CODE_20003000",
            "actual_quantity": 25.0
        }
    ]
    
    print("\n📱 APP DATA:")
    print("-" * 80)
    for p in products:
        print(f"Name: {p['name']}")
        print(f"  Code: {p['nomenclature_code']}")
        print(f"  Barcode: {p['barcode']}")
        print(f"  Qty: {p['actual_quantity']}")
        print()
    
    # Call debug endpoint first
    print("🔍 Calling debug endpoint...")
    debug_response = requests.post(
        'http://localhost:8001/api/export-excel-debug',
        json=products,
        timeout=30
    )
    
    if debug_response.status_code == 200:
        debug_data = debug_response.json()
        print(f"\n📊 Debug Results:")
        print(f"  Total received: {debug_data.get('total_received')}")
        print(f"  Matches found: {debug_data.get('matches_found')}")
        print(f"  Unmatched: {debug_data.get('unmatched')}")
        
        print(f"\n  Matches detail:")
        for m in debug_data.get('matches', []):
            print(f"    Row {m['row']}: {m['excel_name'][:40]}")
            print(f"      Excel Code: {m.get('excel_code')}")
            print(f"      DB Code: {m.get('db_code')}")
            print(f"      Barcode: {m['barcode']}")
            print()
    
    # Export
    print("\n📤 Exporting to Excel...")
    response = requests.post(
        'http://localhost:8001/api/export-excel',
        json=products,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ Export failed: {response.status_code}")
        return False
    
    # Save and verify
    output_file = '/tmp/duplicate_names_test.xls'
    with open(output_file, 'wb') as f:
        f.write(response.content)
    
    print(f"✅ File saved: {output_file}")
    
    # Read and check
    print("\n📖 Reading exported Excel...")
    wb = xlrd.open_workbook(output_file)
    sheet = wb.sheet_by_index(0)
    
    # Find both products in Excel
    found_products = []
    
    for row_idx in range(9, min(500, sheet.nrows)):
        col_0 = str(sheet.cell(row_idx, 0).value).strip()
        col_8 = str(sheet.cell(row_idx, 8).value).strip()
        col_9 = str(sheet.cell(row_idx, 9).value).strip()
        
        # Check if this row has our test data
        if col_8 in ['CODE_20002659', 'CODE_20003000']:
            # Get the code from 2 rows down
            code_row_idx = row_idx + 2
            if code_row_idx < sheet.nrows:
                code = str(sheet.cell(code_row_idx, 0).value).strip()
                
                found_products.append({
                    'row': row_idx + 1,
                    'name': col_0,
                    'code': code,
                    'barcode': col_8,
                    'quantity': float(col_9) if col_9 else None
                })
    
    print(f"\n📊 EXCEL EXPORT:")
    print("-" * 80)
    for p in found_products:
        print(f"Row {p['row']}: {p['name'][:50]}")
        print(f"  Code: {p['code']}")
        print(f"  Barcode: {p['barcode']}")
        print(f"  Qty: {p['quantity']}")
        print()
    
    # Verify
    print("\n🔍 VERIFICATION:")
    print("=" * 80)
    
    success = True
    
    # Check we found exactly 2 products
    if len(found_products) != 2:
        print(f"❌ Expected 2 products, found {len(found_products)}")
        success = False
    else:
        print(f"✅ Found 2 products (correct count)")
    
    # Check that each code has correct data
    found_by_code = {p['code']: p for p in found_products}
    
    # Check first product (code 20002659)
    if '20002659' in found_by_code:
        p1 = found_by_code['20002659']
        if p1['barcode'] == 'CODE_20002659' and p1['quantity'] == 20.0:
            print(f"✅ Product 1 (20002659): Correct barcode and quantity")
        else:
            print(f"❌ Product 1 (20002659): Wrong data")
            print(f"   Expected: CODE_20002659 / 20.0")
            print(f"   Got: {p1['barcode']} / {p1['quantity']}")
            success = False
    else:
        print(f"❌ Product 1 (20002659): Not found in export")
        success = False
    
    # Check second product (code 20003000)
    if '20003000' in found_by_code:
        p2 = found_by_code['20003000']
        if p2['barcode'] == 'CODE_20003000' and p2['quantity'] == 25.0:
            print(f"✅ Product 2 (20003000): Correct barcode and quantity")
        else:
            print(f"❌ Product 2 (20003000): Wrong data")
            print(f"   Expected: CODE_20003000 / 25.0")
            print(f"   Got: {p2['barcode']} / {p2['quantity']}")
            success = False
    else:
        print(f"❌ Product 2 (20003000): Not found in export")
        success = False
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED!")
        print("Products with same names but different codes exported correctly!")
    else:
        print("❌ TEST FAILED!")
        print("Products not exported to correct rows")
    print("=" * 80)
    
    return success


if __name__ == '__main__':
    success = test_duplicate_names()
    sys.exit(0 if success else 1)
