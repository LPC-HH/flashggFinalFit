#!/usr/bin/env python3
"""Export nominal and QCD/PDF fitted parameters and shifts to a CSV."""

import argparse
import csv
import json
import math
from pathlib import Path


def main():
    signal_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_dir', nargs='?', type=Path,
                        default=signal_dir / 'outdir_tutorial_combined/signalFit/shapeSystematics')
    parser.add_argument('output_csv', nargs='?', type=Path,
                        default=signal_dir / 'shape_parameter_comparison.csv')
    args = parser.parse_args()

    reports = sorted(args.input_dir.glob('*.json'))
    if not reports:
        parser.error('No fitted parameter reports found in %s' % args.input_dir)

    fields = ['process', 'year', 'category', 'fit_process', 'fit_category',
              'parameter', 'mass', 'nominal']
    for source in ('qcd', 'pdf'):
        for direction in ('up', 'down'):
            name = '%s_%s' % (source, direction)
            fields.extend([name, name + '_diff', name + '_pct'])

    rows = []
    for path in reports:
        process, year, category = path.stem.rsplit('_', 2)
        with path.open() as handle:
            report = json.load(handle)
        for parameter, sources in sorted(report['parameters'].items()):
            for mass in sorted(sources['qcd'], key=float):
                nominal = float(sources['qcd'][mass]['nominal'])
                pdf_nominal = float(sources['pdf'][mass]['nominal'])
                if not math.isfinite(nominal) or not math.isclose(nominal, pdf_nominal):
                    raise ValueError('Invalid or inconsistent nominal for %s %s M%s' % (path, parameter, mass))
                row = dict(process=process, year=year, category=category,
                           fit_process=report['fit_proc'], fit_category=report['fit_cat'],
                           parameter=parameter, mass=mass, nominal=nominal)
                for source in ('qcd', 'pdf'):
                    for direction in ('up', 'down'):
                        name = '%s_%s' % (source, direction)
                        varied = float(sources[source][mass][direction])
                        if not math.isfinite(varied):
                            raise ValueError('Non-finite %s for %s %s M%s' % (name, path, parameter, mass))
                        difference = varied - nominal
                        row[name] = varied
                        row[name + '_diff'] = difference
                        row[name + '_pct'] = 100. * difference / nominal if nominal != 0. else ''
                rows.append(row)

    with args.output_csv.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print('Saved %g parameter rows from %g reports to %s' % (len(rows), len(reports), args.output_csv))
    print('*_diff = variation - nominal; *_pct = 100 * (variation - nominal) / nominal.')
    print('Percentages are blank for zero nominal values; use absolute shifts for mass offsets near zero.')


if __name__ == '__main__':
    main()
