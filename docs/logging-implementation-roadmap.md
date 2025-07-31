# Logging Implementation Roadmap

## Executive Summary

This document provides a step-by-step implementation plan for migrating mailPilot from print statements to a comprehensive, production-ready logging system.

## Implementation Phases

### Phase 1: Foundation (Week 1)
✅ **Completed in Design Phase:**
- Created `src/utils/logging_config.py` with complete logging infrastructure
- Implemented security features (PII redaction, sensitive data filtering)
- Created structured and development formatters
- Built environment-aware configuration

**Next Steps:**
1. Add logging dependencies to `pyproject.toml`:
   ```toml
   [project.optional-dependencies]
   dev = [
       "pytest>=8.0.0",
       "pytest-cov>=5.0.0",
       "pytest-mock>=3.14.0",
       "python-json-logger>=2.0.7",  # For production JSON logging
   ]
   ```

2. Create logging directories:
   ```bash
   mkdir -p logs
   echo "*.log" >> .gitignore
   echo "logs/" >> .gitignore
   ```

3. Add environment configuration to `.env.sample`:
   ```
   # Logging Configuration
   MAILPILOT_ENV=development
   MAILPILOT_LOG_DIR=logs
   ```

### Phase 2: Core Module Migration (Week 2)

**Priority Order:**
1. **Gmail Client** (Most print statements)
   - Replace 11 print statements
   - Add performance logging for API calls
   - Implement retry logging

2. **Main Application**
   - Replace 6 print statements
   - Add startup/shutdown logging
   - Implement application lifecycle logging

3. **ChatGPT Client**
   - Replace 1 print statement
   - Add API performance tracking
   - Log token usage statistics

4. **Thread Memory**
   - Replace 1 print statement
   - Add storage operation logging
   - Implement data integrity logging

### Phase 3: UI/UX Separation (Week 3)

**Approval Interface:**
- Keep Rich console.print() for UI elements
- Add backend logging for:
  - User decisions (approval/rejection)
  - UI state changes
  - Performance metrics

**Implementation Pattern:**
```python
# UI Output (keep as is)
self.console.print("[bold]User Interface Element[/bold]")

# Backend Logging (add)
logger.info("User action logged", extra={"action": "approval", "context": context})
```

### Phase 4: Testing & Validation (Week 4)

1. **Unit Tests**
   - Run `test_logging_config.py`
   - Add logging assertions to existing tests
   - Test log output in different environments

2. **Integration Tests**
   - Test log rotation
   - Verify sensitive data redaction
   - Test performance impact

3. **Manual Testing**
   - Development environment (colored console)
   - Test environment (JSON to console)
   - Production simulation (file output only)

### Phase 5: Monitoring & Operations (Week 5)

1. **Log Analysis Tools**
   ```bash
   # Create analysis scripts
   mkdir scripts/log_analysis
   ```

2. **Monitoring Setup**
   - Error rate tracking
   - Performance metrics
   - Authentication events
   - API usage patterns

3. **Alerting Rules**
   - Critical errors
   - Authentication failures
   - Rate limit warnings
   - Performance degradation

## Migration Checklist

### Per-Module Checklist
- [ ] Add `from utils.logging_config import get_logger`
- [ ] Create module logger: `logger = get_logger(__name__)`
- [ ] Replace all print statements
- [ ] Add structured context with `extra` parameter
- [ ] Add performance logging where appropriate
- [ ] Update tests to verify logging
- [ ] Document any special logging considerations

### Global Checklist
- [ ] Update `pyproject.toml` with dependencies
- [ ] Create log directories
- [ ] Update `.gitignore`
- [ ] Update `.env.sample`
- [ ] Create deployment documentation
- [ ] Set up log rotation scripts
- [ ] Configure monitoring
- [ ] Train team on new logging

## Code Migration Examples

### Before:
```python
print(f"Error: {error}")
```

### After:
```python
logger.error("Operation failed", exc_info=True, extra={
    "operation": "email_send",
    "recipient": recipient_id,
    "error_type": type(error).__name__
})
```

## Performance Considerations

1. **Logging Overhead**
   - Use appropriate log levels
   - Avoid logging in tight loops
   - Use lazy formatting: `logger.debug("Value: %s", expensive_func())`

2. **Disk I/O**
   - Rotation keeps file sizes manageable
   - Async logging for high-throughput scenarios
   - Monitor disk usage

3. **Memory Usage**
   - Logger caching reduces overhead
   - Structured data kept minimal
   - No memory leaks from handlers

## Security Best Practices

1. **Never Log:**
   - Passwords or authentication tokens
   - Full email addresses (use partial)
   - API keys or secrets
   - Personal identification information

2. **Always Log:**
   - Authentication attempts
   - Authorization failures
   - Configuration changes
   - Data access patterns

3. **Log Retention:**
   - General logs: 30 days
   - Error logs: 90 days
   - Security logs: 1 year
   - Implement automated cleanup

## Rollback Plan

If issues arise:
1. Keep original files with print statements as `.py.backup`
2. Environment variable to disable new logging: `MAILPILOT_USE_PRINT=1`
3. Quick revert script to restore print statements
4. Gradual module-by-module rollback option

## Success Metrics

1. **Technical Metrics:**
   - 100% print statement replacement
   - <5% performance impact
   - Zero sensitive data leaks in logs
   - 95%+ test coverage for logging

2. **Operational Metrics:**
   - 50% faster issue diagnosis
   - 90% reduction in debugging time
   - Proactive issue detection
   - Compliance with logging standards

## Next Steps

1. Review and approve the logging design
2. Start with Phase 1 (Foundation)
3. Migrate one module as proof of concept
4. Gather feedback and adjust
5. Complete full migration
6. Deploy to production with monitoring

## Support Resources

- Logging configuration: `src/utils/logging_config.py`
- Migration guide: `docs/logging-migration-guide.md`
- Example implementation: `src/gmail/client_with_logging.py`
- Test suite: `tests/test_logging_config.py`
- Python logging docs: https://docs.python.org/3/library/logging.html