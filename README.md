# SML Prometheus Exporter

This Python script reads Smart Message Language (SML) messages from a serial device (e.g., `/dev/ttyUSB0`), extracts OBIS values, and exposes them as Prometheus metrics via an HTTP server.

## Features
- Parses SML messages from a serial device.
- Extracts OBIS values and converts them into Prometheus metrics.
- Exposes metrics via an HTTP server for Prometheus scraping.
- Configurable via a YAML file.

## Requirements
- Python 3.6+
- `prometheus_client`
- `pyyaml`
- `sml` (with asyncio support)

## Installation
Install dependencies using pip:
```sh
pip install -r requirements.txt
```

## Usage
### Configuration
The script requires a YAML configuration file (default: `config.yml`). The file should define:
- Logging level
- Serial device path
- HTTP server settings
- Metrics to extract

If you need a hint how your OBIS names look like, try running the program
with loglevel set to DEBUG. There will be a lot of output, look for something
like

```output
    OBIS: {'objName': '1-0:1.8.0*255', 'unit': 'Wh', 'value': 1234000}
````

Example `config.yml`:
```yaml
log_level: INFO
sml:
  device: "/dev/ttyUSB0"
server:
  address: "127.0.0.1"
  port: 9000
metrics:
  - name: sml_power_consumption
    description: Current power consumption in kWh
    unit: kWh
    obis_name: 1-0:1.8.0*255
    factor: 0.001
```

This will create a gauge named `sml_power_consumption_kWh` with the value
reported from the meter scaled with by a factor of 0.001, turning Wh
into kWh.

### Running the Script
Run the script with a configuration file:
```sh
python3 sml_exporter.py config.yml
```
If no configuration file is provided, it defaults to `config.yml`.

### Exposing Metrics
Once running, metrics will be available at `http://<address>:<port>/metrics`. Example:
```
http://127.0.0.1:9000/metrics
```

## Logging
Logging levels can be set via the `log_level` field in `config.yml` (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`).

## License
This project is licensed under the MIT License.

## Author
Torsten Dreyer

