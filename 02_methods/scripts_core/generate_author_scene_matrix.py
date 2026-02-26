#!/usr/bin/env python3
"""
Genera matriz autor × escena con tasas normalizadas por tokens
y heatmap visualización

Output:
  04_outputs/tables/author_scene_matrix_rates.csv
  04_outputs/figures/static/fig_author_scene_heatmap.png
  04_outputs/figures/static/fig_author_scene_heatmap.pdf
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse


def load_author_reports(reports_dir):
    """Carga todos los scene_rates de autores"""
    
    tables_dir = reports_dir.parent / 'tables' / 'by_author'
    
    if not tables_dir.exists():
        raise FileNotFoundError(f"Directorio no encontrado: {tables_dir}")
    
    # Buscar todos los archivos *_scene_rates.csv
    rate_files = list(tables_dir.glob('*_scene_rates.csv'))
    
    if len(rate_files) == 0:
        raise FileNotFoundError(f"No se encontraron archivos *_scene_rates.csv en {tables_dir}")
    
    print(f"📂 Encontrados {len(rate_files)} archivos de tasas por autor")
    
    # Cargar y combinar
    all_data = []
    for file in rate_files:
        autor_slug = file.stem.replace('_scene_rates', '')
        # Revertir slug a nombre legible
        autor = autor_slug.replace('_', ' ').title()
        
        df = pd.read_csv(file)
        df['autor'] = autor
        all_data.append(df[['autor', 'escena_tipo', 'rate_per_1k_tokens']])
    
    combined = pd.concat(all_data, ignore_index=True)
    return combined


def create_matrix(data):
    """Crea matriz pivoteada autor × escena"""
    
    matrix = data.pivot_table(
        index='autor',
        columns='escena_tipo',
        values='rate_per_1k_tokens',
        fill_value=0
    )
    
    # Ordenar autores por total de casos (suma de tasas)
    matrix['_total'] = matrix.sum(axis=1)
    matrix = matrix.sort_values('_total', ascending=False)
    matrix = matrix.drop(columns=['_total'])
    
    # Ordenar escenas por frecuencia global
    matrix = matrix[matrix.sum(axis=0).sort_values(ascending=False).index]
    
    return matrix


def plot_heatmap(matrix, output_png, output_pdf):
    """Genera heatmap de la matriz"""
    
    # Configuración
    plt.figure(figsize=(16, 8))
    
    # Heatmap
    sns.heatmap(
        matrix,
        cmap='YlOrRd',
        annot=False,
        fmt='.1f',
        cbar_kws={'label': 'Tasa por 1k tokens'},
        linewidths=0.5,
        linecolor='white'
    )
    
    plt.title('Distribución de Escenas Etnográficas por Autor\n(Tasas normalizadas por 1k tokens)', 
              fontsize=14, pad=20)
    plt.xlabel('Tipo de Escena', fontsize=11)
    plt.ylabel('Autor', fontsize=11)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    
    # Guardar
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.savefig(output_pdf, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Heatmap PNG: {output_png}")
    print(f"✅ Heatmap PDF: {output_pdf}")


def main():
    parser = argparse.ArgumentParser(description='Genera matriz y heatmap autor × escena')
    parser.add_argument('--reports-dir', required=True, help='Directorio by_author')
    parser.add_argument('--output-csv', required=True, help='Path output CSV matriz')
    parser.add_argument('--output-png', required=True, help='Path output PNG heatmap')
    parser.add_argument('--output-pdf', required=True, help='Path output PDF heatmap')
    
    args = parser.parse_args()
    
    reports_dir = Path(args.reports_dir)
    
    # 1. Cargar datos
    print("📂 Cargando datos de reportes por autor...")
    data = load_author_reports(reports_dir)
    
    print(f"   Autores: {data['autor'].nunique()}")
    print(f"   Escenas: {data['escena_tipo'].nunique()}")
    print(f"   Registros: {len(data)}")
    
    # 2. Crear matriz
    print("\n📊 Creando matriz autor × escena...")
    matrix = create_matrix(data)
    
    print(f"   Dimensiones: {matrix.shape}")
    
    # 3. Guardar CSV
    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(output_csv)
    print(f"\n✅ Matriz guardada: {output_csv}")
    
    # 4. Generar heatmap
    print("\n📈 Generando heatmap...")
    output_png = Path(args.output_png)
    output_pdf = Path(args.output_pdf)
    output_png.parent.mkdir(parents=True, exist_ok=True)
    
    plot_heatmap(matrix, output_png, output_pdf)
    
    # 5. Resumen
    print("\n📊 Resumen de la matriz:")
    print(f"   Autor con más casos (total): {matrix.sum(axis=1).idxmax()}")
    print(f"   Escena más frecuente (global): {matrix.sum(axis=0).idxmax()}")
    print(f"\n🔝 Top 5 escenas por frecuencia global:")
    print(matrix.sum(axis=0).sort_values(ascending=False).head(5).to_string())


if __name__ == '__main__':
    main()
