# Common AI Development Playbook Adoption Record

Upstream：`masini1491/ai-development-playbook`

Declared baseline：`main`

Project AI mode：`ChatGPT-Only`

Last reviewed source revision：`178a8d7d7d1d289c16434af80f21bdc5ab71496b`

Relationship：**common AI engineering baseline + conditional activation**。這不是 divination method authority，也不是要求 ordinary reading 每次載入 shared Playbook。

## Adoption contract

本 Repo 把跨專案共通的 AI／repository engineering governance 上移到 `masini1491/ai-development-playbook`，本地只保留：

- project-native bootstrap / activation routing；
- project-specific governance / stricter overrides；
- divination technical truth、runtime、method、Reading lifecycle / record；
- shared rule 在本 Repo 的必要 mapping。

Declared baseline 是 floating `main`。只有 Shared Development Playbook Activation Gate 判定本次工作需要共通 engineering governance 時，才用本 Repo admitted GitHub route把 `main` resolve成 exact immutable revision，再進該 revision 的 `CHAT_INIT.md`；普通 reading 不 probe、不載入。

Shared `REPORTING.md` 是窄化的 adoption-level exception：substantive user-facing engineering／repository-maintenance reply 依 declared baseline 的 reporting contract呈現，即使其他 shared governance 未 activation也適用；為 reporting 只 direct-leaf 到 `REPORTING.md`，不因此載入 `CHAT_INIT.md` 或其他 shared owners。這個 mapping只影響工程狀態／review／validation／completion 等 reporting，不取代本 Repo `CHATGPT_OUTPUT.md` 對占卜題目交付、解讀、完成／回測與方法輸出的 authority。

## Project-specific authority / overrides

下列規則留在本 Repo，且在各自 scope 內高於 shared generic default：

1. **GitHub Connect-only repository authority**：本 Repo 對 GitHub-hosted repository identity／content／diff／workflow／reference acquisition 只接受 GitHub connector / GitHub Connect。Shared Playbook 的 generic public-read recovery ladder不會放寬這個 local restriction。
2. **Public-repository privacy boundary**：真實 Reading Record、可識別 birth / relationship / health / sexual / private-company context 不得寫入本公開 Repo。
3. **Private-context inference-egress boundary**：ordinary reading 不啟動 shared Playbook，因此私人 reading Context 的 disclosure permission 必須由 project-native governance 持續有效；model／provider／router 或 destination materially 改變時不得自動沿用既有 permission。
4. **Divination method authority**：Tarot／Meihua／Liuyao／Astrology、stochastic runtime、deterministic engines、Question / Input Contract、Reading lifecycle與 cross-validation 仍由本 Repo canonical owners負責。
5. **Project-native hot path**：ordinary reading／continuation／method interpretation 不啟動 shared Playbook；repository maintenance／AI engineering governance 才 activate。

## Shared engineering rules｜不在本 Repo 複製第二份

當 shared baseline 被 activate 時，下列跨專案 engineering semantics 直接由 upstream current resolved revision 擁有，本 Repo不再為了同步而另存完整副本：

- capability / permission / authority layering；
- Action Contract Closure 與 completion-evidence closure；
- GitHub operation response-shape、mutation/read-back、workflow-trigger evidence、terminal residue cleanup；
- repository-level absence-claim coverage；
- AI Context / hot-cold / retrieval-cost governance；
- shared actor / host-adapter engineering semantics；
- substantive engineering reporting presentation / timestamp / pre-send contract → upstream `REPORTING.md`；
- generic inference-egress mechanics仍由 upstream說明，但本 Repo的 private-context disclosure boundary由 local governance直接擁有。

若本 Repo需要更嚴限制或 project-specific mapping，才在 local governance明確寫 override；未寫 override的共通 engineering rule在 shared activation scope內依 declared baseline處理。

## Divination-specific adaptations retained locally

部分概念已轉化成占卜 domain contract，這些 local semantics 不因共通規則上移而消失：

- **One Question = One Copy Surface**；
- Draw / Cast Fact、Structured Method Fact、Symbolic Inference 等 evidence roles；
- Reality Update 不回寫 Original Interpretation；
- prediction `completion_rule` / backtest completion evidence；
- lowest-sufficient user-facing interpretation。

它們現在已由本 Repo method／lifecycle／output owners直接擁有，不需要每次回讀 upstream來源。

## Not automatically applicable

目前 `ChatGPT-Only` mode 下，不因 shared baseline存在就自動啟用：

- Codex root / child delegation、child profile override、usage-budget routing；
- TASKS / BACKLOG / coordination surfaces（除非本 Repo未來另行 opt-in）；
- Codex-specific resource-exhaustion fallback；
- 任何會覆蓋本 Repo GitHub Connect-only、privacy、method/runtime 或 Reading Record boundary 的 generic default。

## Review / update rule

Upstream `main` 前進不等於 ordinary reading立即增加 Context。只有 shared activation 成立時才 resolve current baseline；本檔的 Last reviewed revision 只是最近一次 governance review evidence，不把 floating `main`偷偷改成 pinned SHA，也不讓 shared engineering rule直接覆蓋 project-specific authority。
