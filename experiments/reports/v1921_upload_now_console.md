# v1921 Upload Now Console

## 結論

最新使用者榜單中第三名分數仍為 `0.52380`，因此目前 goal 完成條件不變：必須記錄到真實 private score `>0.52380`。

目前 records-backed 最佳真實分數仍是 `0.42894`，所以 goal 尚未完成；下一次建議上傳仍是 structural upside 的 `v1826a`。

## 一行指令

```bash
python3 experiments/scripts/v1921_upload_now_console.py
```

此指令預設只讀取狀態並輸出到 stdout，不更新 report timestamp，不重新產生 submission。

## 建議上傳 path

```text
experiments/final_submission_package/current_upload/submission.csv
```

- Candidate: `v1826a`
- Group/order: `queue#1`
- Rows: `397`
- SHA-256: `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad`
- Stop threshold: real private score `>0.52380`

## 安全 aliases

以下三個檔案與 canonical upload 同 SHA、同 397 rows，可作為人工選檔時的安全交叉檢查：

```text
hw2_D13922024/submission.csv
hw2_D13922024/checkpoints/final_current_private.csv
hw2_D13922024/checkpoints/final_v1826a_private.csv
```

## 不可上傳的 lookalikes

`v1921` 會列出 repo 內其他 `submission.csv` lookalikes；這些 row count 或 SHA 與 current upload 不同，不能選：

```text
experiments/worktrees/consistency-solver/hw2_D13922024/submission.csv
experiments/worktrees/endgame-parser/hw2_D13922024/submission.csv
experiments/worktrees/v53-feedback/hw2_D13922024/submission.csv
werewolf-project/artifacts/legacy-submissions/hw2_D13922024/submission.csv
```

## 最新榜單門檻

| Rank | ID | Private score |
| ---: | --- | ---: |
| 1 | D13922023 | 0.54251 |
| 2 | R14922184 | 0.53461 |
| 3 | R14922115 | 0.52380 |
| 4 | R14942077 | 0.50671 |
| 5 | D13922036 | 0.47792 |
| 6 | r14922187 | 0.47306 |

Top-3 cutoff 是第三名 `0.52380`；等於 `0.52380` 不算完成，必須嚴格大於。

## 上傳後回報分數

拿到真實 private score 後依序執行：

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score
python3 experiments/scripts/v1908_final_goal_status.py
```

只有 `GOAL_COMPLETE=yes` 且分數 `>0.52380` 時，才進入最後完成稽核。

## 驗證證據

```text
python3 -m py_compile experiments/scripts/v1921_upload_now_console.py experiments/scripts/v1921_upload_now_console_regression.py
pass

python3 experiments/scripts/v1921_upload_now_console_regression.py
SCENARIOS=1
FAILURES=0
STDOUT_ONLY_READY=yes

python3 experiments/scripts/v1921_upload_now_console.py
READY_TO_UPLOAD=yes
UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv
CANDIDATE=v1826a
GROUP=queue
ORDER=1
ROWS=397
STOP_IF_SCORE_GREATER_THAN=0.52380
GOAL_COMPLETE_BY_RECORDS=no
BEST_SCORE=0.42894

python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv
OK: 397 predictions validated

python3 experiments/scripts/v1902_upload_alias_guard_regression.py
SCENARIOS=4
FAILURES=0

python3 experiments/scripts/v1919_v1826a_boundary_regression.py
SCENARIOS=8
FAILURES=0
RECORDS_UNCHANGED=yes
```

## Stop condition

目前 stop condition 尚未達成：缺少真實 private score `>0.52380`。下一步是人工上傳本報告指定的 canonical path，回報實際 private score 後再走 score bridge。
