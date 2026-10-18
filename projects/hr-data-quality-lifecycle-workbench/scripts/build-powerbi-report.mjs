import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(here, '..');
const reportRoot = path.join(projectRoot, 'power-bi', 'HRDataQualityScorecard.Report');
const definitionRoot = path.join(reportRoot, 'definition');
const pagesRoot = path.join(definitionRoot, 'pages');
const pagesMetadataPath = path.join(pagesRoot, 'pages.json');
const pagesMetadata = JSON.parse(fs.readFileSync(pagesMetadataPath, 'utf8'));
const pageId = pagesMetadata.pageOrder[0];
const pageRoot = path.join(pagesRoot, pageId);
const visualsRoot = path.join(pageRoot, 'visuals');
const registeredRoot = path.join(reportRoot, 'StaticResources', 'RegisteredResources');
const visualSchema = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json';

fs.mkdirSync(visualsRoot, { recursive: true });
fs.mkdirSync(registeredRoot, { recursive: true });

const literal = (value) => ({ expr: { Literal: { Value: value } } });
const bool = (value) => literal(value ? 'true' : 'false');
const num = (value) => literal(`${value}D`);
const int = (value) => literal(`${value}L`);
const str = (value) => literal(`'${value.replaceAll("'", "''")}'`);
const color = (value) => ({ solid: { color: str(value) } });
const column = (table, property) => ({ Column: { Expression: { SourceRef: { Entity: table } }, Property: property } });
const measure = (table, property) => ({ Measure: { Expression: { SourceRef: { Entity: table } }, Property: property } });
const projection = (field, table, property, nativeQueryRef = property) => ({
  field,
  queryRef: `${table}.${property}`,
  nativeQueryRef
});

const chrome = ({ title, altText, titleColor = '#241E26', showTitle = true, padding = 12 }) => ({
  title: [{ properties: {
    show: bool(showTitle),
    text: str(title),
    fontFamily: str('Segoe UI Semibold'),
    fontSize: num(14),
    fontColor: color(titleColor),
    heading: str('Heading3'),
    titleWrap: bool(true)
  } }],
  general: [{ properties: { altText: str(altText) } }],
  background: [{ properties: { show: bool(true), color: color('#FFFFFF'), transparency: num(0) } }],
  border: [{ properties: { show: bool(true), color: color('#DED7E0'), width: num(1), radius: num(8) } }],
  dropShadow: [{ properties: { show: bool(false) } }],
  padding: [{ properties: { top: num(padding), bottom: num(padding), left: num(padding), right: num(padding) } }],
  visualHeader: [{ properties: { show: bool(false) } }]
});

const writeVisual = (id, visual) => {
  const dir = path.join(visualsRoot, id);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'visual.json'), `${JSON.stringify(visual, null, 2)}\n`);
};

const position = (x, y, width, height, z, tabOrder) => ({ x, y, width, height, z, tabOrder });

const makeTextbox = ({ id, x, y, width, height, z, tabOrder }) => ({
  $schema: visualSchema,
  name: id,
  position: position(x, y, width, height, z, tabOrder),
  visual: {
    visualType: 'textbox',
    objects: {
      general: [{ properties: {
        paragraphs: [
          {
            textRuns: [{
              value: 'Confiabilidad actual, focos recurrentes y eficacia de remediación',
              textStyle: { fontFamily: 'Segoe UI Semibold', fontSize: '24px', color: '#FFFFFF' }
            }],
            horizontalTextAlignment: 'left'
          },
          {
            textRuns: [{
              value: 'Proyecto de portafolio independiente · Datos 100 % sintéticos · No afiliado con Siemens Energy · Dataverse: casos publicados',
              textStyle: { fontFamily: 'Segoe UI', fontSize: '13px', color: '#F3EAF2' }
            }],
            horizontalTextAlignment: 'left'
          }
        ]
      } }]
    },
    visualContainerObjects: {
      background: [{ properties: { show: bool(true), color: color('#3B123C'), transparency: num(0) } }],
      border: [{ properties: { show: bool(false) } }],
      padding: [{ properties: { top: num(10), bottom: num(8), left: num(16), right: num(16) } }],
      general: [{ properties: { altText: str('Título: confiabilidad actual, focos recurrentes y eficacia de remediación. Datos sintéticos y casos publicados de Dataverse.') } }],
      visualHeader: [{ properties: { show: bool(false) } }]
    }
  }
});

