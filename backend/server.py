from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import xlrd
import xlwt
from xlutils.copy import copy as xl_copy


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks


class Product(BaseModel):
    id: int
    name: str
    nomenclature_code: str
    stock_quantity: float
    barcode: Optional[str] = ""
    actual_quantity: Optional[float] = None


@api_router.post("/export-excel")
async def export_excel(products: List[Product]):
    """
    Export Excel with all products, maintaining original formatting
    Data is written to the same row as product name (column 8 and 9)
    """
    try:
        # Load original file with formatting
        original_path = '/app/sample_file.xls'
        rb = xlrd.open_workbook(original_path, formatting_info=True)
        wb = xl_copy(rb)
        sheet = wb.get_sheet(0)
        
        # Create product map
        product_map = {p.name: p for p in products}
        
        # Update products in Excel
        row_idx = 9  # Start from row 10
        original_sheet = rb.sheet_by_index(0)
        
        logger.info(f"Starting Excel export with {len(products)} products")
        updated_count = 0
        
        while row_idx < original_sheet.nrows:
            try:
                cell_a = original_sheet.cell(row_idx, 0)
                cell_b = original_sheet.cell(row_idx + 1, 1) if row_idx + 1 < original_sheet.nrows else None
                
                if not cell_a.value:
                    row_idx += 1
                    continue
                
                cell_value = str(cell_a.value).strip()
                next_cell_value = str(cell_b.value).strip() if cell_b else ''
                
                if next_cell_value == 'Кол.':
                    clean_name = cell_value.replace(' ', '')
                    is_code = clean_name.isdigit()
                    
                    if not is_code and cell_value and cell_value != 'Итого' and cell_value in product_map:
                        product = product_map[cell_value]
                        
                        # Write barcode to column 8 (same row as product name)
                        if product.barcode:
                            sheet.write(row_idx, 8, product.barcode)
                            # Also write to code row (2 rows down)
                            if row_idx + 2 < original_sheet.nrows:
                                sheet.write(row_idx + 2, 8, product.barcode)
                        
                        # Write actual quantity to column 9 (same row as product name)
                        if product.actual_quantity is not None:
                            sheet.write(row_idx, 9, product.actual_quantity)
                            # Also write to code row (2 rows down)
                            if row_idx + 2 < original_sheet.nrows:
                                sheet.write(row_idx + 2, 9, product.actual_quantity)
                        
                        updated_count += 1
                    
                    row_idx += 2
                else:
                    row_idx += 1
            except Exception as e:
                logger.error(f"Error processing row {row_idx}: {e}")
                row_idx += 1
        
        logger.info(f"Updated {updated_count} products in Excel")
        
        # Save to temporary file
        timestamp = datetime.now().strftime("%Y-%m-%d")
        output_path = f'/tmp/updated_inventory_{timestamp}.xls'
        wb.save(output_path)
        
        logger.info(f"Excel file saved to {output_path}")
        
        return FileResponse(
            output_path,
            media_type='application/vnd.ms-excel',
            filename=f'updated_inventory_{timestamp}.xls'
        )
    
    except Exception as e:
        logger.error(f"Error in export_excel: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()