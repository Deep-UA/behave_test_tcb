#!/bin/bash
# Generate the Allure report and keep run history so the Trend widget works.
# Usage: ./scripts/report.sh   (from the project root, after a behave run)
set -e

allure generate allure-results -o allure-report --clean
# Feed this report's history into the next generation — this is what builds the trend
mkdir -p allure-results/history
cp -f allure-report/history/*.json allure-results/history/ 2>/dev/null || true
allure open allure-report
