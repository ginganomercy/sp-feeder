# Database Design Decision - feeding_logs.device_id

## Design Choice: VARCHAR(50) for device_id

### Background

The `feeding_logs` table uses a different approach compared to other tables:

```sql
-- feeding_logs: Uses device_sn (serial number)
CREATE TABLE `feeding_logs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `device_id` varchar(50) DEFAULT NULL,  -- References devices.device_sn
  ...
);

-- Other tables: Use device_id (integer primary key)
CREATE TABLE `feeding_schedules` (
  `device_id` int(11) DEFAULT NULL,  -- References devices.id
  FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`) ON DELETE CASCADE
  ...
);
```

### Rationale

This design is **INTENTIONAL** for IoT performance optimization:

1. **MQTT Message Structure**: ESP32 devices send messages with `device_sn`:
   ```json
   {
     "device_id": "PF-ESP32-001",
     "porsi": 15,
     "metode": "manual"
   }
   ```

2. **Direct Logging**: No database lookup required before insert:
   ```python
   # Fast: Direct insert using device_sn from MQTT message
   cursor.execute("INSERT INTO feeding_logs (device_id, grams_out, method) 
                   VALUES (%s, %s, %s)", (sn, grams, metode))
   
   # vs Slower: Would need extra SELECT first
   cursor.execute("SELECT id FROM devices WHERE device_sn = %s", (sn,))
   device_id = cursor.fetchone()['id']
   cursor.execute("INSERT INTO feeding_logs (device_id, ...) VALUES (%s, ...)", (device_id, ...))
   ```

3. **Log Persistence**: Feeding logs remain available even if device is reset/deleted

### Trade-offs

**Advantages:**
- ✅ Faster MQTT message processing (no JOIN/lookup overhead)
- ✅ Logs persist after device reset
- ✅ Simplified IoT integration
- ✅ Decoupled: Hardware failures don't affect historical data

**Disadvantages:**
- ❌ Schema inconsistency (VARCHAR vs INT)
- ❌ No referential integrity (orphan records possible)
- ❌ No automatic cleanup via CASCADE DELETE

### Performance Impact

**Current Design:**
- MQTT insert: ~1ms (single INSERT)
- Dashboard query: Uses device_sn directly (no JOIN)

**Alternative (Normalized) Design:**
- MQTT insert: ~3-5ms (SELECT + INSERT)
- Dashboard query: Same performance
- **Impact:** 3-5x slower on high-frequency IoT writes

### Conclusion

This design choice prioritizes **IoT performance** over **database normalization**.

For a system that receives frequent MQTT messages from multiple devices, the performance benefit outweighs the schema inconsistency.

**Recommendation:** Keep current design unless:
- Orphan records become a maintenance issue
- Schema consistency is critical requirement
- Application transitions away from real-time IoT logging

### Maintenance

To clean orphan records (optional scheduled task):
```sql
DELETE FROM feeding_logs 
WHERE device_id NOT IN (SELECT device_sn FROM devices);
```

---
**Document Version:** 1.0  
**Last Updated:** 2026-02-12  
**Author:** Smart Pet Feeder Development Team
