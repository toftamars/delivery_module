#!/bin/bash

echo "🚀 Teslimat Planlama Modülü Kurulum Scripti"
echo "=========================================="

# Odoo addons dizinini bul
ODOO_ADDONS_PATH=""

# Olası Odoo addons yolları
POSSIBLE_PATHS=(
    "/opt/odoo/addons"
    "/usr/lib/python3/dist-packages/odoo/addons"
    "/var/lib/odoo/addons"
    "/home/odoo/addons"
    "~/odoo/addons"
    "/usr/local/lib/python3.*/dist-packages/odoo/addons"
)

echo "📁 Odoo addons dizini aranıyor..."
for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -d "$path" ]; then
        ODOO_ADDONS_PATH="$path"
        echo "✅ Addons dizini bulundu: $ODOO_ADDONS_PATH"
        break
    fi
done

if [ -z "$ODOO_ADDONS_PATH" ]; then
    echo "❌ Odoo addons dizini bulunamadı!"
    echo "🔧 Lütfen Odoo kurulum yolunu manuel olarak belirtin:"
    read -p "Odoo addons dizini yolu: " ODOO_ADDONS_PATH
fi

# Modül klasörünü kopyala
echo "📦 Modül kopyalanıyor..."
MODULE_SOURCE="$(pwd)"
MODULE_TARGET="$ODOO_ADDONS_PATH/teslimat_planlama"

if [ -d "$MODULE_TARGET" ]; then
    echo "⚠️  Modül zaten mevcut, güncelleniyor..."
    sudo rm -rf "$MODULE_TARGET"
fi

sudo cp -r "$MODULE_SOURCE" "$MODULE_TARGET"
echo "✅ Modül kopyalandı: $MODULE_TARGET"

# İzinleri ayarla
echo "🔒 İzinler ayarlanıyor..."
sudo chown -R odoo:odoo "$MODULE_TARGET" 2>/dev/null || echo "⚠️  Odoo kullanıcısı bulunamadı, root izinleri kullanılıyor"
sudo chmod -R 755 "$MODULE_TARGET"

echo "🔄 Odoo servisini yeniden başlatın:"
echo "   sudo systemctl restart odoo"
echo ""
echo "📋 Odoo'da modülü yüklemek için:"
echo "   1. Odoo'ya admin olarak giriş yapın"
echo "   2. Uygulamalar > Uygulamalar Güncelle'ye tıklayın"
echo "   3. 'Teslimat Modülü' arayın"
echo "   4. Yükle butonuna tıklayın"
echo ""
echo "✅ Kurulum tamamlandı!"
