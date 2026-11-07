// Helpers that label every request with the part of the test it was sent in
// (load level, time window, before/after a spike). k6 prints a separate line in
// the summary for each label that has a threshold, which is how we read
// "response time at 40 VUs" or "response time 60-90 s after the spike".
import exec from 'k6/execution';

export const SMOKE = __ENV.SMOKE === '1';

export function seconds(duration) {
  const m = /^(\d+)(s|m|h)$/.exec(duration);
  if (!m) throw new Error(`Unsupported duration: ${duration}`);
  return Number(m[1]) * { s: 1, m: 60, h: 3600 }[m[2]];
}

// SMOKE=1 shrinks a test to a few seconds per stage and at most 2 VUs, only to
// prove the script works. Real results must come from a normal run.
export function maybeSmoke(stages) {
  if (!SMOKE) return stages;
  return stages.map((s) => ({ duration: '5s', target: Math.min(s.target, 2), label: s.label }));
}

// stages: [{ duration, target, label }] -> [{ end (s), label }]
export function segmentsFromStages(stages) {
  let t = 0;
  return stages.map((s) => {
    t += seconds(s.duration);
    return { end: t, label: s.label };
  });
}

export function elapsedSeconds() {
  return (Date.now() - exec.scenario.startTime) / 1000;
}

export function labelAt(segments) {
  const t = elapsedSeconds();
  const seg = segments.find((s) => t < s.end);
  return seg ? seg.label : segments[segments.length - 1].label;
}

// k6 stages do not accept extra keys, so strip `label` before handing them to k6.
export function k6Stages(stages) {
  return stages.map(({ duration, target }) => ({ duration, target }));
}

// One threshold per label so each label gets its own line in the summary.
export function perLabelThresholds(tagName, labels, durationRule, failedRule) {
  const out = {};
  for (const label of labels) {
    out[`http_req_duration{${tagName}:${label}}`] = [durationRule];
    out[`http_req_failed{${tagName}:${label}}`] = [failedRule];
  }
  return out;
}
