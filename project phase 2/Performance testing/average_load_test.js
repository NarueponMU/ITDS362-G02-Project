// Average-load test: the number of shoppers we expect on a normal day.
// 0 -> 20 VUs in 2 min, stay at 20 VUs for 6 min, back to 0 in 1 min (9 min total).
import { shopperJourney } from './lib/shopper.js';
import { k6Stages, maybeSmoke } from './lib/timeline.js';

const STAGES = maybeSmoke([
  { duration: '2m', target: 20, label: 'ramp-up' },
  { duration: '6m', target: 20, label: 'steady' },
  { duration: '1m', target: 0, label: 'ramp-down' },
]);

export const options = {
  stages: k6Stages(STAGES),
  thresholds: {
    // Normal traffic should feel fast: 95% under 0.8 s, 99% under 1.5 s.
    http_req_duration: ['p(95)<800', 'p(99)<1500'],
    // Almost nothing may fail under normal load.
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

export default function () {
  shopperJourney(() => ({ test: 'average' }));
}
