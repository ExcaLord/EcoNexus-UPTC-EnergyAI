#!/bin/bash

# Script de verificación final para HackDay 2026
# Ejecutar antes de la presentación

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║              ✅ VERIFICACIÓN FINAL - HACKDAY IA MINDS 2026                 ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de checks
PASSED=0
FAILED=0

# Función para check
check() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ $2${NC}"
        ((FAILED++))
    fi
}

echo "🔍 VERIFICANDO ESTRUCTURA DEL PROYECTO..."
echo ""

# 1. Verificar entorno virtual
if [ -d "venv" ]; then
    check 0 "Entorno virtual existe"
else
    check 1 "Entorno virtual NO encontrado"
fi

# 2. Verificar archivos principales
echo ""
echo "📁 ARCHIVOS PRINCIPALES:"
[ -f "main.py" ] && check 0 "main.py" || check 1 "main.py"
[ -f "modelo_xgboost.py" ] && check 0 "modelo_xgboost.py" || check 1 "modelo_xgboost.py"
[ -f "dashboard.py" ] && check 0 "dashboard.py" || check 1 "dashboard.py"
[ -f "predecir_fecha.py" ] && check 0 "predecir_fecha.py" || check 1 "predecir_fecha.py"
[ -f "predecir_sectores.py" ] && check 0 "predecir_sectores.py" || check 1 "predecir_sectores.py"

# 3. Verificar datos
echo ""
echo "📊 DATOS:"
[ -f "data/raw/consumos_uptc.csv" ] && check 0 "Datos raw: consumos_uptc.csv" || check 1 "Datos raw"
[ -f "data/clean/consumos_uptc_clean.csv" ] && check 0 "Datos clean: consumos_uptc_clean.csv" || check 1 "Datos clean"

# 4. Verificar modelo
echo ""
echo "🤖 MODELO:"
[ -f "models/modelo_xgboost.joblib" ] && check 0 "Modelo entrenado: modelo_xgboost.joblib" || check 1 "Modelo entrenado"

# 5. Verificar outputs
echo ""
echo "📈 VISUALIZACIONES:"
[ -f "output/consumo_temporal.png" ] && check 0 "consumo_temporal.png" || check 1 "consumo_temporal.png"
[ -f "output/patron_horario.png" ] && check 0 "patron_horario.png" || check 1 "patron_horario.png"
[ -f "output/predicciones_xgboost.png" ] && check 0 "predicciones_xgboost.png" || check 1 "predicciones_xgboost.png"
[ -f "output/feature_importance_xgboost.png" ] && check 0 "feature_importance_xgboost.png" || check 1 "feature_importance_xgboost.png"

# 6. Verificar documentación
echo ""
echo "📚 DOCUMENTACIÓN:"
[ -f "README_HACKDAY.md" ] && check 0 "README_HACKDAY.md" || check 1 "README_HACKDAY.md"
[ -f "PRESENTACION_GUIA.md" ] && check 0 "PRESENTACION_GUIA.md" || check 1 "PRESENTACION_GUIA.md"

# 7. Verificar dependencias
echo ""
echo "📦 DEPENDENCIAS:"
source venv/bin/activate 2>/dev/null
python -c "import pandas" 2>/dev/null && check 0 "pandas instalado" || check 1 "pandas"
python -c "import xgboost" 2>/dev/null && check 0 "xgboost instalado" || check 1 "xgboost"
python -c "import streamlit" 2>/dev/null && check 0 "streamlit instalado" || check 1 "streamlit"
python -c "import plotly" 2>/dev/null && check 0 "plotly instalado" || check 1 "plotly"

# 8. Test rápido del pipeline
echo ""
echo "🧪 TEST FUNCIONAL:"
python -c "import dashboard" 2>/dev/null && check 0 "Dashboard importable" || check 1 "Dashboard tiene errores"

# Resumen
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 RESUMEN:"
echo -e "   ${GREEN}✅ Pasados: $PASSED${NC}"
echo -e "   ${RED}❌ Fallados: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                            ║${NC}"
    echo -e "${GREEN}║                  🎉 ¡TODO LISTO PARA LA PRESENTACIÓN! 🎉                   ║${NC}"
    echo -e "${GREEN}║                                                                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "✅ Todos los componentes están en orden"
    echo "✅ El sistema está listo para demostrar"
    echo ""
    echo "🚀 PRÓXIMOS PASOS:"
    echo "   1. Revisar PRESENTACION_GUIA.md"
    echo "   2. Practicar el demo del dashboard"
    echo "   3. Ejecutar: streamlit run dashboard.py"
    echo ""
else
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                                                                            ║${NC}"
    echo -e "${YELLOW}║                      ⚠️  HAY PROBLEMAS POR RESOLVER                        ║${NC}"
    echo -e "${YELLOW}║                                                                            ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "⚠️  Revisa los items marcados con ❌"
    echo ""
    echo "💡 SOLUCIONES COMUNES:"
    echo "   • Datos faltantes: Ejecutar 'python main.py'"
    echo "   • Modelo faltante: Ejecutar 'python modelo_xgboost.py'"
    echo "   • Dependencias: Ejecutar 'pip install -r requirements.txt'"
    echo ""
fi

# Info del sistema
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "ℹ️  INFORMACIÓN DEL SISTEMA:"
echo "   📁 Directorio: $(pwd)"
echo "   🐍 Python: $(python --version 2>&1)"
echo "   📊 Datos: $(wc -l < data/raw/consumos_uptc.csv 2>/dev/null || echo "0") registros"
echo "   🤖 Modelo: $(ls -lh models/modelo_xgboost.joblib 2>/dev/null | awk '{print $5}' || echo "N/A")"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
