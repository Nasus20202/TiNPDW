# Techniki i narzędzia przetwarzania danych wielkoskalowych

Results: [RESULTS.md](RESULTS.md)

## Run

```bash
chmod +x download_data.sh
./download_data.sh
uv sync
uv run python main.py
```

## Rerun Benchmark

```bash
rm -f results.json RESULTS.md
rm -rf outputs
uv run python main.py
```

## Build Report

After benchmark results are available in `results.json`:

```bash
uv run python plot_times.py
typst compile report.typ report.pdf
```

This generates:

- `outputs/execution_times.png` - execution times chart
- `report.pdf` - final PDF report
