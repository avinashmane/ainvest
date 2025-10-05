## Data Security & Privacy

This document describes how AINVEST (the “App”) collects, uses, stores, and protects user data. It is a general, non-legal summary intended to explain the App's practices in simple terms. For formal legal advice, consult a qualified attorney.

### What data we collect

- Account information: email address and basic profile data created when you register.
- Usage data: non-personal usage metrics such as pages you view and features you use, collected to improve the App.
- Financial data you provide: ticker symbols, mock portfolio transactions, and other input you type into the app. The App does not connect to brokerage accounts by default.
- Logs and diagnostics: server or client logs used for debugging and operational monitoring.

### How we use data

- Provide the core app experience (profile, mock portfolio, charts and quotes).
- Improve features and fix bugs using aggregated usage statistics.
- Support and troubleshooting when you report issues.

### Storage and retention

- The App may use Google Firestore (or other configured storage) to persist user profile data and mock transactions. Data is retained until you request deletion or the account is removed.
- Backups and logs may be retained for a limited period for operational reasons.

### Third-party services

The App depends on third-party services and libraries which have their own privacy practices. Notable examples:

- Agno: used for agent/tool integrations.
- Google Cloud Firestore: data persistence if configured.
- yfinance: used to fetch market data from public sources.
- Streamlit: UI framework used to deliver the app.

We do not control third-party data handling. Please review their privacy policies for details.

### Security practices

- Minimal principle: store only what is necessary for the app to function.
- Environment configuration (API keys, credentials) should be kept in a secure place (e.g., `.env` local file, secrets manager in production). Do not commit secrets to source control.
- Where possible, the app uses secure connections (HTTPS) to communicate with external services.
- Access to production resources should be protected by proper IAM/ACL controls when deployed.

### User rights and deletion

- If you want your profile or data removed, contact the maintainers (open an issue in the project repository or use the contact address provided in the app). We will provide instructions to delete data from configured storage.

### Limitations

- This is an informational policy summary, not a substitute for formal legal privacy policies or compliance statements (e.g., GDPR, CCPA). Depending on your jurisdiction and how you deploy the app, additional legal requirements may apply.

### Contact

Open an issue on the project repository or contact the maintainers for privacy-related questions.
