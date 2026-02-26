import csv
import html
import re
from datetime import datetime
from pathlib import Path

# Aumentar limite de tamaño de campo CSV
csv.field_size_limit(10 * 1024 * 1024)

BASE = Path('/Users/Pintxo/corpus-etnografico-galicia')
CASES_CSV = BASE / '03_analysis/cases/cases_sampled.csv'
CASES_DIR = BASE / '03_analysis/cases'
PATTERNS_YML = BASE / '02_methods/patterns/escenas_minimas.yml'
INDEX_PATH = CASES_DIR / 'INDEX_cases.md'
NOTES_PATH = BASE / '02_methods/patterns/escenas_minimas_NOTES.md'
VIGNETTES_PATH = BASE / '03_analysis/writeup/cases_vignettes.md'
KEY_NUMBERS_PATH = BASE / '04_outputs/tables/key_numbers.md'
CASES_RAW = BASE / '01_data/kwic_exports/cases_raw.csv'
COOC_PAIRS = BASE / '04_outputs/tables/cooc_pairs.csv'
UNITS_CSV = BASE / '01_data/text/units.csv'
TEI_DIR = BASE / '01_data/tei/source'


def parse_patterns(yaml_path: Path):
    patterns = {}
    current_key = None
    current_obj = {}
    in_desc = False
    desc_lines = []
    with open(yaml_path, 'r', encoding='utf-8') as f:
        for line in f:
            raw = line.rstrip('\n')
            stripped = raw.strip()
            if not stripped or stripped.startswith('#') or stripped == '---':
                continue
            if not raw.startswith(' ') and stripped.endswith(':'):
                if current_key:
                    if in_desc:
                        current_obj['descripcion'] = ' '.join(desc_lines).strip()
                    patterns[current_key] = current_obj
                current_key = stripped[:-1]
                current_obj = {}
                in_desc = False
                desc_lines = []
                continue
            if current_key:
                if ':' in raw and raw.startswith('  '):
                    key, value = raw.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key == 'descripcion' and value.startswith('>'):
                        in_desc = True
                        desc_lines = []
                        continue
                    if in_desc:
                        current_obj['descripcion'] = ' '.join(desc_lines).strip()
                        in_desc = False
                        desc_lines = []
                    current_obj[key] = value.strip('"\'')
                else:
                    if in_desc:
                        desc_lines.append(stripped)
    if current_key:
        if in_desc:
            current_obj['descripcion'] = ' '.join(desc_lines).strip()
        patterns[current_key] = current_obj
    return patterns


def count_rows(path: Path):
    if not path.exists():
        return 0
    with open(path, 'r', encoding='utf-8') as f:
        return max(0, sum(1 for _ in f) - 1)


