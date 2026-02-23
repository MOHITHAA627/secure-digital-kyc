import { useLocation, useNavigate } from 'react-router-dom';

function Result() {
  const { state } = useLocation();
  const navigate = useNavigate();

  const statusColor = {
    APPROVED: '#10B981',
    REVIEW: '#F59E0B',
    REJECTED: '#EF4444'
  };

  const statusEmoji = {
    APPROVED: '✅',
    REVIEW: '⚠️',
    REJECTED: '❌'
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>KYC Result</h1>
        <div style={{ ...styles.badge, background: statusColor[state?.verification_status] }}>
          {statusEmoji[state?.verification_status]} {state?.verification_status}
        </div>
        <div style={styles.row}>
          <span style={styles.label}>Risk Score</span>
          <span style={styles.value}>{state?.risk_score}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>UIDAI District Risk</span>
          <span style={styles.value}>{state?.uidai_district_risk}</span>
        </div>
        <div style={styles.reasonsBox}>
          <p style={styles.label}>Reasons Flagged:</p>
          {state?.reasons?.length === 0
            ? <p style={{ color: '#10B981' }}>No issues found</p>
            : state?.reasons?.map((r, i) => (
              <p key={i} style={styles.reason}>⚠ {r}</p>
            ))
          }
        </div>
        <p style={styles.emailNote}>
          ✉ A confirmation email has been sent to your registered email address.
        </p>
        {state?.verification_status === 'REJECTED' && (
          <button
            style={{ ...styles.button, marginBottom: '10px' }}
            onClick={() => navigate('/kyc', { state: { mode: 'resubmit' } })}
          >
            Resubmit KYC
          </button>
        )}
        <button style={styles.button} onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', background: '#080C14', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  card: { background: '#0D1421', border: '1px solid #1A2540', borderRadius: '16px', padding: '40px', width: '420px' },
  title: { color: '#00E5FF', textAlign: 'center', marginBottom: '24px', fontSize: '22px' },
  badge: { padding: '12px', borderRadius: '8px', textAlign: 'center', fontSize: '20px', fontWeight: 'bold', color: '#000', marginBottom: '24px' },
  row: { display: 'flex', justifyContent: 'space-between', marginBottom: '12px', padding: '10px', background: '#131B2E', borderRadius: '8px' },
  label: { color: '#888', fontSize: '13px' },
  value: { color: 'white', fontWeight: 'bold' },
  reasonsBox: { background: '#131B2E', padding: '16px', borderRadius: '8px', marginTop: '16px', marginBottom: '24px' },
  reason: { color: '#F59E0B', fontSize: '13px', marginTop: '6px' },
  emailNote: { color: '#888', fontSize: '13px', textAlign: 'center', marginBottom: '16px' },
  button: { width: '100%', padding: '12px', background: '#00E5FF', color: '#000', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer' }
};

export default Result;