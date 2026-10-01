# PAIMANA-AI: Prototype Video Demonstration Guide & Script
## Smart India Hackathon (SIH) Portal Submission (Problem ID: 26103)

> **Recommended Video Duration**: 2 Minutes 45 Seconds to 3 Minutes  
> **Target Audience**: SIH Technical Judges & Ministry Evaluators (MoSPI)  
> **Tone**: Confident, professional, clear, and focused on working features

---

## 🛠️ Recording Setup Checklist (Do This Before Recording)

1. **Start the Platform Backend & Frontend**:
   Open a terminal in `C:\Users\Saba\.gemini\antigravity\scratch\paimana-ai` and run:
   ```cmd
   python -m uvicorn paimana_ai.server.main:app --port 8000
   ```
2. **Open Your Browser**:
   - Go to: `http://127.0.0.1:8000`
   - Press `F11` (or maximize the browser window) for a clean full-screen view.
   - Zoom level: `100%` or `90%` so all KPI cards and charts are clearly visible.
3. **Screen Recorder**:
   - Built-in Windows shortcut: **Win + Alt + R** (starts/stops recording with microphone).
   - Or free tools like **OBS Studio** or **Loom**.

---

# 🎬 Timestamp-by-Timestamp Video Demonstration Script

---

### ⏱️ [0:00 - 0:25] Scene 1: Introduction & Macro Portfolio Overview

* **Screen Action**:
  - Show the top header: *"Ministry of Statistics and Programme Implementation (MoSPI) — PAIMANA-AI"*.
  - Smoothly hover your mouse over the 6 Macro KPI boxes (1,981 Projects, ₹37.13 L Cr Original Cost, ₹42.78 L Cr Revised Outlay, ₹20.36 L Cr Capex, 814 Delayed Projects, and 328 Critical RED Projects).
  - Hover over the **RAG Risk Donut Chart** and the **Sectoral Capital Allocation Bar Chart**.

* **🎙️ Voiceover (Speak clearly)**:
  > *"Hello everyone! This is our demonstration of **PAIMANA-AI** for SIH Problem Statement 26103 from the Ministry of Statistics and Programme Implementation. As of April 2026, MoSPI tracks 1,981 mega-projects worth over ₹42 lakh crore. Over ₹5.6 lakh crore in cost escalations have already occurred. Our platform moves infrastructure monitoring from backward-looking descriptive reports to an autonomous predictive and early warning decision-support system. Here on the executive dashboard, administrators can see the entire national portfolio, the real-time RAG risk distribution, and sector-by-sector capital exposure."*

---

### ⏱️ [0:25 - 0:55] Scene 2: Project Explorer & Explainable AI Deep-Dive

* **Screen Action**:
  - Click on the **"Project Explorer"** tab.
  - In the search bar, type `Railway` or select `Ministry of Railways` from the dropdown. The table filters instantly.
  - Click on a **RED** project row (e.g. `PM-RAI-0012` or click **"Drilldown"**).
  - The **Project Deep-Dive Modal** opens.
  - Scroll down to show:
    1. Financial vs Physical Progress bars.
    2. The **Composite Risk Index (CRI)** sub-indices breakdown.
    3. The **Explainable AI Drivers (SHAP-style root causes)** showing exact percentage impacts.
    4. The **Peer Project Cohort**.

* **🎙️ Voiceover**:
  > *"Let's explore an individual project. In the Project Explorer, we can filter across 17 ministries and 22 sectors. Clicking on this critical railway project opens its full diagnostic dossier. Notice that our system doesn't just display progress; it computes a multi-dimensional Composite Risk Index. More importantly, our explainable AI module breaks down the exact root causes—showing that financial burn disparity adds +8.5% cost pressure, while unresolved Stage-II forest clearances add another +5.4% delay risk. It even identifies similar peer projects to project expected delivery trajectories."*

---

### ⏱️ [0:55 - 1:25] Scene 3: Early Warning Alert Desk (EWS)

* **Screen Action**:
  - Close the modal.
  - Click on the **"Early Warning Desk"** tab.
  - Scroll through the alert cards with red and amber borders.
  - Point to the badge for `EWS-01-GHOST-PROGRESS` and `EWS-02-MILESTONE-CASCADE`.
  - Highlight the text: *"Prescriptive Action: Mandate third-party technical audit..."*.

