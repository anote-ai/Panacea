# Pengaturan Ekstensi VS Code

Konfigurasikan ekstensi di UI pengaturan VS Code atau `settings.json`.

| Pengaturan | Default | Deskripsi |
|------------|---------|-----------|
| `anote.model` | `claude-sonnet-4-6` | Model default yang digunakan |
| `anote.apiKey` | `""` | Kunci API Anthropic (atau gunakan env var) |
| `anote.permissionMode` | `default` | Mode izin alat: `default`, `auto`, `manual` |
| `anote.showToolUse` | `true` | Tampilkan panggilan alat di panel obrolan |

```json
{
  "anote.model": "claude-sonnet-4-6",
  "anote.permissionMode": "default"
}
```
