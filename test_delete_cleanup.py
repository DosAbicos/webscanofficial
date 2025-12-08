#!/usr/bin/env python3
"""
Test that deleted products are properly removed from export
Scenario:
1. Export 5 products with barcodes
2. Export 3 products with barcodes (2 were deleted)
3. Verify only 3 products in final export
"""

import sys
import xlrd
import requests

def test_delete_cleanup():
    print("=" * 80)
    print("TEST: DELETE CLEANUP - Products removed should not appear in export")
    print("=" * 80)
    
    # Step 1: Export 5 products
    print("\n📦 STEP 1: Export 5 products with barcodes")
    products_step1 = [
        {
            "id": 1,
            "name": "IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (10L)",
            "nomenclature_code": "20002755",
            "stock_quantity": 15.0,
            "barcode": "1111111111111",
            "actual_quantity": 10.0
        },
        {
            "id": 2,
            "name": "IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (2,5L)",
            "nomenclature_code": "20002659",
            "stock_quantity": 25.0,
            "barcode": "2222222222222",
            "actual_quantity": 20.0
        },
        {
            "id": 3,
            "name": "КРАСКА ПОЛИЭФИРНАЯ BORITEX CLASSIC CHERRY 6 (0,75L)",
            "nomenclature_code": "20002634",
            "stock_quantity": 30.0,
            "barcode": "3333333333333",
            "actual_quantity": 25.0
        },
        {
            "id": 4,
            "name": "КРАСКА ПОЛИЭФИРНАЯ BORITEX CLASSIC WALNUT 4 (0,75L)",
            "nomenclature_code": "20002620",
            "stock_quantity": 60.0,
            "barcode": "4444444444444",
            "actual_quantity": 55.0
        },
        {
            "id": 5,
            "name": "КРАСКА ПОЛИЭФИРНАЯ BORITEX ULTRA CHERRY 6 (0,75L)",
            "nomenclature_code": "20002652",
            "stock_quantity": 30.0,
            "barcode": "5555555555555",
            "actual_quantity": 27.0
        }
    ]
    
    response1 = requests.post('http://localhost:8001/api/export-excel', json=products_step1, timeout=30)
    
    if response1.status_code != 200:
        print(f"❌ Export 1 failed: {response1.status_code}")
        return False
    
    with open('/tmp/export_step1.xls', 'wb') as f:
        f.write(response1.content)
    
    # Verify step 1
    wb1 = xlrd.open_workbook('/tmp/export_step1.xls')
    sheet1 = wb1.sheet_by_index(0)
    
    count1 = 0
    for row_idx in range(9, min(200, sheet1.nrows)):
        col_8 = str(sheet1.cell(row_idx, 8).value).strip()
        if col_8 and col_8 in ['1111111111111', '2222222222222', '3333333333333', '4444444444444', '5555555555555']:
            count1 += 1
    
    print(f"✅ Step 1 complete: Found {count1} products in export")
    
    # Step 2: Export only 3 products (simulating deletion of 2 products)
    print("\n📦 STEP 2: Export 3 products (2 deleted from app)")
    products_step2 = [
        products_step1[0],  # Keep first
        products_step1[2],  # Keep third
        products_step1[4],  # Keep fifth
        # Delete second and fourth
    ]
    
    print(f"   Exporting: {len(products_step2)} products")
    print(f"   Product 1: {products_step2[0]['name'][:40]} | {products_step2[0]['barcode']}")
    print(f"   Product 2: {products_step2[1]['name'][:40]} | {products_step2[1]['barcode']}")
    print(f"   Product 3: {products_step2[2]['name'][:40]} | {products_step2[2]['barcode']}")
    
    response2 = requests.post('http://localhost:8001/api/export-excel', json=products_step2, timeout=30)
    
    if response2.status_code != 200:
        print(f"❌ Export 2 failed: {response2.status_code}")
        return False
    
    with open('/tmp/export_step2.xls', 'wb') as f:
        f.write(response2.content)
    
    # Verify step 2
    print("\n🔍 Verifying final export...")
    wb2 = xlrd.open_workbook('/tmp/export_step2.xls')
    sheet2 = wb2.sheet_by_index(0)
    
    found_barcodes = []
    for row_idx in range(9, min(200, sheet2.nrows)):
        col_8 = str(sheet2.cell(row_idx, 8).value).strip()
        if col_8 and len(col_8) > 5:  # Valid barcode
            found_barcodes.append(col_8)
    
    # Remove duplicates (code rows)
    unique_barcodes = list(set(found_barcodes))
    
    print(f"✅ Found {len(unique_barcodes)} unique products in final export")
    print(f"   Barcodes: {unique_barcodes}")
    
    # Check that ONLY the 3 expected barcodes exist
    expected_barcodes = {'1111111111111', '3333333333333', '5555555555555'}
    found_set = set(unique_barcodes)
    
    if found_set == expected_barcodes:
        print("\n✅ TEST PASSED!")
        print("   ✓ Only 3 products in export")
        print("   ✓ Deleted products (2 and 4) removed")
        print("   ✓ Correct products remain")
        return True
    else:
        print("\n❌ TEST FAILED!")
        print(f"   Expected: {expected_barcodes}")
        print(f"   Found: {found_set}")
        print(f"   Missing: {expected_barcodes - found_set}")
        print(f"   Extra: {found_set - expected_barcodes}")
        return False


if __name__ == '__main__':
    success = test_delete_cleanup()
    sys.exit(0 if success else 1)
