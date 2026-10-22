# V-UNIVERSAL

> Одна модель версионирования — `trunk + дерево версий` — применённая к
> **девяти** разным доменам. Железо, квантовая механика, биология,
> физика, математика, право, экономика и сознание — всё на одних и тех
> же трёх примитивах: `fork / write / commit`.

[![CI](https://img.shields.io/badge/CI-pytest%20%2B%20ruff-blue)](.github/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)
[![Built with uv](https://img.shields.io/badge/built%20with-uv-purple)](https://docs.astral.sh/uv/)

Документация на других языках: [**English**](README.md)

---

## Кратко

Каждый домен в этой библиотеке построен на одних и тех же трёх примитивах:

```python
v = layer.fork()      # дешёвая in-memory ветка
v.write(key, value)   # стадировать изменение в черновик
v.commit()            # опубликовать черновик обратно в trunk
# или
v.abort()             # выкинуть черновик
```

Это, по сути, всё что делает `git`. Интересное утверждение V-UNIVERSAL:
**этих трёх примитивов достаточно, чтобы промоделировать неожиданно
широкий круг систем** — от hardware transactional memory, через
квантовые состояния и биологические геномы, вплоть до игрушечной модели
сознания. Библиотека — это рабочий пример этого утверждения, с тестами.

## Девять доменов

| Модуль | Trunk | Версия | Commit |
|---|---|---|---|
| `VHardware` | регистры / шина / кэш | транзакция | атомарная публикация |
| `VQuantum` | вектор состояния | применение гейта | измерение (коллапс) |
| `VBio` | геном | мутация | отбор |
| `VPhysics` | законы + мир | ветка начальных условий | закоммиченная история |
| `VMath` | аксиомы | теорема + доказательство | принятая теорема |
| `VLaw` | конституция | законопроект | принятый закон |
| `VEconomy` | бухгалтерская книга | перевод | подтверждённая транзакция |
| `VConsciousness` | ощущения + эмоции | мысль + решение | исполненное решение |
| `bench_universal` | — | кросс-доменный микробенчмарк | — |

## Установка

```bash
git clone https://github.com/your-org/v-universal.git
cd v-universal
uv sync --extra dev         # или: pip install -e ".[dev]"
pytest                      # <1 секунды на CPU
```

## Быстрый старт

```python
from v_universal import VHardware

hw = VHardware()
hw.begin_tx()           # форкаем все три слоя
hw.write_reg(0, 42)
hw.bus_write(0x1000, 0xDEAD)
hw.abort_tx()           # выкидываем — trunk не изменился

hw.begin_tx()
hw.write_reg(0, 42)
hw.commit_tx()          # публикуем — в trunk теперь r0=42
```

Тот же паттерн работает для всех остальных доменов:

```python
from v_universal import VEconomy, InsufficientFunds

eco = VEconomy()
v = eco.ledger.fork()
try:
    eco.transfer(v, "alice", "bob", 100)
    v.commit()
except InsufficientFunds:
    v.abort()
```

## Примеры

| Файл | Домен | Что показывает |
|---|---|---|
| `01_hardware.py` | V-HARDWARE | HTM: begin / write / abort / commit |
| `02_quantum.py` | V-QUANTUM | Суперпозиция Адамара, коллапс при измерении |
| `03_bio.py` | V-BIO | Мутируем 10 кандидатов, отбираем и коммитим лучшего |
| `04_physics_multiverse.py` | V-PHYSICS | Одно тело под Лунной / Земной / Юпитерной гравитацией |
| `05_math.py` | V-MATH | Аксиомы → теоремы, с проваленным доказательством, которое abort |
| `06_law.py` | V-LAW | Законы + поправки к конституции + непрошедший законопроект |
| `07_economy.py` | V-ECONOMY | Переводы, нехватка средств, параллельные ветки |
| `08_consciousness.py` | V-CONSCIOUSNESS | Мысли, решения, сожаление |
| `09_benchmark.py` | — | Кросс-доменный микробенчмарк |

Запуск: `python examples/<file>.py`.

## Как это работает

### Ключевые примитивы

Вся библиотека — три класса в `v_universal/core.py`:

* **`Version`** — иммутабельный узел дерева версий. Хранит словарь
  `changes` относительно родителя. Чтение ключа поднимается по цепочке
  родителей.
* **`VLayer`** — trunk. Владеет корневым `Version`, текущим head,
  плоским last-writer-wins индексом и опциональным базовым слоем для
  наследования. `crystallize()` замораживает `set_base`, чтобы
  начальные значения задавались заранее.
* **`VVersion`** — дешёвый in-memory форк. Записи идут в черновик
  `draft`; `commit()` публикует черновик в trunk, `abort()` его
  выкидывает.

Это всё. Каждый доменный модуль добавляет поверх доменные аксессоры —
`VHardware.write_reg`, `VQuantum.apply_gate`, `VBio.mutate` и т.д. — но
механика под капотом всегда `fork / write / commit`.

### Зачем это надо?

Три причины:

1. **Педагогика.** Когда вы внутренне усвоите `fork / write / commit`,
   вы начнёте видеть этот паттерн везде — в `git`, в транзакциях БД, в
   блокчейн-консенсусе, в hardware TM, в эволюционной динамике.
   V-UNIVERSAL делает паттерн конкретным в девяти доменах на одних и
   тех же трёх Python-классах.

2. **Композиция.** Поскольку все домены используют одни примитивы,
   можно строить гибридные системы. Генетический алгоритм, чья функция
   приспособленности запускает физическую симуляцию. Юридическая
   система, которая атомарно проводит финансовые переводы. Примитивы
   компонуются бесплатно.

3. **Тестируемость.** Поведение каждого домена сводится к «был коммит
   или abort». Сьют из 85 тестов короткий именно потому, что
   абстракция схлопывает девять тестовых поверхностей в одну.

### Ограничения

Это research preview, не production-библиотека:

* **Персистентность**: ничего не сериализуется. `VLayer` живёт в RAM;
  если процесс умер — trunk исчез.
* **Конкурентность**: никаких блокировок. Два потока, коммитящие в
  один слой, будут состязаться.
* **Производительность**: `Version.resolve` поднимается по цепочке
  родителей при каждом чтении. ОК для тысяч версий, плохо для
  миллионов. Плоский снапшот на версию это починил бы.
* **Квантовая механика**: только однокубитные гейты + CNOT, без GPU,
  только state-vector formalism (без tensor networks).

## Структура репозитория

```
v-universal/
├── src/v_universal/
│   ├── core.py              # Version, VLayer, VVersion
│   ├── hardware.py          # VHardware
│   ├── quantum.py           # VQuantum + хелперы для гейтов
│   ├── bio.py               # VBio
│   ├── physics.py           # VPhysics (мультивселенная)
│   ├── math_layer.py        # VMath (аксиомы + теоремы)
│   ├── law.py               # VLaw (конституция + законы)
│   ├── economy.py           # VEconomy (ledger + переводы)
│   ├── consciousness.py     # VConsciousness (ощущения + мысли)
│   └── benchmark.py         # bench_universal
├── tests/                   # 10 pytest-модулей, всего 85 тестов
├── examples/                # 9 runnable-демо
├── notebooks/               # Очищенный .ipynb
├── .github/workflows/ci.yml # Python 3.10 / 3.11 / 3.12
├── pyproject.toml           # uv + hatchling + ruff
└── README.md / README.ru.md
```

## Статус

Research preview. Apache-2.0. Контрибьюции приветствуются — см.
[Контрибьюция](#контрибьюция).

## Контрибьюция

1. `uv sync --extra dev`
2. `pre-commit install`
3. Добавьте тест в `tests/`, который падает без вашего изменения.
4. `pytest` и `ruff check .` должны быть зелёными.
5. Откройте PR — CI гоняет Python 3.10/3.11/3.12.

## Цитирование

```bibtex
@misc{vuniversal2025,
  title  = {V-UNIVERSAL: one versioning model for everything},
  author = {V-UNIVERSAL Contributors},
  year   = {2025},
  note   = {Research preview, Apache-2.0}
}
```

## Лицензия

Apache License 2.0 — см. [LICENSE](LICENSE).