def read_cases(csv_path: Path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def kwic_short(kwic: str, max_len=80):
    text = html.unescape(kwic)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        return text[:max_len-1] + '…'
    return text


def main():
    patterns = parse_patterns(PATTERNS_YML)
    cases = read_cases(CASES_CSV)

    # INDEX_cases.md
    headers = ['case_id', 'obra_id', 'escena_tipo', 'cluster_k4', 'kwic (corto)']
    lines = [
        '# Index de casos muestreados',
        '',
        'Tabla de referencia rapida para navegar el muestreo etnografico.',
        '',
        '| ' + ' | '.join(headers) + ' |',
        '|---|---|---|---|---|'
    ]

    has_cluster = 'cluster_k4' in cases[0] if cases else False
    for row in cases:
        cluster_val = row.get('cluster_k4', '-') if has_cluster else '-'
        lines.append(
            '| {case_id} | {obra_id} | {escena_tipo} | {cluster} | {kwic} |'.format(
                case_id=row.get('case_id', ''),
                obra_id=row.get('obra_id', ''),
                escena_tipo=row.get('escena_tipo', ''),
                cluster=cluster_val if cluster_val else '-',
                kwic=kwic_short(row.get('kwic', ''))
            )
        )
    INDEX_PATH.write_text('\n'.join(lines), encoding='utf-8')

    # update case markdowns
    for row in cases:
        case_id = row.get('case_id', '')
        escena = row.get('escena_tipo', '')
        case_path = CASES_DIR / f"{case_id}.md"
        if not case_path.exists():
            continue
        content = case_path.read_text(encoding='utf-8')
        if '## Preguntas reflexivas' in content:
            continue
        ventana = patterns.get(escena, {}).get('ventana', 'N/D')
        fecha = 'no disponible'
        for line in content.splitlines():
            if line.strip().startswith('**Fecha generación:**'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    fecha = parts[1].replace('**', '').strip()
                break
        block = [
            '',
            '---',
            '',
            '## Preguntas reflexivas',
            '',
            '- ¿Quién narra y desde qué posición?',
            '- ¿Qué afectos y tonos dominan la escena?',
            '- ¿Qué normatividades se legitiman o cuestionan?',
            '- ¿Qué mediaciones de género literario están operando?',
            '- ¿Qué silencios o ausencias estructuran la escena?',
            '- ¿Cómo se sitúa la escena respecto a otras del corpus?',
            '- ¿Qué sesgos míos aparecen al leer este caso?',
            '',
            '## Notas de trazabilidad',
            '',
            f'- Escena/patrón: {escena}',
            f'- Ventana KWIC: {ventana}',
            f'- Fecha de generación: {fecha}',
            ''
        ]
        case_path.write_text(content + '\n'.join(block), encoding='utf-8')

    # Actualizar fechas en notas de trazabilidad ya existentes
    for row in cases:
        case_id = row.get('case_id', '')
        case_path = CASES_DIR / f"{case_id}.md"
        if not case_path.exists():
            continue
        content = case_path.read_text(encoding='utf-8')
        if 'Fecha de generación: no disponible' not in content:
            continue
        fecha = None
        for line in content.splitlines():
            if line.strip().startswith('**Fecha generación:**'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    fecha = parts[1].replace('**', '').strip()
                break
        if fecha:
            updated = content.replace('Fecha de generación: no disponible', f'Fecha de generación: {fecha}')
            case_path.write_text(updated, encoding='utf-8')

    # escenas_minimas_NOTES.md
    examples = {}
    if CASES_RAW.exists():
        with open(CASES_RAW, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                escena = row.get('escena_tipo', '')
                kwic = row.get('kwic', '')
                if not escena or not kwic:
                    continue
                examples.setdefault(escena, [])
                if len(examples[escena]) < 2:
                    examples[escena].append(kwic_short(kwic, max_len=140))

    confusion = {
        'migracion_embarque': ('movilidad_interna', 'retorno_indiano'),
        'retorno_indiano': ('migracion_embarque', 'herencia_tierra'),
        'herencia_tierra': ('muerte_duelo', 'deuda_usura'),
        'hambre_subsistencia': ('deuda_usura', 'trabajo_jornalero'),
        'trabajo_jornalero': ('ciclo_agricola', 'caciquismo_poder'),
        'deuda_usura': ('herencia_tierra', 'hambre_subsistencia'),
        'caciquismo_poder': ('violencia_agresion', 'herencia_tierra'),
        'violencia_agresion': ('muerte_duelo', 'caciquismo_poder'),
        'genero_roles': ('amor_deseo', 'muerte_duelo'),
        'muerte_duelo': ('violencia_agresion', 'religiosidad_supersticion'),
        'religiosidad_supersticion': ('muerte_duelo', 'amor_deseo'),
        'ciclo_agricola': ('trabajo_jornalero', 'aldea_ciudad'),
        'aldea_ciudad': ('movilidad_interna', 'morriña_nostalgia'),
        'movilidad_interna': ('migracion_embarque', 'aldea_ciudad'),
        'morriña_nostalgia': ('amor_deseo', 'migracion_embarque'),
        'amor_deseo': ('genero_roles', 'morriña_nostalgia'),
    }

    missing = {
        'migracion_embarque': 'escenas donde la partida se describe sin America explicita',
        'retorno_indiano': 'retornos empobrecidos o fallidos',
        'herencia_tierra': 'conflictos por tierras sin vocabulario juridico',
        'hambre_subsistencia': 'metaforas de hambre sin hambre literal',
        'trabajo_jornalero': 'trabajos femeninos no nombrados como jornales',
        'deuda_usura': 'deudas informales o de cuidado',
        'caciquismo_poder': 'autoridades sin titulos explicitos',
        'violencia_agresion': 'violencia simbolica o estructural',
        'genero_roles': 'roles masculinos no marcados',
        'muerte_duelo': 'duelos sin muerte literal',
        'religiosidad_supersticion': 'devociones sin lenguaje religioso directo',
        'ciclo_agricola': 'trabajos agrarios sin terminos tecnicos',
        'aldea_ciudad': 'contrastes espaciales sin palabras ciudad/aldea',
        'movilidad_interna': 'movilidad cotidiana no explicitada',
        'morriña_nostalgia': 'nostalgias sin la palabra morrina',
        'amor_deseo': 'afectos sin vocabulario romantico',
    }

    notes_lines = [
        '# Notas sobre escenas (taxonomia provisional)',
        '',
        'Este documento describe lo que cada escena captura, posibles confusiones y lo que queda fuera. Incluye ejemplos reales (KWIC) desde el muestreo.',
        '',
        '---',
        ''
    ]

    for escena in patterns.keys():
        nombre = patterns.get(escena, {}).get('nombre', escena)
        desc = patterns.get(escena, {}).get('descripcion', '').strip()
        conf = confusion.get(escena, ('otras_escenas', ''))
        miss = missing.get(escena, 'ausencias no tipificadas')
        ex = examples.get(escena, [])

        notes_lines.extend([
            f'## {escena}',
            '',
            f'- Captura: {nombre}.',
            f'- Descripcion: {desc}',
            f'- Puede confundirse con: {conf[0]}, {conf[1]}.',
            f'- Se queda fuera: {miss}.',
            '',
            '- Ejemplos (KWIC):',
        ])

        if ex:
            for i, e in enumerate(ex, 1):
                notes_lines.append(f'  {i}. "{e}"')
        else:
            notes_lines.append('  1. (sin ejemplo disponible)')
        notes_lines.append('')

    scene_counts = {}
    if CASES_RAW.exists():
        with open(CASES_RAW, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                escena = row.get('escena_tipo', '')
                if escena:
                    scene_counts[escena] = scene_counts.get(escena, 0) + 1

    if scene_counts:
        sorted_counts = sorted(scene_counts.items(), key=lambda x: -x[1])
        broad = [s for s, _ in sorted_counts[:3]]
        narrow = [s for s, _ in sorted_counts[-2:]]

        notes_lines.extend([
            '---',
            '',
            '## Escenas demasiado anchas (diagnostico)',
            ''
        ])
        for escena in broad:
            regex = patterns.get(escena, {}).get('regex', '')
            notes_lines.append(f'- {escena}: conteo alto. Regex actual: {regex}')
            notes_lines.append('  - Propuesta prudente 1: agregar co-ocurrencia de contexto (p. ej. verbo cercano).')
            notes_lines.append('  - Propuesta prudente 2: restringir a formas verbales especificas (evitar sustantivos ambiguos).')
            notes_lines.append('  - Propuesta prudente 3: excluir usos metaforicos frecuentes en revisiones.')

        notes_lines.extend([
            '',
            '## Escenas demasiado estrechas (diagnostico)',
            ''
        ])
        for escena in narrow:
            regex = patterns.get(escena, {}).get('regex', '')
            notes_lines.append(f'- {escena}: conteo bajo. Regex actual: {regex}')
            notes_lines.append('  - Propuesta minima: incluir sinonimos cercanos y variantes ortograficas.')
            notes_lines.append('  - Propuesta minima: permitir perifrasticas sin el verbo canonico.')

    NOTES_PATH.write_text('\n'.join(notes_lines), encoding='utf-8')

    # vignettes
    selected = cases[:3]
    vin_lines = [
        '# Vinetas de casos (borrador)',
        '',
        '> Estas vinetas se basan en casos reales del muestreo. No son resultados finales.',
        ''
    ]

    for i, row in enumerate(selected, 1):
        kwic = html.unescape(row.get('kwic', '')).replace('\n', ' ')
        kwic = re.sub(r'\s+', ' ', kwic).strip()
        escena = row.get('escena_tipo', '')
        obra = row.get('obra_id', '')
        unidad = row.get('unidad_id', '')
        match_term = row.get('match_term', '')

        vin_lines.extend([
            f'## Vigneta {i}',
            '',
            f'**Caso:** {row.get("case_id", "")} | **Obra:** {obra} | **Unidad:** {unidad} | **Escena:** {escena}',
            '',
            '**KWIC**',
            '',
            '```',
            kwic,
            '```',
            '',
            '**Lectura reflexiva (5-7 lineas)**',
            '',
            f'- La escena activa la categoria `{escena}` a partir del termino "{match_term}".',
            '- Se observa una tension narrativa que requiere lectura situada (quien habla y desde donde).',
            '- El fragmento sugiere una norma implicita, pero no fija una unica interpretacion.',
            '- El contexto abre preguntas sobre afectos (miedo, deseo, resignacion) sin cerrarlos.',
            '- Quedan por indagar silencios: quienes no aparecen en el fragmento.',
            '- Esta escena debe leerse en dialogo con otras del mismo tipo para evitar generalizar.',
            ''
        ])

    VIGNETTES_PATH.write_text('\n'.join(vin_lines), encoding='utf-8')

    # key numbers
    tei_count = len(list(TEI_DIR.glob('*.xml')))
    units_count = count_rows(UNITS_CSV)
    cases_count = count_rows(CASES_RAW)
    sampled_count = count_rows(CASES_CSV)
    cooc_count = count_rows(COOC_PAIRS)
    ventanas_kwic = sorted({patterns[k].get('ventana', '') for k in patterns if patterns[k].get('ventana')})
    escenas_activas = len(patterns)
    fecha = datetime.now().strftime('%Y-%m-%d')

    key_lines = [
        '# Numeros clave (descriptivos)',
        '',
        f'- TEI procesados: {tei_count}',
        f'- Unidades textuales: {units_count}',
        f'- Casos detectados: {cases_count}',
        f'- Casos muestreados: {sampled_count}',
        f'- Escenas activas: {escenas_activas}',
        f'- Ventanas KWIC: {", ".join(ventanas_kwic)}',
        f'- Pares de coocurrencia: {cooc_count}',
        f'- Fecha de ultima ejecucion: {fecha}',
    ]

    KEY_NUMBERS_PATH.write_text('\n'.join(key_lines), encoding='utf-8')


if __name__ == '__main__':
    main()