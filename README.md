# homeassistant-healthchecks

This custom component for Home Assistant allows you to integrate your [Healthchecks.io](https://healthchecks.io) checks as sensors, indicating their status (up or down) within your Home Assistant setup.

## Installation

Use [HACS](https://hacs.xyz) or manually installed the files into your `config/custom_components/` directory.

```sh
$ ssh homeassistant
$ cd /config/custom_components/
$ curl -L https://github.com/josh/homeassistant-healthchecks/archive/refs/heads/main.tar.gz |
    tar -xz --strip-components=2 homeassistant-healthchecks-main/custom_components/healthchecks
```
