# Konfigurasi CLI

Anote CLI dapat dikonfigurasi melalui `.anote.json` di root proyek Anda atau `~/.anote/config.json` secara global.

## File Konfigurasi

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "provider": "anthropic"
}
```

## Mengelola Konfigurasi

```bash
anote config list          # Tampilkan semua pengaturan
anote config get model     # Dapatkan nilai
anote config set model claude-haiku-4-5-20251001  # Atur nilai
anote config unset model   # Hapus nilai
```
