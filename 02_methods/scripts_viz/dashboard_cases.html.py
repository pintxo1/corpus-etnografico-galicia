#!/usr/bin/env python3
"""
dashboard_cases.html - Interactive case browser (filter, sort, view markdown ficha)
"""

import sys
from pathlib import Path
import json
import pandas as pd
from html import escape


def generate_dashboard(packs_dir, outdir):
    """Generate interactive HTML dashboard for browsing cases"""
    
    # Load reading packs (search in subdirectories)
    packs_dir = Path(packs_dir)
    
    dfs = []
    
    # Look for diverse pack
    diverse_candidates = list(packs_dir.glob('**/reading_pack_diverse.csv'))
    if diverse_candidates:
        df_diverse = pd.read_csv(diverse_candidates[0])
        df_diverse['pack'] = 'diverse'
        dfs.append(df_diverse)
    
    # Look for balanced pack
    balanced_candidates = list(packs_dir.glob('**/reading_pack_balanced.csv'))
    if balanced_candidates:
        df_balanced = pd.read_csv(balanced_candidates[0])
        df_balanced['pack'] = 'balanced'
        dfs.append(df_balanced)
    
    if not dfs:
        print("No reading packs found.")
        return
    
    df = pd.concat(dfs, ignore_index=True)
    
    # Get unique scenes and packs
    scenes = sorted(df['escena_tipo'].unique())
    packs = sorted(df['pack'].unique())
    
    # Prepare data for JavaScript
    cases_data = []
    for _, row in df.iterrows():
        cases_data.append({
            'id': str(row['case_id']),
            'escena': row['escena_tipo'],
            'pack': row['pack'],
            'salience': float(row.get('salience_z', 0)) if 'salience_z' in row else 0,
            'obra': str(row.get('obra_id', 'unknown')),
            'kwic': escape(str(row.get('kwic', ''))),
            'note': escape(str(row.get('note_breve', ''))) if 'note_breve' in row else ''
        })
    
    # JSON for data embedding
    cases_json = json.dumps(cases_data)
    
    # HTML Template
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Corpus de Casos - Dashboard Interactivo</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        
        .subtitle {{
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        
        .help-section {{
            background: #f0f8ff;
            border: 1px solid #b3d9ff;
            border-radius: 6px;
            padding: 0;
            margin-bottom: 30px;
            overflow: hidden;
        }}
        
        .help-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            padding: 15px 20px;
            background: #e6f2ff;
            border-bottom: 1px solid #b3d9ff;
            font-weight: 600;
            color: #0056b3;
            user-select: none;
        }}
        
        .help-header:hover {{
            background: #d4e8ff;
        }}
        
        .help-toggle {{
            font-size: 18px;
            transition: transform 0.3s;
        }}
        
        .help-toggle.open {{
            transform: rotate(180deg);
        }}
        
        .help-content {{
            padding: 20px;
            display: none;
            max-height: 1000px;
            overflow: hidden;
            animation: slideDown 0.3s ease-out;
        }}
        
        .help-content.open {{
            display: block;
        }}
        
        @keyframes slideDown {{
            from {{
                max-height: 0;
                opacity: 0;
            }}
            to {{
                max-height: 1000px;
                opacity: 1;
            }}
        }}
        
        .help-content h3 {{
            color: #0056b3;
            font-size: 13px;
            font-weight: 600;
            margin-top: 15px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}
        
        .help-content ol {{
            list-style-position: inside;
            color: #333;
            font-size: 13px;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        
        .help-content li {{
            margin-bottom: 6px;
        }}
        
        .help-content p {{
            color: #555;
            font-size: 13px;
            line-height: 1.5;
            margin-bottom: 10px;
        }}
        
        .help-example {{
            background: white;
            border-left: 3px solid #0056b3;
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
            color: #333;
            font-family: 'Courier New', monospace;
        }}
        
        .tooltip {{
            display: inline-block;
            margin-left: 5px;
            cursor: help;
        }}
        
        .tooltip-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            background: #b3d9ff;
            color: #0056b3;
            border-radius: 50%;
            font-size: 12px;
            font-weight: bold;
            position: relative;
        }}
        
        .tooltip-icon:hover::after {{
            content: attr(data-tooltip);
            position: absolute;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            white-space: nowrap;
            font-size: 12px;
            font-weight: normal;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            pointer-events: none;
        }}
        
        .tooltip-icon:hover::before {{
            content: '';
            position: absolute;
            bottom: 115%;
            left: 50%;
            transform: translateX(-50%);
            border: 6px solid transparent;
            border-top-color: #333;
            z-index: 1000;
            pointer-events: none;
        }}
        
        .warning-box {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 4px;
            padding: 12px;
            margin-top: 15px;
            font-size: 13px;
            color: #664d03;
            display: none;
        }}
        
        .warning-box.show {{
            display: block;
        }}
        
        .controls {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}
        
        .control-group {{
            display: flex;
            flex-direction: column;
        }}
        
        label {{
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        select, input {{
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: inherit;
            transition: border 0.2s;
        }}
        
        select:focus, input:focus {{
            outline: none;
            border-color: #FF6B9D;
            box-shadow: 0 0 4px rgba(255, 107, 157, 0.2);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .stat {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
            border-left: 4px solid #FF6B9D;
        }}
        
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #FF6B9D;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #999;
            margin-top: 5px;
            text-transform: uppercase;
        }}
        
        .cases-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .case-card {{
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            background: white;
            transition: all 0.2s;
            cursor: pointer;
        }}
        
        .case-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: #FF6B9D;
            transform: translateY(-2px);
        }}
        
        .case-escena {{
            display: inline-block;
            background: #FF6B9D;
            color: white;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        
        .case-pack {{
            display: inline-block;
            background: #e0e0e0;
            color: #666;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            margin-left: 5px;
        }}
        
        .case-id {{
            font-weight: 600;
            color: #333;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        
        .case-kwic {{
            background: #f9f9f9;
            padding: 10px;
            border-left: 3px solid #FF6B9D;
            font-size: 12px;
            line-height: 1.4;
            margin-bottom: 10px;
            font-family: 'Courier New', monospace;
            color: #444;
            overflow-y: auto;
            max-height: 60px;
        }}
        
        .case-obra {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .case-salience {{
            font-size: 12px;
            color: #FF6B9D;
            font-weight: 600;
        }}
        
        .case-note {{
            font-size: 11px;
            color: #999;
            margin-top: 8px;
            font-style: italic;
        }}
        
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 14px;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 12px;
        }}
        
        @media (max-width: 768px) {{
            .controls {{
                grid-template-columns: 1fr;
            }}
            .stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .cases-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Corpus Etnográfico: Explorador de Casos</h1>
        <p class="subtitle">Navega, filtra y explora 3,550 casos textuales organizados por escena y lectura</p>
        
        <div class="help-section">
            <div class="help-header" onclick="toggleHelp()">
                <span>❓ Cómo usar este explorador</span>
                <span class="help-toggle" id="helpToggle">▼</span>
            </div>
            <div class="help-content" id="helpContent">
                <h3>4 Pasos para Explorar</h3>
                <ol>
                    <li><strong>Selecciona una Escena:</strong> Ej. "amor_deseo", "muerte_duelo". O déjalo en "Todas" para ver el corpus completo.</li>
                    <li><strong>Elige un Pack de Lectura:</strong> "diverse" = amplia cobertura del corpus; "balanced" = casos distribuidos equitativamente por escena.</li>
                    <li><strong>Ordena por Salience:</strong> "Mayor" muestra casos más representativos; "Menor" muestra outliers o excepciones.</li>
                    <li><strong>Lee el KWIC y Explora:</strong> Haz clic en una tarjeta para expandir. Nota: cambiar filtros resetea la exploración.</li>
                </ol>
                
                <h3>Ejemplos de Combinaciones</h3>
                <div class="help-example">
                    🔍 <strong>Ejemplo 1:</strong> Escena "migracion_embarque" + Pack "diverse" + Salience "mayor"<br>
                    → Casos más representativos de migración en diversos autores
                </div>
                <div class="help-example">
                    🔍 <strong>Ejemplo 2:</strong> Escena "hambre_subsistencia" + Pack "balanced" + Salience "menor"<br>
                    → Excepciones: cómo se representa hambre de formas no-canónicas
                </div>
                <div class="help-example">
                    🔍 <strong>Ejemplo 3:</strong> Todas las escenas + Pack "diverse" + Salience "mayor"<br>
                    → Visión general: qué escenas dominan el corpus por presencia
                </div>
                
                <h3>Diverse vs. Balanced: ¿Cuál usar?</h3>
                <p><strong>Diverse:</strong> Maximiza cobertura del corpus. Elige 180 casos de ~76 obras distintas. Ideal para ver variedad de autores, géneros, épocas.</p>
                <p><strong>Balanced:</strong> Equilibra por escena. Elige ~10-13 casos por escena (160 total, 29 obras). Ideal para comparar cómo cada escena varía entre autores.</p>
                
                <h3>¿Qué es Salience?</h3>
                <p>Salience (z-score) mide <strong>cuán representativo es un caso</strong> dentro de su escena relativizado por densidad textual. Mayor valor = más relevante estadísticamente en ese patrón narrativo. ⚠️ NO significa "mejor escrita" ni "más importante" etnográficamente; es una <strong>heurística</strong> para orientar lectura.</p>
                
                <h3>⚠️ Limitaciones & Reflexividad</h3>
                <p>Este explorador muestra patrones textuales, NO "realidad" social. Las escenas son <strong>heurísticas de nuestra codificación</strong>, no categorías naturales. Coocurrencias NO implican causación. Use como herramienta para <strong>leer etnográficamente</strong>, no para hacer claims cuantitativos.</p>
            </div>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label for="escenaFilter">
                    Escena
                    <span class="tooltip">
                        <span class="tooltip-icon" data-tooltip="Tipo de escena/patrón. 'Todas' muestra el conjunto.">?</span>
                    </span>
                </label>
                <select id="escenaFilter">
                    <option value="">Todas las escenas</option>
                </select>
            </div>
            <div class="control-group">
                <label for="packFilter">
                    Lectura
                    <span class="tooltip">
                        <span class="tooltip-icon" data-tooltip="diverse: cobertura corpus. balanced: ecuanimidad por escena.">?</span>
                    </span>
                </label>
                <select id="packFilter">
                    <option value="">Todas las lecturas</option>
                </select>
            </div>
            <div class="control-group">
                <label for="sortBy">
                    Ordenar por
                    <span class="tooltip">
                        <span class="tooltip-icon" data-tooltip="Salience: relevancia estadística en escena. Mayor/Menor para ver canónico/excepcional.">?</span>
                    </span>
                </label>
                <select id="sortBy">
                    <option value="salience_desc">Salience (mayor)</option>
                    <option value="salience_asc">Salience (menor)</option>
                    <option value="id">ID (ascendente)</option>
                </select>
            </div>
        </div>
        
        <div class="warning-box" id="fewResultsWarning" role="alert">
            ℹ️ <strong>Pocos casos encontrados.</strong> Prueba seleccionando "Todas las lecturas" o cambia el orden. Si ves esta nota con todos los filtros en "Todas", tienes la lista completa: usa los filtros para explorar.
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number" id="totalCases">0</div>
                <div class="stat-label">Casos</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="filteredCases">0</div>
                <div class="stat-label">Mostrados</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="uniqueObras">0</div>
                <div class="stat-label">Obras</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="avgSalience">0</div>
                <div class="stat-label">Salience promedio</div>
            </div>
        </div>
        
        <div class="cases-grid" id="casesContainer">
            <!-- Populated by JavaScript -->
        </div>
        
        <div class="no-results" id="noResults" style="display: none;">
            No hay casos que coincidan con los filtros seleccionados.
        </div>
        
        <div class="footer">
            <strong>Leyenda:</strong> Salience (z-score) indica relevancia estadística. Mayor valor = más relevante en el contexto de la escena.
        </div>
    </div>
    
    <script>
        // Data
        const allCases = {cases_json};
        
        // Help toggle
        function toggleHelp() {{
            const helpContent = document.getElementById('helpContent');
            const helpToggle = document.getElementById('helpToggle');
            helpContent.classList.toggle('open');
            helpToggle.classList.toggle('open');
        }}
        
        // Initialize selects
        const scenes = [...new Set(allCases.map(c => c.escena))].sort();
        const packs = [...new Set(allCases.map(c => c.pack))].sort();
        
        const scenaSelect = document.getElementById('escenaFilter');
        scenes.forEach(s => {{
            const opt = document.createElement('option');
            opt.value = s;
            opt.textContent = s;
            scenaSelect.appendChild(opt);
        }});
        
        const packSelect = document.getElementById('packFilter');
        packs.forEach(p => {{
            const opt = document.createElement('option');
            opt.value = p;
            opt.textContent = p;
            packSelect.appendChild(opt);
        }});
        
        // Update total stats
        document.getElementById('totalCases').textContent = allCases.length;
        const uniqueObras = new Set(allCases.map(c => c.obra)).size;
        document.getElementById('uniqueObras').textContent = uniqueObras;
        
        // Filter and render
        function renderCases() {{
            const escenaValue = scenaSelect.value;
            const packValue = packSelect.value;
            const sortValue = document.getElementById('sortBy').value;
            
            let filtered = allCases.filter(c => 
                (!escenaValue || c.escena === escenaValue) &&
                (!packValue || c.pack === packValue)
            );
            
            // Sort
            if (sortValue === 'salience_desc') {{
                filtered.sort((a, b) => b.salience - a.salience);
            }} else if (sortValue === 'salience_asc') {{
                filtered.sort((a, b) => a.salience - b.salience);
            }} else {{
                filtered.sort((a, b) => parseInt(a.id) - parseInt(b.id));
            }}
            
            // Update filtered stats
            document.getElementById('filteredCases').textContent = filtered.length;
            
            // Calculate average salience for filtered results
            const filteredAvgSalience = filtered.length > 0 
                ? (filtered.reduce((s, c) => s + c.salience, 0) / filtered.length).toFixed(2)
                : 'N/A';
            document.getElementById('avgSalience').textContent = filteredAvgSalience;
            
            // Compute unique obras in filtered results
            const filteredObras = new Set(filtered.map(c => c.obra)).size;
            document.getElementById('uniqueObras').textContent = filteredObras;
            
            const container = document.getElementById('casesContainer');
            const noResults = document.getElementById('noResults');
            const warningBox = document.getElementById('fewResultsWarning');
            
            if (filtered.length === 0) {{
                container.style.display = 'none';
                noResults.style.display = 'block';
                warningBox.classList.remove('show');
                return;
            }}
            
            container.style.display = 'grid';
            noResults.style.display = 'none';
            
            // Show warning if few results
            if (filtered.length < 5) {{
                warningBox.classList.add('show');
            }} else {{
                warningBox.classList.remove('show');
            }}
            
            container.innerHTML = filtered.map(c => `
                <div class="case-card">
                    <div>
                        <span class="case-escena">${{c.escena}}</span>
                        <span class="case-pack">${{c.pack}}</span>
                    </div>
                    <div class="case-id">Caso #${{c.id}}</div>
                    <div class="case-kwic">${{c.kwic}}</div>
                    <div class="case-obra"><strong>Obra:</strong> ${{c.obra}}</div>
                    <div class="case-salience"><strong>Salience:</strong> ${{c.salience.toFixed(3)}}</div>
                    ${{c.note ? `<div class="case-note">${{c.note}}</div>` : ''}}
                </div>
            `).join('');
        }}
        
        // Event listeners
        scenaSelect.addEventListener('change', renderCases);
        packSelect.addEventListener('change', renderCases);
        document.getElementById('sortBy').addEventListener('change', renderCases);
        
        // Initial render
        renderCases();
    </script>
</body>
</html>
"""
    
    html_path = Path(outdir) / "dashboard_cases.html"
    html_path.write_text(html)
    print(f"✅ {html_path} ({len(cases_data)} casos interactivos)")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--packs-dir', required=True)
    parser.add_argument('--outdir', required=True)
    
    args = parser.parse_args()
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    
    generate_dashboard(args.packs_dir, args.outdir)
