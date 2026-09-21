# ARCHITECTURE MAP
Implemented foundation: src/lifeverse with configuration, persistence, domain rules, application services and API transport.
Target boundaries: core/domain → application → infrastructure → api/clients/workers.
Current initial implementation keeps domain rules framework-light; later phases will extract explicit ports/repositories as needed.
Forbidden: Core/application dependency on Telegram, Railway or concrete external AI providers; clients must not write authoritative state directly.
