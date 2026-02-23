import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';

function KYCForm() {
  const [form, setForm] = useState({ 
    name: '', aadhaar_number: '', district: '', age: '' 
  });
  const [file, setFile] = useState(null);
  const [fileError, setFileError] = useState('');
  const [uploadMsg, setUploadMsg] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);
  const [attemptInfo, setAttemptInfo] = useState(null);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const isResubmit = location.state?.mode === 'resubmit';

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    axios.get('http://127.0.0.1:8000/kyc/status', {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => {
      setAttemptInfo(res.data);
    }).catch(() => {
      setAttemptInfo(null);
    });
  }, [navigate]);

  // ---- FRONTEND FILE VALIDATION ----
  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setFileError('');
    setUploadMsg('');
    setUploadSuccess(false);

    if (!selected) return;

    // Check file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    if (!allowedTypes.includes(selected.type)) {
      setFileError('❌ Invalid file type. Only JPG, PNG, PDF allowed.');
      setFile(null);
      return;
    }

    // Check file size (max 2MB)
    const maxSize = 2 * 1024 * 1024;
    if (selected.size > maxSize) {
      setFileError('❌ File too large. Maximum size is 2MB.');
      setFile(null);
      return;
    }

    // Check file name for suspicious characters
    const suspicious = /[<>:"/\\|?*]/.test(selected.name);
    if (suspicious) {
      setFileError('❌ Filename contains invalid characters.');
      setFile(null);
      return;
    }

    // Check image dimensions if it's an image
    if (selected.type.startsWith('image/')) {
      const img = new Image();
      img.src = URL.createObjectURL(selected);
      img.onload = () => {
        if (img.width < 200 || img.height < 200) {
          setFileError('❌ Image too small. Minimum 200x200 pixels required.');
          setFile(null);
          return;
        }
        setFile(selected);
        setUploadMsg('✅ File looks valid. Click Upload Document.');
      };
      return;
    }

    setFile(selected);
    setUploadMsg('✅ File looks valid. Click Upload Document.');
  };

  // ---- UPLOAD TO BACKEND ----
  const handleUpload = async () => {
    if (!file) {
      setFileError('❌ Please select a valid file first.');
      return;
    }

    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(
        `http://127.0.0.1:8000/kyc/upload?name=${encodeURIComponent(form.name)}`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      setUploadSuccess(true);
      setUploadMsg(`✅ ${res.data.message}`);
      setFileError('');
      setOcrResult(res.data);
    } catch (err) {
      setUploadSuccess(false);
      setFileError(`❌ ${err.response?.data?.detail || 'Upload failed'}`);
    }
  };

  // ---- KYC SUBMIT ----
  const handleSubmit = async () => {
    if (!uploadSuccess) {
      setMessage('❌ Please upload your document before submitting.');
      return;
    }

    const token = localStorage.getItem('token');
    if (!token) { navigate('/login'); return; }

    const flagsString = ocrResult?.flags?.join('; ') || '';

    const baseUrl = isResubmit
      ? 'http://127.0.0.1:8000/kyc/resubmit'
      : 'http://127.0.0.1:8000/kyc/submit';

    try {
      const res = await axios.post(
        `${baseUrl}?name=${encodeURIComponent(form.name)}&aadhaar_number=${form.aadhaar_number}&district=${encodeURIComponent(form.district)}&age=${form.age}` +
        `&ocr_aadhaar_found=${ocrResult?.aadhaar_found || false}` +
        `&ocr_name_found=${ocrResult?.name_found || false}` +
        `&face_detected=${ocrResult?.face_detected || false}` +
        `&ocr_flags=${encodeURIComponent(flagsString)}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      navigate('/result', { state: res.data });
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (detail === 'Maximum resubmission attempts reached') {
        setMessage('❌ You have reached the maximum number of resubmission attempts. Please contact support.');
      } else {
        setMessage('❌ Submission failed. Please login again.');
      }
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>📋 KYC Submission</h1>
        <p style={styles.subtitle}>Fill in your details below</p>

        <input style={styles.input} placeholder="Full Name (min 3 characters)"
          onChange={e => setForm({ ...form, name: e.target.value })} />
        <input style={styles.input} placeholder="Aadhaar Number (12 digits)"
          maxLength={12}
          onChange={e => setForm({ ...form, aadhaar_number: e.target.value })} />
        <input style={styles.input} placeholder="District (e.g. Chennai)"
          onChange={e => setForm({ ...form, district: e.target.value })} />
        <input style={styles.input} placeholder="Age" type="number"
          onChange={e => setForm({ ...form, age: e.target.value })} />

        {/* Document Upload Section */}
        <div style={styles.uploadBox}>
          <p style={styles.uploadLabel}>📄 Upload Aadhaar Document</p>
          <p style={styles.uploadHint}>JPG, PNG or PDF • Max 2MB • Min 200x200px</p>
          <input
            type="file"
            accept="image/jpeg,image/png,image/jpg,application/pdf"
            style={styles.fileInput}
            onChange={handleFileChange}
          />
          {uploadMsg && !fileError && (
            <p style={styles.uploadMsg}>{uploadMsg}</p>
          )}
          {fileError && (
            <p style={styles.errorMsg}>{fileError}</p>
          )}
          <button
            style={uploadSuccess ? styles.uploadBtnSuccess : styles.uploadBtn}
            onClick={handleUpload}
            disabled={uploadSuccess}
          >
            {uploadSuccess ? '✅ Document Uploaded' : 'Upload Document'}
          </button>
        </div>

        <button style={styles.button} onClick={handleSubmit}>
          Submit KYC
        </button>

        {ocrResult && !fileError && (
          <div style={{ marginTop: '12px' }}>
            <p style={{ color: ocrResult.aadhaar_found ? '#10B981' : '#EF4444', fontSize: '12px' }}>
              {ocrResult.aadhaar_found ? '✅ Aadhaar number detected in document' : '❌ No Aadhaar number detected in document'}
            </p>
            <p style={{ color: ocrResult.name_found ? '#10B981' : '#EF4444', fontSize: '12px' }}>
              {ocrResult.name_found ? '✅ Name found in document' : '❌ Name mismatch between form and document'}
            </p>
            <p style={{ color: ocrResult.face_detected ? '#10B981' : '#EF4444', fontSize: '12px' }}>
              {ocrResult.face_detected ? '✅ Face detected in document (looks like a valid ID photo)' : '❌ No face detected — document may not be a valid ID'}
            </p>
            {ocrResult.flags && ocrResult.flags.length > 0 && (
              <ul style={{ marginTop: '6px', paddingLeft: '18px', color: '#F59E0B', fontSize: '12px' }}>
                {ocrResult.flags.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        {attemptInfo && attemptInfo.status === 'REJECTED' && (
          <p style={{ color: '#F59E0B', fontSize: '12px', marginTop: '10px' }}>
            Attempt {Math.min((attemptInfo.attempt_number || 1) + (isResubmit ? 1 : 0), 3)} of 3
          </p>
        )}

        {message && <p style={styles.errorMsg}>{message}</p>}
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', background: '#080C14', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' },
  card: { background: '#0D1421', border: '1px solid #1A2540', borderRadius: '16px', padding: '40px', width: '420px' },
  title: { color: '#00E5FF', textAlign: 'center', marginBottom: '8px' },
  subtitle: { color: '#888', textAlign: 'center', marginBottom: '24px', fontSize: '14px' },
  input: { width: '100%', padding: '12px', marginBottom: '14px', background: '#131B2E', border: '1px solid #1A2540', borderRadius: '8px', color: 'white', fontSize: '14px', boxSizing: 'border-box' },
  uploadBox: { background: '#131B2E', border: '1px dashed #1A2540', borderRadius: '10px', padding: '16px', marginBottom: '16px' },
  uploadLabel: { color: '#00E5FF', fontSize: '13px', fontWeight: 'bold', marginBottom: '4px' },
  uploadHint: { color: '#555', fontSize: '11px', marginBottom: '12px' },
  fileInput: { width: '100%', color: '#888', fontSize: '13px', marginBottom: '10px', boxSizing: 'border-box' },
  uploadMsg: { color: '#10B981', fontSize: '12px', marginBottom: '10px' },
  errorMsg: { color: '#EF4444', fontSize: '12px', marginBottom: '10px' },
  uploadBtn: { width: '100%', padding: '10px', background: 'transparent', color: '#00E5FF', border: '1px solid #00E5FF', borderRadius: '8px', fontSize: '13px', cursor: 'pointer', marginBottom: '4px' },
  uploadBtnSuccess: { width: '100%', padding: '10px', background: '#052e16', color: '#10B981', border: '1px solid #10B981', borderRadius: '8px', fontSize: '13px', cursor: 'not-allowed', marginBottom: '4px' },
  button: { width: '100%', padding: '12px', background: '#00E5FF', color: '#000', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', marginTop: '8px' },
};

export default KYCForm;