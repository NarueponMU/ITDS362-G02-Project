// Soak test: a steady, slightly-below-normal load (15 VUs) for a long time to see
// whether the system gets slower or starts failing as time goes on (memory leaks,
// growing sessions/carts, full disks, ...).
// Default: 2 min ramp-up, 30 min hold, 1 min ramp-down. Change with SOAK_MINUTES=60.
// Requests are tagged window=<from>-<to>min so the summary shows p(95) and error
// rate for every 5-minute window (answers README question c).
import { shopperJourney } from './lib/shopper.js';
import { elapsedSeconds, k6Stages, maybeSmoke, perLabelThresholds, SMOKE } from './lib/timeline.js';

const VUS = 15;
const HOLD_MIN = Number(__ENV.SOAK_MINUTES || 30);
const WINDOW_MIN = SMOKE ? 0.25 : 5;

const STAGES = maybeSmoke([
  { duration: '2m', target: VUS },
  { duration: `${HOLD_MIN}m`, target: VUS },
  { duration: '1m', target: 0 },
]);

const TOTAL_MIN = SMOKE ? 0.25 : HOLD_MIN + 3;
const WINDOWS = [];
for (let from = 0; from < TOTAL_MIN; from += WINDOW_MIN) {
  WINDOWS.push(`${String(from).padStart(2, '0')}-${String(from + WINDOW_MIN).padStart(2, '0')}min`);
}

function currentWindow() {
  const i = Math.min(Math.floor(elapsedSeconds() / 60 / WINDOW_MIN), WINDOWS.length - 1);
  return WINDOWS[i];
}

export const options = {
  stages: k6Stages(STAGES),
  thresholds: {
    // Same limits as the average-load test: a long run must not be worse than a short one.
    http_req_duration: ['p(95)<800', 'p(99)<1500'],
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
    ...perLabelThresholds('window', WINDOWS, 'p(95)<800', 'rate<0.01'),
  },
};

export default function () {
  shopperJourney(() => ({ test: 'soak', window: currentWindow() }));
}