const makeSlicer = ({ id, x, table, property, label, tabOrder }) => ({
  $schema: visualSchema,
  name: id,
  position: position(x, 24, 264, 80, 2000 + tabOrder, tabOrder),
  visual: {
    visualType: 'slicer',
    query: {
      queryState: {
        Values: { projections: [projection(column(table, property), table, property)] }
      }
    },
    objects: {
      data: [{ properties: { mode: str('Dropdown') } }],
      header: [{ properties: { show: bool(true), text: str(label) } }]
    },
    visualContainerObjects: chrome({
      title: label,
      altText: `Filtro desplegable de ${label}.`,
      showTitle: false,
      padding: 8
    })
  }
});

const cardObjects = (accent, valueFontSize, labelFontSize) => ({
  outline: [{ properties: { show: bool(false) }, selector: { id: 'default' } }],
  accentBar: [{ properties: {
    show: bool(true),
    position: str('Left'),
    width: num(5),
    color: color(accent)
  }, selector: { id: 'default' } }],
  value: [{ properties: {
    fontSize: num(valueFontSize),
    fontColor: color(accent),
    bold: bool(true)
  }, selector: { id: 'default' } }],
  label: [{ properties: {
    show: bool(true),
    fontSize: num(labelFontSize),
    fontColor: color('#514A53'),
    textWrap: bool(true)
  }, selector: { id: 'default' } }],
  padding: [{ properties: { paddingUniform: num(8) }, selector: { id: 'default' } }],
  layout: [{ properties: {
    topOuterMargin: int(0),
    bottomOuterMargin: int(0),
    leftOuterMargin: int(0),
    rightOuterMargin: int(0),
    paddingUniform: int(0)
  }, selector: { id: 'default' } }],
  cardCalloutArea: [{ properties: {
    show: bool(true),
    paddingUniform: int(4),
    rectangleRoundedCurve: int(6),
    backgroundFillColor: color('#FFFFFF'),
    backgroundTransparency: num(0)
  } }]
});

const makeCard = ({ id, x, width = 446, measures, accent, title, altText, tabOrder, valueFontSize, labelFontSize }) => ({
  $schema: visualSchema,
  name: id,
  position: position(x, 128, width, 176, 3000 + tabOrder, tabOrder),
  visual: {
    visualType: 'cardVisual',
    query: {
      queryState: {
        Data: {
          projections: measures.map(({ table, name, label }) => projection(measure(table, name), table, name, label ?? name))
        }
      }
    },
    objects: cardObjects(
      accent,
      valueFontSize ?? (measures.length > 1 ? 20 : 32),
      labelFontSize ?? (measures.length > 1 ? 8 : 12)
    ),
    visualContainerObjects: {
      ...chrome({ title, altText, showTitle: true, padding: 8 }),
      spacing: [{ properties: { customizeSpacing: bool(true), verticalSpacing: num(2), spaceBelowTitleArea: num(4) } }]
    }
  }
});

