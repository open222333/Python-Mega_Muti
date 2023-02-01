# MEGA備份

```
監聽指定資料夾 分割檔案並上傳至mega雲端
```

## 用法

```bash
# test.tar._xx 分割檔數字xx除於[總數] 根據 [餘數] 進行分配上傳
python -u mega_sql_script.py [餘數] [總數] [監聽功能 0: '分割', 1: '上傳',2: '檢查過期']
```