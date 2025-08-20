# AI Agent Rules & Project Standards

## 🤖 **Core AI Agent Principles**

### 1. **File Structure Immutability**
- **NEVER** create new requirements files beyond the established two:
  - `requirements-backend.txt` (FastAPI + OpenAI + audio processing)
  - `requirements-frontend.txt` (minimal FastAPI static server)
- **NEVER** create `requirements.txt` in root (causes Render build confusion)
- **NEVER** create multiple YAML deployment files
- **ALWAYS** use the single `render.yaml` for deployment configuration

### 2. **Deployment Configuration Standards**
- **ONE YAML RULE**: Only `render.yaml` exists for deployment
- Backend service uses `requirements-backend.txt`
- Frontend service uses `requirements-frontend.txt`
- Python version controlled via `PYTHON_VERSION` env var, not `runtime.txt`

### 3. **Version Control Practices**
- Update version numbers in `index.html` with meaningful descriptions
- Use semantic versioning (major.minor.patch)
- Include timestamp and feature description in version updates
- Commit messages should be descriptive and reference version changes

### 4. **Code Quality Standards**
- **Frontend**: Vanilla JavaScript only, no frameworks
- **Backend**: FastAPI with direct HTTP calls (no external HTTP libraries like `httpx`)
- **Audio Processing**: Use `pydub` for format conversion to MP3 before OpenAI
- **Error Handling**: Comprehensive try/catch with user-friendly messages

### 5. **Progress Tracking UI Standards**
- Use green color scheme (#20c997) for completed states
- White color for active states (better visibility than dark green)
- Checkmark icons for completed steps, original icons for active/pending
- Four-step process: Upload → Transcribe → Analyze → Complete

### 6. **Environment & Deployment Rules**
- **Render Auto-Deploy**: Push to `main` branch triggers deployment
- **Environment Detection**: JavaScript auto-detects local/Render/GitHub environments
- **OpenAI API**: Use direct urllib HTTP calls, not external libraries
- **CORS**: Enabled for all origins during development

### 7. **Audio Format Support**
- Accept: MP3, M4A, WAV, OGG, AAC
- Convert non-MP3 formats to MP3 using `pydub` before OpenAI API
- Maximum file size: 50MB
- Provide clear error messages for unsupported formats

### 8. **Dependencies Management**
- Backend: Minimal FastAPI stack + `pydub` for audio + `python-dotenv`
- Frontend: Only FastAPI + uvicorn for static serving
- **NO** external HTTP libraries, **NO** OpenAI SDK
- **NO** additional audio libraries beyond `pydub`

### 9. **Error Prevention Rules**
- **BEFORE** creating new files, check if they already exist
- **BEFORE** modifying requirements, verify which file should be updated
- **BEFORE** deployment changes, confirm single YAML approach
- **ALWAYS** test locally before pushing to production

### 10. **Documentation Standards**
- Keep README.md updated with current architecture
- Maintain deployment docs in `docs/RENDER_DEPLOYMENT.md`
- Update this ruleset when new patterns emerge
- Include troubleshooting sections for common issues

## 🚫 **Prohibited Actions**

1. ❌ Creating `requirements.txt` in project root
2. ❌ Adding new YAML deployment files
3. ❌ Installing external HTTP libraries (requests, httpx, aiohttp)
4. ❌ Using OpenAI SDK instead of direct API calls
5. ❌ Creating `runtime.txt` files
6. ❌ Modifying the two-service Render architecture
7. ❌ Adding JavaScript frameworks or build processes
8. ❌ Changing the established green progress UI theme

## ✅ **Required Actions**

1. ✅ Always use `requirements-backend.txt` and `requirements-frontend.txt`
2. ✅ Maintain single `render.yaml` configuration
3. ✅ Update version numbers with feature descriptions
4. ✅ Test audio format conversion with `pydub`
5. ✅ Implement proper error handling for all user interactions
6. ✅ Keep deployment documentation current
7. ✅ Use descriptive commit messages with feature context

## 🔄 **Change Management**

When proposing changes to this ruleset:
1. Document the reason for the change
2. Update relevant documentation
3. Test the change in a separate branch first
4. Update this file with the new standard
5. Communicate breaking changes clearly

## 📞 **Escalation Path**

If conflicting requirements arise:
1. Prioritize user experience and functionality
2. Maintain deployment stability
3. Keep architecture simple and maintainable
4. Document any temporary exceptions clearly
5. Plan migration path for permanent solutions

---
**Last Updated**: December 18, 2024  
**Version**: 1.0.0  
**Applies To**: AI Post Report Project v2.5.0+