const makeLineChart = ({ id, tabOrder }) => ({
  $schema: visualSchema,
  name: id,
  position: position(32, 328, 916, 320, 4000 + tabOrder, tabOrder),
  visual: {
    visualType: 'lineChart',
    query: {
      queryState: {
        Category: { projections: [projection(column('Fecha', 'Fecha de snapshot'), 'Fecha', 'Fecha de snapshot')] },
        Y: { projections: [projection(measure('Desempeño de reglas', 'Data Quality Score'), 'Desempeño de reglas', 'Data Quality Score')] }
      },
      sortDefinition: {
        sort: [{ field: column('Fecha', 'Fecha de snapshot'), direction: 'Ascending' }],
        isDefaultSort: false
      }
    },
    objects: {
      dataPoint: [{ properties: { fill: color('#7A1E6C'), transparency: num(82) }, selector: { metadata: 'Desempeño de reglas.Data Quality Score' } }],
      lineStyles: [{ properties: {
        strokeWidth: num(3),
        lineChartType: str('smooth'),
        interpolationSmooth: str('monotoneX'),
        areaShow: bool(true),
        areaMatchStrokeColor: bool(true),
        showMarker: bool(true),
        markerShape: str('circle'),
        markerSize: num(6)
      }, selector: { metadata: 'Desempeño de reglas.Data Quality Score' } }],
      legend: [{ properties: { show: bool(false) } }]
    },
    visualContainerObjects: chrome({
      title: 'Evolución del Data Quality Score por corte',
      altText: 'Evolución del Data Quality Score en seis snapshots; el último corte alcanza 98.9 %, por encima del 98.2 % anterior.'
    })
  }
});

const makeMatrix = ({ id, tabOrder }) => ({
  $schema: visualSchema,
  name: id,
  position: position(972, 328, 916, 320, 4000 + tabOrder, tabOrder),
  visual: {
    visualType: 'pivotTable',
    query: {
      queryState: {
        Rows: { projections: [
          projection(column('Regla', 'Dimensión de calidad'), 'Regla', 'Dimensión de calidad'),
          projection(column('Regla', 'Nombre de regla'), 'Regla', 'Nombre de regla')
        ] },
        Values: { projections: [
          projection(measure('Desempeño de reglas', 'Data Quality Score'), 'Desempeño de reglas', 'Data Quality Score'),
          projection(measure('Desempeño de reglas', 'Checks fallidos'), 'Desempeño de reglas', 'Checks fallidos'),
          projection(measure('Excepciones', 'Instancias de excepción'), 'Excepciones', 'Instancias de excepción'),
          projection(measure('Excepciones', 'Tasa de recurrencia'), 'Excepciones', 'Tasa de recurrencia')
        ] }
      },
      sortDefinition: {
        sort: [{ field: measure('Desempeño de reglas', 'Checks fallidos'), direction: 'Descending' }],
        isDefaultSort: false
      }
    },
    objects: {
      columnHeaders: [{ properties: { columnAdjustment: str('growToFit'), autoSizeColumnWidth: bool(true) } }],
      rowHeaders: [{ properties: { stepped: bool(true), fontColor: color('#241E26') } }],
      values: [{ properties: {
        backColorPrimary: color('#FFFFFF'),
        backColorSecondary: color('#FAF7FA'),
        fontColorPrimary: color('#241E26'),
        fontColorSecondary: color('#241E26')
      } }]
    },
    visualContainerObjects: {
      ...chrome({
        title: 'Riesgo por dimensión y regla',
        altText: 'Matriz de reglas por dimensión con score, checks fallidos, instancias y tasa de recurrencia, ordenada por checks fallidos.'
      }),
      stylePreset: [{ properties: { name: str('None') } }]
    }
  }
});

const makeCasesTable = ({ id, tabOrder }) => ({
  $schema: visualSchema,
  name: id,
  position: position(32, 672, 916, 376, 5000 + tabOrder, tabOrder),
  visual: {
    visualType: 'tableEx',
    query: {
      queryState: {
        Values: { projections: [
          projection(column('Caso', 'Número de caso'), 'Caso', 'Número de caso'),
          projection(column('Caso', 'Título del caso'), 'Caso', 'Título del caso'),
          projection(column('Estado', 'Estado'), 'Estado', 'Estado'),
          projection(column('Responsable', 'Responsable'), 'Responsable', 'Responsable'),
          projection(column('Caso', 'Vence el'), 'Caso', 'Vence el')
        ] }
      },
      sortDefinition: {
        sort: [{ field: column('Caso', 'Vence el'), direction: 'Ascending' }],
        isDefaultSort: false
      }
    },
    objects: {
      columnHeaders: [{ properties: { columnAdjustment: str('growToFit'), autoSizeColumnWidth: bool(true) } }],
      values: [{ properties: {
        backColorPrimary: color('#FFFFFF'),
        backColorSecondary: color('#F7FAFB'),
        fontColorPrimary: color('#241E26'),
        fontColorSecondary: color('#241E26')
      } }],
      
    },
    visualContainerObjects: {
      ...chrome({
        title: 'Cinco casos publicados; tres permanecen abiertos',
        altText: 'Lista de cinco casos publicados con estado, responsable y fecha de vencimiento; tres permanecen abiertos.'
      }),
      stylePreset: [{ properties: { name: str('None') } }]
    }
  }
});

