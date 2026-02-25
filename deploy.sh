#!/bin/bash
# ══════════════════════════════════════════════════════════
# DEPLOY SCRIPT: Dashboard Transparansi APBA Aceh 2025
# Otomatis setup Git repo dan push ke GitHub
# ══════════════════════════════════════════════════════════

echo "🏛️ Dashboard Transparansi APBA Aceh 2025 — Deployment Script"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ── 1. Check prerequisites ──
echo "📋 Checking prerequisites..."

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Install: https://git-scm.com"
    exit 1
fi
echo "  ✓ Git found"

if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI not found (optional). Install: https://cli.github.com"
    echo "   You can still deploy manually via github.com"
    GH_CLI=false
else
    echo "  ✓ GitHub CLI found"
    GH_CLI=true
fi

# ── 2. Initialize Git repo ──
echo ""
echo "📦 Initializing Git repository..."

REPO_NAME="dashboard-apba-aceh-2025"

git init
git add dashboard_apba_2025.py
git add requirements.txt
git add .gitignore
git add .streamlit/config.toml
git add 02_lampiran2_rincian_apbd_2025.csv
git add 03_lampiran3_hibah_2025.csv
git add 04_lampiran5_bantuan_keuangan_2025.csv
git add 05_lampiran7_dana_otsus_2025.csv
git add 06_raw_semua_data_2025.csv

echo "  ✓ Files staged"

git commit -m "🏛️ Dashboard Transparansi APBA Aceh 2025 — Initial deploy

- 6 halaman interaktif (Ringkasan, Eksplorasi, Otsus, Hibah, Analisis, Pencarian)
- 10+ visualisasi Plotly (pie, bar, treemap, sunburst, sankey, heatmap, scatter, radar)
- 36 SKPD ter-mapping, 10.255 item belanja
- Data: Lampiran I, II, III, V, VII APBA 2025
- Built with Streamlit + Plotly"

echo "  ✓ Initial commit created"

# ── 3. Create GitHub repo and push ──
echo ""

if [ "$GH_CLI" = true ]; then
    echo "🌐 Creating GitHub repository..."
    gh repo create $REPO_NAME --public --description "Dashboard Transparansi APBA Aceh 2025 — Streamlit + Plotly" --push --source=.
    echo "  ✓ Repository created and pushed"
    echo ""
    echo "📋 Repository URL:"
    gh repo view --web
else
    echo "📝 Manual deployment steps:"
    echo "   1. Go to https://github.com/new"
    echo "   2. Create repository: $REPO_NAME"
    echo "   3. Run these commands:"
    echo ""
    echo "   git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
fi

# ── 4. Deploy to Streamlit Cloud ──
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "☁️  DEPLOY TO STREAMLIT CLOUD:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  1. Buka https://share.streamlit.io"
echo "  2. Klik 'New app'"
echo "  3. Pilih repository: YOUR_USERNAME/$REPO_NAME"
echo "  4. Branch: main"
echo "  5. Main file: dashboard_apba_2025.py"
echo "  6. Klik 'Deploy!'"
echo ""
echo "  Dashboard akan live dalam 2-3 menit di:"
echo "  https://YOUR_USERNAME-$REPO_NAME.streamlit.app"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Deployment setup complete!"
echo "═══════════════════════════════════════════════════════════"
