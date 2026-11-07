#!/usr/bin/env bash
# Run one k6 test and keep its summary with the date and time of the run.
#   ./run.sh average_load_test        -> full run
#   SMOKE=1 ./run.sh spike_test       -> a few seconds, 2 VUs, only to check the script
# Output: results/<test>-<YYYYMMDD-HHMM>[-smoke].txt  (k6 end-of-test summary)
#         results/<test>-<YYYYMMDD-HHMM>[-smoke].json (same summary as JSON)
set -euo pipefail
cd "$(dirname "$0")"

TEST="${1:?usage: ./run.sh <average_load_test|stress_test|soak_test|spike_test>}"
TEST="${TEST%.js}"
STAMP="$(date +%Y%m%d-%H%M)"
SUFFIX=""
[ "${SMOKE:-0}" = "1" ] && SUFFIX="-smoke"
OUT="results/${TEST}-${STAMP}${SUFFIX}"
mkdir -p results

{
  echo "Test:    ${TEST}${SUFFIX}"
  echo "Start:   $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "Machine: $(uname -sm), $(k6 version | head -1)"
  echo
} > "${OUT}.txt"

set +e
k6 run --summary-export "${OUT}.json" "${TEST}.js" 2>&1 | tee -a "${OUT}.txt"
STATUS=${PIPESTATUS[0]}
set -e

echo "End:     $(date '+%Y-%m-%d %H:%M:%S %Z')  (k6 exit code ${STATUS}; 99 = a threshold was crossed)" | tee -a "${OUT}.txt"
