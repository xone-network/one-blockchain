#!/usr/bin/env bash
# Post install script for the UI .rpm to place symlinks in places to allow the CLI to work similarly in both versions

set -e

ln -s /opt/one/resources/app.asar.unpacked/daemon/one /usr/bin/one || true
ln -s /opt/one/one-blockchain /usr/bin/one-blockchain || true
