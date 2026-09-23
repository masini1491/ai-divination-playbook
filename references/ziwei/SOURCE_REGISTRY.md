# Zi Wei Dou Shu Source Registry

Authority：`REFERENCE-ONLY / RESEARCH EVIDENCE`

本表記錄目前 bounded research 已實際使用的來源、revision、角色與限制。External evidence ≠ project adoption。

## Tier A — calculation / profile references

| Source | Exact revision | License | Research role | Boundary |
| --- | --- | --- | --- | --- |
| `matharts/ziwei` | `596f43c43ff6fbae526314c7f668bbf346445ff1` | MIT | normalized-core architecture、命身宮、五行局、紫微／十四主星、四化、大限；另含 primary-scan research notes | development-state project；project-confirmed rules 不自動等於古籍唯一真值 |
| `SylarLong/iztro` | `2c7ef9be669df7b19d1799f4dce335fed3794f78` | MIT | mature configurable implementation；default / Zhongzhou placement、閏月、子時、year/horoscope boundary | `algorithm=zhongzhou` 不等於四化也自動切 Zhongzhou |
| `airicyu/fortel-ziweidoushu` | `2620cc895395f9f6994abd4927e739d31015c67d` | MIT | Zhongzhou comparator；天／地／人盤、五行局、四化 variant | named-school implementation evidence，不是獨立 primary text |
| `RedSC1/js-ephemeris-lite/packages/ziwei` (`ziwei-lite`) | `559d4957bc063a6e03a3c810066be4eccf3ea2be` | MPL-2.0 | composable calendar/profile/boundary architecture、rule variants、validation design | license 與 lineage 必須分開處理；不直接 vendor |
| `BingerYuan/zwds` | `5e1fdee1122f64116d2401e2a4654bb395708858` | unresolved in bounded pass | Go comparator；命身、十四主星、四化、大限；紫微 150-table comparator | license 未確認 → REFERENCE-ONLY；五行局依 external NaYin dependency，未做完整 dependency closure |

## Tier B — lineage-derived / auxiliary implementation evidence

| Source | Exact revision | Role | Boundary |
| --- | --- | --- | --- |
| `RedSC1/ziwei_core` | `f7700c91ba683df2b0da9386d842171a6aec835f` | ziwei-lite family 的 Dart rewrite / parity、large fixture architecture | 同 lineage；JS↔Dart parity 是 implementation consistency，不是 doctrinal independence |

## Tier P — primary / historical candidates

| Source | Identity | Role | Boundary |
| --- | --- | --- | --- |
| National Archives of Japan / Nanyang-Hall witness | `新鋟希夷陳先生紫微斗数全書１`，collection entry `4468520` | 命／身宮、納音定局、紫微生日配置、十四主星、左右昌曲、大限方向與四化 witness research | 已鎖定具體 witness；不同規則的 evidence level 分開記錄，四化／大限不得因館藏 identity 已確立就自動宣稱 image-verified |
| Toyo Bunko Quanji witness | `新刊希夷陳先生紫微斗數全集`，call mark `VII-3-157`，1冊100張 | 《全集》系四化／大限起歲 witness identity |館藏 identity 已 cross-catalog verified；四化與大限規則頁仍 `IMAGE GAP OPEN`，目前只到 witness-identified transcription support |
| Wenguang-Hall early Quanshu collation | 明末清初文光堂木刻本（敦化堂／繼述堂系，依現代影印校勘說明） | 庚干四化異文 witness family | 目前只有 publisher/editorial collation claim；原頁 facsimile 尚未取得，保持 `IMAGE GAP OPEN` |
| `kanripo/KR5h0055` | revision `86d036859da6d0352b0fc1d6edf46eb5745759d2` | historical text candidate：`紫微鬥數` / DZ1485 | 與現代十四主星／四化體系的 lineage 尚未解決，不得因同名就直接當 modern-rule proof |

## Current adoption map

```text
matharts/ziwei                    REFERENCE-ONLY / selected architecture evidence
SylarLong/iztro                   REFERENCE-ONLY / profile & implementation evidence
airicyu/fortel-ziweidoushu        REFERENCE-ONLY / Zhongzhou comparator
ziwei-lite                        REFERENCE-ONLY / profile & validation architecture
BingerYuan/zwds                   REFERENCE-ONLY / comparator; license unresolved
ziwei_core                        REFERENCE-ONLY / derived-lineage parity evidence
historical / primary candidates   REFERENCE-ONLY / rule-specific source evidence
Source Reconciliation v1          CLOSED WITH EXPLICIT IMAGE GAPS
```

任何 upstream rule 只有在本 research owner 明確採用後，才成為本研究線的 candidate contract；仍不因此取得 production authority。