* **🎙️ Voiceover**:
  > *"Next is our Early Warning Alert Desk. Instead of waiting for monthly flash reports, our rule engine autonomously detects operational anomalies months before budgets fail. For example, Alert 1 catches 'Ghost Progress'—where financial disbursement is running 1.8 times faster than audited physical construction on site, warning of contractor advance risks. Alert 2 catches statutory clearance cascades up to 12 months ahead, providing an exact prescriptive administrative action—such as triggering Cabinet Project Monitoring Group escalation."*

---

### ⏱️ [1:25 - 1:55] Scene 4: What-If Scenario Simulator

* **Screen Action**:
  - Click on the **"Scenario Simulator"** tab.
  - Select a project from the dropdown.
  - Drag the **"Statutory Clearance Delay"** slider from `0` to `+8 Months`.
  - Drag the **"Steel / Cement Inflation Shock"** slider to `+15%`.
  - Watch the right-hand panel instantly update:
    - *Simulated Project Cost* jumps in orange.
    - *Anticipated DOC* shifts forward.
    - *Policy Takeaway* recalculates the exact added Capex in ₹ Crore.

* **🎙️ Voiceover**:
  > *"Now, look at our What-If Scenario Simulator. Senior policymakers can test policy interventions or macro shocks in real time. If we simulate an 8-month delay in statutory clearances and a 15% surge in steel prices, the model instantly recalculates the revised completion date, updates the risk score, and shows the exact additional Capex impact in crores. This empowers the Ministry of Finance and MoSPI to stress-test projects before approving revised cost estimates."*

---

### ⏱️ [1:55 - 2:25] Scene 5: Scientific Evaluation (Dimensions b & c)

* **Screen Action**:
  - Click on the **"AI vs Statistical Arena"** tab.
  - Show the comparative table comparing OLS, Ridge, and HistGradientBoosting ($R^2$, RMSE, ROC-AUC).
  - Click on the **"CUF Reform Lab"** tab.
  - Show the three metric cards (`Regime A`, `Regime B`, and `Predictive Uplift: +16.8%`).
  - Scroll down to the table of **Policy Recommendations for MoSPI DIID**.

* **🎙️ Voiceover**:
  > *"Our platform directly answers the hackathon's core research dimensions. In the AI vs Statistical Arena, our empirical tests prove that Modern AI/ML delivers a 22.4% improvement in R² and an ROC-AUC of 0.91 over classical linear models, because it captures non-linear compounding delays. In the CUF Reform Lab, our ablation study proves that adding four non-CUF indicators—like contractor track record and commodity price exposure—unlocks an additional 16.8% in explainable variance, giving MoSPI evidence-based recommendations on how to upgrade the Common Upload Form."*

---

### ⏱️ [2:25 - 2:50] Scene 6: LLM Project Intelligence Copilot

* **Screen Action**:
  - Click on the orange **"AI Project Copilot"** button in the top right.
  - The side drawer slides in.
  - Click on the quick prompt: **"🚆 Railway Delays"** or type: *"Analyze Railway bottlenecks"*.
  - The AI assistant outputs an instant portfolio analysis with figures.
  - Re-open a project modal and click **"Generate Cabinet Brief"**.
  - The Copilot immediately formats a structured executive brief with financial health, bottlenecks, and prescriptive remedies.

* **🎙️ Voiceover**:
  > *"Finally, we integrated an LLM Project Intelligence Copilot. Administrators can ask conversational questions across all 1,981 projects. With one click, the assistant synthesizes complex project data into a crisp executive briefing formatted specifically for the Cabinet Secretary or Minister, complete with prescriptive remediation pathways. It works 100% offline with zero latency."*

---

### ⏱️ [2:50 - 3:00] Scene 7: Conclusion & Wrap-Up

* **Screen Action**:
  - Switch back to the Executive Overview tab.
  - Show the whole dashboard.

* **🎙️ Voiceover**:
  > *"PAIMANA-AI is 100% open source, lightweight, and fully tested with automated test suites. By preventing even 1% of cost overruns across this ₹42 lakh crore portfolio, this platform can save over ₹42,000 crore for India's exchequer. Thank you!"*

---

## 💡 Top Tips for Winning Maximum Hackathon Points

1. **Speak with Confidence**: Keep your voice energetic and steady. Don't rush; pause slightly after highlighting key numbers like *₹42 lakh crore* or *+22.4% $R^2$*.
2. **Show the Working Product**: Judges love seeing live interactions—dragging the simulator sliders and clicking the Copilot creates maximum visual impact.
3. **Keep the Recording under 3 Minutes**: Most hackathon evaluators review hundreds of submissions; a crisp 2:45 to 2:55 video stands out immediately.
