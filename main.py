import json
import os

import pandas as pd
from PyInquirer import prompt
from scrapy.crawler import CrawlerProcess

from lavoz.configs import Configs
from lavoz.output import OutputFormats
from lavoz.process import (
    add_has_balcony,
    add_has_garage,
    add_has_garden,
    add_has_terrace,
    capitalize_location,
    drop_nan_expenses,
    drop_nan_prices,
    normalize_title,
    fill_nan_strings,
)
from lavoz.settings import OUTPUT_FILE
from lavoz.spiders import LavozSpider


questions = [
    {
        'type': 'input',
        'name': 'base_url',
        'message': 'URL base de Clasificados LaVoz:'
    },
    {
        'type': 'list',
        'name': 'output_format',
        'message': 'Exportar a:',
        'choices': [
            OutputFormats.CSV,
            OutputFormats.JSON
        ]
    },
    {
        'type': 'checkbox',
        'name': 'config',
        'message': 'Configuración:',
        'choices': [
            {
                'name': Configs.DROP_NAN_EXPENSES
            }
        ]
    }
]


def postprocess(config: dict) -> pd.DataFrame:
    data = pd.DataFrame.from_records(
        json.load(open(OUTPUT_FILE, encoding='utf-8'))
    )

    if Configs.DROP_NAN_EXPENSES in config:
        data = data.pipe(drop_nan_expenses)

    return (data.pipe(drop_nan_prices)
                .pipe(fill_nan_strings)
                .pipe(capitalize_location)
                .pipe(normalize_title)
                .pipe(add_has_balcony)
                .pipe(add_has_terrace)
                .pipe(add_has_garage)
                .pipe(add_has_garden))


def export(data: pd.DataFrame, format: str) -> None:
    if format == OutputFormats.CSV:
        data.to_csv('alquileres.csv', index=False)

    if format == OutputFormats.JSON:
        data.to_json('alquileres.json', orient='records')

    os.remove(OUTPUT_FILE)


def main():
    answers = prompt(questions)
    spider = LavozSpider
    spider.base_url = answers['base_url']
    spider.start_urls = [spider.base_url]
    crawler_settings = {'FEEDS': {OUTPUT_FILE: {'format': 'json',
                                                'overwrite': True}}}
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(spider)
    process.start()
    data = postprocess(answers['config'])
    export(data, answers['output_format'])


if __name__ == '__main__':
    main()
