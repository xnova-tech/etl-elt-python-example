# ETL и ELT на одном наборе заказов

Небольшой воспроизводимый пример XNova сравнивает порядок операций ETL и ELT на одном синтетическом снимке заказов. Оба маршрута используют SQLite в памяти и создают одинаковую подготовленную таблицу, но ETL проверяет и преобразует строки в Python до загрузки, а ELT сначала сохраняет исходные значения и затем преобразует их SQL-запросом.

Проект не сравнивает производительность промышленных хранилищ и не обращается к сети или внешнему API.

## Что понадобится

- Python 3.12;
- Git;
- терминал.

## Установка

```bash
git clone https://github.com/xnova-tech/etl-elt-python-example.git
cd etl-elt-python-example
python3.12 -m venv .venv
```

Активируйте окружение:

- macOS и Linux: `source .venv/bin/activate`;
- Windows PowerShell: `.venv\Scripts\Activate.ps1`;
- Windows cmd: `.venv\Scripts\activate.bat`.

Установите закреплённые инструменты разработки:

```bash
python -m pip install -r requirements-dev.txt
```

## Запуск

```bash
python run_example.py
python -m pytest -q
```

Основной пример выводит:

```text
etl_rows: 2
etl_total_cents: 3500
elt_rows: 2
elt_total_cents: 3500
same_result: true
```

Тесты проверяют одинаковый подготовленный результат, сохранение исходного слоя ELT, повтор полного снимка и откат обеих таблиц при неверной сумме, неизвестном статусе, пустом или повторяющемся идентификаторе.

## Структура

- `etl_elt_example/domain.py` — неизменяемые модели входных, проверенных и подготовленных заказов;
- `etl_elt_example/validation.py` — проверка входного снимка для ETL;
- `etl_elt_example/storage.py` — транзакции и SQL-преобразование для ELT;
- `etl_elt_example/pipelines.py` — явный порядок действий двух маршрутов;
- `etl_elt_example/demo.py` — сравнение результатов без вывода в терминал;
- `run_example.py` — тонкая CLI-точка входа;
- `tests/test_pipelines.py` — pytest-сценарии и отрицательные контроли.

Исходники распространяются по Apache-2.0; условия находятся в `LICENSE`.
