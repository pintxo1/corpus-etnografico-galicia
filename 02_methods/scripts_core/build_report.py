#!/usr/bin/env python3
"""
Build Report: Informe etnográfico automático del pipeline
Genera un REPORT.md con resumen de outputs, auditoría y limitaciones
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
import yaml

import pandas as pd


def build_report(
    cases_raw_path,
    scene_summary_path,
    case_rankings_path,
    diverse_pack_path=None,
    balanced_pack_path=None,
    cooc_pairs_path=None,
    pack_report_path=None,
    sampling_audit_path=None,
    rules_yaml_path=None,
    output_dir="04_outputs/reports"
):
    """
    Genera un informe REPORT.md con 8 secciones estándar.
    
    Maneja gracefully si archivos opcionales no existen.
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Leer archivos críticos
    try:
        df_cases = pd.read_csv(cases_raw_path)
        df_scenes = pd.read_csv(scene_summary_path)
        df_rankings = pd.read_csv(case_rankings_path)
    except Exception as e:
        print(f"❌ Error leyendo archivos críticos: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Contar units si existen
    n_units = 0
    units_path = "01_data/text/units.csv"
    if os.path.exists(units_path):
        try:
            df_units = pd.read_csv(units_path)
            n_units = len(df_units)
        except:
            pass
    
    # Archivos opcionales
    df_cooc = None
    if cooc_pairs_path and os.path.exists(cooc_pairs_path):
        try:
            df_cooc = pd.read_csv(cooc_pairs_path)
        except:
            pass
    
    df_diverse = None
    if diverse_pack_path and os.path.exists(diverse_pack_path):
        try:
            df_diverse = pd.read_csv(diverse_pack_path)
        except:
            pass
    
    df_balanced = None
    if balanced_pack_path and os.path.exists(balanced_pack_path):
        try:
            df_balanced = pd.read_csv(balanced_pack_path)
        except:
            pass
    
    pack_report_content = None
    if pack_report_path and os.path.exists(pack_report_path):
        try:
            with open(pack_report_path, 'r') as f:
                pack_report_content = f.read()
        except:
            pass
    
    sampling_audit_content = None
    if sampling_audit_path and os.path.exists(sampling_audit_path):
        try:
            with open(sampling_audit_path, 'r') as f:
                sampling_audit_content = f.read()
        except:
            pass
    
    rules_yaml_content = None
    rules_hash = "unknown"
    if rules_yaml_path and os.path.exists(rules_yaml_path):
        try:
            with open(rules_yaml_path, 'r') as f:
                rules_yaml_content = yaml.safe_load(f)
                # Calcular hash simple del contenido
                import hashlib
                with open(rules_yaml_path, 'rb') as f:
                    rules_hash = hashlib.sha256(f.read()).hexdigest()[:8]
        except:
            pass
    
    # ============================================================================
    # SECCIÓN 1: RUN SUMMARY
    # ============================================================================
    n_tei = len(set(df_cases.get('obra_id', [])))  # Aproximado
    n_cases = len(df_cases)
    n_escenas = len(df_scenes)
    
    section1 = f"""# Ethnographic Pipeline Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Run Summary

| Metric | Value |
|--------|-------|
| **TEI sources** | {n_tei} |
| **Units (extracts)** | {n_units if n_units > 0 else "N/A"} |
| **Cases (raw KWIC)** | {n_cases:,} |
| **Scenes** | {n_escenas} |

---
"""
    
    # ============================================================================
    # SECCIÓN 2: SCENE COVERAGE & CONCENTRATION
    # ============================================================================
    scene_stats = []
    for _, row in df_scenes.iterrows():
        n_casos = row.get('n_cases', 0)
        pct_total = (n_casos / n_cases * 100) if n_cases > 0 else 0
        n_obras = row.get('n_obras', '?')
        top3_pct = row.get('top3_obras_pct', 0)
        
        # Indicador de concentración
        concentration = '⚠️ HIGH' if top3_pct > 50 else '✓'
        
        scene_stats.append({
            'Scene': row.get('escena_tipo', 'unknown'),
            'Cases': n_casos,
            '% Total': f"{pct_total:.1f}%",
            'Works': n_obras,
            'Concentration': concentration
        })
    
    scene_table = "| " + " | ".join(scene_stats[0].keys()) + " |\n"
    scene_table += "|" + "|".join(["---"] * len(scene_stats[0])) + "|\n"
    for stat in scene_stats:
        scene_table += "| " + " | ".join(str(v) for v in stat.values()) + " |\n"
    
    section2 = f"""## 2. Scene Coverage & Concentration

{scene_table}

**Notes:**
- ⚠️ HIGH: Top 3 works represent >50% of scene's cases (concentration risk)
- Cases: n_cases from scene_summary.csv
- Works: n_obras detected in each scene

---
"""
    
    # ============================================================================
    # SECCIÓN 3: READING PACKS SUMMARY
    # ============================================================================
    section3 = "## 3. Reading Packs\n\n"
    
    if df_diverse is not None:
        n_diverse = len(df_diverse)
        n_obras_diverse = df_diverse['obra_id'].nunique()
        n_scenes_diverse = df_diverse['escena_tipo'].nunique()
        top_works_diverse = df_diverse['obra_id'].value_counts().head(3)
        top_works_diverse_str = ", ".join([f"{w} ({c})" for w, c in top_works_diverse.items()])
        section3 += f"""### Diverse Pack
- **Cases:** {n_diverse}
- **Unique works:** {n_obras_diverse}/80 ({n_obras_diverse/80*100:.1f}%)
- **Scenes:** {n_scenes_diverse}/16
- **Top 3 works:** {top_works_diverse_str}
- **Purpose:** Corpus-scale representativeness

"""
    else:
        section3 += "### Diverse Pack\n- ℹ️ Not yet generated\n\n"
    
    if df_balanced is not None:
        n_balanced = len(df_balanced)
        n_obras_balanced = df_balanced['obra_id'].nunique()
        n_scenes_balanced = df_balanced['escena_tipo'].nunique()
        top_works_balanced = df_balanced['obra_id'].value_counts().head(3)
        top_works_balanced_str = ", ".join([f"{w} ({c})" for w, c in top_works_balanced.items()])
        section3 += f"""### Balanced Pack
- **Cases:** {n_balanced}
- **Unique works:** {n_obras_balanced}/80 ({n_obras_balanced/80*100:.1f}%)
- **Scenes:** {n_scenes_balanced}/16
- **Top 3 works:** {top_works_balanced_str}
- **Purpose:** Cross-scene computational analysis (10 per scene)

"""
    else:
        section3 += "### Balanced Pack\n- ℹ️ Not yet generated\n\n"
    
    section3 += "---\n\n"    
    # ============================================================================
    # SECCIÓN 2B: TOKEN-NORMALIZED RATES (si existen)
    # ============================================================================
    section2b = ""
    rates_path = "04_outputs/tables/scene_rates_per_1k_tokens.csv"
    if os.path.exists(rates_path):
        try:
            df_rates = pd.read_csv(rates_path)
            section2b = """## 2b. Token-normalized Rates

Normalización por volumen textual (casos por 1,000 tokens de corpus):

| Scene | Cases | Rate/1k tokens | Works |
|-------|-------|----------------|-------|
"""
            for _, row in df_rates.head(8).iterrows():
                escena = row['escena_tipo']
                n_cases = row['n_cases']
                rate = row['cases_per_1k_tokens']
                n_obras = row['n_obras']
                section2b += f"| {escena} | {n_cases} | {rate:.4f} | {n_obras} |\n"
            
            section2b += """
**Interpretation:**
- Top scenes by token-normalized rate may indicate thematic prominence relative to corpus volume
- Low rates suggest sparse distribution across large textual regions
- ⚠️ **Caution:** This is a heuristic, not evidence of "thematic importance"—requires ethnographic interpretation

---
"""
        except:
            section2b = ""    
    # ============================================================================
    # SECCIÓN 4: AUDIT & DATASETS
    # ============================================================================
    section4 = """## 4. Audit & Reproducibility

"""
    
    if sampling_audit_content:
        section4 += "### Sampling Audit\n[See `04_outputs/tables/sampling_audit.md` for details]\n\n"
    else:
        section4 += "### Sampling Audit\n- ℹ️ Not yet generated\n\n"
    
    if pack_report_content:
        section4 += "### Pack Comparison\n[See `04_outputs/tables/pack_report.md` for detailed comparison]\n\n"
    else:
        section4 += "### Pack Comparison\n- ℹ️ Not yet generated\n\n"
    
    section4 += "---\n\n"
    
    # ============================================================================
    # SECCIÓN 5: CO-OCCURRENCE NETWORKS
    # ============================================================================
    section5 = "## 5. Co-occurrence Networks & Tensions\n\n"
    
    if df_cooc is not None and len(df_cooc) > 0:
        top_cooc = df_cooc.nlargest(10, 'n_cooc')
        section5 += "### Top 10 Co-occurrence Pairs\n\n"
        section5 += "| Term 1 | Term 2 | Co-occurrences | Jaccard |\n"
        section5 += "|--------|--------|----------------|----------|\n"
        for _, row in top_cooc.iterrows():
            term1 = row['term_1'][:25]
            term2 = row['term_2'][:25]
            n_cooc = row['n_cooc']
            jaccard = f"{row['jaccard']:.3f}"
            section5 += f"| {term1} | {term2} | {n_cooc} | {jaccard} |\n"
        section5 += "\n"
        section5 += "**Interpretation:** Top pairs indicate narrative tensions, thematic resonance, or"
        section5 += " intertextual references in the corpus.\n\n"
        section5 += "📁 **Network files:** See `04_outputs/networks/` for GraphML exports\n\n"
    else:
        section5 += "- ℹ️ Co-occurrence pairs not yet computed\n\n"
    
    section5 += "---\n\n"
    
    # ============================================================================
    # SECCIÓN 6: FIGURES GENERATED
    # ============================================================================
    section6 = "## 6. Figures Generated\n\n"
    figures_dir = "04_outputs/figures"
    if os.path.exists(figures_dir):
        figs = [f for f in os.listdir(figures_dir) if f.endswith('.png')]
        if figs:
            section6 += "| Figure | Path |\n|--------|------|\n"
            for fig in sorted(figs)[:10]:  # Listar máximo 10
                section6 += f"| {fig} | `{figures_dir}/{fig}` |\n"
            section6 += "\n"
        else:
            section6 += "- ℹ️ No PNG figures found yet\n\n"
    else:
        section6 += "- ℹ️ Figures directory not found\n\n"
    
    section6 += "---\n\n"
    
    # ============================================================================
    # SECCIÓN 6B: ENHANCED VISUALIZATIONS (NEW - Advanced DH)
    # ============================================================================
    section6b = "## 6b. Enhanced Visualizations\n\n"
    section6b += "Publication-ready statistical and network visualizations (Phase 9).\n\n"
    section6b += "**Figure Registry:** See [04_outputs/figures/FIGURE_REGISTRY.md](04_outputs/figures/FIGURE_REGISTRY.md) for complete inventory.\n\n"
    
    static_dir = "04_outputs/figures/static"
    interactive_dir = "04_outputs/figures/interactive"
    
    # Static (PNG/PDF) visualizations
    if os.path.exists(static_dir):
        static_figs = [f for f in os.listdir(static_dir) if f.endswith('.png')]
        if static_figs:
            section6b += "### Static Visualizations (PNG/PDF @ 300 DPI)\n\n"
            section6b += "| Visualization | Description | Purpose |\n"
            section6b += "|---|---|---|\n"
            
            viz_descriptions = {
                'fig_scene_scatter': ('Scene coverage vs. concentration (scatter plot)', 'Corpus-level scene characterization'),
                'fig_scene_work_heatmap': ('Scene × Work heatmap (top 40 obras, per 1k tokens)', 'Publication heatmap (legible)'),
                'fig_scene_work_heatmap_full': ('Scene × Work heatmap (all 80 works, archive)', 'Reference/archive (PDF only)'),
                'fig_scene_rates_distribution': ('Rate distributions across 5 diverse scenes (violin plots)', 'Variability visualization'),
                'fig_cooc_network_filtered': ('Term co-occurrence network (13 nodes, Louvain communities)', 'Semantic clustering & tensions'),
                'fig_scene_rates_per_1k_tokens': ('Top 10 scenes by case rate (horizontal bars)', 'Scene prevalence ranking')
            }
            
            for fig_prefix, (description, purpose) in viz_descriptions.items():
                png_files = [f for f in static_figs if fig_prefix in f]
                if png_files:
                    png_set = ', '.join([f'`png`' for f in png_files if f.endswith('.png')])
                    pdf_files = [f for f in os.listdir(static_dir) if fig_prefix in f and f.endswith('.pdf')]
                    files = png_set
                    if pdf_files:
                        files += ', ' + ', '.join([f'`pdf`' for f in pdf_files])
                    section6b += f"| {fig_prefix} | {description} | {purpose} |\n"
            
            # Special note for full heatmap
            section6b += "\n**Note:** `fig_scene_work_heatmap_full` available as PDF only (large reference format).\n\n"
        else:
            section6b += "- ℹ️ No static figures found\n\n"
    else:
        section6b += "- ℹ️ Static figures directory not found\n\n"
    
    # Interactive (HTML) visualizations
    if os.path.exists(interactive_dir):
        interactive_files = [f for f in os.listdir(interactive_dir) if f.endswith('.html')]
        if interactive_files:
            section6b += "### Interactive Visualizations (HTML)\n\n"
            section6b += "| Dashboard | Description | Purpose |\n"
            section6b += "|---|---|---|\n"
            
            interactive_descriptions = {
                'dashboard_cases.html': ('Case Browser (340 curated cases)', 'Exploration & KWIC context viewing'),
            }
            
            for html_file in interactive_files:
                if 'dashboard_cases' in html_file:
                    desc, purpose = interactive_descriptions['dashboard_cases.html']
                else:
                    desc, purpose = ('Interactive visualization', 'Exploration')
                section6b += f"| {html_file} | {desc} | {purpose} |\n"
            
            section6b += "\n**Technology:** Vanilla HTML/CSS/JS. Self-contained (no external dependencies). Works offline.\n\n"
        else:
            section6b += "- Status: Interactive dashboards not yet generated\n\n"
    else:
        section6b += "- Status: Interactive directory not found\n\n"
    
    section6b += "### Quality Standards\n\n"
    section6b += "- **PNG:** 300 DPI (publication quality for print/web)\n"
    section6b += "- **PDF:** Vectorial format (no pixelation, scales indefinitely)\n"
    section6b += "- **Colorblind-friendly:** Designed with accessible palettes\n"
    section6b += "- **Typography:** 8-13pt fonts (legible at publication size)\n"
    section6b += "- **Reproducibility:** All figures generated from source CSVs via `make viz-all`\n\n"
    section6b += "---\n\n"
    
    # ============================================================================
    # SECCIÓN 7: RUN PARAMETERS
    # ============================================================================
    section7 = """## 7. Run Parameters & Configuration

"""
    
    if rules_yaml_content:
        section7 += "### Reading Pack Rules (reading_pack_rules.yml)\n\n"
        section7 += "```yaml\n"
        section7 += yaml.dump(rules_yaml_content, default_flow_style=False)
        section7 += "```\n\n"
    
    section7 += f"""### Pipeline Configuration
- **Rules file:** `02_methods/patterns/reading_pack_rules.yml`
- **Rules hash:** {rules_hash}
- **CWD:** {os.getcwd()}
- **Python:** {sys.version.split()[0]}
- **Timestamp:** {datetime.now().isoformat()}

---
"""
    
    # ============================================================================
    # SECCIÓN 8: LIMITATIONS & REFLEXIVITY
    # ============================================================================
    section8 = """## 8. Limitations & Methodological Reflexivity

**This pipeline does NOT:**
- ⚠️ Assume texts are transparent representations of "reality"
- ⚠️ Reify scenes, works, or co-occurrence pairings as causal structures
- ⚠️ Claim statistical significance or inference beyond the corpus
- ⚠️ Neutralize the ethnographer's presence in case selection
- ⚠️ Substitute algorithmic pattern detection for interpretive depth

**What this IS:**
- ✓ A systematic heuristic for navigating a complex cultural corpus
- ✓ A trace of our analytical choices (scene definitions, cooc windows)
- ✓ A scaffold for ethnographic writing and comparative work
- ✓ A reproducible documentation of what was selected and why
- ✓ An artifact: the pipeline itself embeds theoretical commitments

**Data quality notes:**
- Cooc window: 40 words (configurable)
- Scene definitions: Hand-crafted patterns (see `02_methods/patterns/escenas_minimas.yml`)
- Case selection: Stratified by salience + obra diversity (see packs)
- Network reification: GraphML exports should be **visualized cautiously**

---

*Generated by ethnographic-pipeline v0.1 | Not for quantitative claims*
"""
    
    # ============================================================================
    # Combinar todo y escribir
    # ============================================================================
    full_report = section1 + section2 + section2b + section3 + section4 + section5 + section6 + section6b + section7 + section8
    
    output_path = os.path.join(output_dir, "REPORT.md")
    with open(output_path, 'w') as f:
        f.write(full_report)
    
    print(f"✅ Report written: {output_path}")
    print("\n" + "="*70)
    print("RUN SUMMARY")
    print("="*70)
    print(f"TEI sources: {n_tei}")
    print(f"Cases (raw KWIC): {n_cases:,}")
    print(f"Scenes: {n_escenas}")
    if df_diverse is not None:
        print(f"\n✅ Diverse pack: {n_diverse} cases, {n_obras_diverse} works")
    if df_balanced is not None:
        print(f"✅ Balanced pack: {n_balanced} cases, {n_obras_balanced} works")
    print("="*70)
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Build ethnographic pipeline report"
    )
    parser.add_argument('--cases-raw', default='01_data/kwic_exports/cases_raw.csv')
    parser.add_argument('--scene-summary', default='04_outputs/tables/scene_summary.csv')
    parser.add_argument('--case-rankings', default='04_outputs/tables/case_rankings.csv')
    parser.add_argument('--diverse-pack', default='03_analysis/reading_pack/diverse/reading_pack_diverse.csv')
    parser.add_argument('--balanced-pack', default='03_analysis/reading_pack/balanced/reading_pack_balanced.csv')
    parser.add_argument('--cooc-pairs', default='04_outputs/tables/cooc_pairs.csv')
    parser.add_argument('--pack-report', default='04_outputs/tables/pack_report.md')
    parser.add_argument('--sampling-audit', default='04_outputs/tables/sampling_audit.md')
    parser.add_argument('--rules', default='02_methods/patterns/reading_pack_rules.yml')
    parser.add_argument('--outdir', default='04_outputs/reports')
    
    args = parser.parse_args()
    
    build_report(
        cases_raw_path=args.cases_raw,
        scene_summary_path=args.scene_summary,
        case_rankings_path=args.case_rankings,
        diverse_pack_path=args.diverse_pack,
        balanced_pack_path=args.balanced_pack,
        cooc_pairs_path=args.cooc_pairs,
        pack_report_path=args.pack_report,
        sampling_audit_path=args.sampling_audit,
        rules_yaml_path=args.rules,
        output_dir=args.outdir
    )


if __name__ == '__main__':
    main()
