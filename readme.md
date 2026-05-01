# Эмулятор классического рынка (версия 2.0)

Модульная симуляция «фабрики — рынок — потребители — модернизация» с конфигом YAML, чистым ядром без UI и опциональными фичами (нерациональность потребителей, занятость на фабриках).

## Структура

| Путь | Назначение |
|------|------------|
| [econom_sim/](econom_sim/) | Пакет: `config`, `engine`, `domain`, `metrics`, `events`, `market/*`, `io/*`, `ui/*` |
| [configs/](configs/) | Сценарии YAML (`base.yaml`, `irrational.yaml`, `employment.yaml`) |
| [tests/](tests/) | Юнит-тесты (`python -m unittest discover -s tests -p 'test_*.py' -v`) |
| [old_versions/](old_versions/) | Архив: `smith_legacy.py`, `Base_econom_model_1.2.ipynb` |
| [smith.py](smith.py) | Тонкий shim: `import smith` подгружает `old_versions/smith_legacy.py` для старых ноутбуков |

## Установка

Обычный (не редактируемый) режим ставится всегда; **редактируемый** (`-e`) требует `setuptools>=64` и современный `pip`:

```bash
cd econom_models
pip install -U pip setuptools wheel
pip install ".[ui]"          # обычная установка пакета + UI-дополнения
# Либо в режиме разработки (PEP 660):
pip install -e ".[ui]"
```

Если `pip install -e` ругается на `build_editable`, обновите `pip` и `setuptools` или просто используйте `pip install ".[ui]"` и добавьте корень проекта в `PYTHONPATH`:

```bash
PYTHONPATH=. streamlit run econom_sim/ui/streamlit_app.py
```

Зависимости ядра: `numpy`, `pandas`, `pydantic`, `pyyaml`, `pyarrow`.

## Запуск

**Программный API:**

```python
from econom_sim import load_config, init_state, run_period

cfg = load_config("configs/base.yaml")
state = init_state(cfg)
for _ in range(cfg.periods):
    snap = run_period(state)
    print(snap.metrics)
```

**Streamlit (графики по мере раундов):**

```bash
streamlit run econom_sim/ui/streamlit_app.py
```

**Пошаговый CLI (разработка):**

```bash
econom-sim-cli --config configs/base.yaml
# команды: n | c K | set path value | raw | q
```

## Конфиг YAML

Корневые поля: `seed`, `periods`, `agents`, `salary`, `factory_init`, `consumer`, `modernisation`, `pricing`, `features`.

- **Нерациональность:** `consumer.rationality` (1 = как в старом `smith.py`), плюс `consumer.noise` для шума восприятия.
- **Занятость:** `features.employment: true` и `salary.model: employment` — зарплата с фабрики, покупка списывает деньги жителя; `bankrupt_layoffs` — увольнение при банкротстве работодателя.

Подробности полей см. схемы в [econom_sim/config.py](econom_sim/config.py).

## Новая фича

1. Добавьте поле в `FeaturesConfig` или в соответствующий раздел конфига.
2. Реализуйте ветку в `econom_sim/market/` или в `engine.py`, завернув в `if cfg.features....`.
3. Добавьте тест в `tests/`.

## Мессенджеры

Каркас подписчика на `EventBus`: [econom_sim/ui/telegram_bot.py](econom_sim/ui/telegram_bot.py). Логика симуляции не зависит от UI.

## Лицензия / история

История изменений — в git; прежняя монолитная версия лежит в `old_versions/`.