const makeEffectivenessChart = ({ id, tabOrder }) => ({
  $schema: visualSchema,
  name: id,
  position: position(972, 672, 916, 376, 5000 + tabOrder, tabOrder),
  visual: {
    visualType: 'clusteredBarChart',
    query: {
      queryState: {
        Category: { projections: [projection(column('Caso', 'Tipo de resolución visible'), 'Caso', 'Tipo de resolución visible', 'Tipo de resolución')] },
        Series: { projections: [projection(column('Caso', 'Estado de corrección de origen'), 'Caso', 'Estado de corrección de origen')] },
        Y: { projections: [projection(measure('Caso', 'Casos publicados'), 'Caso', 'Casos publicados')] }
      },
      sortDefinition: {
        sort: [{ field: measure('Caso', 'Casos publicados'), direction: 'Descending' }],
        isDefaultSort: false
      }
    },
    objects: {
      valueAxis: [{ properties: { start: num(0), show: bool(false), gridlineShow: bool(false) } }],
      labels: [{ properties: { show: bool(true), labelPosition: str('OutsideEnd') } }],
      legend: [{ properties: { show: bool(true), position: str('Top') } }],
      dataPoint: [{ properties: { fill: color('#D59B28') } }]
    },
    visualContainerObjects: chrome({
      title: 'Resolución administrativa vs. corrección del origen',
      altText: 'Casos publicados por tipo de resolución y estado de corrección de origen. La tasa confirmada es cero por ciento en la muestra actual.'
    })
  }
});

const visuals = [
  makeTextbox({ id: '10000000000000000001', x: 32, y: 24, width: 976, height: 80, z: 1000, tabOrder: 1 }),
  makeSlicer({ id: '10000000000000000002', x: 1032, table: 'Fecha', property: 'Fecha de snapshot', label: 'Corte', tabOrder: 2 }),
  makeSlicer({ id: '10000000000000000003', x: 1320, table: 'Sistema fuente', property: 'Sistema fuente', label: 'Sistema fuente', tabOrder: 3 }),
  makeSlicer({ id: '10000000000000000004', x: 1608, table: 'Regla', property: 'Dimensión de calidad', label: 'Dimensión', tabOrder: 4 }),
  makeCard({
    id: '10000000000000000005', x: 32, accent: '#7A1E6C', title: 'Calidad actual', tabOrder: 5,
    valueFontSize: 12,
    altText: 'Calidad actual 98.9 %, con una variación positiva de 0.7 puntos porcentuales frente al corte anterior.',
    measures: [
      { table: 'Desempeño de reglas', name: 'Data Quality Score actual', label: 'DQ score' },
      { table: 'Desempeño de reglas', name: 'Variación DQ Score (pp)', label: 'Cambio (pp)' },
      { table: 'Cortes de calidad', name: 'Última actualización', label: 'Último corte' }
    ]
  }),
  makeCard({
    id: '10000000000000000006', x: 502, accent: '#C64B5B', title: 'Riesgo agregado', tabOrder: 6,
    altText: 'Tasa actual de excepción 3.0 %, equivalente a 78 registros con excepción de 2,635 evaluados.',
    measures: [
      { table: 'Cortes de calidad', name: 'Tasa de excepción actual', label: 'Tasa' },
      { table: 'Cortes de calidad', name: 'Registros con excepción actuales', label: 'Afectados' },
      { table: 'Cortes de calidad', name: 'Registros evaluados actuales', label: 'Evaluados' }
    ]
  }),
  makeCard({
    id: '10000000000000000007', x: 972, accent: '#006B8F', title: 'Casos publicados', tabOrder: 7,
    altText: 'Tres casos publicados están abiertos de un total de cinco. La cobertura frente a Gold es 0.9 %.',
    measures: [
      { table: 'Caso', name: 'Casos publicados abiertos', label: 'Abiertos' },
      { table: 'Caso', name: 'Casos publicados', label: 'Total' },
      { table: 'Excepción publicada', name: 'Cobertura de casos publicados', label: 'Cobertura' }
    ]
  }),
  makeCard({
    id: '10000000000000000008', x: 1442, accent: '#00A6A6', title: 'Cumplimiento SLA', tabOrder: 8,
    altText: 'No hay casos terminales con vencimiento y fecha de resolución suficientes para calcular cumplimiento SLA.',
    valueFontSize: 24,
    labelFontSize: 10,
    measures: [{ table: 'Caso', name: 'Estado de cumplimiento SLA', label: 'Estado' }]
  }),
  makeLineChart({ id: '10000000000000000009', tabOrder: 9 }),
  makeMatrix({ id: '1000000000000000000a', tabOrder: 10 }),
  makeCasesTable({ id: '1000000000000000000b', tabOrder: 11 }),
  makeEffectivenessChart({ id: '1000000000000000000c', tabOrder: 12 })
];

