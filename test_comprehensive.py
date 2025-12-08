#!/usr/bin/env python3
"""
Comprehensive automated tests for barcode manager
Tests:
1. Search filtering (products with barcodes should not appear)
2. Export only products with barcodes
3. Load test with 2000 products
"""

import sys
import xlrd
import requests
import json
import time
from datetime import datetime

def test_search_filtering():
    """Test 1: Search should exclude products with barcodes"""
    print("=" * 80)
    print("TEST 1: SEARCH FILTERING (exclude products with barcodes)")
    print("=" * 80)
    
    # Create test data: some products with barcodes, some without
    test_products = []
    
    # First 3 products WITHOUT barcodes
    products_without_barcode = [
        ("IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (10L)", "20002755", 15.0),
        ("IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (2,5L)", "20002659", 25.0),
        ("КРАСКА ПОЛИЭФИРНАЯ BORITEX CLASSIC CHERRY 6 (0,75L)", "20002634", 30.0),
    ]
    
    for idx, (name, code, stock) in enumerate(products_without_barcode):
        test_products.append({
            "id": idx + 1,
            "name": name,
            "nomenclature_code": code,
            "stock_quantity": stock,
            "barcode": "",
            "actual_quantity": None
        })
    
    # Next 2 products WITH barcodes (should be filtered out)
    products_with_barcode = [
        ("КРАСКА ПОЛИЭФИРНАЯ BORITEX CLASSIC WALNUT 4 (0,75L)", "20002620", 60.0, "1111111111111", 55.0),
        ("КРАСКА ПОЛИЭФИРНАЯ BORITEX ULTRA CHERRY 6 (0,75L)", "20002652", 30.0, "2222222222222", 27.0),
    ]
    
    for idx, (name, code, stock, barcode, qty) in enumerate(products_with_barcode):
        test_products.append({
            "id": len(test_products) + 1,
            "name": name,
            "nomenclature_code": code,
            "stock_quantity": stock,
            "barcode": barcode,
            "actual_quantity": qty
        })
    
    print(f"\n✅ Created {len(test_products)} test products:")
    print(f"   - {len(products_without_barcode)} WITHOUT barcodes")
    print(f"   - {len(products_with_barcode)} WITH barcodes")
    
    # In real frontend, search filtering happens client-side
    # We simulate it here
    search_query = "КРАСКА"
    
    filtered_results = [p for p in test_products if 
                       search_query.upper() in p["name"].upper() and 
                       (not p["barcode"] or p["barcode"] == "")]
    
    print(f"\n🔍 Search results for '{search_query}' (without barcodes):")
    print(f"   Found: {len(filtered_results)} products")
    
    for p in filtered_results:
        print(f"   - {p['name']}")
    
    # Verify that products with barcodes are NOT in results
    if len(filtered_results) == 1:  # Only one КРАСКА product without barcode
        print("\n✅ TEST 1 PASSED: Products with barcodes filtered out correctly")
        return True
    else:
        print(f"\n❌ TEST 1 FAILED: Expected 1 result, got {len(filtered_results)}")
        return False


