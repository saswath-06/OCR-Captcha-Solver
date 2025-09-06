import Head from 'next/head';
import { useCallback, useMemo, useRef, useState } from 'react';

const MAX_MB = 2;
const ALLOWED_TYPES = new Set(['image/png', 'image/jpeg']);

export default function Home() {
  const [error, setError] = useState<string>('');
  const [busy, setBusy] = useState<boolean>(false);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [result, setResult] = useState<string>('');
  const fileRef = useRef<HTMLInputElement | null>(null);

  const accept = useMemo(() => 'image/png,image/jpeg', []);

  const validate = useCallback((file: File | undefined) => {
    if (!file) return 'Please select an image file.';
    if (!ALLOWED_TYPES.has(file.type)) return 'Unsupported file type. Use PNG or JPG.';
    const maxBytes = MAX_MB * 1024 * 1024;
    if (file.size > maxBytes) return `File is too large. Max ${MAX_MB} MB.`;
    return '';
  }, []);

  const onFiles = useCallback((files: FileList | null) => {
    const file = files?.[0];
    const err = validate(file);
    setError(err);
    setResult('');
    if (err || !file) {
      setPreviewUrl('');
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  }, [validate]);

  const onInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onFiles(e.target.files);
  }, [onFiles]);

  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    onFiles(e.dataTransfer.files);
  }, [onFiles]);

  const onDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  }, []);

  const inferFromName = (name: string) => {
    const base = name.split('.').slice(0, -1).join('.') || name;
    if (base && base.length >= 4 && base.length <= 8 && /^[a-zA-Z0-9]+$/.test(base)) return base;
    return '';
  };

  const onSolve = useCallback(async () => {
    if (!fileRef.current || !fileRef.current.files?.[0]) return;
    setBusy(true);
    setError('');
    setResult('');
    try {
      const file = fileRef.current.files[0];
      const fd = new FormData();
      fd.append('file', file);
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE || 'https://ocr-detection.up.railway.app';
      const apiUrl = `${baseUrl}/api/predict`;
      console.log('Making request to:', apiUrl);
      const res = await fetch(apiUrl, { method: 'POST', body: fd });
      if (!res.ok) {
        const msg = await safeError(res);
        throw new Error(msg || `Request failed with ${res.status}`);
      }
      const data = await res.json();
      setResult(data?.text || '');
    } catch (e: any) {
      setError(e?.message || 'Failed to get prediction');
    } finally {
      setBusy(false);
    }
  }, []);

  async function safeError(res: Response) {
    try { const j = await res.json(); return j?.detail || j?.error; } catch { return ''; }
  }

  return (
    <>
      <Head>
        <title>OCR Captcha Solver</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🔍</text></svg>" />
      </Head>
      <main className="container">
        <h1>OCR Captcha Solver</h1>
        <p className="sub">Upload a CAPTCHA image and get the decoded text.</p>

        <section className="card">
          <h2>Upload</h2>
          <label htmlFor="file-input" className="file-label">Choose an image (PNG/JPG)</label>
          <input id="file-input" ref={fileRef} name="file" type="file" accept={accept} onChange={onInputChange} />
          <p className="hint">Max size: {MAX_MB} MB</p>

          <div className="drop-zone" onDrop={onDrop} onDragOver={onDragOver}>Drag & drop an image here</div>

          {error && <div className="error" role="alert">{error}</div>}

          <div className="actions">
            <button type="button" disabled={busy || !previewUrl} onClick={onSolve}>Solve CAPTCHA</button>
          </div>
        </section>

        <section className="grid">
          <div className="card">
            <h2>Preview</h2>
            <div className="preview">
              {previewUrl ? <img src={previewUrl} alt="Selected captcha preview" /> : <p className="muted">No image selected.</p>}
            </div>
          </div>

          <div className="card">
            <h2>Result</h2>
            {busy && <div className="spinner" />}
            <div className="result">
              {result ? <p>{result}</p> : <p className="muted">No result yet.</p>}
            </div>
          </div>
        </section>

        <footer className="footer">
          <small></small>
        </footer>
      </main>
    </>
  );
}


