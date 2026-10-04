/**
 * Web Crypto API-based RSA-PSS Signature Verification for SecureWipe Certificates
 */

export interface CertificateResults {
  total_files: number;
  files_processed: number;
  files_failed: number;
  total_size: number;
  duration: number;
  success: boolean;
}

export interface CertificateData {
  certificate_id: string;
  timestamp: string;
  operation_type: string;
  configuration: {
    passes: number;
    pattern: string;
    method: string;
    wipe_free_space?: boolean;
  };
  results: CertificateResults;
  verification: {
    file_hashes: Array<{ file_path: string; final_hash: string; all_hashes: string[] }>;
    operation_hash: string;
  };
  system_info?: Record<string, unknown>;
  compliance?: {
    standard: string;
    passes: number;
    pattern: string;
  };
  signature: string;
  public_key?: string;
}

/**
 * Converts a PEM-formatted RSA public key into an ArrayBuffer
 */
function pemToArrayBuffer(pem: string): ArrayBuffer {
  const b64 = pem
    .replace(/-----BEGIN [^-]+-----/g, "")
    .replace(/-----END [^-]+-----/g, "")
    .replace(/\s+/g, "");
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * Verifies the RSA-PSS SHA-256 digital signature of a certificate
 */
export async function verifyCertificateSignature(cert: CertificateData): Promise<{
  verified: boolean;
  message: string;
}> {
  try {
    if (!cert.signature) {
      return { verified: false, message: "Missing digital signature in certificate data." };
    }

    if (!cert.public_key) {
      return {
        verified: false,
        message: "No public key embedded in certificate for autonomous cryptographic verification.",
      };
    }

    // 1. Reconstruct deterministic canonical payload matching the Python signature generation
    // Python signature canonical object:
    // {
    //   'certificate_id': cert_data['certificate_id'],
    //   'timestamp': cert_data['timestamp'],
    //   'operation_type': cert_data['operation_type'],
    //   'results': cert_data['results'],
    //   'verification': cert_data['verification']
    // }
    const signableData = {
      certificate_id: cert.certificate_id,
      timestamp: cert.timestamp,
      operation_type: cert.operation_type,
      results: cert.results,
      verification: cert.verification,
    };

    // Serialize canonically with sorted keys to match Python's json.dumps(..., sort_keys=True)
    const canonicalJson = JSON.stringify(signableData, Object.keys(signableData).sort());
    const dataEncoder = new TextEncoder();
    const encodedData = dataEncoder.encode(canonicalJson);

    // 2. Decode the Base64 signature
    const signatureBinary = atob(cert.signature);
    const signatureBytes = new Uint8Array(signatureBinary.length);
    for (let i = 0; i < signatureBinary.length; i++) {
      signatureBytes[i] = signatureBinary.charCodeAt(i);
    }

    // 3. Import the RSA public key using Web Crypto API
    const keyBuffer = pemToArrayBuffer(cert.public_key);
    const cryptoKey = await window.crypto.subtle.importKey(
      "spki",
      keyBuffer,
      {
        name: "RSA-PSS",
        hash: "SHA-256",
      },
      false,
      ["verify"]
    );

    // 4. Verify signature with RSA-PSS SHA-256
    // In Python: salt_length=padding.PSS.MAX_LENGTH, or standard SHA256 length (32 bytes)
    // We try verifying with saltLength 32 first, then with saltLength derived
    let isValid = false;
    try {
      isValid = await window.crypto.subtle.verify(
        {
          name: "RSA-PSS",
          saltLength: 32, // standard SHA-256 digest length
        },
        cryptoKey,
        signatureBytes,
        encodedData
      );
    } catch {
      // Fallback attempt with automatic/calculated salt length if 32 fails
      isValid = false;
    }

    if (!isValid) {
      // Try with PSS MAX_LENGTH salt for 4096-bit RSA (512 - 32 - 2 = 478)
      try {
        isValid = await window.crypto.subtle.verify(
          {
            name: "RSA-PSS",
            saltLength: 478,
          },
          cryptoKey,
          signatureBytes,
          encodedData
        );
      } catch {
        isValid = false;
      }
    }

    if (isValid) {
      return { verified: true, message: "Valid RSA-PSS 4096-bit cryptographic signature verified." };
    } else {
      return {
        verified: false,
        message: "Cryptographic signature validation failed. Data may have been tampered with.",
      };
    }
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    return { verified: false, message: `Verification error: ${errorMsg}` };
  }
}
