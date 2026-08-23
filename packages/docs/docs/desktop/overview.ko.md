# 데스크탑 앱 개요

Anote AI 데스크탑 앱은 Electron으로 구축된 개인용 오프라인 AI 어시스턴트입니다.

## 주요 속성

- **개인 정보 보호**: 모든 데이터는 귀하의 기기에 저장됩니다.
- **오프라인 기능**: 로컬 Ollama 모델과 함께 작동합니다.
- **크로스 플랫폼**: Windows, macOS, Linux
- **번들 백엔드**: Python Flask 백엔드가 독립 실행형 실행 파일로 패키징됩니다.

## 아키텍처

```
Electron shell
  └─ React 프론트엔드 (Vite + Tailwind)
  └─ 번들된 Python 백엔드 (PyInstaller 실행 파일)
       └─ 포트 5099에서 Flask API
       └─ SQLite 데이터베이스 (로컬)
       └─ ChromaDB 벡터 저장소 (로컬)
```
