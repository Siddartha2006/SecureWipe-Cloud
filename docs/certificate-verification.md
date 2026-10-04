# Certificate records and verification

## Cloud certificates

After successful object deletion and an object-absence check, the worker stores a JSON record and ReportLab PDF. The signed payload includes a certificate ID, issue time, job ID, selected failed-upload retention, advisory classification, input size and SHA-256 hash, verification URL, result, and explicit cloud-deletion limitations. It does not include the original filename or file contents.

The payload is serialized as UTF-8 JSON with sorted keys and compact separators. It is signed with RSA-PSS using SHA-256 and a 32-byte salt. Certificate JSON contains the signature and the public key. The account owner can download JSON/PDF; the public `/verify/{certificate_id}` endpoint loads the stored record and verifies the signature before returning its status.

A valid signature means the stored payload matches the signature under the embedded public key. Since that public key is self-contained, an independent verifier must pin/trust the key separately to establish organizational identity. A valid signature does not establish the truth of the operation claims. Specifically, cloud object absence does not prove erasure from provider backups, replicas, or physical storage media.

## Desktop certificates

The older desktop application creates a different JSON format with a local key pair and local file-operation metadata. Its private key stays on that machine. The current cloud public lookup is for cloud certificates stored in the cloud database; it is not an upload endpoint for desktop certificate JSON. Desktop verification can be performed with its public key and the verification helper in `src/certificate_generator.py` or a compatible RSA-PSS implementation.

## Key configuration

Set `CERTIFICATE_PRIVATE_KEY` in the API and worker secret stores to base64-encoded PEM RSA private-key bytes (3072 bits recommended; 2048-bit minimum accepted). The private key is not returned to the browser. Optionally set `PUBLIC_VERIFICATION_KEY` to the matching PEM public key to make startup fail fast on a mismatch. Plan secure storage, backup, rotation, and out-of-band key distribution before production use.
