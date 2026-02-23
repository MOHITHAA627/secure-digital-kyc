import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleRegister = async () => {
    try {
      await axios.post(
        `http://127.0.0.1:8000/register?email=${email}&password=${password}`
      );
      setMessage('Registered successfully! Redirecting to login...');
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      setMessage('Registration failed. Email may already exist.');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>🔐 SecureKYC-AI</h1>
        <p style={styles.subtitle}>Create your account</p>
        <input
          style={styles.input}
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <input
          style={styles.input}
          placeholder="Password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
        <button style={styles.button} onClick={handleRegister}>
          Register
        </button>
        {message && <p style={styles.message}>{message}</p>}
        <p style={styles.link} onClick={() => navigate('/login')}>
          Already have an account? Login
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', background: '#080C14', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  card: { background: '#0D1421', border: '1px solid #1A2540', borderRadius: '16px', padding: '40px', width: '380px' },
  title: { color: '#00E5FF', textAlign: 'center', marginBottom: '8px' },
  subtitle: { color: '#888', textAlign: 'center', marginBottom: '24px' },
  input: { width: '100%', padding: '12px', marginBottom: '16px', background: '#131B2E', border: '1px solid #1A2540', borderRadius: '8px', color: 'white', fontSize: '14px', boxSizing: 'border-box' },
  button: { width: '100%', padding: '12px', background: '#00E5FF', color: '#000', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer' },
  message: { color: '#10B981', textAlign: 'center', marginTop: '16px' },
  link: { color: '#00E5FF', textAlign: 'center', marginTop: '16px', cursor: 'pointer', fontSize: '14px' }
};

export default Register;