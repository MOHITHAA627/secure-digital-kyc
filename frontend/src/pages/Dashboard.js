import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const [data, setData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      const token = localStorage.getItem('token');
      if (!token) { navigate('/login'); return; }
      try {
        const res = await axios.get('http://127.0.0.1:8000/kyc/history', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setData(res.data);
      } catch (err) {
        navigate('/login');
      }
    };
    fetchHistory();
  }, [navigate]);

  const statusColor = {
    APPROVED: '#10B981',
    REVIEW: '#F59E0B',
    REJECTED: '#EF4444'
  };

  return (
    <div style={styles.container}>
      <div style={styles.wrapper}>
        <div style={styles.header}>
          <h1 style={styles.title}>🔐 SecureKYC-AI</h1>
          <button
            style={styles.logoutBtn}
            onClick={() => {
              localStorage.removeItem('token');
              navigate('/login');
            }}
          >
            Logout
          </button>
        </div>

        <p style={styles.welcome}>Welcome back! Here is your KYC overview.</p>

        {data && (
          <>
            <div style={styles.statsRow}>
              <div style={styles.statCard}>
                <p style={styles.statNumber}>{data.total}</p>
                <p style={styles.statLabel}>Total Submissions</p>
              </div>
              <div style={{ ...styles.statCard, borderColor: '#10B981' }}>
                <p style={{ ...styles.statNumber, color: '#10B981' }}>{data.approved}</p>
                <p style={styles.statLabel}>Approved</p>
              </div>
              <div style={{ ...styles.statCard, borderColor: '#F59E0B' }}>
                <p style={{ ...styles.statNumber, color: '#F59E0B' }}>{data.review}</p>
                <p style={styles.statLabel}>Under Review</p>
              </div>
              <div style={{ ...styles.statCard, borderColor: '#EF4444' }}>
                <p style={{ ...styles.statNumber, color: '#EF4444' }}>{data.rejected}</p>
                <p style={styles.statLabel}>Rejected</p>
              </div>
            </div>

            <button style={styles.newKycBtn} onClick={() => navigate('/kyc')}>
              + Submit New KYC Application
            </button>

            <div style={styles.tableWrapper}>
              <h2 style={styles.tableTitle}>📋 Your KYC Submissions</h2>
              {data.records.length === 0 ? (
                <p style={styles.noRecords}>No submissions yet. Click above to start.</p>
              ) : (
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>Name</th>
                      <th style={styles.th}>District</th>
                      <th style={styles.th}>Age</th>
                      <th style={styles.th}>Risk Score</th>
                      <th style={styles.th}>Status</th>
                      <th style={styles.th}>Attempt</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.records.map((r, i) => (
                      <tr key={i} style={styles.tr}>
                        <td style={styles.td}>{r.name}</td>
                        <td style={styles.td}>{r.district}</td>
                        <td style={styles.td}>{r.age}</td>
                        <td style={styles.td}>{r.risk_score}</td>
                        <td style={styles.td}>
                          <span
                            style={{
                              ...styles.badge,
                              background: statusColor[r.status]
                            }}
                          >
                            {r.status}
                          </span>
                        </td>
                        <td style={styles.td}>
                          {r.status === 'REJECTED' ? (r.attempt_number || 1) : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', background: '#080C14', padding: '20px' },
  wrapper: { maxWidth: '900px', margin: '0 auto' },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
    paddingTop: '20px'
  },
  title: { color: '#00E5FF', fontSize: '22px' },
  logoutBtn: {
    background: 'transparent',
    color: '#EF4444',
    border: '1px solid #EF4444',
    padding: '8px 16px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '13px'
  },
  welcome: { color: '#888', marginBottom: '24px', fontSize: '14px' },
  statsRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr 1fr 1fr',
    gap: '16px',
    marginBottom: '24px'
  },
  statCard: {
    background: '#0D1421',
    border: '1px solid #1A2540',
    borderRadius: '12px',
    padding: '20px',
    textAlign: 'center'
  },
  statNumber: {
    color: '#00E5FF',
    fontSize: '32px',
    fontWeight: 'bold',
    margin: '0 0 4px 0'
  },
  statLabel: { color: '#888', fontSize: '12px', margin: 0 },
  newKycBtn: {
    width: '100%',
    padding: '14px',
    background: '#00E5FF',
    color: '#000',
    border: 'none',
    borderRadius: '10px',
    fontSize: '15px',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginBottom: '24px'
  },
  tableWrapper: {
    background: '#0D1421',
    border: '1px solid #1A2540',
    borderRadius: '12px',
    padding: '24px'
  },
  tableTitle: { color: '#00E5FF', fontSize: '16px', marginBottom: '16px' },
  noRecords: { color: '#888', textAlign: 'center', padding: '20px' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: {
    color: '#888',
    fontSize: '12px',
    textAlign: 'left',
    padding: '10px',
    borderBottom: '1px solid #1A2540',
    textTransform: 'uppercase',
    letterSpacing: '1px'
  },
  tr: { borderBottom: '1px solid #0D1421' },
  td: { color: 'white', fontSize: '13px', padding: '12px 10px' },
  badge: {
    padding: '4px 10px',
    borderRadius: '20px',
    fontSize: '11px',
    fontWeight: 'bold',
    color: '#000'
  }
};

export default Dashboard;

