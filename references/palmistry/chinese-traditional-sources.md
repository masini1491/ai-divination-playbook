# Source Dossier｜中國傳統手相古籍來源

Status: **REFERENCE-ONLY｜僅供參考**

本 dossier 建立中國傳統手相 interpretation 的 provenance baseline。它只保存來源、流派邊界、可用範圍與授權／轉錄注意事項；不把古籍內容直接升格成 `PALMISTRY.md` production rule。

## 1. Primary provenance surface｜《古今圖書集成》藝術典第 640 卷

Source surface: 中文維基文庫

URL: https://zh.wikisource.org/zh-hant/欽定古今圖書集成/博物彙編/藝術典/第640卷

Relevant section:

```text
相術部彙考十
→ 神相全編十
→ 論手
→ 玉掌圖 / named palm patterns
→ 相手 / 許負相手篇
→ 論掌紋
→ 論手背紋
→ 玉掌記
→ 相掌善惡 / 合相格 / 破相格
```

此卷特別有價值，因為它不是現代 AI prompt 或二手網站整理，而是古籍 compilation 中明確收錄的「手／掌／掌紋」專門內容；可作為中國傳統手相 vocabulary 與 rule-family 的主要 provenance anchor。

### Authority boundary

- 它證明「中國相術傳統中存在何種掌形、掌紋、宮位與 interpretation vocabulary」。
- 不證明這些 interpretation 具有現代科學、統計或醫學效度。
- 《神相全編》在此是被《古今圖書集成》收錄的文本傳統；不要因收錄關係就把所有後世版本、現代圖解本或網路整理視為逐字等同。
- named pattern（例如玉柱紋、智慧紋、三才紋等）需要依原 source definition 建模；只看名稱不得自行對應現代 Western palmistry term。

## 2. Secondary traditional source｜《神相鐵關刀》

Source surface: 中文維基文庫

URL: https://zh.wikisource.org/zh-hant/神相鐵關刀

Relevant sections include multiple `相掌秘訣` passages。其內容涵蓋：

- 掌形與身形／面形的配合；
- 掌厚薄、大小、筋節、色澤；
- 掌中八卦／宮位；
- 掌紋深淺、直橫、位置與破損；
- 以巽、離、坤等掌宮作傳統 interpretation。

### Provenance caution

此類傳統相書常帶有後世傳承、題署或託名問題。此 dossier 只把它當成「現存文本 tradition」的 evidence，不以傳說作者、秘傳 lineage 或序言自述建立歷史作者 authority。

## 3. Secondary traditional source｜《太清神鑑》（四庫全書本）卷五

Source surface: 中文維基文庫；另有 GitHub searchable mirror 可交叉定位。

Relevant content includes：

- 論四肢；
- 論手；
- 相掌紋；
- 掌上三紋／紋深淺粗細／橫縱紋；
- 手背紋與部分 named patterns。

此來源可用來交叉比較《神相全編》與其他中國相術文本是否共用相似 vocabulary / rule family，但不可因重複出現就自動推定「多來源獨立驗證」；古籍之間可能有承襲、輯錄或同源關係。

## 4. GitHub retrieval mirror｜look-fate/lookfate-book

Repository: `look-fate/lookfate-book`

Reviewed revision: `5cd1a3c3bd0337ec24f2963684fb96e67cb32301`

Root license: MIT

Relevant tree under `content/相/` includes at least：

- `太清神鉴/`
- `神相全编/`
- `神相铁关刀.md`
- `柳庄神相/`
- `公笃相法/`

The reviewed revision also contains searchable palm passages，例如《太清神鑑》卷五的 `掌上三纹`，以及《神相鐵關刀》的掌紋／八卦內容。

### Mirror authority boundary

本 Repo 很適合 AI / GitHub connector 做 bounded search，但目前 README 主要是資料庫貢獻說明，未建立每部古籍逐卷的 edition / scan / transcription provenance。

因此：

```text
GitHub mirror = retrieval convenience / cross-check
Wikisource / public-domain edition lineage = primary provenance
```

Root MIT license 可確認 repository 自己宣告的 license，但**不得機械推定每一份第三方古籍轉錄的 upstream provenance、edition fidelity 與再授權鏈都因此獨立獲得證明**。目前只做摘要／交叉查找，不搬整部轉錄進本 Playbook。

## 5. Screened GitHub mirror｜youngzs/xuanxue

Repository: `youngzs/xuanxue`

Reviewed revision: `aa7bc942602d2d88ef94778a726c0d19a4d286ff`

此 repo 的 `docs/麻衣神相/` 提供可讀的《麻衣神相》整理，GitHub code search 也能命中相關文本。

但在本輪 reviewed root tree 中未看到清楚的 `LICENSE`，README 也沒有提供《麻衣神相》版本／底本／轉錄 provenance。因此目前只視為 discovery / comparison surface，不作 reuse source，也不拿它作 canonical interpretation authority。

## 6. License / reuse boundary

中文維基文庫的 copyright policy 說明其 contribution layer 以 CC BY-SA 4.0 / GFDL 發布，並接受 public-domain works；其簡明政策也將作者已去世逾一百年且 1930 年前發表的作品列為可安心加入的類型之一。

對本 Playbook：

- 優先保存 source citation、section identity 與自己的摘要；
- 不需要把整段維基文庫 transcription 複製進 repo；
- 若未來需要 verbatim Wikisource transcription，另依 CC BY-SA attribution / share-alike 條件處理；
- 古籍原作 public-domain status 與現代 transcription / edition / annotation 的權利層要分開；
- 現代出版社的重新標點、評注、圖解與排版本不得因原古籍 public domain 就自動視為 public domain。

## 7. Interpretation normalization guard

中國傳統手相不能直接用現代 Western labels 一對一替換。

目前至少要保留以下 distinction：

```text
source-specific 天 / 人 / 地紋
source-specific 八卦 / 掌宮
source-specific named patterns
modern heart / head / life / fate-line terminology
```

未經 source mapping，不得假設：

- `天紋 == heart line`
- `人紋 == head line`
- `地紋 == life line`
- `玉柱紋 == modern fate line`

即使位置看起來相近，也要先確認 source 定義、位置、形狀與 interpretation responsibility。

## 8. Adoption decision

目前中國傳統 source gap 已從「沒有可追溯來源」縮小成「已有 provenance anchors，但尚未正規化 rule set」。

Adoption state 仍為：

**REFERENCE-ONLY｜僅供參考**

下一階段若繼續，應做 **source-specific rule normalization matrix**，而不是直接把古籍句子貼進 `PALMISTRY.md`。
