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
