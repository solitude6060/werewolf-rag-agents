# Notes: Multi-Agent Werewolf Prediction

## 作業理解

### 任務概述
- 狼人殺遊戲記錄分析
- 多代理Langchain系統
- 預測玩家角色和狼人分數

### 關鍵字
- Multi-agent reasoning
- Deception detection in dialogue
- Social deduction game

## 數據結構
(See Dataset_README.md when available)

### 預期格式
- Dataset_README.md: 遊戲規則說明
- Werewolf_Corpus/: 50場遊戲記錄
  - 20場public, 30場private
- roles.csv: 角色數據
- roles_with_gt.csv: 帶ground truth的角色數據

## 系統架構 (根據PDF)

### Stage 1: Fetching Relevant Data
- 分析整體文本
- 確定證據和事件
- 識別每場遊戲人數和每日事件

### Stage 2: Analyzing Events
- 根據遊戲規則推斷
- 角色行為動機分析
- 候選角色排名

### Stage 3: Constrained Solver
- 汇总各角色排名
- 證據關聯
- 貪心分配確定最終分數

## 評估指標
- Macro-F1
- AP (Average Precision)

## 限制
- 不可訓練/fine-tune
- 不可用外部API
- 模型 ≤12GB VRAM
- 建議: Qwen2.5-7B-Instruct-GGUF, GLM-4-32B-0414, Gemma 4 E2B

---

## 研究發現 (from Librarian)

### GitHub 資源
1. **wolfcha** (oil-oil/wolfcha) - 多LLM狼人殺平台，Apache 2.0
   - 雙層角色扮演系統
   - 支持 DeepSeek, Qwen, Gemini 等多模型

2. **werewolf_ai_agents** (WuJunde/werewolf_ai_agents)
   - 基於MetaGPT的LLM代理
   -  retrieval and reflection framework

3. **mafiAI** (sstarr1879/mafiAI)
   - 研究LLM代理邊界違規
   - Tool system with configurable security boundaries

4. **WOLF benchmark** (arXiv:2512.09187, NeurIPS 2025)
   - 測量欺騙產生和檢測的 comprehensive multi-agent benchmark
   - 31% of turns contain deceptive statements
   - 71-73% detection precision

### 欺騙檢測方法 (WOLF taxonomy)
| Category | Definition |
|----------|------------|
| **Omission** | 遺漏相關資訊 |
| **Distortion** | 扭曲事實資訊 |
| **Fabrication** | 捏造假資訊 |
| **Misdirection** | 轉移注意力 |

### 關鍵實現洞察
1. **Game State Machine**: Phase-based state management
2. **Role Prompt Engineering**: Distinct prompts per role
3. **Memory Buffer**: Rolling window of recent events
4. **Action Selection**: Multi-candidate generation + selection policy

### 開放挑戰
1. Scalability - 6-12 players處理
2. Human-AI mixed gameplay
3. Real-time constraints
4. Deception robustness

---

## 研究發現 (from Langchain Librarian)

### LangChain Multi-Agent Patterns

#### 1. Subagents Pattern
- Main agent 協調多個 subagents
- 每個 subagent 有獨立的 system prompt 和 tools
- 支援 sequential 和 parallel execution
- 適合隔離不同遊戲角色的 context

#### 2. Handoffs Pattern
- 動態轉移控制權給其他 agent
- 保持累積的對話狀態
- 適合遊戲中不同 NPC 交替主導的場景
- 使用 `Command` 結構進行轉移

#### 3. Supervisor Pattern
- 中央 supervisor 做路由決策
- 清晰的決策可見性
- 適合需要複雜多步推理的遊戲場景
- 層次結構：supervisor → workers

#### 4. Swarm Pattern
- 完全去中心化
- Agent 直接互相溝通
- 適合大量 NPC 的遊戲
- 缺點：觀測性低，可能有 routing loops

### Deception Detection (WOLF Benchmark)
- **71-73%** detection precision
- **31%** of turns contain deceptive statements
- 主要形式：
  - **Concealment**: 遺漏相關資訊
  - **Distortion**: 扭曲/誤導
  - **Fabrication**: 捏造假資訊
- LLM deception 主要是 **equivocation** 而非 outright lying

### RAG Patterns for Game
- Query routing 決定使用哪個 knowledge base
- Parallel retrieval from multiple sources
- Game-specific: rules, lore, characters, strategy 分離

### 推薦實現架構
```python
# Supervisor Pattern for Game Coordination
game_supervisor → [narrative_agent, combat_agent, social_agent]
                 ↓
         使用 RAG for game knowledge
```

### 欺騙檢測代碼模式
```python
class DeceptionDetector:
    def __init__(self, llm):
        self.llm = llm
        # 分析 statement, speaker_role, game_context
        # 輸出 deception probability (0-1)
```

### 關鍵洞察
1. **No single prompt string** - persona 是 controlled assembly pipeline
2. **Dynamic system prompts** - runtime 動態組合
3. **Context isolation** - 保持遊戲角色神秘感
4. **Supervisor > free-form chat** - 更好的可控性和可觀測性
