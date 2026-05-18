---
id: OSY-052
title: File Descriptor Leak Anti-Pattern
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-034, OSY-044
used_by: []
related: OSY-034, OSY-044, OSY-025
tags:
  - anti-pattern
  - file-descriptor
  - leak
  - resource-management
  - try-with-resources
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 52
permalink: /technical-mastery/osy/file-descriptor-leak-anti-pattern/
---

## TL;DR

File descriptor leaks occur when open() or socket() is
called without a corresponding close(). The per-process
limit (default 1024) exhausts silently over hours, then
fails loudly with "Too many open files". Fix: always use
try-with-resources. Detect: lsof FD count growth.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-052 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | FD leak, anti-pattern, try-with-resources, lsof |
| **Prerequisites** | OSY-034, OSY-044 |

---

### Why FD Leaks Are Insidious

```
FD limit: 1024 (soft default) per process
  (increase with: ulimit -n 65535)
  
The silent failure pattern:
  Startup:     FD count = 50 (JVM baseline + threads)
  After 1hr:   FD count = 200
  After 4hrs:  FD count = 800
  After 6hrs:  FD count = 1024 -> ERROR
  
  Application works fine for hours, then:
    new connections fail: "Too many open files"
    new files fail to open: "Too many open files"
    (All without any code change or deployment)
  
  Developer investigation: "It was working fine, nothing changed!"
  Root cause: slow FD leak over many requests

FD limit includes:
  Regular files, log files, temp files
  TCP/UDP sockets (including idle keep-alive connections)
  Unix domain sockets
  Pipes (anonymous and named)
  Device files
  Event file descriptors (eventfd, epoll fd)
```

---

### Anti-Pattern Code Examples

```java
// BAD: classic FD leak - exception prevents close()
public class FDLeakService {
    public String readConfig(String path) throws IOException {
        FileInputStream fis = new FileInputStream(path);
        InputStreamReader isr = new InputStreamReader(fis);
        BufferedReader br = new BufferedReader(isr);
        
        String content = br.lines().collect(Collectors.joining("\n"));
        
        // If ANYTHING throws above, we never reach here:
        br.close();     // FD leak if exception before here!
        isr.close();
        fis.close();
        
        return content;
    }
}
// Each call on error = +1 leaked FD
// After 974 error calls: "Too many open files"

// BAD: socket FD leak in HTTP client
public class HttpClientLeaky {
    public String fetch(String url) throws IOException {
        HttpURLConnection conn =
            (HttpURLConnection) new URL(url).openConnection();
        conn.setRequestMethod("GET");
        
        if (conn.getResponseCode() != 200) {
            // Oops: threw exception or returned early
            // conn.disconnect() never called!
            throw new IOException("HTTP error: " + conn.getResponseCode());
        }
        
        String response = new String(conn.getInputStream().readAllBytes());
        conn.disconnect();  // not reached on error!
        return response;
    }
}
// Every non-200 response = 1 leaked socket FD
```

---

### Fixed Pattern: Try-with-Resources

```java
// GOOD: try-with-resources - auto-closes even on exception
public class FDSafeService {
    public String readConfig(String path) throws IOException {
        // All Closeable resources in try-with-resources:
        try (FileInputStream fis = new FileInputStream(path);
             InputStreamReader isr = new InputStreamReader(fis);
             BufferedReader br = new BufferedReader(isr)) {
            
            return br.lines().collect(Collectors.joining("\n"));
        }
        // close() called automatically in reverse order:
        // br.close() -> isr.close() -> fis.close()
        // Even if an exception is thrown anywhere!
    }
}

// GOOD: HTTP with proper cleanup
public class HttpClientSafe {
    public String fetch(String url) throws IOException {
        HttpURLConnection conn =
            (HttpURLConnection) new URL(url).openConnection();
        try {
            conn.setRequestMethod("GET");
            int code = conn.getResponseCode();
            if (code != 200) {
                // Read error stream to allow connection reuse,
                // then throw (finally block disconnects)
                InputStream err = conn.getErrorStream();
                if (err != null) err.close();
                throw new IOException("HTTP error: " + code);
            }
            try (InputStream is = conn.getInputStream()) {
                return new String(is.readAllBytes());
            }
        } finally {
            conn.disconnect(); // ALWAYS called (finally)
        }
    }
}
```

---

### Detection and Monitoring

```bash
# Step 1: Establish FD baseline
PID=$(pgrep java)
echo "FD count at startup: $(lsof -p $PID 2>/dev/null | wc -l)"

# Step 2: Monitor over time (cron-like check)
watch -n 60 "lsof -p $PID 2>/dev/null | wc -l"
# Growing count over time = leak

# Step 3: Identify what type of FDs are growing
lsof -p $PID | awk '{print $5}' | sort | uniq -c | sort -rn
# REG: regular files (FileInputStream/OutputStream)
# IPv4/IPv6: socket (HttpClient, JDBC, Redis)
# PIPE: pipes (ProcessBuilder subprocess)

# Step 4: Find specific leaking files
lsof -p $PID | grep REG | awk '{print $NF}' | sort | uniq -c | sort -rn
# Find which file path appears most frequently -> that's the leak

# Step 5: Check FD limit
cat /proc/$PID/limits | grep "Open files"
# Soft Limit: default 1024, Hard Limit: 4096
# Increase for emergency: ulimit -n 65535
# Permanent: edit /etc/security/limits.conf or systemd service

# Prometheus/monitoring:
# JVM metric: process_open_fds (from JVM metric registry)
# Alert: when process_open_fds > 80% of process_max_fds
```

---

### Production FD Leak Postmortem Pattern

```
Timeline:
  00:00  Service deployed (FD count: 52)
  06:00  FD count: 350 (normal operations)
  14:00  FD count: 780 (approaching limit)
  16:23  FD count: 1024, service starts failing:
         "java.io.IOException: Too many open files"
         New requests fail, health check still passes
  16:24  On-call alert: p99 latency spike, error rate 5%
  16:30  Restart restores service (FD count reset to 52)
  
Root cause investigation:
  lsof before restart shows: 900+ REG file FDs
  All pointing to: /tmp/upload-*.tmp files
  
  Code review found:
  public void handleUpload(MultipartFile file) throws IOException {
      File tmp = File.createTempFile("upload", ".tmp");
      file.transferTo(tmp);
      processFile(tmp);
      tmp.delete();  // file deleted but FD never closed!
  }
  
  Fix:
  File tmp = File.createTempFile("upload", ".tmp");
  try {
      file.transferTo(tmp);
      processFile(tmp);  // processFile should use try-with-resources
  } finally {
      if (!tmp.delete()) tmp.deleteOnExit();
  }
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Deleting a file closes its FD" | Deleting (unlink()) removes the directory entry but does NOT close open FDs. The file data persists until all FDs are closed. lsof shows deleted files with FDs as "(deleted)" in the NAME column - still consuming FDs and disk space |
| "Java GC closes streams when objects are garbage collected" | Finalizers for Closeable objects are not guaranteed to run promptly or at all. The JVM may call finalize() eventually but never rely on it for FD cleanup. Always close explicitly with try-with-resources |

---

### Mastery Checklist

- [ ] Knows per-process FD limit (default 1024) and how to increase it
- [ ] Can diagnose FD leak using `lsof -p PID | wc -l` growth pattern
- [ ] Always uses try-with-resources for all Closeable resources
- [ ] Knows deleting a file does NOT close its FD
