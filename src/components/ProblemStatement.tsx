const researchQuestions = [
  ["01", "Exposure", "How do bedtime screen time, repeated scrolling sessions, and negative-news consumption relate to sleep quality?"],
  ["02", "Consequences", "Which sleep outcomes—latency, duration, awakenings, debt, and daytime fatigue—shift most clearly with heavier exposure?"],
  ["03", "Protection", "Which routines and environmental choices appear to weaken the relationship between high exposure and poor sleep?"],
  ["04", "Prediction", "Can poor-sleep risk be estimated before the night’s sleep outcomes are known, and with what uncertainty and subgroup limitations?"],
];

const stakeholders = [
  ["Individuals", "Need understandable signals that support healthier bedtime choices without blame or diagnosis."],
  ["Researchers", "Need transparent definitions, reproducible analysis, uncertainty, and clear separation between association and causation."],
  ["Designers", "Need evidence about friction, content boundaries, and routine-support features—not merely more screen-time warnings."],
  ["Wellbeing teams", "Need defensible screening evidence and explicit safeguards before considering any real-world intervention."],
];

const auditChecks = [
  ["Missingness", "220 missing cells across six variables; handled explicitly before analysis."],
  ["Identity", "Respondent IDs and duplicate rows checked before modelling or grouping."],
  ["Ranges", "Age, minutes, sleep hours, scores, and category levels screened for invalid values."],
  ["Structure", "Ceiling effects, target balance, exact formulas, and unusually strong correlations flagged."],
];

