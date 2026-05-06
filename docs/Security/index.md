---
layout: default
title: "Security"
parent: "Technical Dictionary"
nav_order: 44
has_children: true
permalink: /security/
---

# Security

CIA triad, authentication & authorization, cryptography, common vulnerabilities (OWASP Top 10), attack types, defensive practices, and security testing.

**Keywords:** 1771–1882 (112 terms)

| # | Keyword | Difficulty |
|---|---|---|
| 1771 | CIA Triad (Confidentiality, Integrity, Availability) | ★☆☆ |
| 1772 | Authentication vs Authorization | ★☆☆ |
| 1773 | Identification, Authentication, Authorization, Accounting (IAAA) | ★★☆ |
| 1774 | Principle of Least Privilege | ★☆☆ |
| 1775 | Defense in Depth | ★★☆ |
| 1776 | Security by Design | ★★☆ |
| 1777 | Secure SDLC | ★★☆ |
| 1778 | Threat Modeling | ★★☆ |
| 1779 | STRIDE (Spoofing, Tampering, Repudiation, Info Disclosure, DoS, EoP) | ★★★ |
| 1780 | Attack Surface | ★★☆ |
| 1781 | Zero Trust Security Model | ★★★ |
| 1782 | Security Misconfiguration | ★★☆ |
| 1783 | Session-Based Authentication | ★★☆ |
| 1784 | Token-Based Authentication | ★★☆ |
| 1785 | Access Token | ★★☆ |
| 1786 | Refresh Token | ★★☆ |
| 1787 | HttpOnly Cookie | ★★☆ |
| 1788 | Secure Cookie Flag | ★★☆ |
| 1789 | SameSite Cookie | ★★★ |
| 1790 | JWT Anatomy (Header, Payload, Signature) | ★★☆ |
| 1791 | JWT Verification Without DB Lookup | ★★★ |
| 1792 | JWT Security Vulnerabilities | ★★★ |
| 1793 | JWT Algorithm Confusion Attack | ★★★ |
| 1794 | OAuth 2.0 Authorization Code Flow | ★★★ |
| 1795 | OAuth 2.0 Client Credentials Flow | ★★★ |
| 1796 | OAuth 2.0 PKCE | ★★★ |
| 1797 | OAuth 2.0 Implicit Flow (deprecated) | ★★★ |
| 1798 | OpenID Connect (OIDC) | ★★★ |
| 1799 | SAML (Security Assertion Markup Language) | ★★★ |
| 1800 | SSO (Single Sign-On) | ★★☆ |
| 1801 | MFA / 2FA | ★★☆ |
| 1802 | TOTP (Time-Based One-Time Password) | ★★★ |
| 1803 | Passkeys / WebAuthn | ★★★ |
| 1804 | RBAC (Role-Based Access Control) | ★★☆ |
| 1805 | ABAC (Attribute-Based Access Control) | ★★★ |
| 1806 | ACL (Access Control List) | ★★☆ |
| 1807 | Hashing (Bcrypt, Argon2, SHA-256) | ★★☆ |
| 1808 | Encryption (AES, RSA) | ★★☆ |
| 1809 | Encoding (Base64) | ★☆☆ |
| 1810 | Hashing vs Encryption vs Encoding | ★★☆ |
| 1811 | Symmetric vs Asymmetric Encryption | ★★☆ |
| 1812 | Public Key / Private Key | ★★☆ |
| 1813 | PKI (Public Key Infrastructure) | ★★★ |
| 1814 | Digital Signature | ★★★ |
| 1815 | Certificate Authority (CA) | ★★☆ |
| 1816 | TLS Certificate Lifecycle | ★★★ |
| 1817 | Certificate Pinning | ★★★ |
| 1818 | Key Management | ★★★ |
| 1819 | Hardware Security Module (HSM) | ★★★ |
| 1820 | Key Rotation | ★★★ |
| 1821 | Envelope Encryption | ★★★ |
| 1822 | Password Storage Best Practices | ★★☆ |
| 1823 | Salt (Cryptographic) | ★★☆ |
| 1824 | Rainbow Table Attack | ★★★ |
| 1825 | OWASP Top 10 | ★★☆ |
| 1826 | XSS (Cross-Site Scripting) | ★★☆ |
| 1827 | Stored XSS | ★★★ |
| 1828 | Reflected XSS | ★★★ |
| 1829 | DOM-Based XSS | ★★★ |
| 1830 | CSRF (Cross-Site Request Forgery) | ★★☆ |
| 1831 | Anti-CSRF Token | ★★★ |
| 1832 | SQL Injection | ★★☆ |
| 1833 | Parameterized Queries | ★★☆ |
| 1834 | NoSQL Injection | ★★★ |
| 1835 | SSRF (Server-Side Request Forgery) | ★★★ |
| 1836 | Command Injection | ★★★ |
| 1837 | Path Traversal | ★★★ |
| 1838 | XXE (XML External Entity) | ★★★ |
| 1839 | Insecure Deserialization | ★★★ |
| 1840 | Broken Access Control | ★★☆ |
| 1841 | Security Misconfiguration | ★★☆ |
| 1842 | Cryptographic Failures | ★★★ |
| 1843 | Vulnerable and Outdated Components | ★★☆ |
| 1844 | Brute-Force Attack | ★★☆ |
| 1845 | Credential Stuffing | ★★★ |
| 1846 | Timing Attack | ★★★ |
| 1847 | Replay Attack | ★★★ |
| 1848 | Man-in-the-Middle Attack | ★★☆ |
| 1849 | DDoS Attack | ★★☆ |
| 1850 | Phishing | ★☆☆ |
| 1851 | Social Engineering | ★★☆ |
| 1852 | Supply Chain Attack | ★★★ |
| 1853 | Prompt Injection (AI Security) | ★★★ |
| 1854 | Input Sanitization vs Escaping | ★★☆ |
| 1855 | Content Security Policy (CSP) | ★★★ |
| 1856 | Security Headers (HSTS, X-Frame-Options) | ★★★ |
| 1857 | Secrets Management | ★★☆ |
| 1858 | Environment Variables for Secrets | ★☆☆ |
| 1859 | .env File Pattern | ★☆☆ |
| 1860 | Vault (HashiCorp) | ★★★ |
| 1861 | API Key Security | ★★☆ |
| 1862 | Rate Limiting for Security | ★★☆ |
| 1863 | Brute-Force Prevention | ★★☆ |
| 1864 | Account Lockout Policy | ★★★ |
| 1865 | DDoS Protection | ★★★ |
| 1866 | WAF (Web Application Firewall) | ★★★ |
| 1867 | Penetration Testing | ★★★ |
| 1868 | Red Team / Blue Team | ★★★ |
| 1869 | SAST (Static Application Security Testing) | ★★☆ |
| 1870 | DAST (Dynamic Application Security Testing) | ★★★ |
| 1871 | SCA (Software Composition Analysis) | ★★★ |
| 1872 | SBOM (Software Bill of Materials) | ★★★ |
| 1873 | CVE (Common Vulnerabilities and Exposures) | ★★☆ |
| 1874 | CVSS Score | ★★★ |
| 1875 | Security Audit | ★★★ |
| 1876 | SIEM (Security Information and Event Management) | ★★★ |
| 1877 | Security Logging and Monitoring | ★★★ |
| 1878 | Incident Response | ★★★ |
| 1879 | RASP (Runtime Application Self-Protection) | ★★★ |
| 1880 | Dependency Scanning | ★★☆ |
| 1881 | Container Security Scanning | ★★★ |
| 1882 | Secret Scanning (in Git) | ★★★ |
