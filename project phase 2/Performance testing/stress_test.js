// Stress test: raise the load step by step past normal (20 VUs) up to 5x normal
// (100 VUs) to find where the system starts to slow down or fail.
// Each step: 1 min ramp + 1.5 min hold. 13.5 min total.
// Requests are tagged load=<N>vu during each hold so the summary shows p(95) and
// error rate at every load level (answers README questions a and b).
import { shopperJourney } from './lib/shopper.js';
import { k6Stages, labelAt, maybeSmoke, perLabelThresholds, segmentsFromStages } from './lib/timeline.js';

const LEVELS = [20, 40, 60, 80, 100];

const STAGES = maybeSmoke(
  LEVELS.flatMap((vus) => [
    { duration: '1m', target: vus, label: `ramp-${vus}vu` },
    { duration: '90s', target: vus, label: `${vus}vu` },
  ]).concat([{ duration: '1m', target: 0, label: 'ramp-down' }])
);
const SEGMENTS = segmentsFromStages(STAGES);

export const options = {
  stages: k6Stages(STAGES),
  thresholds: {
    // Overall: under stress we accept slower answers, but most must still succeed.
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.05'],
    // Per load level: the "healthy" limit is 1 s and 1% errors. The first level
    // that breaks these is where the system starts to struggle.
    ...perLabelThresholds('load', LEVELS.map((v) => `${v}vu`), 'p(95)<1000', 'rate<0.01'),
  },
};

export default function () {
  shopperJourney(() => ({ test: 'stress', load: labelAt(SEGMENTS) }));
}