export default function ProblemStatement() {
  return <section className="page-section problem-page">
    <header className="problem-hero">
      <img src="/assets/night-signals-hero.png" alt="A person using a phone in bed at night" />
      <div className="problem-hero-scrim" />
      <div className="problem-hero-copy">
        <span className="section-label">PROBLEM / CONTEXT / RESEARCH NEED</span>
        <h1>Rest has an<br /><em>attention problem.</em></h1>
        <p>Bedtime is meant to reduce stimulation. Infinite feeds, emotionally charged news, and habitual checking keep attention active precisely when the mind needs a transition into sleep.</p>
      </div>
      <div className="problem-signal" aria-label="Central tension">
        <span>THE CENTRAL TENSION</span>
        <b>Always-on information<br />meets a finite need for rest.</b>
      </div>
    </header>

    <div className="problem-thesis">
      <span>Formal problem statement</span>
      <p>We lack a clear, evidence-led account of how doomscrolling intensity, negative-news exposure, and bedtime routines combine around sleep—and which modifiable behaviours may reduce risk without treating screen use as destiny. This project organizes those relationships into a transparent descriptive and predictive framework while preserving the limits of self-reported, cross-sectional survey data.</p>
    </div>

    <section className="problem-context" aria-labelledby="why-title">
      <div><span className="section-label">WHY THIS MATTERS</span><h2 id="why-title">The cost appears across the whole night.</h2></div>
      <p>The concern is broader than “too much phone time.” Late-night exposure can coincide with delayed sleep onset, shorter realized sleep, repeated awakenings, accumulated sleep debt, and next-day fatigue. Negative content may add emotional arousal, while the feed’s lack of a natural stopping point makes disengagement harder.</p>
      <div className="problem-evidence-strip">
        <article><b>47.6%</b><span>classified as doomscrollers in this dataset</span></article>
        <article><b>+10.6 min</b><span>average sleep-latency gap</span></article>
        <article><b>+1.5 h</b><span>average weekly sleep-debt gap</span></article>
      </div>
    </section>

    <section className="problem-chain" aria-labelledby="chain-title">
      <div className="problem-section-heading"><span className="section-label">SYSTEM VIEW</span><h2 id="chain-title">A reinforcing bedtime-disruption chain</h2><p>The project studies a sequence, not a single bad habit.</p></div>
      <div className="problem-chain-grid">
        <article><span>01</span><b>Attention capture</b><p>Infinite feeds and repeated sessions remove natural stopping cues.</p></article><i aria-hidden="true">→</i>
        <article><span>02</span><b>Cognitive arousal</b><p>Negative or urgent content can sustain alertness and emotional activation.</p></article><i aria-hidden="true">→</i>
        <article><span>03</span><b>Sleep disruption</b><p>Later onset, awakenings, and reduced duration accumulate into sleep debt.</p></article><i aria-hidden="true">→</i>
        <article><span>04</span><b>Daytime trace</b><p>Fatigue and distress may then make passive scrolling more appealing again.</p></article>
      </div>
    </section>

    <section className="problem-audit" aria-labelledby="audit-title">
      <div className="problem-section-heading"><span className="section-label">DATASET RELIABILITY AUDIT</span><h2 id="audit-title">The data is useful, but unusually orderly.</h2><p>The Kaggle Sleep &amp; Doomscrolling Habits dataset is treated as a self-reported cross-sectional survey with only partially documented provenance. The audit is part of the story because model performance can reflect the survey's structure and unverified sampling as much as generalisable behaviour.</p></div>
      <div className="problem-audit-grid">
        {auditChecks.map(([label, copy]) => <article key={label}><b>{label}</b><p>{copy}</p></article>)}
      </div>
    </section>

    <section className="problem-dag-section" aria-labelledby="dag-title">
      <div className="problem-section-heading"><span className="section-label">CAUSAL BOUNDARY</span><h2 id="dag-title">Confounding is expected, not accidental.</h2><p>The analysis describes associations. Stress, routine, age, occupation, and baseline health can influence both scrolling and sleep, so the platform avoids causal claims.</p></div>
      <div className="problem-dag" aria-label="Simplified causal diagram">
        <div className="dag-node confounder">Stress / anxiety</div>
        <div className="dag-node exposure">Digital exposure</div>
        <div className="dag-node mediator">Sleep routine</div>
        <div className="dag-node outcome">Sleep outcome</div>
        <div className="dag-node context">Age / work / country</div>
      </div>
    </section>

    <section className="problem-questions" aria-labelledby="questions-title">
      <div className="problem-section-heading"><span className="section-label">WHAT THE STUDY ASKS</span><h2 id="questions-title">Four questions turn concern into analysis.</h2></div>
      <div className="problem-question-grid">
        {researchQuestions.map(([number, label, question]) => <article key={number}><span>{number}</span><div><b>{label}</b><p>{question}</p></div></article>)}
      </div>
    </section>

    <section className="problem-stakeholders" aria-labelledby="stakeholders-title">
      <div className="problem-section-heading"><span className="section-label">WHO NEEDS THE ANSWER</span><h2 id="stakeholders-title">One problem, different decisions.</h2></div>
      <div className="problem-stakeholder-grid">
        {stakeholders.map(([name, need]) => <article key={name}><b>{name}</b><p>{need}</p></article>)}
      </div>
    </section>

    <section className="problem-scope" aria-labelledby="scope-title">
      <div className="problem-section-heading"><span className="section-label">SCOPE &amp; BOUNDARIES</span><h2 id="scope-title">What this project is—and is not.</h2></div>
      <div className="problem-scope-grid">
        <article className="in-scope"><span>IN SCOPE</span><ul><li>Describe patterns across 1,000 survey respondents</li><li>Compare exposure, sleep, wellbeing, and protective routines</li><li>Test a pre-outcome screening model under leakage-safe validation</li><li>Surface uncertainty, exceptions, and subgroup weaknesses</li></ul></article>
        <article className="out-scope"><span>OUT OF SCOPE</span><ul><li>Prove that doomscrolling causes poor sleep</li><li>Diagnose a sleep or mental-health condition</li><li>Claim population prevalence or clinical utility</li><li>Deploy the model without independent real-world validation</li></ul></article>
      </div>
    </section>

    <aside className="problem-boundary"><span>ANALYTICAL BOUNDARY</span><p>The dataset is self-reported and cross-sectional. Findings describe this survey sample; they are hypotheses for real-world validation, not medical advice, causal estimates, or evidence that any individual will experience the same outcome.</p></aside>
  </section>;
}
