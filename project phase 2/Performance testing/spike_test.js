// Spike test: a sudden jump from 5 to 100 VUs in 10 s (for example a flash sale
// link shared on social media), hold 1 min, drop back to 5 VUs and watch recovery.
// 5 min 30 s total.
// Requests are tagged phase=... so the summary shows p(95) and error rate before,
// during and in 30-second windows after the spike (answers README question d).
import { shopperJourney } from './lib/shopper.js';
import { k6Stages, labelAt, maybeSmoke, perLabelThresholds, segmentsFromStages } from './lib/timeline.js';

const BASE_VUS = 5;
const SPIKE_VUS = 100;

const STAGES = maybeSmoke([
  { duration: '1m', target: BASE_VUS, label: 'before' },
  { duration: '10s', target: SPIKE_VUS, label: 'spike-up' },
  { duration: '1m', target: SPIKE_VUS, label: 'spike' },
  { duration: '10s', target: BASE_VUS, label: 'spike-down' },
  { duration: '30s', target: BASE_VUS, label: 'after-000-030s' },
  { duration: '30s', target: BASE_VUS, label: 'after-030-060s' },
  { duration: '30s', target: BASE_VUS, label: 'after-060-090s' },
  { duration: '30s', target: BASE_VUS, label: 'after-090-120s' },
  { duration: '30s', target: BASE_VUS, label: 'after-120-150s' },
  { duration: '30s', target: BASE_VUS, label: 'after-150-180s' },
  { duration: '10s', target: 0, label: 'ramp-down' },
]);
const SEGMENTS = segmentsFromStages(STAGES);
const PHASES = STAGES.map((s) => s.label).filter((l) => l !== 'ramp-down');

export const options = {
  stages: k6Stages(STAGES),
  thresholds: {
    // During a spike we accept slower answers and a few errors overall...
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.10'],
    // ...but each phase is compared with the normal limit (1 s, 1% errors).
    // "Recovered" = the first after-* window that is back under these limits.
    ...perLabelThresholds('phase', PHASES, 'p(95)<1000', 'rate<0.01'),
  },
};

export default function () {
  shopperJourney(() => ({ test: 'spike', phase: labelAt(SEGMENTS) }));
}
