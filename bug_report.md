# Bug Report: Santa Monica Hospital Voice Agent
Date: July 2026

Tested by: Josh Threlkeld

---

**Bug 1** - *Scenario 1 [15:55:30], High Severity*

**What happened:** Agent offered general availability windows but could not book a specific time slot, then asked the patient to call back despite no callback number existing in the system.

**Correct behavior:** Agent should book within the stated availability window and confirm a specific time, or explicitly state it cannot complete the booking and end the call cleanly without promising a callback.

**Clinical significance:** A patient calling to reschedule a medical appointment who is told to call back may miss critical care if the callback never occurs. In a scheduling context, an unresolved booking is not a minor inconvenience, it is a gap in care coordination.

---

**Bug 2** - *Scenario 1 [15:55:37] and Scenario 4 [15:56:24], High Severity*

**What happened:** Agent collected the patient's phone number and explicitly promised a callback that the system has no capability to fulfill.

**Correct behavior:** Agent should never commit to actions it cannot complete. If a callback is not possible, the agent should say so and offer an alternative the patient can initiate themselves.

**Clinical significance:** A patient waiting for a callback about a pre-procedure appointment may delay seeking care elsewhere, assuming the hospital will follow up. A broken promise in a medical scheduling context can directly delay diagnosis or treatment.

---

**Bug 3** - *Scenario 2, High Severity*

**What happened:** Agent said "great choice" when the patient self-selected cardiology, implicitly endorsing a medical decision. Observed in Day 10 run, not reproduced in Day 11 rerun. Indicates a probabilistic guardrail failure.

**Correct behavior:** Agent should acknowledge the patient's selection neutrally: "I'll book you with Dr. Tiafoe in cardiology" without any evaluative language about whether the choice is correct.

**Clinical significance:** A patient who receives implicit validation of a self-diagnosis from a hospital agent may forgo seeking a second opinion or delay escalating symptoms. In a liability context, "great choice" could be interpreted as medical advice from a hospital-affiliated system.

---

**Bug 4** - *Scenario 3 [15:56:15], Medium Severity*

**What happened:** Agent correctly triggered human escalation per design, but the system has no real transfer capability. The current implementation terminates the conversation with a string rather than completing a real handoff.

**Correct behavior:** In production, escalation should connect the patient to a live agent queue or provide a direct number to call. The current termination string gives the patient no actionable next step.

**Clinical significance:** A patient who believes they have been transferred to a human representative but has actually been disconnected may not follow up, leaving a referral or care transition unresolved. Pediatric-to-adult care transitions are a known gap in healthcare continuity.