for (const visual of visuals) writeVisual(visual.name, visual);

const pagePath = path.join(pageRoot, 'page.json');
const page = JSON.parse(fs.readFileSync(pagePath, 'utf8'));
page.width = 1920;
page.height = 1080;
page.displayOption = 'FitToPage';
page.objects = {
  background: [{ properties: { color: color('#F4F2F5'), transparency: num(0) } }],
  outspace: [{ properties: { color: color('#241E26'), transparency: num(0) } }]
};
fs.writeFileSync(pagePath, `${JSON.stringify(page, null, 2)}\n`);

const themeFile = 'HRDataQuality-8d2a4f10.json';
const theme = {
  $schema: 'https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.153.json',
  name: themeFile,
  dataColors: ['#3D7F45', '#D59B28', '#C64B5B', '#7A1E6C', '#006B8F', '#00A6A6', '#5A4D61', '#A98EA5'],
  good: '#3D7F45',
  neutral: '#D59B28',
  bad: '#C64B5B',
  maximum: '#7A1E6C',
  center: '#D59B28',
  minimum: '#EFE2ED',
  null: '#A98EA5',
  foreground: '#241E26',
  background: '#FFFFFF',
  tableAccent: '#7A1E6C',
  textClasses: {
    callout: { fontSize: 28, fontFace: 'Segoe UI', color: '#241E26' },
    title: { fontSize: 14, fontFace: 'Segoe UI Semibold', color: '#241E26' },
    header: { fontSize: 12, fontFace: 'Segoe UI Semibold', color: '#241E26' },
    label: { fontSize: 10, fontFace: 'Segoe UI', color: '#241E26' }
  },
  visualStyles: {
    '*': {
      '*': {
        border: [{ show: true, color: { solid: { color: '#DED7E0' } }, radius: 8 }],
        dropShadow: [{ show: false }],
        padding: [{ top: 8, bottom: 8, left: 8, right: 8 }],
        visualHeader: [{ show: false }],
        categoryAxis: [{ gridlineStyle: 'dotted', gridlineColor: { solid: { color: '#EEE9EF' } } }],
        valueAxis: [{ gridlineStyle: 'dotted', gridlineColor: { solid: { color: '#EEE9EF' } } }]
      }
    },
    textbox: {
      '*': {
        padding: [{ top: 0, bottom: 0, left: 0, right: 0 }],
        background: [{ show: false }],
        border: [{ show: false }]
      }
    },
    cardVisual: {
      '*': {
        value: [{ bold: true, $id: 'default' }],
        label: [{ show: true, $id: 'default' }],
        cardCalloutArea: [{ paddingUniform: 0 }],
        title: [{ show: false }],
        spacing: [{ verticalSpacing: 2 }]
      }
    },
    tableEx: {
      '*': {
        columnHeaders: [{ autoSizeColumnWidth: true, columnAdjustment: 'growToFit', backColor: { solid: { color: '#F1ECF2' } }, fontColor: { solid: { color: '#241E26' } }, bold: true }],
        values: [{ backColorPrimary: { solid: { color: '#FFFFFF' } }, backColorSecondary: { solid: { color: '#F7FAFB' } }, fontColorPrimary: { solid: { color: '#241E26' } }, fontColorSecondary: { solid: { color: '#241E26' } } }]
      }
    },
    pivotTable: {
      '*': {
        columnHeaders: [{ autoSizeColumnWidth: true, columnAdjustment: 'growToFit', backColor: { solid: { color: '#F1ECF2' } }, fontColor: { solid: { color: '#241E26' } }, bold: true }],
        values: [{ backColorPrimary: { solid: { color: '#FFFFFF' } }, backColorSecondary: { solid: { color: '#FAF7FA' } }, fontColorPrimary: { solid: { color: '#241E26' } }, fontColorSecondary: { solid: { color: '#241E26' } } }]
      }
    },
    lineChart: {
      '*': {
        lineStyles: [{ strokeWidth: 3, lineChartType: 'smooth', interpolationSmooth: 'monotoneX', areaShow: true, areaMatchStrokeColor: true }],
        labels: [{ show: true, labelPosition: 'Above', fontSize: 9, color: { solid: { color: '#241E26' } }, labelDensity: 25 }],
        categoryAxis: [{ show: true, fontSize: 10, labelColor: { solid: { color: '#615762' } }, showAxisTitle: false, gridlineShow: false }],
        valueAxis: [{ show: true, fontSize: 9, labelColor: { solid: { color: '#615762' } }, showAxisTitle: false, gridlineStyle: 'dotted', gridlineColor: { solid: { color: '#DED7E0' } } }],
        legend: [{ show: false }]
      }
    },
    clusteredBarChart: {
      '*': {
        labels: [{ show: true, fontSize: 10 }],
        valueAxis: [{ show: false, gridlineShow: false, showAxisTitle: false }],
        categoryAxis: [{ show: true, fontSize: 10, labelColor: { solid: { color: '#615762' } }, showAxisTitle: false, innerPadding: 20, gridlineShow: false }],
        dataPoint: [{ borderShow: false }],
        legend: [{ show: true, fontSize: 9, labelColor: { solid: { color: '#615762' } } }]
      }
    },
    slicer: {
      '*': {
        header: [{ fontFamily: 'Segoe UI Semibold', textSize: 10, fontColor: { solid: { color: '#241E26' } }, outlineStyle: 0 }],
        items: [{ fontFamily: 'Segoe UI', textSize: 9, fontColor: { solid: { color: '#241E26' } }, outlineStyle: 0, padding: 2 }],
        date: [{ fontFamily: 'Segoe UI', textSize: 9, fontColor: { solid: { color: '#241E26' } } }]
      }
    }
  }
};
const priorTheme = fs.readdirSync(registeredRoot).find((name) => /^HRDataQuality-[0-9a-f]+\.json$/i.test(name) && name !== themeFile);
if (priorTheme) fs.renameSync(path.join(registeredRoot, priorTheme), path.join(registeredRoot, themeFile));
fs.writeFileSync(path.join(registeredRoot, themeFile), `${JSON.stringify(theme, null, 2)}\n`);

const reportPath = path.join(definitionRoot, 'report.json');
const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
report.themeCollection.customTheme = {
  name: themeFile,
  reportVersionAtImport: { ...report.themeCollection.baseTheme.reportVersionAtImport },
  type: 'RegisteredResources'
};
const registeredPackage = {
  name: 'RegisteredResources',
  type: 'RegisteredResources',
  items: [{ name: themeFile, path: themeFile, type: 'CustomTheme' }]
};
report.resourcePackages = report.resourcePackages.filter((pkg) => pkg.name !== 'RegisteredResources');
report.resourcePackages.push(registeredPackage);
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);

console.log(JSON.stringify({ pageId, visualCount: visuals.length, themeFile, canvas: '1920x1080' }));