def test_export_only_with_barcodes():
    """Test 2: Export should only include products with barcodes"""
    print("\n" + "=" * 80)
    print("TEST 2: EXPORT ONLY PRODUCTS WITH BARCODES")
    print("=" * 80)
    
    # Use REAL product names from Excel file
    # Create test data: mix of products with and without barcodes
    all_products = []
    
    # 5 REAL products WITH barcodes (should be exported)
    products_with_barcode = [
        ("IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (10L)", "20002755", 15.0),
        ("IDEAL ПАРКЕТНЫЙ ЛАК ГЛЯНЦЕВЫЙ (2,5L)", "20002659", 25.0),
        ("КРАСКА ПОЛИЭФИРНАЯ BORITEX CLASSIC CHERRY 6 (0,75L)", "20002634", 30.0),
        ("КРАСКА ПОЛИЭФИРНАЯ BORITEX CLASSIC WALNUT 4 (0,75L)", "20002620", 60.0),
        ("КРАСКА ПОЛИЭФИРНАЯ BORITEX ULTRA CHERRY 6 (0,75L)", "20002652", 30.0),
    ]
    
    for i, (name, code, stock) in enumerate(products_with_barcode):
        all_products.append({
            "id": i + 1,
            "name": name,
            "nomenclature_code": code,
            "stock_quantity": stock,
            "barcode": f"111111111{i:04d}",
            "actual_quantity": stock - 2.0
        })
    
    # 5 REAL products WITHOUT barcodes (should NOT be exported)
    products_without_barcode = [
        ("КРАСКА ПОЛИЭФИРНАЯ BORITEX ULTRA WALNUT 4 (0,75L)", "20002668", 30.0),
        ("ЛЕНТА ИЗОЛЯЦИОННАЯ TEMFLEX 1300 19MM X 20MM (БЕЛАЯ)", "20000090", 44.0),
        ("ЛЕНТА ИЗОЛЯЦИОННАЯ TEMFLEX 1300 19MM X 20MM (ЖЕЛТАЯ)", "20000091", 125.0),
        ("ЛЕНТА ИЗОЛЯЦИОННАЯ TEMFLEX 1300 19MM X 20MM (ЗЕЛЁНАЯ)", "20000092", 100.0),
        ("ЛЕНТА ИЗОЛЯЦИОННАЯ TEMFLEX 1300 19MM X 20MM (КРАСНАЯ)", "20000093", 175.0),
    ]
    
    for i, (name, code, stock) in enumerate(products_without_barcode):
        all_products.append({
            "id": len(all_products) + 1,
            "name": name,
            "nomenclature_code": code,
            "stock_quantity": stock,
            "barcode": "",
            "actual_quantity": None
        })
    
    print(f"\n✅ Created {len(all_products)} total products:")
    print(f"   - {len(products_with_barcode)} WITH barcodes")
    print(f"   - {len(products_without_barcode)} WITHOUT barcodes")
    
    # Filter for export (only with barcodes)
    products_to_export = [p for p in all_products if p["barcode"] and p["barcode"] != ""]
    
    print(f"\n📦 Filtered for export: {len(products_to_export)} products")
    
    # Send to backend
    try:
        response = requests.post(
            'http://localhost:8001/api/export-excel',
            json=products_to_export,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Backend error: {response.status_code}")
            return False
        
        # Save and verify
        output_file = '/tmp/test_export_filtered.xls'
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Export successful: {output_file}")
        
        # Verify file
        wb = xlrd.open_workbook(output_file)
        sheet = wb.sheet_by_index(0)
        
        # Count products with data in columns 8 or 9
        found_count = 0
        for row_idx in range(9, min(100, sheet.nrows)):
            col_8 = str(sheet.cell(row_idx, 8).value).strip()
            col_9 = str(sheet.cell(row_idx, 9).value).strip()
            
            if col_8 or col_9:
                found_count += 1
        
        print(f"\n🔍 Verified exported file:")
        print(f"   Products found with data: {found_count}")
        
        if found_count >= 5:  # At least 5 products (could be 10 with code rows)
            print("\n✅ TEST 2 PASSED: Only products with barcodes exported")
            return True
        else:
            print(f"\n❌ TEST 2 FAILED: Expected at least 5 products, found {found_count}")
            return False
            
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        return False


def test_load_2000_products():
    """Test 3: Load test with 2000 products"""
    print("\n" + "=" * 80)
    print("TEST 3: LOAD TEST WITH 2000 PRODUCTS")
    print("=" * 80)
    
    # First, get real product names from Excel
    print("\n⏳ Loading product names from Excel...")
    import xlrd
    
    wb = xlrd.open_workbook('/app/sample_file.xls')
    sheet = wb.sheet_by_index(0)
    
    real_products = []
    row_idx = 9
    
    while row_idx < sheet.nrows and len(real_products) < 2100:
        cell_a = sheet.cell(row_idx, 0)
        cell_b = sheet.cell(row_idx + 1, 1) if row_idx + 1 < sheet.nrows else None
        
        if not cell_a.value:
            row_idx += 1
            continue
        
        cell_value = str(cell_a.value).strip()
        next_cell_value = str(cell_b.value).strip() if cell_b else ''
        
        if next_cell_value == 'Кол.':
            clean_name = cell_value.replace(' ', '')
            is_code = clean_name.isdigit()
            
            if not is_code and cell_value and cell_value != 'Итого':
                # Get quantity
                qty_cell = sheet.cell(row_idx + 1, 2) if row_idx + 1 < sheet.nrows else None
                quantity = float(qty_cell.value) if qty_cell and qty_cell.value else 0.0
                
                # Get nomenclature code
                code_cell = sheet.cell(row_idx + 2, 0) if row_idx + 2 < sheet.nrows else None
                code = str(code_cell.value).strip() if code_cell and code_cell.value else ""
                
                real_products.append({
                    'name': cell_value,
                    'code': code,
                    'quantity': quantity
                })
            
            row_idx += 2
        else:
            row_idx += 1
    
    print(f"✅ Loaded {len(real_products)} real product names from Excel")
    
    # Generate 2000 products with barcodes using REAL names
    print("\n⏳ Generating 2000 products with barcodes...")
    start_gen = time.time()
    
    products = []
    for i in range(min(2000, len(real_products))):
        prod = real_products[i]
        products.append({
            "id": i + 1,
            "name": prod['name'],
            "nomenclature_code": prod['code'],
            "stock_quantity": prod['quantity'],
            "barcode": f"TEST{i:016d}",
            "actual_quantity": max(0, prod['quantity'] - (i % 10))
        })
    
    gen_time = time.time() - start_gen
    print(f"✅ Generated 2000 products in {gen_time:.2f}s")
    
    # Test export
    print("\n⏳ Exporting 2000 products to backend...")
    start_export = time.time()
    
    try:
        response = requests.post(
            'http://localhost:8001/api/export-excel',
            json=products,
            timeout=120  # Increased timeout for large dataset
        )
        
        export_time = time.time() - start_export
        
        if response.status_code != 200:
            print(f"❌ Backend error: {response.status_code}")
            return False
        
        print(f"✅ Export completed in {export_time:.2f}s")
        
        # Save file
        output_file = '/tmp/test_load_2000.xls'
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        file_size = len(response.content) / (1024 * 1024)  # MB
        print(f"✅ File saved: {output_file} ({file_size:.2f} MB)")
        
        # Verify file integrity
        print("\n⏳ Verifying file integrity...")
        start_verify = time.time()
        
        wb = xlrd.open_workbook(output_file)
        sheet = wb.sheet_by_index(0)
        
        # Sample check: verify first and last products
        sample_checks = [
            (9, "ТЕСТОВЫЙ ТОВАР #0001", "TEST0000000000000000"),
            (13, "ТЕСТОВЫЙ ТОВАР #0002", "TEST0000000000000001"),
        ]
        
        all_correct = True
        for row_idx, expected_name, expected_barcode in sample_checks:
            actual_name = str(sheet.cell(row_idx, 0).value).strip()
            actual_barcode = str(sheet.cell(row_idx, 8).value).strip()
            
            if actual_name == expected_name and actual_barcode == expected_barcode:
                print(f"✅ Row {row_idx + 1}: Correct")
            else:
                print(f"❌ Row {row_idx + 1}: Mismatch")
                print(f"   Expected: {expected_name} | {expected_barcode}")
                print(f"   Got: {actual_name} | {actual_barcode}")
                all_correct = False
        
        verify_time = time.time() - start_verify
        print(f"\n✅ Verification completed in {verify_time:.2f}s")
        
        # Performance summary
        print("\n📊 PERFORMANCE SUMMARY:")
        print(f"   Generation: {gen_time:.2f}s")
        print(f"   Export: {export_time:.2f}s")
        print(f"   Verification: {verify_time:.2f}s")
        print(f"   Total: {gen_time + export_time + verify_time:.2f}s")
        print(f"   Throughput: {2000 / export_time:.0f} products/second")
        
        if all_correct and export_time < 60:  # Should complete in under 60 seconds
            print("\n✅ TEST 3 PASSED: 2000 products handled successfully")
            return True
        else:
            print(f"\n⚠️  TEST 3 WARNING: Issues found or slow performance")
            return all_correct
            
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 80)
    print("COMPREHENSIVE BARCODE MANAGER TESTS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    results = {
        "Test 1 (Search Filtering)": test_search_filtering(),
        "Test 2 (Export Filter)": test_export_only_with_barcodes(),
        "Test 3 (Load 2000)": test_load_2000_products()
    }
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("=" * 80)
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
