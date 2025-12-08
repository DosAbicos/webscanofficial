#!/usr/bin/env python3
"""
Test exact matching between app and Excel export
Shows detailed comparison to find any discrepancies
"""

import sys
import xlrd
import requests
import json

def test_exact_match():
    print("=" * 80)
    print("EXACT MATCH TEST - Compare App Data vs Excel Export")
    print("=" * 80)
    
    # Test with 5 products with unique barcodes
    products = [
        {
            "id": 1,
            "name": "IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (10L)",
            "nomenclature_code": "20002755",
            "stock_quantity": 15.0,
            "barcode": "BAR001",
            "actual_quantity": 10.5
        },
        {
            "id": 2,
            "name": "IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (2,5L)",
            "nomenclature_code": "20002659",
            "stock_quantity": 25.0,
            "barcode": "BAR002",
            "actual_quantity": 20.3
        },
        {
            "id": 3,
            "name": "КРАСКА ПОЛИЭФИРНАЯ BORITEX CLASSIC CHERRY 6 (0,75L)",
            "nomenclature_code": "20002634",
            "stock_quantity": 30.0,
            "barcode": "BAR003",
            "actual_quantity": 25.7
        },
        {
            "id": 4,
            "name": "КРАСКА ПОЛИЭФИРНАЯ BORITEX CLASSIC WALNUT 4 (0,75L)",
            "nomenclature_code": "20002620",
            "stock_quantity": 60.0,
            "barcode": "BAR004",
            "actual_quantity": 55.1
        },
        {
            "id": 5,
            "name": "КРАСКА ПОЛИЭФИРНАЯ BORITEX ULTRA CHERRY 6 (0,75L)",
            "nomenclature_code": "20002652",
            "stock_quantity": 30.0,
            "barcode": "BAR005",
            "actual_quantity": 27.9
        }
    ]
    
    print(f"\n📱 APP DATA (what should be in Excel):")
    print("-" * 80)
    for p in products:
        print(f"ID {p['id']}: {p['name'][:50]}")
        print(f"  Barcode: {p['barcode']}")
        print(f"  Quantity: {p['actual_quantity']}")
        print()
    
    # First, call debug endpoint to see matches
    print("\n🔍 Calling debug endpoint...")
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
        
        if debug_data.get('unmatched_products'):
            print(f"\n⚠️  UNMATCHED PRODUCTS:")
            for up in debug_data.get('unmatched_products', []):
                print(f"    - {up['name']} | Barcode: {up['barcode']}")
    
    # Now export
    print("\n📤 Exporting to Excel...")
    response = requests.post(
        'http://localhost:8001/api/export-excel',
        json=products,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ Export failed: {response.status_code}")
        return False
    
    # Save and analyze
    output_file = '/tmp/exact_match_test.xls'
    with open(output_file, 'wb') as f:
        f.write(response.content)
    
    print(f"✅ File saved: {output_file}")
    
    # Read and compare
    print("\n📖 Reading exported Excel...")
    wb = xlrd.open_workbook(output_file)
    sheet = wb.sheet_by_index(0)
    
    # Extract all data from Excel
    excel_data = {}
    for row_idx in range(9, min(500, sheet.nrows)):
        col_0 = str(sheet.cell(row_idx, 0).value).strip()
        col_8 = str(sheet.cell(row_idx, 8).value).strip()
        col_9 = str(sheet.cell(row_idx, 9).value).strip()
        
        if col_8:  # Has barcode
            # Skip codes (rows with only digits)
            if col_0:
                clean = col_0.replace(' ', '')
                if not clean.isdigit():
                    excel_data[col_8] = {
                        'name': col_0,
                        'barcode': col_8,
                        'quantity': float(col_9) if col_9 else None,
                        'row': row_idx + 1
                    }
    
    print(f"\n📊 EXCEL EXPORT (what was actually written):")
    print("-" * 80)
    for barcode, data in sorted(excel_data.items()):
        print(f"Row {data['row']}: {data['name'][:50]}")
        print(f"  Barcode: {data['barcode']}")
        print(f"  Quantity: {data['quantity']}")
        print()
    
    # Compare
    print("\n🔍 COMPARISON:")
    print("=" * 80)
    
    all_match = True
    
    for p in products:
        print(f"\n{p['name'][:50]}")
        
        if p['barcode'] in excel_data:
            excel_p = excel_data[p['barcode']]
            
            # Check name
            if p['name'] == excel_p['name']:
                print(f"  ✅ Name: Match")
            else:
                print(f"  ❌ Name: Mismatch")
                print(f"     App: {p['name']}")
                print(f"     Excel: {excel_p['name']}")
                all_match = False
            
            # Check barcode
            if p['barcode'] == excel_p['barcode']:
                print(f"  ✅ Barcode: {p['barcode']}")
            else:
                print(f"  ❌ Barcode mismatch")
                all_match = False
            
            # Check quantity
            if p['actual_quantity'] == excel_p['quantity']:
                print(f"  ✅ Quantity: {p['actual_quantity']}")
            else:
                print(f"  ❌ Quantity mismatch")
                print(f"     App: {p['actual_quantity']}")
                print(f"     Excel: {excel_p['quantity']}")
                all_match = False
        else:
            print(f"  ❌ NOT FOUND IN EXCEL!")
            print(f"     Barcode: {p['barcode']}")
            print(f"     Quantity: {p['actual_quantity']}")
            all_match = False
    
    # Check for extra items in Excel
    app_barcodes = {p['barcode'] for p in products}
    extra_in_excel = set(excel_data.keys()) - app_barcodes
    
    if extra_in_excel:
        print(f"\n⚠️  EXTRA ITEMS IN EXCEL (not in app):")
        for barcode in extra_in_excel:
            data = excel_data[barcode]
            print(f"  - {data['name'][:50]}")
            print(f"    Barcode: {barcode}")
            all_match = False
    
    print("\n" + "=" * 80)
    if all_match:
        print("✅ PERFECT MATCH! App and Excel are 100% synchronized")
        return True
    else:
        print("❌ MISMATCH DETECTED! App and Excel data don't match")
        return False


if __name__ == '__main__':
    success = test_exact_match()
    sys.exit(0 if success else 1)
