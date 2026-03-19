# sqlalchemy-test

## 起動方法

### 1. docker を起動

```bash
docker compose up -d
```

### 2. containerに入って実行

```bash
# containerに入る
docker compose exec app bash

# container内で実行
python -m app.main
```
