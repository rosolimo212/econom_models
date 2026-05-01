"""Streamlit: load config preview, then run simulation (status text, charts at end)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _merge_dict(base: dict, overrides: dict) -> dict:
    out = dict(base)
    for k, v in overrides.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _merge_dict(out[k], v)
        else:
            out[k] = v
    return out


def _sidebar_merged_yaml(
    *,
    raw: dict,
    seed: int,
    periods: int,
    n_cit: int,
    n_fact: int,
) -> dict:
    return _merge_dict(
        raw,
        {
            "seed": int(seed),
            "periods": int(periods),
            "agents": {"citizens": int(n_cit), "factories": int(n_fact)},
        },
    )


def _current_key(pick: str, seed: int, periods: int, n_cit: int, n_fact: int) -> tuple:
    return (pick, int(seed), int(periods), int(n_cit), int(n_fact))


def _distinct_products_sold(snap) -> int:
    seen: set[tuple[float, float]] = set()
    for r in snap.citizen_rows:
        if r.get("id", -1) >= 0:
            seen.add((float(r["price"]), float(r["quality"])))
    return len(seen)


def _scatter_price_quality(snap, title: str):
    import pandas as pd
    import plotly.express as px

    pts = []
    for row in snap.factory_rows:
        p = float(row.get("price") or 0)
        if p > 0:
            pts.append(
                {
                    "quality": float(row["max_quality"]),
                    "price": p,
                    "id": row["id"],
                    "sales": int(row.get("pur", 0) or 0),
                }
            )
    dfp = pd.DataFrame(pts)
    if dfp.empty:
        return None
    kw: dict = dict(
        x="quality",
        y="price",
        hover_data=["id"],
        title=title,
        labels={"quality": "Качество (max_quality)", "price": "Цена"},
    )
    if len(dfp) and dfp["sales"].max() > 0:
        kw["size"] = "sales"
    return px.scatter(dfp, **kw)


def main() -> None:
    import importlib.util

    if importlib.util.find_spec("streamlit") is None:
        raise SystemExit("Install UI extras: pip install 'econom-sim[ui]'")
    if importlib.util.find_spec("plotly") is None:
        raise SystemExit("Install UI extras: pip install 'econom-sim[ui]'")

    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import streamlit as st
    import yaml
    from plotly.subplots import make_subplots

    from econom_sim.config import Config
    from econom_sim.engine import init_state, run_period
    from econom_sim.io.snapshot import snapshots_to_csv, snapshots_to_parquet

    st.set_page_config(page_title="Econom Sim", layout="wide")
    st.title("Классический рынок — симуляция")

    if "load_stamp" not in st.session_state:
        st.session_state.load_stamp = None
    if "loaded_merged" not in st.session_state:
        st.session_state.loaded_merged = None

    cfg_dir = _ROOT / "configs"
    yaml_files = sorted(cfg_dir.glob("*.yaml")) if cfg_dir.is_dir() else []
    if not yaml_files:
        st.error("Не найдено configs/*.yaml")
        return
    default_name = "base.yaml" if (cfg_dir / "base.yaml").exists() else yaml_files[0].name
    names = [p.name for p in yaml_files]
    pick = st.sidebar.selectbox(
        "Конфиг YAML",
        names,
        index=names.index(default_name) if default_name in names else 0,
    )
    raw = yaml.safe_load((cfg_dir / pick).read_text(encoding="utf-8"))

    st.sidebar.subheader("Переопределения")
    seed = st.sidebar.number_input("seed", value=int(raw.get("seed", 42)), step=1)
    periods = st.sidebar.number_input("periods", value=int(raw.get("periods", 30)), min_value=1, step=1)
    agents = raw.get("agents") or {}
    n_cit = st.sidebar.number_input(
        "citizens", value=int(agents.get("citizens", 100)), min_value=1, step=1
    )
    n_fact = st.sidebar.number_input(
        "factories", value=int(agents.get("factories", 10)), min_value=1, step=1
    )

    key = _current_key(pick, seed, periods, n_cit, n_fact)
    merged_now = _sidebar_merged_yaml(
        raw=raw, seed=seed, periods=periods, n_cit=n_cit, n_fact=n_fact
    )

    load_btn = st.sidebar.button("Загрузить конфиг")
    run_btn = st.sidebar.button("Запустить симуляцию", type="primary")

    if load_btn:
        try:
            Config.model_validate(merged_now)
        except Exception as e:
            st.sidebar.error(f"Ошибка конфига: {e}")
        else:
            st.session_state.load_stamp = key
            st.session_state.loaded_merged = json.loads(json.dumps(merged_now))
            st.sidebar.success("Конфиг принят — можно запускать симуляцию.")

    config_loaded = (
        st.session_state.loaded_merged is not None and st.session_state.load_stamp == key
    )

    if config_loaded:
        cfg_prev = Config.model_validate(st.session_state.loaded_merged)
        st.subheader("Загруженный конфиг")
        st.markdown("Структура JSON (как будет использован при запуске):")
        st.json(json.loads(cfg_prev.model_dump_json()))

        prv = init_state(cfg_prev)
        df_c = pd.DataFrame({"money": [c.money for c in prv.citizens]})
        df_f = pd.DataFrame({"capital": [f.capital for f in prv.factories]})
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Граждане: распределение стартовых денег")
            st.plotly_chart(
                px.histogram(df_c, x="money", nbins=min(80, max(10, len(df_c) // 5))),
                use_container_width=True,
            )
            st.caption(
                f"n={len(df_c)}, min={df_c['money'].min():.2f}, max={df_c['money'].max():.2f}"
            )
        with c2:
            st.markdown("### Фабрики: распределение стартового капитала")
            st.plotly_chart(
                px.histogram(df_f, x="capital", nbins=min(80, max(10, len(df_f) // 2))),
                use_container_width=True,
            )
            st.caption(
                f"n={len(df_f)}, min={df_f['capital'].min():.2f}, max={df_f['capital'].max():.2f}"
            )
    else:
        st.info(
            "Выберите YAML и параметры в сайдбаре → **«Загрузить конфиг»** "
            "(появится JSON и гистограммы). Затем **«Запустить симуляцию»**. "
            "После любого изменения сайдбара загрузите конфиг снова."
        )

    if run_btn:
        if not config_loaded:
            st.warning(
                "Сначала **«Загрузить конфиг»** для текущих значений сайдбара."
            )
        else:
            cfg = Config.model_validate(st.session_state.loaded_merged)
            state = init_state(cfg)
            snaps = []

            status = st.empty()
            log_lines: list[str] = []

            periods_x: list[int] = []
            gini_f: list[float] = []
            gini_c: list[float] = []
            sales: list[int] = []
            mean_p: list[float] = []
            mean_q: list[float] = []
            distinct_p: list[int] = []

            rows_cap: list[dict] = []

            for _i in range(cfg.periods):
                snap = run_period(state)
                snaps.append(snap)
                periods_x.append(snap.period)
                gini_f.append(snap.metrics["gini_factory_capital"])
                gini_c.append(snap.metrics["gini_citizen_money"])
                sales.append(snap.metrics["sales_count"])
                mean_p.append(snap.metrics["mean_price"])
                mean_q.append(snap.metrics["mean_quality"])
                dp = _distinct_products_sold(snap)
                distinct_p.append(dp)
                for r in snap.factory_rows:
                    rows_cap.append(
                        {
                            "period": snap.period,
                            "factory_id": r["id"],
                            "capital": r["capital"],
                        }
                    )
                line = (
                    f"Раунд **{snap.period + 1}** / {cfg.periods} | "
                    f"продаж: {snap.metrics['sales_count']} | "
                    f"ср. цена: {snap.metrics['mean_price']:.5g} | "
                    f"ср. качество: {snap.metrics['mean_quality']:.5g} | "
                    f"разных товаров (продажи): {dp} | "
                    f"Gini фабрики: {snap.metrics['gini_factory_capital']:.4f} | "
                    f"Σ капитал фабрик: {snap.metrics['total_factory_capital']:.2f}"
                )
                log_lines.append(line)
                status.markdown("**Статус**\n\n" + "\n\n".join(log_lines[-15:]))

            status.markdown(
                "**Статус (последние строки)**\n\n" + "\n\n".join(log_lines[-30:])
            )
            st.success(f"Готово: {cfg.periods} раундов.")

            dfm = pd.DataFrame(
                {
                    "period": periods_x,
                    "gini_factory_capital": gini_f,
                    "gini_citizen_money": gini_c,
                    "sales": sales,
                    "mean_price": mean_p,
                    "mean_quality": mean_q,
                    "distinct_products_sold": distinct_p,
                    "total_factory_capital": [
                        s.metrics["total_factory_capital"] for s in snaps
                    ],
                    "total_citizen_money": [
                        s.metrics["total_citizen_money"] for s in snaps
                    ],
                }
            )

            df_cap_long = pd.DataFrame(rows_cap)
            top_ids: list[int] = []
            if not df_cap_long.empty and snaps:
                last_period_num = snaps[-1].period
                last_caps = df_cap_long[df_cap_long["period"] == last_period_num]
                top_ids = (
                    last_caps.nlargest(10, "capital")["factory_id"].astype(int).tolist()
                )

            st.subheader("Графики после расчёта")
            a1, a2 = st.columns(2)
            with a1:
                st.plotly_chart(
                    px.line(dfm, x="period", y="gini_factory_capital", title="Gini капитала фабрик"),
                    use_container_width=True,
                )
            with a2:
                st.plotly_chart(
                    px.line(dfm, x="period", y="gini_citizen_money", title="Gini денег жителей"),
                    use_container_width=True,
                )

            b1, b2 = st.columns(2)
            with b1:
                st.plotly_chart(
                    px.bar(dfm, x="period", y="sales", title="Число продаж"),
                    use_container_width=True,
                )
            with b2:
                st.plotly_chart(
                    px.line(
                        dfm,
                        x="period",
                        y=["total_factory_capital", "total_citizen_money"],
                        title="Σ капитал фабрик и Σ денег жителей",
                    ),
                    use_container_width=True,
                )

            st.markdown("##### Топ‑10 фабрик по капиталу на последнем периоде — динамика капитала")
            if top_ids and not df_cap_long.empty:
                d_top = df_cap_long[df_cap_long["factory_id"].isin(top_ids)].copy()
                d_top["factory_id"] = d_top["factory_id"].astype(str)
                fig_top = px.line(
                    d_top,
                    x="period",
                    y="capital",
                    color="factory_id",
                    title="Капитал",
                    labels={"capital": "Капитал", "period": "Период", "factory_id": "Фабрика"},
                )
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.caption("Недостаточно данных.")

            st.markdown("##### Средняя цена, среднее качество и число разных товаров с продажами")
            fig_mq = make_subplots(specs=[[{"secondary_y": True}]])
            fig_mq.add_trace(
                go.Scatter(x=dfm["period"], y=dfm["mean_price"], name="Средняя цена", mode="lines+markers"),
                secondary_y=False,
            )
            fig_mq.add_trace(
                go.Scatter(
                    x=dfm["period"],
                    y=dfm["mean_quality"],
                    name="Среднее качество",
                    mode="lines+markers",
                ),
                secondary_y=False,
            )
            fig_mq.add_trace(
                go.Bar(
                    x=dfm["period"],
                    y=dfm["distinct_products_sold"],
                    name="Разных товаров с продажами",
                    opacity=0.35,
                ),
                secondary_y=True,
            )
            fig_mq.update_layout(height=440, title_text="Цена, качество, разнообразие продаж")
            fig_mq.update_yaxes(title_text="Цена / качество", secondary_y=False, rangemode="tozero")
            fig_mq.update_yaxes(title_text="Количество", secondary_y=True, rangemode="tozero")
            st.plotly_chart(fig_mq, use_container_width=True)

            st.markdown("##### Цена × качество (фабричное предложение): начало и конец")
            sc1, sc2 = st.columns(2)
            with sc1:
                f0 = _scatter_price_quality(snaps[0], f"Период {snaps[0].period}")
                if f0:
                    st.plotly_chart(f0, use_container_width=True)
                else:
                    st.caption("Нет точек с ценой > 0.")
            with sc2:
                fl = _scatter_price_quality(snaps[-1], f"Период {snaps[-1].period}")
                if fl:
                    st.plotly_chart(fl, use_container_width=True)
                else:
                    st.caption("Нет точек с ценой > 0.")

            out_base = str(_ROOT / "data" / "streamlit_last")
            Path(_ROOT / "data").mkdir(exist_ok=True)
            pcit, pfact = snapshots_to_parquet(snaps, out_base)
            ccit, cfact = snapshots_to_csv(snaps, out_base)
            st.download_button("citizens.parquet", Path(pcit).read_bytes(), "citizens.parquet")
            st.download_button("factories.parquet", Path(pfact).read_bytes(), "factories.parquet")
            st.download_button(
                "citizens.csv",
                Path(ccit).read_bytes(),
                "citizens.csv",
                mime="text/csv",
            )
            st.download_button(
                "factories.csv",
                Path(cfact).read_bytes(),
                "factories.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    main()
