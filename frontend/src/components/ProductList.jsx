import React, { useState, useEffect } from 'react';
import { Search, Barcode, Package, Edit2, Trash2, Save, X, Scan } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { toast } from 'sonner';
import { updateProductBarcode, updateProductActualQuantity, deleteProductBarcode, searchProducts } from '../lib/db';
import { useNavigate } from 'react-router-dom';

export const ProductList = ({ products, hasBarcode, onUpdate }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredProducts, setFilteredProducts] = useState(products);
  const [editingId, setEditingId] = useState(null);
  const [editBarcode, setEditBarcode] = useState('');
  const [editQuantity, setEditQuantity] = useState('');

  useEffect(() => {
    const filtered = products.filter(p => {
      const query = searchQuery.toLowerCase();
      return p.name.toLowerCase().includes(query) || 
             p.nomenclature_code.toLowerCase().includes(query);
    });
    setFilteredProducts(filtered);
  }, [searchQuery, products]);

  const handleEdit = (product) => {
    setEditingId(product.id);
    setEditBarcode(product.barcode || '');
    setEditQuantity(product.actual_quantity !== null ? String(product.actual_quantity) : '');
  };

  const handleSave = async (id) => {
    try {
      await updateProductBarcode(id, editBarcode, editQuantity ? parseFloat(editQuantity) : null);
      setEditingId(null);
      toast.success('Данные обновлены');
      onUpdate();
    } catch (error) {
      toast.error('Ошибка при сохранении');
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteProductBarcode(id);
      toast.success('Штрихкод удален');
      onUpdate();
    } catch (error) {
      toast.error('Ошибка при удалении');
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditBarcode('');
    setEditQuantity('');
  };

  const handleQuantityUpdate = async (id, value) => {
    try {
      const quantity = value ? parseFloat(value) : null;
      await updateProductActualQuantity(id, quantity);
      toast.success('Количество обновлено');
      onUpdate();
    } catch (error) {
      toast.error('Ошибка при обновлении количества');
    }
  };

  return (
    <div className="space-y-4">
      <div className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80 pb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-5 w-5" />
          <Input
            placeholder="Поиск по названию или накладному номеру..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 h-12 text-base"
          />
        </div>
      </div>

      <div className="space-y-3">
        {filteredProducts.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Package className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground text-center">Нет товаров</p>
            </CardContent>
          </Card>
        ) : (
          filteredProducts.map((product) => (
            <Card key={product.id} className="product-card">
              <CardContent className="p-4">
                <div className="space-y-3">
                  {/* Product Name and Stock */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-base line-clamp-2">
                        {product.name}
                      </h3>
                      {product.nomenclature_code && (
                        <p className="text-sm text-muted-foreground mt-1">
                          № {product.nomenclature_code}
                        </p>
                      )}
                    </div>
                    <Badge variant="secondary" className="shrink-0">
                      {product.stock_quantity} шт
                    </Badge>
                  </div>

                  {/* Barcode Display/Edit */}
                  {editingId === product.id ? (
                    <div className="space-y-2">
                      <Input
                        placeholder="Штрихкод"
                        value={editBarcode}
                        onChange={(e) => setEditBarcode(e.target.value)}
                        className="h-10"
                      />
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="Количество по факту"
                        value={editQuantity}
                        onChange={(e) => setEditQuantity(e.target.value)}
                        className="h-10"
                      />
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleSave(product.id)}
                          className="flex-1"
                        >
                          <Save className="h-4 w-4 mr-2" />
                          Сохранить
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={handleCancel}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <>
                      {product.barcode && (
                        <>
                          <div className="flex items-center gap-2 px-3 py-2 bg-muted/50 rounded-md">
                            <Barcode className="h-4 w-4 text-primary shrink-0" />
                            <span className="text-sm font-mono flex-1 truncate">
                              {product.barcode}
                            </span>
                          </div>

                          {/* Actual Quantity - Only for products WITH barcode */}
                          <div className="flex items-center gap-2">
                            <label className="text-sm font-medium text-muted-foreground shrink-0">
                              По факту:
                            </label>
                            <Input
                              type="number"
                              step="0.01"
                              placeholder="0"
                              value={product.actual_quantity !== null ? product.actual_quantity : ''}
                              onChange={(e) => handleQuantityUpdate(product.id, e.target.value)}
                              className="h-9 flex-1"
                            />
                            <span className="text-sm text-muted-foreground shrink-0">шт</span>
                          </div>

                          {/* Action Buttons - Only for products WITH barcode */}
                          <div className="flex gap-2 pt-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleEdit(product)}
                              className="flex-1"
                            >
                              <Edit2 className="h-4 w-4 mr-2" />
                              Редактировать
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleDelete(product.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </>
                      )}
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};